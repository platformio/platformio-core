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

# pylint: disable=unused-argument

import logging
import os
import time
from pathlib import Path
from random import random

import pytest
import semantic_version

from platformio import fs, util
from platformio.package.exception import (
    MissingPackageManifestError,
    UnknownPackageError,
)
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.package.pack import PackagePacker


def test_download(isolated_pio_core):
    url = "https://github.com/platformio/platformio-core/archive/v4.3.4.zip"
    checksum = "69d59642cb91e64344f2cdc1d3b98c5cd57679b5f6db7accc7707bd4c5d9664a"
    lm = LibraryPackageManager()
    lm.set_log_level(logging.ERROR)
    archive_path = lm.download(url, checksum)
    assert fs.calculate_file_hashsum("sha256", archive_path) == checksum
    lm.cleanup_expired_downloads(random())
    assert os.path.isfile(archive_path)
    # test outdated downloads
    lm.set_download_utime(archive_path, time.time() - lm.DOWNLOAD_CACHE_EXPIRE - 1)
    lm.cleanup_expired_downloads(random())
    assert not os.path.isfile(archive_path)
    # check that key is deleted from DB
    with open(lm.get_download_usagedb_path(), encoding="utf8") as fp:
        assert os.path.basename(archive_path) not in fp.read()


def test_find_pkg_root(isolated_pio_core, tmpdir_factory):
    # has manifest
    pkg_dir = tmpdir_factory.mktemp("package-has-manifest")
    root_dir = pkg_dir.join("nested").mkdir().join("folder").mkdir()
    root_dir.join("platform.json").write("")
    pm = PlatformPackageManager()
    found_dir = pm.find_pkg_root(str(pkg_dir), spec=None)
    assert os.path.realpath(str(root_dir)) == os.path.realpath(found_dir)

    # does not have manifest
    pkg_dir = tmpdir_factory.mktemp("package-does-not-have-manifest")
    pkg_dir.join("nested").mkdir().join("folder").mkdir().join("readme.txt").write("")
    pm = PlatformPackageManager()
    with pytest.raises(MissingPackageManifestError):
        pm.find_pkg_root(str(pkg_dir), spec=None)

    # library package without manifest, should find source root
    pkg_dir = tmpdir_factory.mktemp("library-package-without-manifest")
    root_dir = pkg_dir.join("nested").mkdir().join("folder").mkdir()
    root_dir.join("src").mkdir().join("main.cpp").write("")
    root_dir.join("include").mkdir().join("main.h").write("")
    assert os.path.realpath(str(root_dir)) == os.path.realpath(
        LibraryPackageManager.find_library_root(str(pkg_dir))
    )

    # library manager should create "library.json"
    lm = LibraryPackageManager()
    spec = PackageSpec("custom-name@1.0.0")
    pkg_root = lm.find_pkg_root(str(pkg_dir), spec)
    manifest_path = os.path.join(pkg_root, "library.json")
    assert os.path.realpath(str(root_dir)) == os.path.realpath(pkg_root)
    assert os.path.isfile(manifest_path)
    manifest = lm.load_manifest(pkg_root)
    assert manifest["name"] == "custom-name"
    assert "0.0.0" in str(manifest["version"])


def test_build_legacy_spec(isolated_pio_core, tmpdir_factory):
    storage_dir = tmpdir_factory.mktemp("storage")
    pm = PlatformPackageManager(str(storage_dir))
    # test src manifest
    pkg1_dir = storage_dir.join("pkg-1").mkdir()
    pkg1_dir.join(".pio").mkdir().join(".piopkgmanager.json").write(
        """
{
    "name": "StreamSpy-0.0.1.tar",
    "url": "https://dl.platformio.org/e8936b7/StreamSpy-0.0.1.tar.gz",
    "requirements": null
}
"""
    )
    assert pm.build_legacy_spec(str(pkg1_dir)) == PackageSpec(
        name="StreamSpy-0.0.1.tar",
        uri="https://dl.platformio.org/e8936b7/StreamSpy-0.0.1.tar.gz",
    )

    # without src manifest
    pkg2_dir = storage_dir.join("pkg-2").mkdir()
    pkg2_dir.join("main.cpp").write("")
    with pytest.raises(MissingPackageManifestError):
        pm.build_legacy_spec(str(pkg2_dir))

    # with package manifest
    pkg3_dir = storage_dir.join("pkg-3").mkdir()
    pkg3_dir.join("platform.json").write('{"name": "pkg3", "version": "1.2.0"}')
    assert pm.build_legacy_spec(str(pkg3_dir)) == PackageSpec(name="pkg3")


