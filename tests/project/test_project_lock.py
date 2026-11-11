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

from platformio.package.manager.library import LibraryPackageManager
from platformio.project.cli import cli


def test_lock_records_registry_artifact_and_preserves_existing_file_on_error(
    tmp_path, clirunner, monkeypatch
):
    config = tmp_path / "platformio.ini"
    config.write_text("[env:demo]\nlib_deps = publisher/Demo@^1\n", encoding="utf8")
    lib = tmp_path / ".pio" / "libdeps" / "demo" / "Demo"
    lib.mkdir(parents=True)
    (lib / "library.json").write_text(
        '{"name": "Demo", "version": "1.2.3"}', encoding="utf8"
    )
    (lib / ".piopm").write_text(
        json.dumps(
            {
                "type": "library",
                "name": "Demo",
                "version": "1.2.3",
                "spec": {"owner": "publisher", "name": "Demo", "id": 42},
            }
        ),
        encoding="utf8",
    )
    monkeypatch.setattr(
        LibraryPackageManager,
        "fetch_registry_package",
        lambda _manager, _spec: {
            "id": 42,
            "name": "Demo",
            "owner": {"username": "publisher"},
            "versions": [
                {"name": "1.2.3", "files": [{"checksum": {"sha256": "a" * 64}}]}
            ],
        },
    )
    args = ["lock", "-d", str(tmp_path)]
    result = clirunner.invoke(cli, args)
    assert result.exit_code == 0, result.output
    path = tmp_path / "platformio.lock"
    original = path.read_bytes()
    locked = json.loads(original)
    assert locked["version"] == 1
    assert locked["environments"]["demo"]["packages"] == [
        {
            "type": "library",
            "id": 42,
            "owner": "publisher",
            "name": "Demo",
            "version": "1.2.3",
            "sha256": "a" * 64,
        }
    ]
    assert clirunner.invoke(cli, args).exit_code == 0
    assert path.read_bytes() == original

    config.write_text("[env:demo]\nlib_deps = Missing\n", encoding="utf8")
    result = clirunner.invoke(cli, args)
    assert result.exit_code == 1, result.output
    assert "unresolved" in str(result.exception)
    assert path.read_bytes() == original
