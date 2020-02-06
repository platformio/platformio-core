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

import inspect
import json
import os
import re

import requests

from platformio import util
from platformio.compat import get_class_attributes, string_types
from platformio.fs import get_file_contents
from platformio.package.exception import ManifestParserError, UnknownManifestError
from platformio.project.helpers import is_platformio_project

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


class ManifestFileType(object):
    PLATFORM_JSON = "platform.json"
    LIBRARY_JSON = "library.json"
    LIBRARY_PROPERTIES = "library.properties"
    MODULE_JSON = "module.json"
    PACKAGE_JSON = "package.json"

    @classmethod
    def items(cls):
        return get_class_attributes(ManifestFileType)

    @classmethod
    def from_uri(cls, uri):
        for t in sorted(cls.items().values()):
            if uri.endswith(t):
                return t
        return None

    @classmethod
    def from_dir(cls, path):
        for t in sorted(cls.items().values()):
            if os.path.isfile(os.path.join(path, t)):
                return t
        return None


class ManifestParserFactory(object):
    @staticmethod
    def new_from_file(path, remote_url=False):
        if not path or not os.path.isfile(path):
            raise UnknownManifestError("Manifest file does not exist %s" % path)
        type_from_uri = ManifestFileType.from_uri(path)
        if not type_from_uri:
            raise UnknownManifestError("Unknown manifest file type %s" % path)
        return ManifestParserFactory.new(
            get_file_contents(path, encoding="utf8"), type_from_uri, remote_url
        )

    @staticmethod
    def new_from_dir(path, remote_url=None):
        assert os.path.isdir(path), "Invalid directory %s" % path

        type_from_uri = ManifestFileType.from_uri(remote_url) if remote_url else None
        if type_from_uri and os.path.isfile(os.path.join(path, type_from_uri)):
            return ManifestParserFactory.new(
                get_file_contents(os.path.join(path, type_from_uri), encoding="utf8"),
                type_from_uri,
                remote_url=remote_url,
                package_dir=path,
            )

        type_from_dir = ManifestFileType.from_dir(path)
        if not type_from_dir:
            raise UnknownManifestError(
                "Unknown manifest file type in %s directory" % path
            )
        return ManifestParserFactory.new(
            get_file_contents(os.path.join(path, type_from_dir), encoding="utf8"),
            type_from_dir,
            remote_url=remote_url,
            package_dir=path,
        )

    @staticmethod
    def new_from_url(remote_url):
        r = requests.get(remote_url)
        r.raise_for_status()
        return ManifestParserFactory.new(
            r.text,
            ManifestFileType.from_uri(remote_url) or ManifestFileType.LIBRARY_JSON,
            remote_url,
        )

    @staticmethod
    def new(  # pylint: disable=redefined-builtin
        contents, type, remote_url=None, package_dir=None
    ):
        for _, cls in globals().items():
            if (
                inspect.isclass(cls)
                and issubclass(cls, BaseManifestParser)
                and cls != BaseManifestParser
                and cls.manifest_type == type
            ):
                return cls(contents, remote_url, package_dir)
        raise UnknownManifestError("Unknown manifest file type %s" % type)


