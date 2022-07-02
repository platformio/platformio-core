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
import shutil
import tarfile
import tempfile

from platformio import fs
from platformio.compat import IS_WINDOWS
from platformio.package.exception import PackageException, UserSideException
from platformio.package.manifest.parser import (
    LibraryPropertiesManifestParser,
    ManifestFileType,
    ManifestParserFactory,
)
from platformio.package.manifest.schema import ManifestSchema
from platformio.package.meta import PackageItem
from platformio.package.unpack import FileUnpacker


class PackagePacker:
    INCLUDE_DEFAULT = list(ManifestFileType.items().values()) + [
        "README",
        "README.md",
        "README.rst",
        "LICENSE",
    ]
    EXCLUDE_DEFAULT = [
        # PlatformIO internal files
        PackageItem.METAFILE_NAME,
        ".pio/",
        "**/.pio/",
        # Hidden files
        "._*",
        "__*",
        ".DS_Store",
        ".vscode",
        ".cache",
        "**/.cache",
        "**/__pycache__",
        "**/*.pyc",
        # VCS
        ".git/",
        ".hg/",
        ".svn/",
    ]
    EXCLUDE_EXTRA = [
        # Tests
        "test",
        "tests",
        # Docs
        "doc",
        "docs",
        "mkdocs",
        "doxygen",
        "*.doxyfile",
        "html",
        "media",
        "**/*.[pP][dD][fF]",
        "**/*.[dD][oO][cC]",
        "**/*.[dD][oO][cC][xX]",
        "**/*.[pP][pP][tT]",
        "**/*.[pP][pP][tT][xX]",
        "**/*.[xX][lL][sS]",
        "**/*.[xX][lL][sS][xX]",
        "**/*.[dD][oO][xX]",
        "**/*.[hH][tT][mM]",
        "**/*.[hH][tT][mM][lL]",
        "**/*.[tT][eE][xX]",
        "**/*.[jJ][sS]",
        "**/*.[cC][sS][sS]",
        # Binary files
        "**/*.[jJ][pP][gG]",
        "**/*.[jJ][pP][eE][gG]",
        "**/*.[pP][nN][gG]",
        "**/*.[gG][iI][fF]",
        "**/*.[sS][vV][gG]",
        "**/*.[zZ][iI][pP]",
        "**/*.[gG][zZ]",
        "**/*.3[gG][pP]",
        "**/*.[mM][oO][vV]",
        "**/*.[mM][pP][34]",
        "**/*.[pP][sS][dD]",
        "**/*.[wW][aA][wW]",
        "**/*.sqlite",
    ]
    EXCLUDE_LIBRARY_EXTRA = [
        "assets",
        "extra",
        "extras",
        "resources",
        "**/build/",
        "**/*.flat",
        "**/*.[jJ][aA][rR]",
        "**/*.[eE][xX][eE]",
        "**/*.[bB][iI][nN]",
        "**/*.[hH][eE][xX]",
        "**/*.[dD][bB]",
        "**/*.[dD][aA][tT]",
        "**/*.[dD][lL][lL]",
    ]

    def __init__(self, package, manifest_uri=None):
        self.package = package
        self.manifest_uri = manifest_uri
        self.manifest_parser = None

    @staticmethod
    def get_archive_name(name, version, system=None):
        return re.sub(
            r"[^\da-zA-Z\-\._\+]+",
            "",
            "{name}{system}-{version}.tar.gz".format(
                name=name,
                system=("-" + system) if system else "",
                version=version,
            ),
        )

    @staticmethod
    def load_gitignore_filters(path):
        result = []
        with open(path, encoding="utf8") as fp:
            for line in fp.readlines():
                line = line.strip()
                if not line or line.startswith(("#")):
                    continue
                if line.startswith("!"):
                    result.append(f"+<{line[1:]}>")
                else:
                    result.append(f"-<{line}>")
        return result

    def pack(self, dst=None):
        tmp_dir = tempfile.mkdtemp()
        try:
            src = self.package

            # if zip/tar.gz -> unpack to tmp dir
            if not os.path.isdir(src):
                if IS_WINDOWS:
                    raise UserSideException(
                        "Packaging from an archive does not work on Windows OS. Please "
                        "extract data from `%s` manually and pack a folder instead"
                        % src
                    )
                with FileUnpacker(src) as fu:
                    assert fu.unpack(tmp_dir, silent=True)
                src = tmp_dir

            src = self.find_source_root(src)
            self.manifest_parser = ManifestParserFactory.new_from_dir(src)
            manifest = ManifestSchema().load_manifest(self.manifest_parser.as_dict())
            filename = self.get_archive_name(
                manifest["name"],
                manifest["version"],
                manifest["system"][0] if "system" in manifest else None,
            )

            if not dst:
                dst = os.path.join(os.getcwd(), filename)
            elif os.path.isdir(dst):
                dst = os.path.join(dst, filename)

            return self.create_tarball(src, dst, manifest)
        finally:
            shutil.rmtree(tmp_dir)

    def find_source_root(self, src):
        if self.manifest_uri:
            mp = (
                ManifestParserFactory.new_from_file(self.manifest_uri[5:])
                if self.manifest_uri.startswith("file:")
                else ManifestParserFactory.new_from_url(self.manifest_uri)
            )
            manifest = ManifestSchema().load_manifest(mp.as_dict())
            include = manifest.get("export", {}).get("include", [])
            if len(include) == 1:
                if not os.path.isdir(os.path.join(src, include[0])):
                    raise PackageException(
                        "Non existing `include` directory `%s` in a package"
                        % include[0]
                    )
                return os.path.join(src, include[0])

        for root, _, __ in os.walk(src):
            if ManifestFileType.from_dir(root):
                return root

        return src

    def create_tarball(self, src, dst, manifest):
        include = manifest.get("export", {}).get("include")
        exclude = manifest.get("export", {}).get("exclude")
        # remap root
        if (
            include
            and len(include) == 1
            and os.path.isdir(os.path.join(src, include[0]))
        ):
            src = os.path.join(src, include[0])
            with open(
                os.path.join(src, "library.json"), mode="w", encoding="utf8"
            ) as fp:
                manifest_updated = manifest.copy()
                del manifest_updated["export"]["include"]
                json.dump(manifest_updated, fp, indent=2, ensure_ascii=False)
            include = None

        src_filters = self.compute_src_filters(src, include, exclude)
        with tarfile.open(dst, "w:gz") as tar:
            for f in fs.match_src_files(src, src_filters, followlinks=False):
                tar.add(os.path.join(src, f), f)
        return dst

    def compute_src_filters(self, src, include, exclude):
        exclude_extra = self.EXCLUDE_EXTRA[:]
        # extend with library extra filters
        if any(
            os.path.isfile(os.path.join(src, name))
            for name in (
                ManifestFileType.LIBRARY_JSON,
                ManifestFileType.LIBRARY_PROPERTIES,
                ManifestFileType.MODULE_JSON,
            )
        ):
            exclude_extra.extend(self.EXCLUDE_LIBRARY_EXTRA)

        result = ["+<%s>" % p for p in include or ["*", ".*"]]
        result += ["-<%s>" % p for p in self.EXCLUDE_DEFAULT]
        # exclude items declared in manifest
        result += ["-<%s>" % p for p in exclude or []]

        # apply extra excludes if no custom "export" field in manifest
        if (not include and not exclude) or isinstance(
            self.manifest_parser, LibraryPropertiesManifestParser
        ):
            result += ["-<%s>" % p for p in exclude_extra]
            if os.path.exists(os.path.join(src, ".gitignore")):
                result += self.load_gitignore_filters(os.path.join(src, ".gitignore"))

        # always include manifests and relevant files
        result += ["+<%s>" % p for p in self.INCLUDE_DEFAULT]
        return result
