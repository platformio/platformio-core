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

import requests

from platformio.compat import get_class_attributes, string_types
from platformio.exception import PlatformioException
from platformio.fs import get_file_contents

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class ManifestException(PlatformioException):
    pass


class ManifestParserException(ManifestException):
    pass


class ManifestFileType(object):
    PLATFORM_JSON = "platform.json"
    LIBRARY_JSON = "library.json"
    LIBRARY_PROPERTIES = "library.properties"
    MODULE_JSON = "module.json"
    PACKAGE_JSON = "package.json"

    @classmethod
    def from_uri(cls, uri):
        if uri.endswith(".properties"):
            return ManifestFileType.LIBRARY_PROPERTIES
        if uri.endswith("platform.json"):
            return ManifestFileType.PLATFORM_JSON
        if uri.endswith("module.json"):
            return ManifestFileType.MODULE_JSON
        if uri.endswith("package.json"):
            return ManifestFileType.PACKAGE_JSON
        return ManifestFileType.LIBRARY_JSON


class ManifestParserFactory(object):
    @staticmethod
    def type_to_clsname(t):
        t = t.replace(".", " ")
        t = t.title()
        return "%sManifestParser" % t.replace(" ", "")

    @staticmethod
    def new_from_file(path, remote_url=False):
        if not path or not os.path.isfile(path):
            raise ManifestException("Manifest file does not exist %s" % path)
        for t in get_class_attributes(ManifestFileType).values():
            if path.endswith(t):
                return ManifestParserFactory.new(get_file_contents(path), t, remote_url)
        raise ManifestException("Unknown manifest file type %s" % path)

    @staticmethod
    def new_from_dir(path, remote_url=None):
        assert os.path.isdir(path), "Invalid directory %s" % path
        file_order = [
            ManifestFileType.PLATFORM_JSON,
            ManifestFileType.LIBRARY_JSON,
            ManifestFileType.LIBRARY_PROPERTIES,
            ManifestFileType.MODULE_JSON,
            ManifestFileType.PACKAGE_JSON,
        ]
        for t in file_order:
            if not os.path.isfile(os.path.join(path, t)):
                continue
            return ManifestParserFactory.new(
                get_file_contents(os.path.join(path, t)), t, remote_url
            )
        raise ManifestException("Unknown manifest file type in %s directory" % path)

    @staticmethod
    def new_from_url(remote_url):
        r = requests.get(remote_url)
        r.raise_for_status()
        return ManifestParserFactory.new(
            r.text, ManifestFileType.from_uri(remote_url), remote_url
        )

    @staticmethod
    def new(contents, type, remote_url=None):
        # pylint: disable=redefined-builtin
        clsname = ManifestParserFactory.type_to_clsname(type)
        if clsname not in globals():
            raise ManifestException("Unknown manifest file type %s" % clsname)
        return globals()[clsname](contents, remote_url)


class BaseManifestParser(object):
    def __init__(self, contents, remote_url=None):
        self.remote_url = remote_url
        self._data = self.parse(contents)

    def parse(self, contents):
        raise NotImplementedError

    def as_dict(self):
        return self._data

    @staticmethod
    def _cleanup_author(author):
        if author.get("email"):
            author["email"] = re.sub(r"\s+[aA][tT]\s+", "@", author["email"])
        return author

    @staticmethod
    def parse_author_name_and_email(raw):
        if raw == "None" or "://" in raw:
            return (None, None)
        name = raw
        email = None
        for ldel, rdel in [("<", ">"), ("(", ")")]:
            if ldel in raw and rdel in raw:
                name = raw[: raw.index(ldel)]
                email = raw[raw.index(ldel) + 1 : raw.index(rdel)]
        return (name.strip(), email.strip() if email else None)


class LibraryJsonManifestParser(BaseManifestParser):
    def parse(self, contents):
        data = json.loads(contents)
        data = self._process_renamed_fields(data)

        # normalize Union[str, list] fields
        for k in ("keywords", "platforms", "frameworks"):
            if k in data:
                data[k] = self._str_to_list(data[k], sep=",")

        if "authors" in data:
            data["authors"] = self._parse_authors(data["authors"])
        if "platforms" in data:
            data["platforms"] = self._parse_platforms(data["platforms"]) or None
        if "export" in data:
            data["export"] = self._parse_export(data["export"])

        return data

    @staticmethod
    def _str_to_list(value, sep=",", lowercase=True):
        if isinstance(value, string_types):
            value = value.split(sep)
        assert isinstance(value, list)
        result = []
        for item in value:
            item = item.strip()
            if not item:
                continue
            if lowercase:
                item = item.lower()
            result.append(item)
        return result

    @staticmethod
    def _process_renamed_fields(data):
        if "url" in data:
            data["homepage"] = data["url"]
            del data["url"]

        for key in ("include", "exclude"):
            if key not in data:
                continue
            if "export" not in data:
                data["export"] = {}
            data["export"][key] = data[key]
            del data[key]

        return data

    def _parse_authors(self, raw):
        if not raw:
            return None
        # normalize Union[dict, list] fields
        if not isinstance(raw, list):
            raw = [raw]
        return [self._cleanup_author(author) for author in raw]

    @staticmethod
    def _parse_platforms(raw):
        assert isinstance(raw, list)
        result = []
        # renamed platforms
        for item in raw:
            if item == "espressif":
                item = "espressif8266"
            result.append(item)
        return result

    @staticmethod
    def _parse_export(raw):
        if not isinstance(raw, dict):
            return None
        result = {}
        for k in ("include", "exclude"):
            if k not in raw:
                continue
            result[k] = raw[k] if isinstance(raw[k], list) else [raw[k]]
        return result


