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

import hashlib
import json
from zipfile import ZipFile

from platformio import util
from platformio.package.commands.install import package_install_cmd
from platformio.package.manager.library import LibraryPackageManager
from platformio.project.config import ProjectConfig
from platformio.project.dependency_lock import environment_fingerprint


def test_locked_install_verifies_archive_and_rejects_stale_project(
    tmp_path, monkeypatch, clirunner
):
    monkeypatch.setenv("PLATFORMIO_CORE_DIR", str(tmp_path / "core"))
    config_path = tmp_path / "platformio.ini"
    config_path.write_text(
        "[env:demo]\nlib_deps = publisher/Demo@^1\n", encoding="utf8"
    )
    archive = tmp_path / "demo.zip"
    with ZipFile(archive, "w") as stream:
        stream.writestr("library.json", '{"name": "Demo", "version": "1.2.3"}')
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    lock_path = tmp_path / "platformio.lock"
    lock_path.write_text(
        json.dumps(
            {
                "version": 1,
                "system": util.get_systype(),
                "environments": {
                    "demo": {
                        "config_sha256": environment_fingerprint(
                            ProjectConfig(str(config_path)), "demo"
                        ),
                        "packages": [
                            {
                                "type": "library",
                                "id": 42,
                                "owner": "publisher",
                                "name": "Demo",
                                "version": "1.2.3",
                                "sha256": checksum,
                            }
                        ],
                    }
                },
            }
        ),
        encoding="utf8",
    )
    monkeypatch.setattr(
        LibraryPackageManager,
        "fetch_registry_package",
        lambda _manager, _spec: {
            "id": 42,
            "versions": [
                {
                    "name": "1.2.3",
                    "files": [
                        {
                            "download_url": "https://example.invalid/demo.zip",
                            "checksum": {"sha256": checksum},
                        }
                    ],
                }
            ],
        },
    )
    monkeypatch.setattr(
        "platformio.project.locked_install.RegistryFileMirrorIterator",
        lambda url: iter([(url, None)]),
    )
    served = tmp_path / "served.zip"
    served.write_bytes(b"corrupt cached archive")
    monkeypatch.setattr(
        LibraryPackageManager, "download", lambda _manager, _url, _sha: str(served)
    )
    args = ["-d", str(tmp_path), "--locked"]
    result = clirunner.invoke(package_install_cmd, args)
    assert "checksum" in str(result.exception).lower()
    installed = tmp_path / ".pio" / "libdeps" / "demo" / "Demo"
    assert not installed.exists()

    served.write_bytes(archive.read_bytes())
    result = clirunner.invoke(package_install_cmd, args)
    assert result.exit_code == 0, (result.output, result.exception)
    assert (
        installed / "library.json"
    ).read_bytes() == b'{"name": "Demo", "version": "1.2.3"}'

    config_path.write_text(
        "[env:demo]\nlib_deps = publisher/Demo@^2\n", encoding="utf8"
    )
    result = clirunner.invoke(package_install_cmd, args)
    assert "stale" in str(result.exception).lower()
