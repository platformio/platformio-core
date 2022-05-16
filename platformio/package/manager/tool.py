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

from platformio.package.manager.base import BasePackageManager
from platformio.package.meta import PackageType
from platformio.project.config import ProjectConfig


class ToolPackageManager(BasePackageManager):  # pylint: disable=too-many-ancestors
    def __init__(self, package_dir=None):
        super().__init__(
            PackageType.TOOL,
            package_dir
            or ProjectConfig.get_instance().get("platformio", "packages_dir"),
        )

    @property
    def manifest_names(self):
        return PackageType.get_manifest_map()[PackageType.TOOL]
