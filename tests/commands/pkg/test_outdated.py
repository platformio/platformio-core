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

import re

from platformio.package.commands.install import package_install_cmd
from platformio.package.commands.outdated import package_outdated_cmd

PROJECT_OUTDATED_CONFIG_TPL = """
[env:devkit]
platform = platformio/atmelavr@^2
framework = arduino
board = attiny88
lib_deps = milesburton/DallasTemperature@~3.9.0
"""

PROJECT_UPDATED_CONFIG_TPL = """
[env:devkit]
platform = platformio/atmelavr@<4
framework = arduino
board = attiny88
lib_deps = milesburton/DallasTemperature@^3.9.0
"""


def test_project(clirunner, validate_cliresult, isolated_pio_core, tmp_path):
    project_dir = tmp_path / "project"
    project_dir.mkdir()
    (project_dir / "platformio.ini").write_text(PROJECT_OUTDATED_CONFIG_TPL)
    result = clirunner.invoke(package_install_cmd, ["-d", str(project_dir)])
    validate_cliresult(result)

    # overwrite config
    (project_dir / "platformio.ini").write_text(PROJECT_UPDATED_CONFIG_TPL)
    result = clirunner.invoke(package_outdated_cmd, ["-d", str(project_dir)])
    validate_cliresult(result)

    # validate output
    assert "Checking" in result.output
    assert re.search(
        r"^atmelavr\s+2\.2\.0\s+3\.\d+\.\d+\s+[456789]\.\d+\.\d+\s+Platform\s+devkit",
        result.output,
        re.MULTILINE,
    )
    assert re.search(
        r"^DallasTemperature\s+3\.\d\.1\s+3\.\d+\.\d+\s+3\.\d+\.\d+\s+Library\s+devkit",
        result.output,
        re.MULTILINE,
    )