def test_build_metadata(isolated_pio_core, tmpdir_factory):
    pm = PlatformPackageManager()
    vcs_revision = "a2ebfd7c0f"
    pkg_dir = tmpdir_factory.mktemp("package")

    # test package without manifest
    with pytest.raises(MissingPackageManifestError):
        pm.load_manifest(str(pkg_dir))
    with pytest.raises(MissingPackageManifestError):
        pm.build_metadata(str(pkg_dir), PackageSpec("MyLib"))

    # with manifest
    pkg_dir.join("platform.json").write(
        '{"name": "Dev-Platform", "version": "1.2.3-alpha.1"}'
    )
    metadata = pm.build_metadata(str(pkg_dir), PackageSpec("owner/platform-name"))
    assert metadata.name == "Dev-Platform"
    assert str(metadata.version) == "1.2.3-alpha.1"

    # with vcs
    metadata = pm.build_metadata(
        str(pkg_dir), PackageSpec("owner/platform-name"), vcs_revision
    )
    assert str(metadata.version) == ("1.2.3-alpha.1+sha." + vcs_revision)
    assert metadata.version.build[1] == vcs_revision


def test_install_from_uri(isolated_pio_core, tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp("tmp")
    storage_dir = tmpdir_factory.mktemp("storage")
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)

    # install from local directory
    src_dir = tmp_dir.join("local-lib-dir").mkdir()
    src_dir.join("main.cpp").write("")
    spec = PackageSpec("file://%s" % src_dir)
    pkg = lm.install(spec)
    assert os.path.isfile(os.path.join(pkg.path, "main.cpp"))
    manifest = lm.load_manifest(pkg)
    assert manifest["name"] == "local-lib-dir"
    assert manifest["version"].startswith("0.0.0+")
    assert spec == pkg.metadata.spec

    # install from local archive
    src_dir = tmp_dir.join("archive-src").mkdir()
    root_dir = src_dir.mkdir("root")
    root_dir.mkdir("src").join("main.cpp").write("#include <stdio.h>")
    root_dir.join("library.json").write(
        '{"name": "manifest-lib-name", "version": "2.0.0"}'
    )
    tarball_path = PackagePacker(str(src_dir)).pack(str(tmp_dir))
    spec = PackageSpec("file://%s" % tarball_path)
    pkg = lm.install(spec)
    assert os.path.isfile(os.path.join(pkg.path, "src", "main.cpp"))
    assert pkg == lm.get_package(spec)
    assert spec == pkg.metadata.spec

    # install from registry
    src_dir = tmp_dir.join("registry-1").mkdir()
    src_dir.join("library.properties").write(
        """
name = wifilib
version = 5.2.7
"""
    )
    spec = PackageSpec("company/wifilib @ ^5")
    pkg = lm.install_from_uri("file://%s" % src_dir, spec)
    assert str(pkg.metadata.version) == "5.2.7"

    # check package folder names
    lm.memcache_reset()
    assert ["local-lib-dir", "manifest-lib-name", "wifilib"] == [
        os.path.basename(pkg.path) for pkg in lm.get_installed()
    ]


def test_install_from_registry(isolated_pio_core, tmpdir_factory):
    # Libraries
    lm = LibraryPackageManager(str(tmpdir_factory.mktemp("lib-storage")))
    lm.set_log_level(logging.ERROR)
    # library with dependencies
    lm.install("AsyncMqttClient-esphome @ 0.8.6")
    assert len(lm.get_installed()) == 3
    pkg = lm.get_package("AsyncTCP-esphome")
    assert pkg.metadata.spec.owner == "esphome"
    assert not lm.get_package("non-existing-package")
    # mbed library
    assert lm.install("wolfSSL")
    assert len(lm.get_installed()) == 4
    # case sensitive author name
    assert lm.install("DallasTemperature")
    assert lm.get_package("OneWire").metadata.version.major >= 2
    assert len(lm.get_installed()) == 6

    # test conflicted names
    lm = LibraryPackageManager(str(tmpdir_factory.mktemp("conflicted-storage")))
    lm.set_log_level(logging.ERROR)
    lm.install("z3t0/IRremote")
    lm.install("mbed-yuhki50/IRremote")
    assert len(lm.get_installed()) == 2

    # Tools
    tm = ToolPackageManager(str(tmpdir_factory.mktemp("tool-storage")))
    tm.set_log_level(logging.ERROR)
    pkg = tm.install("platformio/tool-stlink @ ~1.10400.0")
    manifest = tm.load_manifest(pkg)
    assert tm.is_system_compatible(manifest.get("system"))
    assert util.get_systype() in manifest.get("system", [])

    # Test unknown
    with pytest.raises(UnknownPackageError):
        tm.install("unknown-package-tool @ 9.1.1")
    with pytest.raises(UnknownPackageError):
        tm.install("owner/unknown-package-tool")


