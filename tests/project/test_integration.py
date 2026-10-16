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

# pylint: disable=protected-access,redefined-outer-name

import json
import os

import pytest

from platformio.project.config import ProjectConfig
from platformio.project.integration import generator as generator_module
from platformio.project.integration.generator import ProjectGenerator


@pytest.fixture
def project_config(tmp_path):
    project_dir = tmp_path / "project"
    (project_dir / "src").mkdir(parents=True)
    (project_dir / "lib").mkdir()
    (project_dir / "test").mkdir()
    config_path = project_dir / "platformio.ini"
    config_path.write_text(
        """[platformio]
default_envs = hardware

[env]
platform = test-platform
board = test-board

[env:simulation]
build_type = debug

[env:hardware]
""",
        encoding="utf8",
    )
    return ProjectConfig(str(config_path))


def test_vscode_debug_launch_uses_metadata_for_default_debug_env(
    project_config, monkeypatch
):
    metadata_calls = []

    def load_build_metadata(project_dir, env_name, **kwargs):
        metadata_calls.append((env_name, kwargs))
        return {
            "hardware": {
                "prog_path": os.path.join(project_dir, ".pio/build/hardware/app.elf"),
                "cc_path": os.path.join(
                    project_dir, ".platformio/packages/toolchain-hardware/bin/cc"
                ),
                "includes": ["hardware-include"],
            },
            "simulation": {
                "prog_path": os.path.join(project_dir, ".pio/build/simulation/app.elf"),
                "cc_path": os.path.join(
                    project_dir, ".platformio/packages/toolchain-simulation/bin/cc"
                ),
                "includes": ["simulation-include"],
            },
        }[env_name]

    monkeypatch.setattr(generator_module, "load_build_metadata", load_build_metadata)
    project_generator = ProjectGenerator(project_config, None, "vscode")
    template_vars = project_generator._load_tplvars()
    template_vars.setdefault("svd_path", "")
    launch_template = os.path.join(
        project_generator.get_ide_tpls_dir(),
        "vscode",
        ".vscode",
        "launch.json.tpl",
    )
    rendered = project_generator.render_tpl(launch_template, template_vars)
    launch = json.loads(rendered[rendered.index("{") :])

    pio_launches = launch["configurations"]
    assert len(pio_launches) == 3
    assert all(item["projectEnvName"] == "simulation" for item in pio_launches)
    assert all(
        item["executable"].endswith(".pio/build/simulation/app.elf")
        for item in pio_launches
    )
    assert all(
        item["toolchainBinDir"].endswith("toolchain-simulation/bin")
        for item in pio_launches
    )
    assert project_generator.env_name == "hardware"
    assert template_vars["includes"] == ["hardware-include"]
    assert metadata_calls == [
        ("hardware", {}),
        ("simulation", {"build_type": "debug"}),
    ]


def test_vscode_debug_launch_falls_back_to_available_metadata(
    project_config, monkeypatch
):
    monkeypatch.setattr(
        generator_module,
        "load_build_metadata",
        lambda project_dir, env_name, **kwargs: (
            {
                "prog_path": os.path.join(project_dir, ".pio/build/hardware/app.elf"),
                "cc_path": os.path.join(
                    project_dir, ".platformio/packages/toolchain-hardware/bin/cc"
                ),
            }
            if env_name == "hardware"
            else None
        ),
    )
    project_generator = ProjectGenerator(project_config, None, "vscode")
    template_vars = project_generator._load_tplvars()
    template_vars.setdefault("svd_path", "")
    launch_template = os.path.join(
        project_generator.get_ide_tpls_dir(),
        "vscode",
        ".vscode",
        "launch.json.tpl",
    )
    rendered = project_generator.render_tpl(launch_template, template_vars)
    launch = json.loads(rendered[rendered.index("{") :])

    assert template_vars["default_debug_env_name"] == "hardware"
    assert all(
        item["projectEnvName"] == "hardware"
        and item["executable"].endswith(".pio/build/hardware/app.elf")
        and item["toolchainBinDir"].endswith("toolchain-hardware/bin")
        for item in launch["configurations"]
    )
