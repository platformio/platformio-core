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
import io
import json
import os
import re
import tarfile
from urllib.parse import urlparse

from platformio import util
from platformio.compat import get_object_members, string_types
from platformio.http import fetch_remote_content
from platformio.package.exception import ManifestParserError, UnknownManifestError
from platformio.project.helpers import is_platformio_project


class ManifestFileType:
    PLATFORM_JSON = "platform.json"
    LIBRARY_JSON = "library.json"
    LIBRARY_PROPERTIES = "library.properties"
    MODULE_JSON = "module.json"
    PACKAGE_JSON = "package.json"

    @classmethod
    def items(cls):
        return get_object_members(cls)

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


class ManifestParserFactory:
    @staticmethod
    def read_manifest_contents(path):
        last_err = None
        for encoding in ("utf-8", "latin-1"):
            try:
                with io.open(path, encoding=encoding) as fp:
                    return fp.read()
            except UnicodeDecodeError as exc:
                last_err = exc
        raise last_err

    @classmethod
    def new_from_file(cls, path, remote_url=False):
        if not path or not os.path.isfile(path):
            raise UnknownManifestError("Manifest file does not exist %s" % path)
        type_from_uri = ManifestFileType.from_uri(path)
        if not type_from_uri:
            raise UnknownManifestError("Unknown manifest file type %s" % path)
        return ManifestParserFactory.new(
            cls.read_manifest_contents(path), type_from_uri, remote_url
        )

    @classmethod
    def new_from_dir(cls, path, remote_url=None):
        assert os.path.isdir(path), "Invalid directory %s" % path

        type_from_uri = ManifestFileType.from_uri(remote_url) if remote_url else None
        if type_from_uri and os.path.isfile(os.path.join(path, type_from_uri)):
            return ManifestParserFactory.new(
                cls.read_manifest_contents(os.path.join(path, type_from_uri)),
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
            cls.read_manifest_contents(os.path.join(path, type_from_dir)),
            type_from_dir,
            remote_url=remote_url,
            package_dir=path,
        )

    @staticmethod
    def new_from_url(remote_url):
        content = fetch_remote_content(remote_url)
        return ManifestParserFactory.new(
            content,
            ManifestFileType.from_uri(remote_url) or ManifestFileType.LIBRARY_JSON,
            remote_url,
        )

    @staticmethod
    def new_from_archive(path):
        assert path.endswith("tar.gz")
        with tarfile.open(path, mode="r:gz") as tf:
            for t in sorted(ManifestFileType.items().values()):
                for member in (t, "./" + t):
                    try:
                        return ManifestParserFactory.new(
                            tf.extractfile(member).read().decode(), t
                        )
                    except KeyError:
                        pass
        raise UnknownManifestError("Unknown manifest file type in %s archive" % path)

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


