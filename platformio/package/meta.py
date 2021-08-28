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
import re
import tarfile
from binascii import crc32

import semantic_version

from platformio.compat import get_object_members, hashlib_encode_data, string_types
from platformio.package.manifest.parser import ManifestFileType
from platformio.package.version import cast_version_to_semver

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


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


class PackageOutdatedResult(object):
    def __init__(self, current, latest=None, wanted=None, detached=False):
        self.current = current
        self.latest = latest
        self.wanted = wanted
        self.detached = detached

    def __repr__(self):
        return (
            "PackageOutdatedResult <current={current} latest={latest} wanted={wanted} "
            "detached={detached}>".format(
                current=self.current,
                latest=self.latest,
                wanted=self.wanted,
                detached=self.detached,
            )
        )

    def __setattr__(self, name, value):
        if (
            value
            and name in ("current", "latest", "wanted")
            and not isinstance(value, semantic_version.Version)
        ):
            value = cast_version_to_semver(str(value))
        return super(PackageOutdatedResult, self).__setattr__(name, value)

    def is_outdated(self, allow_incompatible=False):
        if self.detached or not self.latest or self.current == self.latest:
            return False
        if allow_incompatible:
            return self.current != self.latest
        if self.wanted:
            return self.current != self.wanted
        return True


class PackageSpec(object):  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=redefined-builtin,too-many-arguments
        self, raw=None, owner=None, id=None, name=None, requirements=None, url=None
    ):
        self._requirements = None
        self.owner = owner
        self.id = id
        self.name = name
        self.url = url
        self.raw = raw
        if requirements:
            try:
                self.requirements = requirements
            except ValueError as exc:
                if not self.name or self.url or self.raw:
                    raise exc
                self.raw = "%s=%s" % (self.name, requirements)
        self._name_is_custom = False
        self._parse(self.raw)

    def __eq__(self, other):
        return all(
            [
                self.owner == other.owner,
                self.id == other.id,
                self.name == other.name,
                self.requirements == other.requirements,
                self.url == other.url,
            ]
        )

    def __hash__(self):
        return crc32(
            hashlib_encode_data(
                "%s-%s-%s-%s-%s"
                % (self.owner, self.id, self.name, self.requirements, self.url)
            )
        )

    def __repr__(self):
        return (
            "PackageSpec <owner={owner} id={id} name={name} "
            "requirements={requirements} url={url}>".format(**self.as_dict())
        )

    @property
    def external(self):
        return bool(self.url)

    @property
    def requirements(self):
        return self._requirements

    @requirements.setter
    def requirements(self, value):
        if not value:
            self._requirements = None
            return
        self._requirements = (
            value
            if isinstance(value, semantic_version.SimpleSpec)
            else semantic_version.SimpleSpec(str(value))
        )

    def humanize(self):
        result = ""
        if self.url:
            result = self.url
        elif self.name:
            if self.owner:
                result = self.owner + "/"
            result += self.name
        elif self.id:
            result = "id:%d" % self.id
        if self.requirements:
            result += " @ " + str(self.requirements)
        return result

    def has_custom_name(self):
        return self._name_is_custom

    def as_dict(self):
        return dict(
            owner=self.owner,
            id=self.id,
            name=self.name,
            requirements=str(self.requirements) if self.requirements else None,
            url=self.url,
        )

    def as_dependency(self):
        if self.url:
            return self.raw or self.url
        result = ""
        if self.name:
            result = "%s/%s" % (self.owner, self.name) if self.owner else self.name
        elif self.id:
            result = str(self.id)
        assert result
        if self.requirements:
            result = "%s@%s" % (result, self.requirements)
        return result

    def _parse(self, raw):
        if raw is None:
            return
        if not isinstance(raw, string_types):
            raw = str(raw)
        raw = raw.strip()

        parsers = (
            self._parse_local_file,
            self._parse_requirements,
            self._parse_custom_name,
            self._parse_id,
            self._parse_owner,
            self._parse_url,
        )
        for parser in parsers:
            if raw is None:
                break
            raw = parser(raw)

        # if name is not custom, parse it from URL
        if not self.name and self.url:
            self.name = self._parse_name_from_url(self.url)
        elif raw:
            # the leftover is a package name
            self.name = raw

    @staticmethod
    def _parse_local_file(raw):
        if raw.startswith("file://") or not any(c in raw for c in ("/", "\\")):
            return raw
        if os.path.exists(raw):
            return "file://%s" % raw
        return raw

    def _parse_requirements(self, raw):
        if "@" not in raw or raw.startswith("file://"):
            return raw
        tokens = raw.rsplit("@", 1)
        if any(s in tokens[1] for s in (":", "/")):
            return raw
        self.requirements = tokens[1].strip()
        return tokens[0].strip()

    def _parse_custom_name(self, raw):
        if "=" not in raw or raw.startswith("id="):
            return raw
        tokens = raw.split("=", 1)
        if "/" in tokens[0]:
            return raw
        self.name = tokens[0].strip()
        self._name_is_custom = True
        return tokens[1].strip()

    def _parse_id(self, raw):
        if raw.isdigit():
            self.id = int(raw)
            return None
        if raw.startswith("id="):
            return self._parse_id(raw[3:])
        return raw

    def _parse_owner(self, raw):
        if raw.count("/") != 1 or "@" in raw:
            return raw
        tokens = raw.split("/", 1)
        self.owner = tokens[0].strip()
        self.name = tokens[1].strip()
        return None

    def _parse_url(self, raw):
        if not any(s in raw for s in ("@", ":", "/")):
            return raw
        self.url = raw.strip()
        parts = urlparse(self.url)

        # if local file or valid URL with scheme vcs+protocol://
        if parts.scheme == "file" or "+" in parts.scheme or self.url.startswith("git+"):
            return None

        # parse VCS
        git_conditions = [
            parts.path.endswith(".git"),
            # Handle GitHub URL (https://github.com/user/package)
            parts.netloc in ("github.com", "gitlab.com", "bitbucket.com")
            and not parts.path.endswith((".zip", ".tar.gz")),
        ]
        hg_conditions = [
            # Handle Developer Mbed URL
            # (https://developer.mbed.org/users/user/code/package/)
            # (https://os.mbed.com/users/user/code/package/)
            parts.netloc
            in ("mbed.com", "os.mbed.com", "developer.mbed.org")
        ]
        if any(git_conditions):
            self.url = "git+" + self.url
        elif any(hg_conditions):
            self.url = "hg+" + self.url

        return None

    @staticmethod
    def _parse_name_from_url(url):
        if url.endswith("/"):
            url = url[:-1]
        stop_chars = ["#", "?"]
        if url.startswith("file://"):
            stop_chars.append("@")  # detached path
        for c in stop_chars:
            if c in url:
                url = url[: url.index(c)]

        # parse real repository name from Github
        parts = urlparse(url)
        if parts.netloc == "github.com" and parts.path.count("/") > 2:
            return parts.path.split("/")[2]

        name = os.path.basename(url)
        if "." in name:
            return name.split(".", 1)[0].strip()
        return name


