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

from platformio import exception, util
from platformio.compat import PY2
from platformio.managers.package import PackageManager
from platformio.proc import get_pythonexe_path
from platformio.project.config import ProjectConfig

CORE_PACKAGES = {
    "contrib-piohome": "~3.2.1",
    "contrib-pysite": "~2.%d%d.0" % (sys.version_info.major, sys.version_info.minor),
    "tool-unity": "~1.20500.0",
    "tool-scons": "~2.20501.7" if PY2 else "~3.30102.0",
    "tool-cppcheck": "~1.190.0",
    "tool-clangtidy": "~1.100000.0",
    "tool-pvs-studio": "~7.7.0",
}

# pylint: disable=arguments-differ,signature-differs


class CorePackageManager(PackageManager):
    def __init__(self):
        config = ProjectConfig.get_instance()
        packages_dir = config.get_optional_dir("packages")
        super(CorePackageManager, self).__init__(
            packages_dir,
            [
                "https://dl.bintray.com/platformio/dl-packages/manifest.json",
                "http%s://dl.platformio.org/packages/manifest.json"
                % ("" if sys.version_info < (2, 7, 9) else "s"),
            ],
        )

    def install(  # pylint: disable=keyword-arg-before-vararg
        self, name, requirements=None, *args, **kwargs
    ):
        PackageManager.install(self, name, requirements, *args, **kwargs)
        self.cleanup_packages()
        return self.get_package_dir(name, requirements)

    def update(self, *args, **kwargs):
        result = PackageManager.update(self, *args, **kwargs)
        self.cleanup_packages()
        return result

    def cleanup_packages(self):
        self.cache_reset()
        best_pkg_versions = {}
        for name, requirements in CORE_PACKAGES.items():
            pkg_dir = self.get_package_dir(name, requirements)
            if not pkg_dir:
                continue
            best_pkg_versions[name] = self.load_manifest(pkg_dir)["version"]
        for manifest in self.get_installed():
            if manifest["name"] not in best_pkg_versions:
                continue
            if manifest["version"] != best_pkg_versions[manifest["name"]]:
                self.uninstall(manifest["__pkg_dir"], after_update=True)
        self.cache_reset()
        return True


def get_core_package_dir(name):
    if name not in CORE_PACKAGES:
        raise exception.PlatformioException("Please upgrade PIO Core")
    requirements = CORE_PACKAGES[name]
    pm = CorePackageManager()
    pkg_dir = pm.get_package_dir(name, requirements)
    if pkg_dir:
        return pkg_dir
    return pm.install(name, requirements)


def update_core_packages(only_check=False, silent=False):
    pm = CorePackageManager()
    for name, requirements in CORE_PACKAGES.items():
        pkg_dir = pm.get_package_dir(name)
        if not pkg_dir:
            continue
        if not silent or pm.outdated(pkg_dir, requirements):
            pm.update(name, requirements, only_check=only_check)
    return True


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
        util.rmtree_(target_dir)
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
