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

from platformio.project.cli import cli


def test_dependency_license_check_reports_unresolved_and_disallowed_packages(
    tmp_path, clirunner
):
    (tmp_path / "platformio.ini").write_text(
        "[env:demo]\nlib_deps =\n    Allowed\n    Restricted\n    Unknown\n    Missing\n",
        encoding="utf8",
    )
    for name, expression in (
        ("Allowed", "mit"),
        ("Restricted", "MIT OR GPL-3.0-only"),
        ("Unknown", None),
    ):
        path = tmp_path / ".pio" / "libdeps" / "demo" / name
        path.mkdir(parents=True)
        (path / "library.json").write_text(
            json.dumps({"name": name, "version": "1.0.0", "license": expression}),
            encoding="utf8",
        )

    args = ["license-check", "-d", str(tmp_path), "--allow-license", "MIT"]
    result = clirunner.invoke(cli, args)
    assert result.exit_code == 1, result.output
    assert "Restricted" in result.stderr
    assert "Unknown" in result.stderr
    assert "Missing" in result.stderr
    assert "Allowed" not in result.stderr

    (tmp_path / "platformio.ini").write_text(
        "[env:demo]\nlib_deps = Allowed\n", encoding="utf8"
    )
    result = clirunner.invoke(cli, args)
    assert result.exit_code == 0, result.output