def test_install_lib_depndencies(isolated_pio_core, tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp("tmp")

    src_dir = tmp_dir.join("lib-with-deps").mkdir()
    root_dir = src_dir.mkdir("root")
    root_dir.mkdir("src").join("main.cpp").write("#include <stdio.h>")
    root_dir.join("library.json").write(
        """
{
  "name": "lib-with-deps",
  "version": "2.0.0",
  "dependencies": [
    {
      "owner": "bblanchon",
      "name": "ArduinoJson",
      "version": "^6.16.1"
    },
    {
      "name": "external-repo",
      "version": "https://github.com/milesburton/Arduino-Temperature-Control-Library.git#4a0ccc1"
    }
  ]
}
"""
    )

    lm = LibraryPackageManager(str(tmpdir_factory.mktemp("lib-storage")))
    lm.set_log_level(logging.ERROR)
    lm.install("file://%s" % str(src_dir))
    installed = lm.get_installed()
    assert len(installed) == 4
    assert set(["external-repo", "ArduinoJson", "lib-with-deps", "OneWire"]) == set(
        p.metadata.name for p in installed
    )


def test_install_force(isolated_pio_core, tmpdir_factory):
    lm = LibraryPackageManager(str(tmpdir_factory.mktemp("lib-storage")))
    lm.set_log_level(logging.ERROR)
    # install #64 ArduinoJson
    pkg = lm.install("64 @ ^5")
    assert pkg.metadata.version.major == 5
    # try install the latest without specification
    pkg = lm.install("64")
    assert pkg.metadata.version.major == 5
    assert len(lm.get_installed()) == 1
    # re-install the latest
    pkg = lm.install(64, force=True)
    assert len(lm.get_installed()) == 1
    assert pkg.metadata.version.major > 5


def test_symlink(tmp_path: Path):
    external_pkg_dir = tmp_path / "External"
    external_pkg_dir.mkdir()
    (external_pkg_dir / "library.json").write_text(
        """
{
    "name": "External",
    "version": "1.0.0"
}
"""
    )

    storage_dir = tmp_path / "storage"
    installed_pkg_dir = storage_dir / "installed"
    installed_pkg_dir.mkdir(parents=True)
    (installed_pkg_dir / "library.json").write_text(
        """
{
    "name": "Installed",
    "version": "1.0.0"
}
"""
    )

    spec = "CustomExternal=symlink://%s" % str(external_pkg_dir)
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)
    pkg = lm.install(spec)
    assert os.path.isfile(str(storage_dir / "CustomExternal.pio-link"))
    assert pkg.metadata.name == "External"
    assert pkg.metadata.version.major == 1
    assert ["External", "Installed"] == [
        pkg.metadata.name for pkg in lm.get_installed()
    ]
    pkg = lm.get_package("External")
    assert Path(pkg.path) == external_pkg_dir
    assert pkg.metadata.spec.uri.startswith("symlink://")
    assert lm.get_package(spec).metadata.spec.uri.startswith("symlink://")

    # try to update
    lm.update(pkg)

    # uninstall
    lm.uninstall("External")
    assert ["Installed"] == [pkg.metadata.name for pkg in lm.get_installed()]
    # ensure original package was not rmeoved
    assert external_pkg_dir.is_dir()

    # install again, remove from a disk
    assert lm.install("symlink://%s" % str(external_pkg_dir))
    assert os.path.isfile(str(storage_dir / "External.pio-link"))
    assert ["External", "Installed"] == [
        pkg.metadata.name for pkg in lm.get_installed()
    ]
    fs.rmtree(str(external_pkg_dir))
    lm.memcache_reset()
    assert ["Installed"] == [pkg.metadata.name for pkg in lm.get_installed()]


def test_scripts(isolated_pio_core, tmp_path: Path):
    pkg_dir = tmp_path / "foo"
    scripts_dir = pkg_dir / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "script.py").write_text(
        """
import sys
from pathlib import Path

action = "postinstall" if len(sys.argv) == 1 else sys.argv[1]
Path("%s.flag" % action).touch()

if action == "preuninstall":
    Path("../%s.flag" % action).touch()
"""
    )
    (pkg_dir / "library.json").write_text(
        """
{
    "name": "foo",
    "version": "1.0.0",
    "scripts": {
        "postinstall": "scripts/script.py",
        "preuninstall2": ["scripts/script.py", "preuninstall"]
    }
}
"""
    )

    storage_dir = tmp_path / "storage"
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)
    lm.install("file://%s" % str(pkg_dir))
    assert os.path.isfile(os.path.join(lm.get_package("foo").path, "postinstall.flag"))
    lm.uninstall("foo")
    (storage_dir / "preuninstall.flag").is_file()


