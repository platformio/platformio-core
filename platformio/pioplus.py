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

PACKAGE_DEPS = {
    "pysite": {
        "name": "pysite-pioplus",
        "requirements": ">=0.3.0,<2"
    },
    "tool": {
        "name": "tool-pioplus",
        "requirements": ">=0.6.6,<2"
    }
}

AUTO_UPDATES_MAX = 100


class PioPlusPackageManager(PackageManager):

    def __init__(self):
        PackageManager.__init__(
            self,
            join(util.get_home_dir(), "packages"), [
                "https://dl.bintray.com/platformio/dl-packages/manifest.json",
                "http%s://dl.platformio.org/packages/manifest.json" %
                ("" if sys.version_info < (2, 7, 9) else "s")
            ])


def pioplus_install():
    pm = PioPlusPackageManager()
    for item in PACKAGE_DEPS.values():
        pm.install(item['name'], item['requirements'], silent=True)


def pioplus_update():
    pm = PioPlusPackageManager()
    for item in PACKAGE_DEPS.values():
        package_dir = pm.get_package_dir(item['name'])
        if package_dir:
            pm.update(item['name'], item['requirements'])


def pioplus_call(args, **kwargs):
    pioplus_install()
    pm = PioPlusPackageManager()
    pioplus_path = join(
        pm.get_package_dir(PACKAGE_DEPS['tool']['name'],
                           PACKAGE_DEPS['tool']['requirements']), "pioplus")
    os.environ['PYTHONEXEPATH'] = util.get_pythonexe_path()
    os.environ['PYTHONPYSITEDIR'] = pm.get_package_dir(
        PACKAGE_DEPS['pysite']['name'], PACKAGE_DEPS['pysite']['requirements'])
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
        if count_value < AUTO_UPDATES_MAX:
            pioplus_update()
            return pioplus_call(args, **kwargs)

    # handle reload request
    elif code == 14:
        return pioplus_call(args, **kwargs)

    if code != 0:
        raise exception.ReturnErrorCode(1)
