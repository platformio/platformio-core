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
from urllib.parse import urlparse

import semantic_version

from platformio import fs
from platformio.compat import get_object_members, hashlib_encode_data, string_types
from platformio.package.manifest.parser import ManifestFileType
from platformio.package.version import SemanticVersionError, cast_version_to_semver
from platformio.util import items_in_list


class PackageType:
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


class PackageCompatibility:
    KNOWN_QUALIFIERS = (
        "owner",
        "name",
        "version",
        "platforms",
        "frameworks",
        "authors",
    )

    @classmethod
    def from_dependency(cls, dependency):
        assert isinstance(dependency, dict)
        qualifiers = {
            key: value
            for key, value in dependency.items()
            if key in cls.KNOWN_QUALIFIERS
        }
        return PackageCompatibility(**qualifiers)

    def __init__(self, **kwargs):
        self.qualifiers = {}
        for key, value in kwargs.items():
            if key not in self.KNOWN_QUALIFIERS:
                raise ValueError(
                    "Unknown package compatibility qualifier -> `%s`" % key
                )
            self.qualifiers[key] = value

    def __repr__(self):
        return "PackageCompatibility <%s>" % self.qualifiers

    def to_search_qualifiers(self, fields=None):
        result = {}
        for name, value in self.qualifiers.items():
            if not fields or name in fields:
                result[name] = value
        return result

    def is_compatible(self, other):
        assert isinstance(other, PackageCompatibility)
        for key, current_value in self.qualifiers.items():
            other_value = other.qualifiers.get(key)
            if not current_value or not other_value:
                continue
            if any(isinstance(v, list) for v in (current_value, other_value)):
                if not items_in_list(current_value, other_value):
                    return False
                continue
            if key == "version":
                if not self._compare_versions(current_value, other_value):
                    return False
                continue
            if current_value != other_value:
                return False
        return True

    def _compare_versions(self, current, other):
        if current == other:
            return True
        try:
            version = (
                other
                if isinstance(other, semantic_version.Version)
                else cast_version_to_semver(other)
            )
            return version in semantic_version.SimpleSpec(current)
        except ValueError:
            pass
        return False


class PackageOutdatedResult:
    UPDATE_INCREMENT_MAJOR = "major"
    UPDATE_INCREMENT_MINOR = "minor"
    UPDATE_INCREMENT_PATCH = "patch"

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
        return super().__setattr__(name, value)

    @property
    def update_increment_type(self):
        if not self.current or not self.latest:
            return None
        patch_conds = [
            self.current.major == self.latest.major,
            self.current.minor == self.latest.minor,
        ]
        if all(patch_conds):
            return self.UPDATE_INCREMENT_PATCH
        minor_conds = [
            self.current.major == self.latest.major,
            self.current.major > 0,
        ]
        if all(minor_conds):
            return self.UPDATE_INCREMENT_MINOR
        return self.UPDATE_INCREMENT_MAJOR

    def is_outdated(self, allow_incompatible=False):
        if self.detached or not self.latest or self.current == self.latest:
            return False
        if allow_incompatible:
            return self.current != self.latest
        if self.wanted:
            return self.current != self.wanted
        return True