def test_install_circular_dependencies(tmp_path: Path):
    storage_dir = tmp_path / "storage"
    # Foo
    pkg_dir = storage_dir / "foo"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "library.json").write_text(
        """
{
    "name": "Foo",
    "version": "1.0.0",
    "dependencies": {
        "Bar": "*"
    }
}
"""
    )
    # Bar
    pkg_dir = storage_dir / "bar"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "library.json").write_text(
        """
{
    "name": "Bar",
    "version": "1.0.0",
    "dependencies": {
        "Foo": "*"
    }
}
"""
    )

    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)
    assert len(lm.get_installed()) == 2

    # root library
    pkg_dir = tmp_path / "root"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "library.json").write_text(
        """
{
    "name": "Root",
    "version": "1.0.0",
    "dependencies": {
        "Foo": "^1.0.0",
        "Bar": "^1.0.0"
    }
}
"""
    )
    lm.install("file://%s" % str(pkg_dir))


def test_get_installed(isolated_pio_core, tmpdir_factory):
    storage_dir = tmpdir_factory.mktemp("storage")
    pm = ToolPackageManager(str(storage_dir))

    # VCS package
    (
        storage_dir.join("pkg-vcs")
        .mkdir()
        .join(".git")
        .mkdir()
        .join(".piopm")
        .write(
            """
{
  "name": "pkg-via-vcs",
  "spec": {
    "id": null,
    "name": "pkg-via-vcs",
    "owner": null,
    "requirements": null,
    "url": "git+https://github.com/username/repo.git"
  },
  "type": "tool",
  "version": "0.0.0+sha.1ea4d5e"
}
"""
        )
    )

    # package without metadata file
    (
        storage_dir.join("foo@3.4.5")
        .mkdir()
        .join("package.json")
        .write('{"name": "foo", "version": "3.4.5"}')
    )

    # package with metadata file
    foo_dir = storage_dir.join("foo").mkdir()
    foo_dir.join("package.json").write('{"name": "foo", "version": "3.6.0"}')
    foo_dir.join(".piopm").write(
        """
{
  "name": "foo",
  "spec": {
    "name": "foo",
    "owner": null,
    "requirements": "^3"
  },
  "type": "tool",
  "version": "3.6.0"
}
"""
    )

    # test "system"
    storage_dir.join("pkg-incompatible-system").mkdir().join("package.json").write(
        '{"name": "check-system", "version": "4.0.0", "system": ["unknown"]}'
    )
    storage_dir.join("pkg-compatible-system").mkdir().join("package.json").write(
        '{"name": "check-system", "version": "3.0.0", "system": "%s"}'
        % util.get_systype()
    )

    # invalid package
    storage_dir.join("invalid-package").mkdir().join("library.json").write(
        '{"name": "SomeLib", "version": "4.0.0"}'
    )

    installed = pm.get_installed()
    assert len(installed) == 4
    assert set(["pkg-via-vcs", "foo", "check-system"]) == set(
        p.metadata.name for p in installed
    )
    assert str(pm.get_package("foo").metadata.version) == "3.6.0"
    assert str(pm.get_package("check-system").metadata.version) == "3.0.0"


def test_uninstall(isolated_pio_core, tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp("tmp")
    storage_dir = tmpdir_factory.mktemp("storage")
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)

    # foo @ 1.0.0
    pkg_dir = tmp_dir.join("foo").mkdir()
    pkg_dir.join("library.json").write('{"name": "foo", "version": "1.0.0"}')
    foo_1_0_0_pkg = lm.install_from_uri("file://%s" % pkg_dir, "foo")
    # foo @ 1.3.0
    pkg_dir = tmp_dir.join("foo-1.3.0").mkdir()
    pkg_dir.join("library.json").write('{"name": "foo", "version": "1.3.0"}')
    lm.install_from_uri("file://%s" % pkg_dir, "foo")
    # bar
    pkg_dir = tmp_dir.join("bar").mkdir()
    pkg_dir.join("library.json").write('{"name": "bar", "version": "1.0.0"}')
    bar_pkg = lm.install("file://%s" % pkg_dir)

    assert len(lm.get_installed()) == 3
    assert os.path.isdir(os.path.join(str(storage_dir), "foo"))
    assert os.path.isdir(os.path.join(str(storage_dir), "foo@1.0.0"))

    # check detaching
    assert lm.uninstall("FOO")
    assert len(lm.get_installed()) == 2
    assert os.path.isdir(os.path.join(str(storage_dir), "foo"))
    assert not os.path.isdir(os.path.join(str(storage_dir), "foo@1.0.0"))

    # uninstall the rest
    assert lm.uninstall(foo_1_0_0_pkg.path)
    assert lm.uninstall(bar_pkg)

    assert not lm.get_installed()

    # test uninstall dependencies
    assert lm.install("AsyncMqttClient-esphome")
    assert len(lm.get_installed()) == 3
    assert lm.uninstall("AsyncMqttClient-esphome", skip_dependencies=True)
    assert len(lm.get_installed()) == 2

    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)
    assert lm.install("AsyncMqttClient-esphome")
    assert lm.uninstall("AsyncMqttClient-esphome")
    assert not lm.get_installed()


