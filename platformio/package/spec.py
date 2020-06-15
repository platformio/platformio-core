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

import tarfile

from platformio.compat import get_object_members
from platformio.package.manifest.parser import ManifestFileType


class PackageType(object):
    LIBRARY = "library"
    PLATFORM = "platform"
    TOOL = "tool"

    @classmethod
    def items(cls):
        return get_object_members(cls)

    @classmethod
    def get_manifest_map(cls):
        return {
            cls.PLATFORM: (ManifestFileType.PLATFORM_JSON,),
            cls.LIBRARY: (
                ManifestFileType.LIBRARY_JSON,
                ManifestFileType.LIBRARY_PROPERTIES,
                ManifestFileType.MODULE_JSON,
            ),
            cls.TOOL: (ManifestFileType.PACKAGE_JSON,),
        }

    @classmethod
    def from_archive(cls, path):
        assert path.endswith("tar.gz")
        manifest_map = cls.get_manifest_map()
        with tarfile.open(path, mode="r:gz") as tf:
            for t in sorted(cls.items().values()):
                for manifest in manifest_map[t]:
                    try:
                        if tf.getmember(manifest):
                            return t
                    except KeyError:
                        pass
        return None


class PackageSpec(object):
    def __init__(self, raw=None, organization=None, name=None, version=None):
        if raw is not None:
            organization, name, version = self.parse(raw)

        self.organization = organization
        self.name = name
        self.version = version

    @staticmethod
    def parse(raw):
        organization = None
        name = None
        version = None
        raw = raw.strip()
        if raw.startswith("@") and "/" in raw:
            tokens = raw[1:].split("/", 1)
            organization = tokens[0].strip()
            raw = tokens[1]
        if "@" in raw:
            name, version = raw.split("@", 1)
            name = name.strip()
            version = version.strip()
        else:
            name = raw.strip()

        return organization, name, version