class BaseManifestParser:
    def __init__(self, contents, remote_url=None, package_dir=None):
        self.remote_url = remote_url
        self.package_dir = package_dir
        try:
            self._data = self.parse(contents)
        except Exception as exc:
            raise ManifestParserError("Could not parse manifest -> %s" % exc) from exc

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
    def str_to_list(value, sep=",", lowercase=False, unique=False):
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
            if unique and item in result:
                continue
            result.append(item)
        return result

    @staticmethod
    def cleanup_author(author):
        assert isinstance(author, dict)
        if author.get("email"):
            author["email"] = re.sub(r"\s+[aA][tT]\s+", "@", author["email"])
            if "@" not in author["email"]:
                author["email"] = None
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
        ldel = "<"
        rdel = ">"
        if ldel in raw and rdel in raw:
            name = raw[: raw.index(ldel)]
            email = raw[raw.index(ldel) + 1 : raw.index(rdel)]
        if "(" in name:
            name = name.split("(")[0]
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
                name=(
                    "Examples"
                    if root == examples_dir
                    else os.path.relpath(root, examples_dir)
                ),
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
                data[k] = self.str_to_list(
                    data[k], sep=",", lowercase=True, unique=True
                )

        if "headers" in data:
            data["headers"] = self.str_to_list(data["headers"], sep=",", unique=True)
        if "authors" in data:
            data["authors"] = self._parse_authors(data["authors"])
        if "platforms" in data:
            data["platforms"] = self._fix_platforms(data["platforms"]) or None
        if "export" in data:
            data["export"] = self._parse_export(data["export"])
        if "dependencies" in data:
            data["dependencies"] = self._parse_dependencies(data["dependencies"])

        return data

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
        return [self.cleanup_author(author) for author in raw]

    @staticmethod
    def _fix_platforms(items):
        assert isinstance(items, list)
        if "espressif" in items:
            items[items.index("espressif")] = "espressif8266"
        return items

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
            result = []
            for name, version in raw.items():
                if "/" in name:
                    owner, name = name.split("/", 1)
                    result.append(dict(owner=owner, name=name, version=version))
                else:
                    result.append(dict(name=name, version=version))
            return result

        if isinstance(raw, list):
            for i, dependency in enumerate(raw):
                if isinstance(dependency, dict):
                    for k, v in dependency.items():
                        if k not in ("platforms", "frameworks", "authors"):
                            continue
                        raw[i][k] = util.items_to_list(v)
                else:
                    raw[i] = {"name": dependency}
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
        if "dependencies" in data:
            data["dependencies"] = self._parse_dependencies(data["dependencies"])
        if "keywords" in data:
            data["keywords"] = self.str_to_list(
                data["keywords"], sep=",", lowercase=True, unique=True
            )
        return data

    def _parse_authors(self, raw):
        if not raw:
            return None
        result = []
        for author in raw.split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            result.append(self.cleanup_author(dict(name=name, email=email)))
        return result

    @staticmethod
    def _parse_license(raw):
        if not raw or not isinstance(raw, list):
            return None
        return raw[0].get("type")

    @staticmethod
    def _parse_dependencies(raw):
        if isinstance(raw, dict):
            return [
                dict(name=name, version=version, frameworks=["mbed"])
                for name, version in raw.items()
            ]
        raise ManifestParserError("Invalid dependencies format, should be a dictionary")


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
                platforms=self._parse_platforms(data) or None,
                keywords=self._parse_keywords(data) or None,
                export=self._parse_export(),
            )
        )
        if "includes" in data:
            data["headers"] = self.str_to_list(data["includes"], sep=",", unique=True)
        if "author" in data:
            data["authors"] = self._parse_authors(data)
            for key in ("author", "maintainer"):
                if key in data:
                    del data[key]
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
            if not value.strip():
                continue
            data[key.strip()] = value.strip()
        return data

    @staticmethod
    def _parse_description(properties):
        lines = []
        for k in ("sentence", "paragraph"):
            if k in properties and properties[k] not in lines:
                lines.append(properties[k])
        if len(lines) == 2:
            if not lines[0].endswith("."):
                lines[0] += "."
            if len(lines[0]) + len(lines[1]) >= 1000:
                del lines[1]
        return " ".join(lines)

    def _parse_keywords(self, properties):
        return self.str_to_list(
            re.split(
                r"[\s/]+",
                properties.get("category", ""),
            ),
            lowercase=True,
            unique=True,
        )

    def _parse_platforms(self, properties):
        result = []
        platforms_map = {
            "avr": "atmelavr",
            "sam": "atmelsam",
            "samd": "atmelsam",
            "esp8266": "espressif8266",
            "esp32": "espressif32",
            "arc32": "intel_arc32",
            "stm32": "ststm32",
            "nrf52": "nordicnrf52",
            "rp2040": "raspberrypi",
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
        return self.str_to_list(result, lowercase=True, unique=True)

    def _parse_authors(self, properties):
        if "author" not in properties:
            return None
        authors = []
        for author in properties["author"].split(","):
            name, email = self.parse_author_name_and_email(author)
            if not name:
                continue
            authors.append(self.cleanup_author(dict(name=name, email=email)))
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
                # pylint: disable=unsupported-membership-test
                if not item.get("email") and email and "@" in email:
                    item["email"] = email
            if not found:
                authors.append(
                    self.cleanup_author(dict(name=name, email=email, maintainer=True))
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
            return dict(include=[include])
        return None

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
        if "keywords" in data:
            data["keywords"] = self.str_to_list(
                data["keywords"], sep=",", lowercase=True, unique=True
            )
        if "frameworks" in data:
            data["frameworks"] = (
                self.str_to_list(
                    list(data["frameworks"].keys()), lowercase=True, unique=True
                )
                if isinstance(data["frameworks"], dict)
                else None
            )
        if "packages" in data:
            data["dependencies"] = self._parse_dependencies(data["packages"])
        return data

    @staticmethod
    def _parse_dependencies(raw):
        result = []
        for name, opts in raw.items():
            item = {"name": name}
            for k in ("owner", "version"):
                if k in opts:
                    item[k] = opts[k]
            result.append(item)
        return result


class PackageJsonManifestParser(BaseManifestParser):
    manifest_type = ManifestFileType.PACKAGE_JSON

    def parse(self, contents):
        data = json.loads(contents)
        if "keywords" in data:
            data["keywords"] = self.str_to_list(
                data["keywords"], sep=",", lowercase=True, unique=True
            )
        data = self._parse_system(data)
        data = self._parse_homepage(data)
        data = self._parse_repository(data)
        return data

    def _parse_system(self, data):
        if "system" not in data:
            return data
        if data["system"] in ("*", ["*"], "all"):
            del data["system"]
            return data
        data["system"] = self.str_to_list(data["system"], lowercase=True, unique=True)
        return data

    @staticmethod
    def _parse_homepage(data):
        if "url" in data:
            data["homepage"] = data["url"]
            del data["url"]
        return data

    @staticmethod
    def _parse_repository(data):
        if isinstance(data.get("repository", {}), dict):
            return data
        data["repository"] = dict(type="git", url=str(data["repository"]))
        if data["repository"]["url"].startswith(("github:", "gitlab:", "bitbucket:")):
            data["repository"]["url"] = "https://{0}.com/{1}".format(
                *(data["repository"]["url"].split(":", 1))
            )
        return data
