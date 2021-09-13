# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import shutil
import subprocess
import sys
from datetime import date

from platformio import __core_packages__, exception, fs, util
from platformio.package.exception import UnknownPackageError
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageItem, PackageSpec
from platformio.proc import get_pythonexe_path


def get_installed_core_packages():
    result = []
    pm = ToolPackageManager()
    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="platformio", name=name, requirements=requirements)
        pkg = pm.get_package(spec)
        if pkg:
            result.append(pkg)
    return result


def get_core_package_dir(name, auto_install=True):
    if name not in __core_packages__:
        raise exception.PlatformioException("Please upgrade PlatformIO Core")
    pm = ToolPackageManager()
    spec = PackageSpec(
        owner="platformio", name=name, requirements=__core_packages__[name]
    )
    pkg = pm.get_package(spec)
    if pkg:
        return pkg.path
    if not auto_install:
        return None
    assert pm.install(spec)
    remove_unnecessary_core_packages()
    return pm.get_package(spec).path


def update_core_packages(only_check=False, silent=False):
    pm = ToolPackageManager()
    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="platformio", name=name, requirements=requirements)
        pkg = pm.get_package(spec)
        if not pkg:
            continue
        if not silent or pm.outdated(pkg, spec).is_outdated():
            pm.update(pkg, spec, only_check=only_check)
    if not only_check:
        remove_unnecessary_core_packages()
    return True


def remove_unnecessary_core_packages(dry_run=False):
    candidates = []
    pm = ToolPackageManager()
    best_pkg_versions = {}

    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="platformio", name=name, requirements=requirements)
        pkg = pm.get_package(spec)
        if not pkg:
            continue
        # pylint: disable=no-member
        best_pkg_versions[pkg.metadata.name] = pkg.metadata.version

    for pkg in pm.get_installed():
        skip_conds = [
            os.path.isfile(os.path.join(pkg.path, ".piokeep")),
            pkg.metadata.spec.owner != "platformio",
            pkg.metadata.name not in best_pkg_versions,
            pkg.metadata.name in best_pkg_versions
            and pkg.metadata.version == best_pkg_versions[pkg.metadata.name],
        ]
        if not any(skip_conds):
            candidates.append(pkg)

    if dry_run:
        return candidates

    for pkg in candidates:
        pm.uninstall(pkg)

    return candidates


def inject_contrib_pysite(verify_openssl=False):
    # pylint: disable=import-outside-toplevel
    from site import addsitedir

    try:
        contrib_pysite_dir = get_core_package_dir("contrib-pysite")
    except UnknownPackageError:
        pm = ToolPackageManager()
        contrib_pysite_dir = build_contrib_pysite_package(
            os.path.join(pm.package_dir, "contrib-pysite")
        )

    if contrib_pysite_dir in sys.path:
        return True

    addsitedir(contrib_pysite_dir)
    sys.path.insert(0, contrib_pysite_dir)

    if not verify_openssl:
        return True

    try:
        # pylint: disable=import-error,unused-import,unused-variable
        from OpenSSL import SSL
    except:  # pylint: disable=bare-except
        build_contrib_pysite_package(contrib_pysite_dir)

    return True


def build_contrib_pysite_package(target_dir, with_metadata=True):
    systype = util.get_systype()
    if os.path.isdir(target_dir):
        fs.rmtree(target_dir)
    os.makedirs(target_dir)

    # issue 3865: There is no "rustup" in "Raspbian GNU/Linux 10 (buster)"
    os.environ["CRYPTOGRAPHY_DONT_BUILD_RUST"] = "1"

    # build dependencies
    args = [
        get_pythonexe_path(),
        "-m",
        "pip",
        "install",
        "--no-compile",
        "-t",
        target_dir,
    ]
    if "linux" in systype:
        args.extend(["--no-binary", ":all:"])
    for dep in get_contrib_pysite_deps():
        subprocess.check_call(args + [dep])

    # build manifests
    with open(
        os.path.join(target_dir, "package.json"), mode="w", encoding="utf8"
    ) as fp:
        json.dump(
            dict(
                name="contrib-pysite",
                version="2.%d%d.%s"
                % (
                    sys.version_info.major,
                    sys.version_info.minor,
                    date.today().strftime("%y%m%d"),
                ),
                system=list(
                    set([systype, "linux_armv6l", "linux_armv7l", "linux_armv8l"])
                )
                if systype.startswith("linux_arm")
                else systype,
                description="Extra Python package for PlatformIO Core",
                keywords=["platformio", "platformio-core"],
                homepage="https://docs.platformio.org/page/core/index.html",
                repository={
                    "type": "git",
                    "url": "https://github.com/platformio/platformio-core",
                },
            ),
            fp,
        )

    # generate package metadata
    if with_metadata:
        pm = ToolPackageManager()
        pkg = PackageItem(target_dir)
        pkg.metadata = pm.build_metadata(
            target_dir, PackageSpec(owner="platformio", name="contrib-pysite")
        )
        pkg.dump_meta()

    # remove unused files
    for root, dirs, files in os.walk(target_dir):
        for t in ("_test", "test", "tests"):
            if t in dirs:
                shutil.rmtree(os.path.join(root, t))
        for name in files:
            if name.endswith((".chm", ".pyc")):
                os.remove(os.path.join(root, name))

    return target_dir


def get_contrib_pysite_deps():
    sys_type = util.get_systype()
    py_version = "%d%d" % (sys.version_info.major, sys.version_info.minor)

    twisted_version = "20.3.0"
    result = [
        "twisted == %s" % twisted_version,
    ]

    # twisted[tls], see setup.py for %twisted_version%
    result.extend(
        ["pyopenssl >= 16.0.0", "service_identity >= 18.1.0", "idna >= 0.6, != 2.3"]
    )

    if "windows" in sys_type:
        result.append("pypiwin32 == 223")
        # workaround for twisted wheels
        twisted_wheel = (
            "https://download.lfd.uci.edu/pythonlibs/x2tqcw5k/Twisted-"
            "%s-cp%s-cp%s-win%s.whl"
            % (
                twisted_version,
                py_version,
                py_version,
                "_amd64" if "amd64" in sys_type else "32",
            )
        )
        result[0] = twisted_wheel
    return result
