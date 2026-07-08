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

from platformio.commands import upgrade as cmd_upgrade
from platformio.dependencies import get_pip_dependencies


def test_pip_is_declared_dependency():
    assert get_pip_dependencies().count("pip") == 1


def test_upgrade_pip_dependencies_upgrades_declared_pip_once(monkeypatch):
    calls = []

    monkeypatch.setattr(cmd_upgrade, "get_pythonexe_path", lambda: "python")
    monkeypatch.setattr(
        cmd_upgrade.subprocess,
        "run",
        lambda args, **kwargs: calls.append((args, kwargs)),
    )

    cmd_upgrade.upgrade_pip_dependencies(verbose=False)

    args, kwargs = calls[0]
    assert args[:5] == ["python", "-m", "pip", "install", "--upgrade"]
    assert args[5:] == get_pip_dependencies()
    assert args[5:].count("pip") == 1
    assert kwargs["check"] is True
    assert kwargs["stdout"] == cmd_upgrade.subprocess.PIPE
