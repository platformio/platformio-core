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


def test_spdx_sbom_includes_declared_licenses_and_dependency_edges(tmp_path, clirunner):
    (tmp_path / "platformio.ini").write_text(
        "[env:demo]\nlib_deps = Top\n", encoding="utf8"
    )
    for name, license_expression, dependencies in (
        ("Top", "mit OR apache-2.0", {"Leaf": "*"}),
        ("Leaf", "Unknown license text", {}),
    ):
        storage = tmp_path / ".pio" / "libdeps" / "demo" / name
        storage.mkdir(parents=True)
        (storage / "library.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "version": "1.2.3",
                    "license": license_expression,
                    "dependencies": dependencies,
                }
            ),
            encoding="utf8",
        )

    result = clirunner.invoke(
        cli, ["sbom", "-d", str(tmp_path), "--standard=spdx", "--format=json"]
    )
    assert result.exit_code == 0, result.output
    document = json.loads(result.stdout)
    assert document["spdxVersion"] == "SPDX-2.3"
    assert document["dataLicense"] == "CC0-1.0"
    by_name = {package["name"]: package for package in document["packages"]}
    assert by_name["Top"]["licenseDeclared"] == "MIT OR Apache-2.0"
    assert by_name["Leaf"]["licenseDeclared"] == "NOASSERTION"
    assert by_name["Top"]["licenseConcluded"] == "NOASSERTION"
    assert {
        "spdxElementId": by_name["Top"]["SPDXID"],
        "relatedSpdxElement": by_name["Leaf"]["SPDXID"],
        "relationshipType": "DEPENDS_ON",
    } in document["relationships"]


def test_spdx_sbom_flags_unresolved_dependencies_and_ambiguous_environment(
    tmp_path, clirunner
):
    (tmp_path / "platformio.ini").write_text(
        "[env:first]\nlib_deps = Missing\n[env:second]\n", encoding="utf8"
    )
    args = ["sbom", "-d", str(tmp_path)]
    result = clirunner.invoke(cli, args)
    assert result.exit_code == 2
    assert "--environment" in result.output
    result = clirunner.invoke(cli, args + ["-e", "first"])
    assert result.exit_code == 0, result.output
    document = json.loads(result.stdout)
    assert "1 unresolved" in document["comment"]
    assert len(document["packages"]) == 1