class PackageSpec:  # pylint: disable=too-many-instance-attributes
    def __init__(  # pylint: disable=redefined-builtin,too-many-arguments,too-many-positional-arguments
        self, raw=None, owner=None, id=None, name=None, requirements=None, uri=None
    ):
        self._requirements = None
        self.owner = owner
        self.id = id
        self.name = name
        self.uri = uri
        self.raw = raw
        if requirements:
            try:
                self.requirements = requirements
            except SemanticVersionError as exc:
                if not self.name or self.uri or self.raw:
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
                self.uri == other.uri,
            ]
        )

    def __hash__(self):
        return crc32(
            hashlib_encode_data(
                "%s-%s-%s-%s-%s"
                % (self.owner, self.id, self.name, self.requirements, self.uri)
            )
        )

    def __repr__(self):
        return (
            "PackageSpec <owner={owner} id={id} name={name} "
            "requirements={requirements} uri={uri}>".format(**self.as_dict())
        )

    @property
    def external(self):
        return bool(self.uri)

    @property
    def symlink(self):
        return self.uri and self.uri.startswith("symlink://")

    @property
    def requirements(self):
        return self._requirements

    @requirements.setter
    def requirements(self, value):
        if not value:
            self._requirements = None
            return
        try:
            self._requirements = (
                value
                if isinstance(value, semantic_version.SimpleSpec)
                else semantic_version.SimpleSpec(str(value))
            )
        except ValueError as exc:
            raise SemanticVersionError(exc) from exc

    def humanize(self):
        result = ""
        if self.uri:
            result = self.uri
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
            uri=self.uri,
        )

    def as_dependency(self):
        if self.uri:
            return self.raw or self.uri
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
            self._parse_uri,
        )
        for parser in parsers:
            if raw is None:
                break
            raw = parser(raw)

        # if name is not custom, parse it from URI
        if not self.name and self.uri:
            self.name = self._parse_name_from_uri(self.uri)
        elif raw:
            # the leftover is a package name
            self.name = raw

    @staticmethod
    def _parse_local_file(raw):
        if raw.startswith(("file://", "symlink://")) or not any(
            c in raw for c in ("/", "\\")
        ):
            return raw
        if os.path.exists(raw):
            return "file://%s" % raw
        return raw

    def _parse_requirements(self, raw):
        if "@" not in raw or raw.startswith(("file://", "symlink://")):
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

    def _parse_uri(self, raw):
        if not any(s in raw for s in ("@", ":", "/")):
            return raw
        self.uri = raw.strip()
        parts = urlparse(self.uri)

        # if local file or valid URI with scheme vcs+protocol://
        if (
            parts.scheme in ("file", "symlink://")
            or "+" in parts.scheme
            or self.uri.startswith("git+")
        ):
            return None

        # parse VCS
        git_conditions = [
            parts.path.endswith(".git"),
            # Handle GitHub URL (https://github.com/user/package)
            parts.netloc in ("github.com", "gitlab.com", "bitbucket.com")
            and not parts.path.endswith((".zip", ".tar.gz", ".tar.xz")),
        ]
        hg_conditions = [
            # Handle Developer Mbed URL
            # (https://developer.mbed.org/users/user/code/package/)
            # (https://os.mbed.com/users/user/code/package/)
            parts.netloc
            in ("mbed.com", "os.mbed.com", "developer.mbed.org")
        ]
        if any(git_conditions):
            self.uri = "git+" + self.uri
        elif any(hg_conditions):
            self.uri = "hg+" + self.uri

        return None

    @staticmethod
    def _parse_name_from_uri(uri):
        if uri.endswith("/"):
            uri = uri[:-1]
        stop_chars = ["#", "?"]
        if uri.startswith(("file://", "symlink://")):
            stop_chars.append("@")  # detached path
        for c in stop_chars:
            if c in uri:
                uri = uri[: uri.index(c)]

        # parse real repository name from Github
        parts = urlparse(uri)
        if parts.netloc == "github.com" and parts.path.count("/") > 2:
            return parts.path.split("/")[2]

        name = os.path.basename(uri)
        if "." in name:
            return name.split(".", 1)[0].strip()
        return name


class PackageMetadata:
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
            "PackageMetadata <type={type} name={name} version={version} "
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
        data = fs.load_json(path)
        if data["spec"]:
            # legacy support for Core<5.3 packages
            if "url" in data["spec"]:
                data["spec"]["uri"] = data["spec"]["url"]
                del data["spec"]["url"]
            data["spec"] = PackageSpec(**data["spec"])
        return PackageMetadata(**data)


class PackageItem:
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
        conds = [
            (
                os.path.realpath(self.path) == os.path.realpath(other.path)
                if self.path and other.path
                else self.path == other.path
            ),
            self.metadata == other.metadata,
        ]
        return all(conds)

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
                return PackageMetadata.load(manifest_path)
        return None

    def dump_meta(self):
        assert self.exists()
        location = None
        for location in self.get_metafile_locations():
            if os.path.isdir(location):
                break
        assert location
        return self.metadata.dump(os.path.join(location, self.METAFILE_NAME))
