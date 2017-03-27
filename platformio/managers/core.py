# Copyright 2014-present PlatformIO <contact@platformio.org>
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
from os.path import join

from platformio import exception, util
from platformio.managers.package import PackageManager

CORE_PACKAGES = {
    "pysite-pioplus": ">=0.3.0,<2",
    "tool-pioplus": ">=0.6.10,<2",
    "tool-unity": "~1.20302.1",
    "tool-scons": "~3.20501.2"
}

PIOPLUS_AUTO_UPDATES_MAX = 100


class CorePackageManager(PackageManager):

    def __init__(self):
        PackageManager.__init__(
            self,
            join(util.get_home_dir(), "packages"), [
                "https://dl.bintray.com/platformio/dl-packages/manifest.json",
                "http%s://dl.platformio.org/packages/manifest.json" %
                ("" if sys.version_info < (2, 7, 9) else "s")
            ])


def get_core_package_dir(name):
    assert name in CORE_PACKAGES
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


def pioplus_call(args, **kwargs):
    pioplus_path = join(get_core_package_dir("tool-pioplus"), "pioplus")
    os.environ['PYTHONEXEPATH'] = util.get_pythonexe_path()
    os.environ['PYTHONPYSITEDIR'] = get_core_package_dir("pysite-pioplus")
    util.copy_pythonpath_to_osenv()
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
