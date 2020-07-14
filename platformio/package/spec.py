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
import tarfile

from platformio.compat import get_object_members, string_types
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
    def __init__(  # pylint: disable=redefined-builtin,too-many-arguments
        self, raw=None, ownername=None, id=None, name=None, requirements=None, url=None
    ):
        self.ownername = ownername
        self.id = id
        self.name = name
        self.requirements = requirements
        self.url = url

        self._parse(raw)

    def __repr__(self):
        return (
            "PackageSpec <ownername={ownername} id={id} name={name} "
            "requirements={requirements} url={url}>".format(
                ownername=self.ownername,
                id=self.id,
                name=self.name,
                requirements=self.requirements,
                url=self.url,
            )
        )

    def __eq__(self, other):
        return all(
            [
                self.ownername == other.ownername,
                self.id == other.id,
                self.name == other.name,
                self.requirements == other.requirements,
                self.url == other.url,
            ]
        )

    def _parse(self, raw):
        if raw is None:
            return
        if not isinstance(raw, string_types):
            raw = str(raw)
        raw = raw.strip()

        parsers = (
            self._parse_requirements,
            self._parse_fixed_name,
            self._parse_id,
            self._parse_ownername,
            self._parse_url,
        )
        for parser in parsers:
            if raw is None:
                break
            raw = parser(raw)

        # if name is not fixed, parse it from URL
        if not self.name and self.url:
            self.name = self._parse_name_from_url(self.url)
        elif raw:
            # the leftover is a package name
            self.name = raw

    def _parse_requirements(self, raw):
        if "@" not in raw:
            return raw
        tokens = raw.rsplit("@", 1)
        if any(s in tokens[1] for s in (":", "/")):
            return raw
        self.requirements = tokens[1].strip()
        return tokens[0].strip()

    def _parse_fixed_name(self, raw):
        if "=" not in raw or raw.startswith("id="):
            return raw
        tokens = raw.split("=", 1)
        if "/" in tokens[0]:
            return raw
        self.name = tokens[0].strip()
        return tokens[1].strip()

    def _parse_id(self, raw):
        if raw.isdigit():
            self.id = int(raw)
            return None
        if raw.startswith("id="):
            return self._parse_id(raw[3:])
        return raw

    def _parse_ownername(self, raw):
        if raw.count("/") != 1 or "@" in raw:
            return raw
        tokens = raw.split("/", 1)
        self.ownername = tokens[0].strip()
        self.name = tokens[1].strip()
        return None

    def _parse_url(self, raw):
        if not any(s in raw for s in ("@", ":", "/")):
            return raw
        self.url = raw.strip()
        return None

    @staticmethod
    def _parse_name_from_url(url):
        if url.endswith("/"):
            url = url[:-1]
        for c in ("#", "?"):
            if c in url:
                url = url[: url.index(c)]
        name = os.path.basename(url)
        if "." in name:
            return name.split(".", 1)[0].strip()
        return name
