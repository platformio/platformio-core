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

import jsondiff
import semantic_version

from platformio.package.meta import (
    PackageMetaData,
    PackageOutdatedResult,
    PackageSpec,
    PackageType,
)


def test_outdated_result():
    result = PackageOutdatedResult(current="1.2.3", latest="2.0.0")
    assert result.is_outdated()
    assert result.is_outdated(allow_incompatible=True)
    result = PackageOutdatedResult(current="1.2.3", latest="2.0.0", wanted="1.5.4")
    assert result.is_outdated()
    assert result.is_outdated(allow_incompatible=True)
    result = PackageOutdatedResult(current="1.2.3", latest="2.0.0", wanted="1.2.3")
    assert not result.is_outdated()
    assert result.is_outdated(allow_incompatible=True)
    result = PackageOutdatedResult(current="1.2.3", latest="2.0.0", detached=True)
    assert not result.is_outdated()
    assert not result.is_outdated(allow_incompatible=True)


def test_spec_owner():
    assert PackageSpec("alice/foo library") == PackageSpec(
        owner="alice", name="foo library"
    )
    spec = PackageSpec(" Bob / BarUpper ")
    assert spec != PackageSpec(owner="BOB", name="BARUPPER")
    assert spec.owner == "Bob"
    assert spec.name == "BarUpper"


def test_spec_id():
    assert PackageSpec(13) == PackageSpec(id=13)
    assert PackageSpec("20") == PackageSpec(id=20)
    spec = PackageSpec("id=199")
    assert spec == PackageSpec(id=199)
    assert isinstance(spec.id, int)


def test_spec_name():
    assert PackageSpec("foo") == PackageSpec(name="foo")
    assert PackageSpec(" bar-24 ") == PackageSpec(name="bar-24")


def test_spec_requirements():
    assert PackageSpec("foo@1.2.3") == PackageSpec(name="foo", requirements="1.2.3")
    assert PackageSpec(
        name="foo", requirements=semantic_version.Version("1.2.3")
    ) == PackageSpec(name="foo", requirements="1.2.3")
    assert PackageSpec("bar @ ^1.2.3") == PackageSpec(name="bar", requirements="^1.2.3")
    assert PackageSpec("13 @ ~2.0") == PackageSpec(id=13, requirements="~2.0")
    assert PackageSpec(
        name="hello", requirements=semantic_version.SimpleSpec("~1.2.3")
    ) == PackageSpec(name="hello", requirements="~1.2.3")
    spec = PackageSpec("id=20 @ !=1.2.3,<2.0")
    assert not spec.external
    assert isinstance(spec.requirements, semantic_version.SimpleSpec)
    assert semantic_version.Version("1.3.0-beta.1") in spec.requirements
    assert spec == PackageSpec(id=20, requirements="!=1.2.3,<2.0")


def test_spec_local_urls(tmpdir_factory):
    assert PackageSpec("file:///tmp/foo.tar.gz") == PackageSpec(
        url="file:///tmp/foo.tar.gz", name="foo"
    )
    assert PackageSpec("customName=file:///tmp/bar.zip") == PackageSpec(
        url="file:///tmp/bar.zip", name="customName"
    )
    assert PackageSpec("file:///tmp/some-lib/") == PackageSpec(
        url="file:///tmp/some-lib/", name="some-lib"
    )
    assert PackageSpec("file:///tmp/foo.tar.gz@~2.3.0-beta.1") == PackageSpec(
        url="file:///tmp/foo.tar.gz", name="foo", requirements="~2.3.0-beta.1"
    )
    # detached folder with "@" symbol
    pkg_dir = tmpdir_factory.mktemp("storage").join("detached@1.2.3").mkdir()
    assert PackageSpec("file://%s" % str(pkg_dir)) == PackageSpec(
        name="detached", url="file://%s" % pkg_dir
    )


def test_spec_external_urls():
    assert PackageSpec(
        "https://github.com/platformio/platformio-core/archive/develop.zip"
    ) == PackageSpec(
        url="https://github.com/platformio/platformio-core/archive/develop.zip",
        name="platformio-core",
    )
    assert PackageSpec(
        "https://github.com/platformio/platformio-core/archive/develop.zip?param=value"
        " @ !=2"
    ) == PackageSpec(
        url="https://github.com/platformio/platformio-core/archive/"
        "develop.zip?param=value",
        name="platformio-core",
        requirements="!=2",
    )
    spec = PackageSpec(
        "Custom-Name="
        "https://github.com/platformio/platformio-core/archive/develop.tar.gz@4.4.0"
    )
    assert spec.external
    assert spec.has_custom_name()
    assert spec.name == "Custom-Name"
    assert spec == PackageSpec(
        url="https://github.com/platformio/platformio-core/archive/develop.tar.gz",
        name="Custom-Name",
        requirements="4.4.0",
    )


