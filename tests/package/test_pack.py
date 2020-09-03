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
import tarfile

import pytest

from platformio import fs
from platformio.compat import WINDOWS
from platformio.package.exception import UnknownManifestError
from platformio.package.pack import PackagePacker


def test_base(tmpdir_factory):
    pkg_dir = tmpdir_factory.mktemp("package")
    pkg_dir.join(".git").mkdir().join("file").write("")
    pkg_dir.join(".gitignore").write("tests")
    pkg_dir.join("._ignored").write("")
    pkg_dir.join("main.cpp").write("#include <stdio.h>")
    p = PackagePacker(str(pkg_dir))
    # test missed manifest
    with pytest.raises(UnknownManifestError):
        p.pack()
    # minimal package
    pkg_dir.join("library.json").write('{"name": "foo", "version": "1.0.0"}')
    pkg_dir.mkdir("include").join("main.h").write("#ifndef")
    with fs.cd(str(pkg_dir)):
        p.pack()
    with tarfile.open(os.path.join(str(pkg_dir), "foo-1.0.0.tar.gz"), "r:gz") as tar:
        assert set(tar.getnames()) == set(
            [".gitignore", "include/main.h", "library.json", "main.cpp"]
        )


def test_filters(tmpdir_factory):
    pkg_dir = tmpdir_factory.mktemp("package")
    src_dir = pkg_dir.mkdir("src")
    src_dir.join("main.cpp").write("#include <stdio.h>")
    src_dir.mkdir("util").join("helpers.cpp").write("void")
    pkg_dir.mkdir("include").join("main.h").write("#ifndef")
    test_dir = pkg_dir.mkdir("tests")
    test_dir.join("test_1.h").write("")
    test_dir.join("test_2.h").write("")

    # test include with remap of root
    pkg_dir.join("library.json").write(
        json.dumps(dict(name="bar", version="1.2.3", export={"include": "src"}))
    )
    p = PackagePacker(str(pkg_dir))
    with tarfile.open(p.pack(str(pkg_dir)), "r:gz") as tar:
        assert set(tar.getnames()) == set(
            ["util/helpers.cpp", "main.cpp", "library.json"]
        )
    os.unlink(str(src_dir.join("library.json")))

    # test include "src" and "include"
    pkg_dir.join("library.json").write(
        json.dumps(
            dict(name="bar", version="1.2.3", export={"include": ["src", "include"]})
        )
    )
    p = PackagePacker(str(pkg_dir))
    with tarfile.open(p.pack(str(pkg_dir)), "r:gz") as tar:
        assert set(tar.getnames()) == set(
            ["include/main.h", "library.json", "src/main.cpp", "src/util/helpers.cpp"]
        )

    # test include & exclude
    pkg_dir.join("library.json").write(
        json.dumps(
            dict(
                name="bar",
                version="1.2.3",
                export={"include": ["src", "include"], "exclude": ["*/*.h"]},
            )
        )
    )
    p = PackagePacker(str(pkg_dir))
    with tarfile.open(p.pack(str(pkg_dir)), "r:gz") as tar:
        assert set(tar.getnames()) == set(
            ["library.json", "src/main.cpp", "src/util/helpers.cpp"]
        )


def test_symlinks(tmpdir_factory):
    # Windows does not support symbolic links
    if WINDOWS:
        return
    pkg_dir = tmpdir_factory.mktemp("package")
    src_dir = pkg_dir.mkdir("src")
    src_dir.join("main.cpp").write("#include <stdio.h>")
    pkg_dir.mkdir("include").join("main.h").write("#ifndef")
    src_dir.join("main.h").mksymlinkto(os.path.join("..", "include", "main.h"))
    pkg_dir.join("library.json").write('{"name": "bar", "version": "2.0.0"}')
    tarball = pkg_dir.join("bar.tar.gz")
    with tarfile.open(str(tarball), "w:gz") as tar:
        for item in pkg_dir.listdir():
            tar.add(str(item), str(item.relto(pkg_dir)))

    p = PackagePacker(str(tarball))
    assert p.pack(str(pkg_dir)).endswith("bar-2.0.0.tar.gz")
    with tarfile.open(os.path.join(str(pkg_dir), "bar-2.0.0.tar.gz"), "r:gz") as tar:
        assert set(tar.getnames()) == set(
            ["include/main.h", "library.json", "src/main.cpp", "src/main.h"]
        )
        m = tar.getmember("src/main.h")
        assert m.issym()


def test_source_root(tmpdir_factory):
    pkg_dir = tmpdir_factory.mktemp("package")
    root_dir = pkg_dir.mkdir("root")
    src_dir = root_dir.mkdir("src")
    src_dir.join("main.cpp").write("#include <stdio.h>")
    root_dir.join("library.json").write('{"name": "bar", "version": "2.0.0"}')
    p = PackagePacker(str(pkg_dir))
    with tarfile.open(p.pack(str(pkg_dir)), "r:gz") as tar:
        assert set(tar.getnames()) == set(["library.json", "src/main.cpp"])


def test_manifest_uri(tmpdir_factory):
    pkg_dir = tmpdir_factory.mktemp("package")
    root_dir = pkg_dir.mkdir("root")
    src_dir = root_dir.mkdir("src")
    src_dir.join("main.cpp").write("#include <stdio.h>")
    root_dir.join("library.json").write('{"name": "foo", "version": "1.0.0"}')
    bar_dir = root_dir.mkdir("library").mkdir("bar")
    bar_dir.join("library.json").write('{"name": "bar", "version": "2.0.0"}')
    bar_dir.mkdir("include").join("bar.h").write("")

    manifest_path = pkg_dir.join("remote_library.json")
    manifest_path.write(
        '{"name": "bar", "version": "3.0.0", "export": {"include": "root/library/bar"}}'
    )

    p = PackagePacker(str(pkg_dir), manifest_uri="file:%s" % manifest_path)
    p.pack(str(pkg_dir))
    with tarfile.open(os.path.join(str(pkg_dir), "bar-2.0.0.tar.gz"), "r:gz") as tar:
        assert set(tar.getnames()) == set(["library.json", "include/bar.h"])
