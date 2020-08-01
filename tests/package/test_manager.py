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
import time

import pytest

from platformio import fs, util
from platformio.package.exception import MissingPackageManifestError
from platformio.package.manager.library import LibraryPackageManager
from platformio.package.manager.platform import PlatformPackageManager
from platformio.package.manager.tool import ToolPackageManager
from platformio.package.meta import PackageSpec
from platformio.package.pack import PackagePacker


def test_download(isolated_pio_core):
    url = "https://github.com/platformio/platformio-core/archive/v4.3.4.zip"
    checksum = "69d59642cb91e64344f2cdc1d3b98c5cd57679b5f6db7accc7707bd4c5d9664a"
    lm = LibraryPackageManager()
    archive_path = lm.download(url, checksum, silent=True)
    assert fs.calculate_file_hashsum("sha256", archive_path) == checksum
    lm.cleanup_expired_downloads()
    assert os.path.isfile(archive_path)
    # test outdated downloads
    lm.set_download_utime(archive_path, time.time() - lm.DOWNLOAD_CACHE_EXPIRE - 1)
    lm.cleanup_expired_downloads()
    assert not os.path.isfile(archive_path)
    # check that key is deleted from DB
    with open(lm.get_download_usagedb_path()) as fp:
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
    pkg_root = lm.find_pkg_root(pkg_dir, spec)
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
        url="https://dl.platformio.org/e8936b7/StreamSpy-0.0.1.tar.gz",
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


def test_install_from_url(isolated_pio_core, tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp("tmp")
    storage_dir = tmpdir_factory.mktemp("storage")
    lm = LibraryPackageManager(str(storage_dir))

    # install from local directory
    src_dir = tmp_dir.join("local-lib-dir").mkdir()
    src_dir.join("main.cpp").write("")
    spec = PackageSpec("file://%s" % src_dir)
    pkg = lm.install(spec, silent=True)
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
    pkg = lm.install(spec, silent=True)
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
    pkg = lm.install_from_url("file://%s" % src_dir, spec)
    assert str(pkg.metadata.version) == "5.2.7"


def test_install_from_registry(isolated_pio_core, tmpdir_factory):
    # Libraries
    lm = LibraryPackageManager(str(tmpdir_factory.mktemp("lib-storage")))
    # library with dependencies
    lm.install("AsyncMqttClient-esphome @ 0.8.4", silent=True)
    assert len(lm.get_installed()) == 3
    pkg = lm.get_package("AsyncTCP-esphome")
    assert pkg.metadata.spec.owner == "ottowinter"
    assert not lm.get_package("non-existing-package")
    # mbed library
    assert lm.install("wolfSSL", silent=True)
    assert len(lm.get_installed()) == 4

    # Tools
    tm = ToolPackageManager(str(tmpdir_factory.mktemp("tool-storage")))
    pkg = tm.install("tool-stlink @ ~1.10400.0", silent=True)
    manifest = tm.load_manifest(pkg)
    assert tm.is_system_compatible(manifest.get("system"))
    assert util.get_systype() in manifest.get("system", [])


def test_install_force(isolated_pio_core, tmpdir_factory):
    lm = LibraryPackageManager(str(tmpdir_factory.mktemp("lib-storage")))
    # install #64 ArduinoJson
    pkg = lm.install("64 @ ^5", silent=True)
    assert pkg.metadata.version.major == 5
    # try install the latest without specification
    pkg = lm.install("64", silent=True)
    assert pkg.metadata.version.major == 5
    assert len(lm.get_installed()) == 1
    # re-install the latest
    pkg = lm.install(64, silent=True, force=True)
    assert len(lm.get_installed()) == 1
    assert pkg.metadata.version.major > 5


def test_get_installed(isolated_pio_core, tmpdir_factory):
    storage_dir = tmpdir_factory.mktemp("storage")
    lm = LibraryPackageManager(str(storage_dir))

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
  "type": "library",
  "version": "0.0.0+sha.1ea4d5e"
}
"""
        )
    )

    # package without metadata file
    (
        storage_dir.join("foo@3.4.5")
        .mkdir()
        .join("library.json")
        .write('{"name": "foo", "version": "3.4.5"}')
    )

    # package with metadata file
    foo_dir = storage_dir.join("foo").mkdir()
    foo_dir.join("library.json").write('{"name": "foo", "version": "3.6.0"}')
    foo_dir.join(".piopm").write(
        """
{
  "name": "foo",
  "spec": {
    "name": "foo",
    "owner": null,
    "requirements": "^3"
  },
  "type": "library",
  "version": "3.6.0"
}
"""
    )

    # invalid package
    storage_dir.join("invalid-package").mkdir().join("package.json").write(
        '{"name": "tool-scons", "version": "4.0.0"}'
    )

    installed = lm.get_installed()
    assert len(installed) == 3
    assert set(["pkg-via-vcs", "foo"]) == set(p.metadata.name for p in installed)
    assert str(lm.get_package("foo").metadata.version) == "3.6.0"


def test_uninstall(isolated_pio_core, tmpdir_factory):
    tmp_dir = tmpdir_factory.mktemp("tmp")
    storage_dir = tmpdir_factory.mktemp("storage")
    lm = LibraryPackageManager(str(storage_dir))

    # foo @ 1.0.0
    pkg_dir = tmp_dir.join("foo").mkdir()
    pkg_dir.join("library.json").write('{"name": "foo", "version": "1.0.0"}')
    foo_1_0_0_pkg = lm.install_from_url("file://%s" % pkg_dir, "foo")
    # foo @ 1.3.0
    pkg_dir = tmp_dir.join("foo-1.3.0").mkdir()
    pkg_dir.join("library.json").write('{"name": "foo", "version": "1.3.0"}')
    lm.install_from_url("file://%s" % pkg_dir, "foo")
    # bar
    pkg_dir = tmp_dir.join("bar").mkdir()
    pkg_dir.join("library.json").write('{"name": "bar", "version": "1.0.0"}')
    bar_pkg = lm.install("file://%s" % pkg_dir, silent=True)

    assert len(lm.get_installed()) == 3
    assert os.path.isdir(os.path.join(str(storage_dir), "foo"))
    assert os.path.isdir(os.path.join(str(storage_dir), "foo@1.0.0"))

    # check detaching
    assert lm.uninstall("FOO", silent=True)
    assert len(lm.get_installed()) == 2
    assert os.path.isdir(os.path.join(str(storage_dir), "foo"))
    assert not os.path.isdir(os.path.join(str(storage_dir), "foo@1.0.0"))

    # uninstall the rest
    assert lm.uninstall(foo_1_0_0_pkg.path, silent=True)
    assert lm.uninstall(bar_pkg, silent=True)

    assert len(lm.get_installed()) == 0
