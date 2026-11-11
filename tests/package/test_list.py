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


def _write_manifest(storage, filename, name, version, **fields):
    package = storage / name
    package.mkdir(parents=True)
    (package / filename).write_text(
        json.dumps({"name": name, "version": version, **fields}),
        encoding="utf8",
    )


def test_package_list_filter_handles_circular_dependencies(tmp_path, clirunner):
    libraries = {
        "A": {"B": "*", "Missing": "*"},
        "B": {"A": "*"},
        "Target": {},
        "WithTarget": {"A": "*", "Target": "*"},
    }
    for name, dependencies in libraries.items():
        _write_manifest(
            tmp_path, "library.json", name, "1.0.0", dependencies=dependencies
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


def test_project_package_list_json_reports_installed_and_missing_dependencies(
    tmp_path, monkeypatch, clirunner
):
    core_dir = tmp_path / "core"
    monkeypatch.setenv("PLATFORMIO_CORE_DIR", str(core_dir))
    (tmp_path / "platformio.ini").write_text(
        "[env:one]\nplatform = example\nlib_deps = First\n"
        "[env:two]\nplatform = missing-platform\nlib_deps =\n"
        "    First\n"
        "    External = https://user:example-token@example.invalid/library.git\n",
        encoding="utf8",
    )
    _write_manifest(
        core_dir / "platforms",
        "platform.json",
        "example",
        "1.0.0",
        packages={
            "compiler": {"version": "*"},
            "optional": {"version": "*", "optional": True},
        },
    )
    _write_manifest(core_dir / "packages", "package.json", "compiler", "3.0.0")
    libdeps = tmp_path / ".pio" / "libdeps"
    _write_manifest(
        libdeps / "one",
        "library.json",
        "First",
        "1.0.0",
        dependencies={"Second": "*", "Missing": "*"},
    )
    _write_manifest(
        libdeps / "one", "library.json", "Second", "1.0.0", dependencies={"First": "*"}
    )
    _write_manifest(libdeps / "two", "library.json", "First", "2.0.0")

    args = ["--project-dir", str(tmp_path), "--json-output"]
    result = clirunner.invoke(package_list_cmd, args)
    assert result.exit_code == 0, result.output
    inventory = json.loads(result.stdout)
    assert list(inventory) == ["one", "two"]
    one, two = inventory["one"], inventory["two"]
    assert {p["name"] for p in one["packages"]} == {
        "example",
        "compiler",
        "First",
        "Second",
    }
    assert [(p["name"], p["version"]) for p in two["packages"]] == [("First", "2.0.0")]

    names = {p["id"]: p["name"] for p in one["packages"]}
    edges = {
        (names.get(edge["from"]), names.get(edge["to"]), edge["requested"]["name"])
        for edge in one["dependencies"]
    }
    assert edges == {
        (None, "example", "example"),
        ("example", "compiler", "compiler"),
        (None, "First", "First"),
        ("First", "Second", "Second"),
        ("First", None, "Missing"),
        ("Second", "First", "First"),
    }
    assert any(
        edge["to"] is None and edge["requested"]["name"] == "missing-platform"
        for edge in two["dependencies"]
    )
    assert any(
        edge["to"] is None
        and edge["requested"]["external"]
        and edge["requested"]["name"] == "External"
        for edge in two["dependencies"]
    )
    assert "example-token" not in result.stdout
    selected = clirunner.invoke(package_list_cmd, args + ["-e", "two"])
    assert selected.exit_code == 0, selected.output
    assert json.loads(selected.stdout) == {"two": two}


def test_project_package_list_json_rejects_global_options(clirunner):
    result = clirunner.invoke(package_list_cmd, ["--json-output", "--global"])
    assert result.exit_code == 2
    assert "--json-output cannot be combined with --global" in result.output
