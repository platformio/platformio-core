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

from platformio.package.spec import PackageSpec


def test_ownername():
    assert PackageSpec("alice/foo library") == PackageSpec(
        ownername="alice", name="foo library"
    )
    assert PackageSpec(" bob / bar ") == PackageSpec(ownername="bob", name="bar")


def test_id():
    assert PackageSpec(13) == PackageSpec(id=13)
    assert PackageSpec("20") == PackageSpec(id=20)
    assert PackageSpec("id=199") == PackageSpec(id=199)


def test_name():
    assert PackageSpec("foo") == PackageSpec(name="foo")
    assert PackageSpec(" bar-24 ") == PackageSpec(name="bar-24")


def test_requirements():
    assert PackageSpec("foo@1.2.3") == PackageSpec(name="foo", requirements="1.2.3")
    assert PackageSpec("bar @ ^1.2.3") == PackageSpec(name="bar", requirements="^1.2.3")
    assert PackageSpec("13 @ ~2.0") == PackageSpec(id=13, requirements="~2.0")
    assert PackageSpec("id=20 @ !=1.2.3,<2.0") == PackageSpec(
        id=20, requirements="!=1.2.3,<2.0"
    )


def test_local_urls():
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


def test_external_urls():
    assert PackageSpec(
        "https://github.com/platformio/platformio-core/archive/develop.zip"
    ) == PackageSpec(
        url="https://github.com/platformio/platformio-core/archive/develop.zip",
        name="develop",
    )
    assert PackageSpec(
        "https://github.com/platformio/platformio-core/archive/develop.zip?param=value"
        " @ !=2"
    ) == PackageSpec(
        url="https://github.com/platformio/platformio-core/archive/"
        "develop.zip?param=value",
        name="develop",
        requirements="!=2",
    )
    assert PackageSpec(
        "platformio-core="
        "https://github.com/platformio/platformio-core/archive/develop.tar.gz@4.4.0"
    ) == PackageSpec(
        url="https://github.com/platformio/platformio-core/archive/develop.tar.gz",
        name="platformio-core",
        requirements="4.4.0",
    )


def test_vcs_urls():
    assert PackageSpec(
        "https://github.com/platformio/platformio-core.git"
    ) == PackageSpec(
        name="platformio-core", url="https://github.com/platformio/platformio-core.git",
    )
    assert PackageSpec(
        "wolfSSL=https://os.mbed.com/users/wolfSSL/code/wolfSSL/"
    ) == PackageSpec(
        name="wolfSSL", url="https://os.mbed.com/users/wolfSSL/code/wolfSSL/",
    )
    assert PackageSpec(
        "git+https://github.com/platformio/platformio-core.git#master"
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
    assert PackageSpec("git@github.com:platformio/platformio-core.git") == PackageSpec(
        name="platformio-core", url="git@github.com:platformio/platformio-core.git",
    )
    assert PackageSpec(
        "pkg=git+git@github.com:platformio/platformio-core.git @ ^1.2.3,!=5"
    ) == PackageSpec(
        name="pkg",
        url="git+git@github.com:platformio/platformio-core.git",
        requirements="^1.2.3,!=5",
    )
