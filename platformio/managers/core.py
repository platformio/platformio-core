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

import os
import subprocess
import sys
from os.path import dirname, join

from platformio import __version__, exception, fs
from platformio.compat import PY2, WINDOWS
from platformio.managers.package import PackageManager
from platformio.proc import copy_pythonpath_to_osenv, get_pythonexe_path
from platformio.project.config import ProjectConfig

CORE_PACKAGES = {
    "contrib-piohome": "~3.1.0",
    "contrib-pysite": "~2.%d%d.0" % (sys.version_info[0], sys.version_info[1]),
    "tool-pioplus": "^2.6.1",
    "tool-unity": "~1.20500.0",
    "tool-scons": "~2.20501.7" if PY2 else "~3.30102.0",
    "tool-cppcheck": "~1.189.0",
    "tool-clangtidy": "^1.80000.0",
    "tool-pvs-studio": "~7.5.0",
}

PIOPLUS_AUTO_UPDATES_MAX = 100

# pylint: disable=arguments-differ


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


def inject_contrib_pysite():
    from site import addsitedir  # pylint: disable=import-outside-toplevel

    contrib_pysite_dir = get_core_package_dir("contrib-pysite")
    if contrib_pysite_dir in sys.path:
        return
    addsitedir(contrib_pysite_dir)
    sys.path.insert(0, contrib_pysite_dir)


def pioplus_call(args, **kwargs):
    if WINDOWS and sys.version_info < (2, 7, 6):
        raise exception.PlatformioException(
            "PlatformIO Core Plus v%s does not run under Python version %s.\n"
            "Minimum supported version is 2.7.6, please upgrade Python.\n"
            "Python 3 is not yet supported.\n" % (__version__, sys.version)
        )

    pioplus_path = join(get_core_package_dir("tool-pioplus"), "pioplus")
    pythonexe_path = get_pythonexe_path()
    os.environ["PYTHONEXEPATH"] = pythonexe_path
    os.environ["PYTHONPYSITEDIR"] = get_core_package_dir("contrib-pysite")
    os.environ["PIOCOREPYSITEDIR"] = dirname(fs.get_source_dir() or "")
    if dirname(pythonexe_path) not in os.environ["PATH"].split(os.pathsep):
        os.environ["PATH"] = (os.pathsep).join(
            [dirname(pythonexe_path), os.environ["PATH"]]
        )
    copy_pythonpath_to_osenv()
    code = subprocess.call([pioplus_path] + args, **kwargs)

    # handle remote update request
    if code == 13:
        count_attr = "_update_count"
        try:
            count_value = getattr(pioplus_call, count_attr)
        except AttributeError:
            count_value = 0
            setattr(pioplus_call, count_attr, 1)
        count_value += 1
        setattr(pioplus_call, count_attr, count_value)
        if count_value < PIOPLUS_AUTO_UPDATES_MAX:
            update_core_packages()
            return pioplus_call(args, **kwargs)

    # handle reload request
    elif code == 14:
        return pioplus_call(args, **kwargs)

    if code != 0:
        raise exception.ReturnErrorCode(1)

    return True