class BaseManifestParser(object):
    def __init__(self, contents, remote_url=None, package_dir=None):
        self.remote_url = remote_url
        self.package_dir = package_dir
        try:
            self._data = self.parse(contents)
        except Exception as e:
            raise ManifestParserError("Could not parse manifest -> %s" % e)

        self._data = self.normalize_repository(self._data)
        self._data = self.parse_examples(self._data)

        # remove None fields
        for key in list(self._data.keys()):
            if self._data[key] is None:
                del self._data[key]

    def parse(self, contents):
        raise NotImplementedError

    def as_dict(self):
        return self._data

    @staticmethod
    def normalize_author(author):
        assert isinstance(author, dict)
        if author.get("email"):
            author["email"] = re.sub(r"\s+[aA][tT]\s+", "@", author["email"])
        for key in list(author.keys()):
            if author[key] is None:
                del author[key]
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

    @staticmethod
    def normalize_repository(data):
        url = (data.get("repository") or {}).get("url")
        if not url or "://" not in url:
            return data
        url_attrs = urlparse(url)
        if url_attrs.netloc not in ("github.com", "bitbucket.org", "gitlab.com"):
            return data
        url = "https://%s%s" % (url_attrs.netloc, url_attrs.path)
        if url.endswith("/"):
            url = url[:-1]
        if not url.endswith(".git"):
            url += ".git"
        data["repository"]["url"] = url
        return data

    def parse_examples(self, data):
        examples = data.get("examples")
        if (
            not examples
            or not isinstance(examples, list)
            or not all(isinstance(v, dict) for v in examples)
        ):
            data["examples"] = None
        if not data["examples"] and self.package_dir:
            data["examples"] = self.parse_examples_from_dir(self.package_dir)
        if "examples" in data and not data["examples"]:
            del data["examples"]
        return data

    @staticmethod
    def parse_examples_from_dir(package_dir):
        assert os.path.isdir(package_dir)
        examples_dir = os.path.join(package_dir, "examples")
        if not os.path.isdir(examples_dir):
            examples_dir = os.path.join(package_dir, "Examples")
            if not os.path.isdir(examples_dir):
                return None

        allowed_exts = (
            ".c",
            ".cc",
            ".cpp",
            ".h",
            ".hpp",
            ".asm",
            ".ASM",
            ".s",
            ".S",
            ".ino",
            ".pde",
        )

        result = {}
        last_pio_project = None
        for root, _, files in os.walk(examples_dir):
            # skip hidden files, symlinks, and folders
            files = [
                f
                for f in files
                if not f.startswith(".") and not os.path.islink(os.path.join(root, f))
            ]
            if os.path.basename(root).startswith(".") or not files:
                continue

            if is_platformio_project(root):
                last_pio_project = root
                result[last_pio_project] = dict(
                    name=os.path.relpath(root, examples_dir),
                    base=os.path.relpath(root, package_dir),
                    files=files,
                )
                continue
            if last_pio_project:
                if root.startswith(last_pio_project):
                    result[last_pio_project]["files"].extend(
                        [
                            os.path.relpath(os.path.join(root, f), last_pio_project)
                            for f in files
                        ]
                    )
                    continue
                last_pio_project = None

            matched_files = [f for f in files if f.endswith(allowed_exts)]
            if not matched_files:
                continue
            result[root] = dict(
                name="Examples"
                if root == examples_dir
                else os.path.relpath(root, examples_dir),
                base=os.path.relpath(root, package_dir),
                files=matched_files,
            )

        result = list(result.values())

        # normalize example names
        for item in result:
            item["name"] = item["name"].replace(os.path.sep, "/")
            item["name"] = re.sub(r"[^a-z\d\d\-\_/]+", "_", item["name"], flags=re.I)

        return result or None


class LibraryJsonManifestParser(BaseManifestParser):
    manifest_type = ManifestFileType.LIBRARY_JSON

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
        if "dependencies" in data:
            data["dependencies"] = self._parse_dependencies(data["dependencies"])

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
        return [self.normalize_author(author) for author in raw]

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
            if not raw.get(k):
                continue
            result[k] = raw[k] if isinstance(raw[k], list) else [raw[k]]
        return result

    @staticmethod
    def _parse_dependencies(raw):
        # compatibility with legacy dependency format
        if isinstance(raw, dict) and "name" in raw:
            raw = [raw]

        if isinstance(raw, dict):
            return [dict(name=name, version=version) for name, version in raw.items()]
        if isinstance(raw, list):
            for i, dependency in enumerate(raw):
                assert isinstance(dependency, dict)
                for k, v in dependency.items():
                    if k not in ("platforms", "frameworks", "authors"):
                        continue
                    if "*" in v:
                        del raw[i][k]
                    raw[i][k] = util.items_to_list(v)
            return raw
        raise ManifestParserError(
            "Invalid dependencies format, should be list or dictionary"
        )


class ModuleJsonManifestParser(BaseManifestParser):
    manifest_type = ManifestFileType.MODULE_JSON

    def parse(self, contents):
        data = json.loads(contents)
        data["frameworks"] = ["mbed"]
        data["platforms"] = ["*"]
        data["export"] = {"exclude": ["tests", "test", "*.doxyfile", "*.pdf"]}
        if "author" in data:
            data["authors"] = self._parse_authors(data.get("author"))
            del data["author"]
        if "licenses" in data:
            data["license"] = self._parse_license(data.get("licenses"))
            del data["licenses"]
        return data

    def _parse_authors(self, raw):
        if not raw:
            return None
        result = []
        for author in raw.split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            result.append(self.normalize_author(dict(name=name, email=email)))
        return result

    @staticmethod
    def _parse_license(raw):
        if not raw or not isinstance(raw, list):
            return None
        return raw[0].get("type")


