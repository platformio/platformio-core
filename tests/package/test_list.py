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

from platformio.package.commands.list import package_list_cmd


def test_package_list_filter_handles_circular_dependencies(tmp_path, clirunner):
    libraries = {
        "A": {"B": "*", "Missing": "*"},
        "B": {"A": "*"},
        "Target": {},
        "WithTarget": {"A": "*", "Target": "*"},
    }
    for name, dependencies in libraries.items():
        library = tmp_path / name
        library.mkdir()
        (library / "library.json").write_text(
            json.dumps(
                {"name": name, "version": "1.0.0", "dependencies": dependencies}
            ),
            encoding="utf8",
        )

    result = clirunner.invoke(
        package_list_cmd,
        ["--global", "--storage-dir", str(tmp_path), "--library", "Target"],
    )

    assert result.exit_code == 0, result.exception
    assert "WithTarget @" in result.output
    assert "Target @" in result.output
    assert "A @" not in result.output
    assert "B @" not in result.output
