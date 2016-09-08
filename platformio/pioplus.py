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
from os.path import dirname, join
from platform import system

from platformio import exception, util
from platformio.managers.package import PackageManager

PACKAGE_PIOPLUS_NAME = "tool-pioplus"


class PioPlusPackageManager(PackageManager):

    def __init__(self):
        PackageManager.__init__(
            self, join(util.get_home_dir(), "packages"),
            ["https://dl.bintray.com/platformio/dl-packages/manifest.json",
             "https://dl.platformio.org/packages/manifest.json"])


def get_pioplusexe_path():
    pm = PioPlusPackageManager()
    package_dir = pm.get_package_dir(PACKAGE_PIOPLUS_NAME)
    if not package_dir:
        pm.install(PACKAGE_PIOPLUS_NAME)
        package_dir = pm.get_package_dir(PACKAGE_PIOPLUS_NAME)
    assert package_dir
    return join(package_dir, "pioplus")


def pioplus_update():
    pm = PioPlusPackageManager()
    if pm.get_package_dir(PACKAGE_PIOPLUS_NAME):
        pm.update(PACKAGE_PIOPLUS_NAME)


def pioplus_call(args, **kwargs):
    pioplus_path = get_pioplusexe_path()
    if system() == "Linux":
        os.environ['LD_LIBRARY_PATH'] = dirname(pioplus_path)
    os.environ['PYTHONEXEPATH'] = util.get_pythonexe_path()
    util.copy_pythonpath_to_osenv()
    if subprocess.call([pioplus_path] + args, **kwargs) != 0:
        raise exception.ReturnErrorCode()