class ModuleJsonManifestParser(BaseManifestParser):
    def parse(self, contents):
        data = json.loads(contents)
        return dict(
            name=data["name"],
            version=data["version"],
            keywords=data.get("keywords"),
            description=data["description"],
            frameworks=["mbed"],
            platforms=["*"],
            homepage=data.get("homepage"),
            export={"exclude": ["tests", "test", "*.doxyfile", "*.pdf"]},
            authors=self._parse_authors(data.get("author")),
            license=self._parse_license(data.get("licenses")),
        )

    def _parse_authors(self, raw):
        if not raw:
            return None
        result = []
        for author in raw.split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            result.append(
                self._cleanup_author(dict(name=name, email=email, maintainer=False))
            )
        return result

    @staticmethod
    def _parse_license(raw):
        if not raw or not isinstance(raw, list):
            return None
        return raw[0].get("type")


class LibraryPropertiesManifestParser(BaseManifestParser):
    def parse(self, contents):
        properties = self._parse_properties(contents)
        repository = self._parse_repository(properties)
        homepage = properties.get("url")
        if repository and repository["url"] == homepage:
            homepage = None
        return dict(
            frameworks=["arduino"],
            homepage=homepage,
            repository=repository or None,
            name=properties.get("name"),
            version=properties.get("version"),
            description=self._parse_description(properties),
            platforms=self._parse_platforms(properties) or ["*"],
            keywords=self._parse_keywords(properties),
            authors=self._parse_authors(properties) or None,
            export=self._parse_export(),
        )

    @staticmethod
    def _parse_properties(contents):
        data = {}
        for line in contents.splitlines():
            line = line.strip()
            if not line or "=" not in line:
                continue
            # skip comments
            if line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
        return data

    @staticmethod
    def _parse_description(properties):
        lines = []
        for k in ("sentence", "paragraph"):
            if k in properties and properties[k] not in lines:
                lines.append(properties[k])
        if len(lines) == 2 and not lines[0].endswith("."):
            lines[0] += "."
        return " ".join(lines)

    @staticmethod
    def _parse_keywords(properties):
        result = []
        for item in re.split(r"[\s/]+", properties.get("category", "uncategorized")):
            item = item.strip()
            if not item:
                continue
            result.append(item.lower())
        return result

    @staticmethod
    def _parse_platforms(properties):
        result = []
        platforms_map = {
            "avr": "atmelavr",
            "sam": "atmelsam",
            "samd": "atmelsam",
            "esp8266": "espressif8266",
            "esp32": "espressif32",
            "arc32": "intel_arc32",
            "stm32": "ststm32",
        }
        for arch in properties.get("architectures", "").split(","):
            if "particle-" in arch:
                raise ManifestParserException("Particle is not supported yet")
            arch = arch.strip()
            if not arch:
                continue
            if arch == "*":
                return ["*"]
            if arch in platforms_map:
                result.append(platforms_map[arch])
        return result

    def _parse_authors(self, properties):
        if "author" not in properties:
            return None
        authors = []
        for author in properties["author"].split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            authors.append(
                self._cleanup_author(dict(name=name, email=email, maintainer=False))
            )
        for author in properties.get("maintainer", "").split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            found = False
            for item in authors:
                if item["name"].lower() != name.lower():
                    continue
                found = True
                item["maintainer"] = True
                if not item["email"]:
                    item["email"] = email
            if not found:
                authors.append(
                    self._cleanup_author(dict(name=name, email=email, maintainer=True))
                )
        return authors

    def _parse_repository(self, properties):
        if self.remote_url:
            repo_parse = urlparse(self.remote_url)
            repo_path_tokens = repo_parse.path[1:].split("/")[:-1]
            if "github" in repo_parse.netloc:
                return dict(
                    type="git",
                    url="%s://github.com/%s"
                    % (repo_parse.scheme, "/".join(repo_path_tokens[:2])),
                )
            if "raw" in repo_path_tokens:
                return dict(
                    type="git",
                    url="%s://%s/%s"
                    % (
                        repo_parse.scheme,
                        repo_parse.netloc,
                        "/".join(repo_path_tokens[: repo_path_tokens.index("raw")]),
                    ),
                )
        if properties.get("url", "").startswith("https://github.com"):
            return dict(type="git", url=properties["url"])
        return None

    def _parse_export(self):
        include = None
        if self.remote_url:
            repo_parse = urlparse(self.remote_url)
            repo_path_tokens = repo_parse.path[1:].split("/")[:-1]
            if "github" in repo_parse.netloc:
                include = "/".join(repo_path_tokens[3:]) or None
            elif "raw" in repo_path_tokens:
                include = (
                    "/".join(repo_path_tokens[repo_path_tokens.index("raw") + 2 :])
                    or None
                )
        return {
            "include": include,
            "exclude": ["extras", "docs", "tests", "test", "*.doxyfile", "*.pdf"],
        }
