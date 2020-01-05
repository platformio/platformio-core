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
import re
import shutil
import tarfile
import tempfile

from platformio import fs
from platformio.package.exception import PackageException
from platformio.package.manifest.parser import ManifestFileType, ManifestParserFactory
from platformio.package.manifest.schema import ManifestSchema
from platformio.unpacker import FileUnpacker


class PackagePacker(object):
    EXCLUDE_DEFAULT = [
        "._*",
        ".DS_Store",
        ".git",
        ".hg",
        ".svn",
        ".pio",
    ]
    INCLUDE_DEFAULT = ManifestFileType.items().values()

    def __init__(self, package, manifest_uri=None):
        self.package = package
        self.manifest_uri = manifest_uri

    def pack(self, dst=None):
        tmp_dir = tempfile.mkdtemp()
        try:
            src = self.package

            # if zip/tar.gz -> unpack to tmp dir
            if not os.path.isdir(src):
                with FileUnpacker(src) as fu:
                    assert fu.unpack(tmp_dir, silent=True)
                src = tmp_dir

            src = self.find_source_root(src)

            manifest = self.load_manifest(src)
            filename = re.sub(
                r"[^\da-zA-Z\-\._]+",
                "",
                "{name}{system}-{version}.tar.gz".format(
                    name=manifest["name"],
                    system="-" + manifest["system"][0] if "system" in manifest else "",
                    version=manifest["version"],
                ),
            )

            if not dst:
                dst = os.path.join(os.getcwd(), filename)
            elif os.path.isdir(dst):
                dst = os.path.join(dst, filename)

            return self._create_tarball(
                src,
                dst,
                include=manifest.get("export", {}).get("include"),
                exclude=manifest.get("export", {}).get("exclude"),
            )
        finally:
            shutil.rmtree(tmp_dir)

    @staticmethod
    def load_manifest(src):
        mp = ManifestParserFactory.new_from_dir(src)
        return ManifestSchema().load_manifest(mp.as_dict())

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

    def _create_tarball(self, src, dst, include=None, exclude=None):
        # remap root
        if (
            include
            and len(include) == 1
            and os.path.isdir(os.path.join(src, include[0]))
        ):
            src = os.path.join(src, include[0])
            include = None

        src_filters = self.compute_src_filters(include, exclude)
        with tarfile.open(dst, "w:gz") as tar:
            for f in fs.match_src_files(src, src_filters, followlinks=False):
                tar.add(os.path.join(src, f), f)
        return dst

    def compute_src_filters(self, include, exclude):
        result = ["+<%s>" % p for p in include or ["*", ".*"]]
        result += ["-<%s>" % p for p in exclude or []]
        result += ["-<%s>" % p for p in self.EXCLUDE_DEFAULT]
        # automatically include manifests
        result += ["+<%s>" % p for p in self.INCLUDE_DEFAULT]
        return result