def test_registry(isolated_pio_core):
    lm = LibraryPackageManager()
    lm.set_log_level(logging.ERROR)

    # reveal ID
    assert lm.reveal_registry_package_id(PackageSpec(id=13)) == 13
    assert lm.reveal_registry_package_id(PackageSpec(name="OneWire")) == 1
    with pytest.raises(UnknownPackageError):
        lm.reveal_registry_package_id(PackageSpec(name="/non-existing-package/"))

    # fetch package data
    assert lm.fetch_registry_package(PackageSpec(id=1))["name"] == "OneWire"
    assert lm.fetch_registry_package(PackageSpec(name="ArduinoJson"))["id"] == 64
    assert (
        lm.fetch_registry_package(
            PackageSpec(id=13, owner="adafruit", name="Renamed library")
        )["name"]
        == "Adafruit GFX Library"
    )
    with pytest.raises(UnknownPackageError):
        lm.fetch_registry_package(
            PackageSpec(owner="unknown<>owner", name="/non-existing-package/")
        )
    with pytest.raises(UnknownPackageError):
        lm.fetch_registry_package(PackageSpec(name="/non-existing-package/"))


def test_update_with_metadata(isolated_pio_core, tmpdir_factory):
    storage_dir = tmpdir_factory.mktemp("storage")
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)

    # test non SemVer in registry
    pkg = lm.install("adafruit/Adafruit NeoPixel @ <1.9")
    outdated = lm.outdated(pkg)
    assert str(outdated.current) == "1.8.7"
    assert outdated.latest > semantic_version.Version("1.10.0")

    pkg = lm.install("ArduinoJson @ 6.19.4")
    # test latest
    outdated = lm.outdated(pkg)
    assert str(outdated.current) == "6.19.4"
    assert outdated.wanted is None
    assert outdated.latest > outdated.current
    assert outdated.latest > semantic_version.Version("5.99.99")

    # test wanted
    outdated = lm.outdated(pkg, PackageSpec("ArduinoJson@~6"))
    assert str(outdated.current) == "6.19.4"
    assert str(outdated.wanted) == "6.21.5"
    assert outdated.latest > semantic_version.Version("6.16.0")

    # update to the wanted 6.x
    new_pkg = lm.update("ArduinoJson@^6", PackageSpec("ArduinoJson@^6"))
    assert str(new_pkg.metadata.version) == "6.21.5"
    # check that old version is removed
    assert len(lm.get_installed()) == 2

    # update to the latest
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)
    pkg = lm.update("ArduinoJson")
    assert pkg.metadata.version == outdated.latest


def test_update_without_metadata(isolated_pio_core, tmpdir_factory):
    storage_dir = tmpdir_factory.mktemp("storage")
    storage_dir.join("legacy-package").mkdir().join("library.json").write(
        '{"name": "AsyncMqttClient-esphome", "version": "0.8"}'
    )
    storage_dir.join("legacy-dep").mkdir().join("library.json").write(
        '{"name": "AsyncTCP-esphome", "version": "1.1.1"}'
    )
    lm = LibraryPackageManager(str(storage_dir))
    pkg = lm.get_package("AsyncMqttClient-esphome")
    outdated = lm.outdated(pkg)
    assert len(lm.get_installed()) == 2
    assert str(pkg.metadata.version) == "0.8.0"
    assert outdated.latest > semantic_version.Version("0.8.0")

    # update
    lm = LibraryPackageManager(str(storage_dir))
    lm.set_log_level(logging.ERROR)
    new_pkg = lm.update(pkg)
    assert len(lm.get_installed()) == 4
    assert new_pkg.metadata.spec.owner == "heman"