class LibraryPropertiesManifestParser(BaseManifestParser):
    manifest_type = ManifestFileType.LIBRARY_PROPERTIES

    def parse(self, contents):
        data = self._parse_properties(contents)
        repository = self._parse_repository(data)
        homepage = data.get("url") or None
        if repository and repository["url"] == homepage:
            homepage = None
        data.update(
            dict(
                frameworks=["arduino"],
                homepage=homepage,
                repository=repository or None,
                description=self._parse_description(data),
                platforms=self._parse_platforms(data) or ["*"],
                keywords=self._parse_keywords(data),
                export=self._parse_export(),
            )
        )
        if "author" in data:
            data["authors"] = self._parse_authors(data)
            del data["author"]
        if "depends" in data:
            data["dependencies"] = self._parse_dependencies(data["depends"])
        return data

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
                raise ManifestParserError("Particle is not supported yet")
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
            authors.append(self.normalize_author(dict(name=name, email=email)))
        for author in properties.get("maintainer", "").split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            found = False
            for item in authors:
                if item.get("name", "").lower() != name.lower():
                    continue
                found = True
                item["maintainer"] = True
                if not item.get("email") and email:
                    item["email"] = email
            if not found:
                authors.append(
                    self.normalize_author(dict(name=name, email=email, maintainer=True))
                )
        return authors

    def _parse_repository(self, properties):
        if self.remote_url:
            url_attrs = urlparse(self.remote_url)
            repo_path_tokens = url_attrs.path[1:].split("/")[:-1]
            if "github" in url_attrs.netloc:
                return dict(
                    type="git",
                    url="https://github.com/" + "/".join(repo_path_tokens[:2]),
                )
            if "raw" in repo_path_tokens:
                return dict(
                    type="git",
                    url="https://%s/%s"
                    % (
                        url_attrs.netloc,
                        "/".join(repo_path_tokens[: repo_path_tokens.index("raw")]),
                    ),
                )
        if properties.get("url", "").startswith("https://github.com"):
            return dict(type="git", url=properties["url"])
        return None

    def _parse_export(self):
        result = {"exclude": ["extras", "docs", "tests", "test", "*.doxyfile", "*.pdf"]}
        include = None
        if self.remote_url:
            url_attrs = urlparse(self.remote_url)
            repo_path_tokens = url_attrs.path[1:].split("/")[:-1]
            if "github" in url_attrs.netloc:
                include = "/".join(repo_path_tokens[3:]) or None
            elif "raw" in repo_path_tokens:
                include = (
                    "/".join(repo_path_tokens[repo_path_tokens.index("raw") + 2 :])
                    or None
                )
        if include:
            result["include"] = [include]
        return result

    @staticmethod
    def _parse_dependencies(raw):
        result = []
        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue
            if item.endswith(")") and "(" in item:
                name, version = item.split("(")
                result.append(
                    dict(
                        name=name.strip(),
                        version=version[:-1].strip(),
                        frameworks=["arduino"],
                    )
                )
            else:
                result.append(dict(name=item, frameworks=["arduino"]))
        return result


class PlatformJsonManifestParser(BaseManifestParser):
    manifest_type = ManifestFileType.PLATFORM_JSON

    def parse(self, contents):
        data = json.loads(contents)
        if "frameworks" in data:
            data["frameworks"] = self._parse_frameworks(data["frameworks"])
        if "packages" in data:
            data["dependencies"] = self._parse_dependencies(data["packages"])
        return data

    @staticmethod
    def _parse_frameworks(raw):
        if not isinstance(raw, dict):
            return None
        return [name.lower() for name in raw.keys()]

    @staticmethod
    def _parse_dependencies(raw):
        return [
            dict(name=name, version=opts.get("version")) for name, opts in raw.items()
        ]


class PackageJsonManifestParser(BaseManifestParser):
    manifest_type = ManifestFileType.PACKAGE_JSON

    def parse(self, contents):
        data = json.loads(contents)
        data = self._parse_system(data)
        data = self._parse_homepage(data)
        return data

    @staticmethod
    def _parse_system(data):
        if "system" not in data:
            return data
        if data["system"] in ("*", ["*"], "all"):
            del data["system"]
            return data
        if not isinstance(data["system"], list):
            data["system"] = [data["system"]]
        data["system"] = [s.strip().lower() for s in data["system"]]
        return data

    @staticmethod
    def _parse_homepage(data):
        if "url" in data:
            data["homepage"] = data["url"]
            del data["url"]
        return data
