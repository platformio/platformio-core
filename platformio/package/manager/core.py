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
import subprocess
import sys

from platformio import __core_packages__, exception, fs, util
from platformio.compat import PY2
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.proc import get_pythonexe_path


def get_core_package_dir(name):
    if name not in __core_packages__:
        raise exception.PlatformioException("Please upgrade PlatformIO Core")
    pm = ToolPackageManager()
    spec = PackageSpec(
        owner="platformio", name=name, requirements=__core_packages__[name]
    )
    pkg = pm.get_package(spec)
    if pkg:
        return pkg.path
    assert pm.install(spec)
    _remove_unnecessary_packages()
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
        _remove_unnecessary_packages()
    return True


def _remove_unnecessary_packages():
    pm = ToolPackageManager()
    best_pkg_versions = {}
    for name, requirements in __core_packages__.items():
        spec = PackageSpec(owner="platformio", name=name, requirements=requirements)
        pkg = pm.get_package(spec)
        if not pkg:
            continue
        best_pkg_versions[pkg.metadata.name] = pkg.metadata.version
    for pkg in pm.get_installed():
        if pkg.metadata.name not in best_pkg_versions:
            continue
        if pkg.metadata.version != best_pkg_versions[pkg.metadata.name]:
            pm.uninstall(pkg)


def inject_contrib_pysite(verify_openssl=False):
    # pylint: disable=import-outside-toplevel
    from site import addsitedir

    contrib_pysite_dir = get_core_package_dir("contrib-pysite")
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
        build_contrib_pysite_deps(get_core_package_dir("contrib-pysite"))

    return True


def build_contrib_pysite_deps(target_dir):
    if os.path.isdir(target_dir):
        fs.rmtree(target_dir)
    os.makedirs(target_dir)
    with open(os.path.join(target_dir, "package.json"), "w") as fp:
        json.dump(
            dict(
                name="contrib-pysite",
                version="2.%d%d.0" % (sys.version_info.major, sys.version_info.minor),
                system=util.get_systype(),
            ),
            fp,
        )

    pythonexe = get_pythonexe_path()
    for dep in get_contrib_pysite_deps():
        subprocess.check_call(
            [
                pythonexe,
                "-m",
                "pip",
                "install",
                # "--no-cache-dir",
                "--no-compile",
                "-t",
                target_dir,
                dep,
            ]
        )
    return True


def get_contrib_pysite_deps():
    sys_type = util.get_systype()
    py_version = "%d%d" % (sys.version_info.major, sys.version_info.minor)

    twisted_version = "19.10.0" if PY2 else "20.3.0"
    result = [
        "twisted == %s" % twisted_version,
        "autobahn == 20.4.3",
        "json-rpc == 1.13.0",
    ]

    # twisted[tls], see setup.py for %twisted_version%
    result.extend(
        ["pyopenssl >= 16.0.0", "service_identity >= 18.1.0", "idna >= 0.6, != 2.3"]
    )

    # zeroconf
    if PY2:
        result.append(
            "https://github.com/ivankravets/python-zeroconf/" "archive/pio-py27.zip"
        )
    else:
        result.append("zeroconf == 0.26.0")

    if "windows" in sys_type:
        result.append("pypiwin32 == 223")
        # workaround for twisted wheels
        twisted_wheel = (
            "https://download.lfd.uci.edu/pythonlibs/g5apjq5m/Twisted-"
            "%s-cp%s-cp%sm-win%s.whl"
            % (
                twisted_version,
                py_version,
                py_version,
                "_amd64" if "amd64" in sys_type else "32",
            )
        )
        result[0] = twisted_wheel
    return result