def test_spec_vcs_urls():
    assert PackageSpec("https://github.com/platformio/platformio-core") == PackageSpec(
        name="platformio-core", url="git+https://github.com/platformio/platformio-core"
    )
    assert PackageSpec("https://gitlab.com/username/reponame") == PackageSpec(
        name="reponame", url="git+https://gitlab.com/username/reponame"
    )
    assert PackageSpec(
        "wolfSSL=https://os.mbed.com/users/wolfSSL/code/wolfSSL/"
    ) == PackageSpec(
        name="wolfSSL", url="hg+https://os.mbed.com/users/wolfSSL/code/wolfSSL/"
    )
    assert PackageSpec(
        "https://github.com/platformio/platformio-core.git#master"
    ) == PackageSpec(
        name="platformio-core",
        url="git+https://github.com/platformio/platformio-core.git#master",
    )
    assert PackageSpec(
        "core=git+ssh://github.com/platformio/platformio-core.git#v4.4.0@4.4.0"
    ) == PackageSpec(
        name="core",
        url="git+ssh://github.com/platformio/platformio-core.git#v4.4.0",
        requirements="4.4.0",
    )
    assert PackageSpec(
        "username@github.com:platformio/platformio-core.git"
    ) == PackageSpec(
        name="platformio-core",
        url="git+username@github.com:platformio/platformio-core.git",
    )
    assert PackageSpec(
        "pkg=git+git@github.com:platformio/platformio-core.git @ ^1.2.3,!=5"
    ) == PackageSpec(
        name="pkg",
        url="git+git@github.com:platformio/platformio-core.git",
        requirements="^1.2.3,!=5",
    )


def test_spec_as_dict():
    assert not jsondiff.diff(
        PackageSpec("bob/foo@1.2.3").as_dict(),
        {
            "owner": "bob",
            "id": None,
            "name": "foo",
            "requirements": "1.2.3",
            "url": None,
        },
    )
    assert not jsondiff.diff(
        PackageSpec(
            "https://github.com/platformio/platformio-core/archive/develop.zip?param=value"
            " @ !=2"
        ).as_dict(),
        {
            "owner": None,
            "id": None,
            "name": "platformio-core",
            "requirements": "!=2",
            "url": "https://github.com/platformio/platformio-core/archive/develop.zip?param=value",
        },
    )


def test_spec_as_dependency():
    assert PackageSpec("owner/pkgname").as_dependency() == "owner/pkgname"
    assert PackageSpec(owner="owner", name="pkgname").as_dependency() == "owner/pkgname"
    assert PackageSpec("bob/foo @ ^1.2.3").as_dependency() == "bob/foo@^1.2.3"
    assert (
        PackageSpec(
            "https://github.com/o/r/a/develop.zip?param=value @ !=2"
        ).as_dependency()
        == "https://github.com/o/r/a/develop.zip?param=value @ !=2"
    )
    assert (
        PackageSpec(
            "wolfSSL=https://os.mbed.com/users/wolfSSL/code/wolfSSL/"
        ).as_dependency()
        == "wolfSSL=https://os.mbed.com/users/wolfSSL/code/wolfSSL/"
    )


def test_metadata_as_dict():
    metadata = PackageMetaData(PackageType.LIBRARY, "foo", "1.2.3")
    # test setter
    metadata.version = "0.1.2+12345"
    assert metadata.version == semantic_version.Version("0.1.2+12345")
    assert not jsondiff.diff(
        metadata.as_dict(),
        {
            "type": PackageType.LIBRARY,
            "name": "foo",
            "version": "0.1.2+12345",
            "spec": None,
        },
    )

    assert not jsondiff.diff(
        PackageMetaData(
            PackageType.TOOL,
            "toolchain",
            "2.0.5",
            PackageSpec("platformio/toolchain@~2.0.0"),
        ).as_dict(),
        {
            "type": PackageType.TOOL,
            "name": "toolchain",
            "version": "2.0.5",
            "spec": {
                "owner": "platformio",
                "id": None,
                "name": "toolchain",
                "requirements": "~2.0.0",
                "url": None,
            },
        },
    )


def test_metadata_dump(tmpdir_factory):
    pkg_dir = tmpdir_factory.mktemp("package")
    metadata = PackageMetaData(
        PackageType.TOOL,
        "toolchain",
        "2.0.5",
        PackageSpec("platformio/toolchain@~2.0.0"),
    )

    dst = pkg_dir.join(".piopm")
    metadata.dump(str(dst))
    assert os.path.isfile(str(dst))
    contents = dst.read()
    assert all(s in contents for s in ("null", '"~2.0.0"'))


def test_metadata_load(tmpdir_factory):
    contents = """
{
  "name": "foo",
  "spec": {
    "name": "foo",
    "owner": "username",
    "requirements": "!=3.4.5"
  },
  "type": "platform",
  "version": "0.1.3"
}
"""
    pkg_dir = tmpdir_factory.mktemp("package")
    dst = pkg_dir.join(".piopm")
    dst.write(contents)
    metadata = PackageMetaData.load(str(dst))
    assert metadata.version == semantic_version.Version("0.1.3")
    assert metadata == PackageMetaData(
        PackageType.PLATFORM,
        "foo",
        "0.1.3",
        spec=PackageSpec(owner="username", name="foo", requirements="!=3.4.5"),
    )

    piopm_path = pkg_dir.join(".piopm")
    metadata = PackageMetaData(
        PackageType.LIBRARY, "mylib", version="1.2.3", spec=PackageSpec("mylib")
    )
    metadata.dump(str(piopm_path))
    restored_metadata = PackageMetaData.load(str(piopm_path))
    assert metadata == restored_metadata