class PackageMetaData(object):
    def __init__(  # pylint: disable=redefined-builtin
        self, type, name, version, spec=None
    ):
        # assert type in PackageType.items().values()
        if spec:
            assert isinstance(spec, PackageSpec)
        self.type = type
        self.name = name
        self._version = None
        self.version = version
        self.spec = spec

    def __repr__(self):
        return (
            "PackageMetaData <type={type} name={name} version={version} "
            "spec={spec}".format(**self.as_dict())
        )

    def __eq__(self, other):
        return all(
            [
                self.type == other.type,
                self.name == other.name,
                self.version == other.version,
                self.spec == other.spec,
            ]
        )

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if not value:
            self._version = None
            return
        self._version = (
            value
            if isinstance(value, semantic_version.Version)
            else cast_version_to_semver(value)
        )

    def as_dict(self):
        return dict(
            type=self.type,
            name=self.name,
            version=str(self.version),
            spec=self.spec.as_dict() if self.spec else None,
        )

    def dump(self, path):
        with open(path, mode="w", encoding="utf8") as fp:
            return json.dump(self.as_dict(), fp)

    @staticmethod
    def load(path):
        with open(path, encoding="utf8") as fp:
            data = json.load(fp)
            if data["spec"]:
                data["spec"] = PackageSpec(**data["spec"])
            return PackageMetaData(**data)


class PackageItem(object):

    METAFILE_NAME = ".piopm"

    def __init__(self, path, metadata=None):
        self.path = path
        self.metadata = metadata
        if not self.metadata and self.exists():
            self.metadata = self.load_meta()

    def __repr__(self):
        return "PackageItem <path={path} metadata={metadata}".format(
            path=self.path, metadata=self.metadata
        )

    def __eq__(self, other):
        if not self.path or not other.path:
            return self.path == other.path
        return os.path.realpath(self.path) == os.path.realpath(other.path)

    def __hash__(self):
        return hash(os.path.realpath(self.path))

    def exists(self):
        return os.path.isdir(self.path)

    def get_safe_dirname(self):
        assert self.metadata
        return re.sub(r"[^\da-z\_\-\. ]", "_", self.metadata.name, flags=re.I)

    def get_metafile_locations(self):
        return [
            os.path.join(self.path, ".git"),
            os.path.join(self.path, ".hg"),
            os.path.join(self.path, ".svn"),
            self.path,
        ]

    def load_meta(self):
        assert self.exists()
        for location in self.get_metafile_locations():
            manifest_path = os.path.join(location, self.METAFILE_NAME)
            if os.path.isfile(manifest_path):
                return PackageMetaData.load(manifest_path)
        return None

    def dump_meta(self):
        assert self.exists()
        location = None
        for location in self.get_metafile_locations():
            if os.path.isdir(location):
                break
        assert location
        return self.metadata.dump(os.path.join(location, self.METAFILE_NAME))
