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
import sys
from unittest.mock import MagicMock

import pytest

from platformio import fs
from platformio.device.finder import SerialPortFinder
from platformio.device.monitor.command import device_monitor_cmd
from platformio.device.monitor.terminal import new_terminal
from platformio.exception import UserSideException


def _patch_monitor_internals(monkeypatch, on_register_filters):
    # `register_filters` is where a platform's monitor filter (e.g. the
    # espressif32 exception decoder) re-enters `project_dir` via
    # `fs.cd()`/`load_build_metadata()`. Stub the heavy, hardware-dependent
    # collaborators so the command can run in CI while still exercising the
    # real `project_dir` value it receives.
    monkeypatch.setattr(
        "platformio.device.monitor.command.register_filters", on_register_filters
    )
    monkeypatch.setattr(
        "platformio.device.monitor.command.start_terminal", lambda options: None
    )
    monkeypatch.setattr(
        SerialPortFinder, "find", lambda self, initial_port=None: "socket://localhost:0"
    )


def test_relative_project_dir_is_resolved_before_use(
    clirunner, validate_cliresult, monkeypatch, tmpdir
):
    # Regression test for https://github.com/platformio/platformio-core/issues/5439
    # `pio device monitor -d <relative-dir>` used to crash with a duplicated
    # path (e.g. `.../examples/distance-ultrasound/examples/distance-ultrasound`)
    # because `project_dir` stayed relative while the working directory had
    # already been changed into it via `fs.cd()`.
    project_dir = os.path.realpath(str(tmpdir.mkdir("project")))
    captured = {}

    def on_register_filters(platform, options):  # pylint: disable=unused-argument
        captured["project_dir"] = options["project_dir"]
        # Mirror `load_build_metadata()`, which re-enters `project_dir` via a
        # second, nested `fs.cd()` while already inside the first one.
        with fs.cd(options["project_dir"]):
            captured["cwd_after_nested_cd"] = os.getcwd()

    _patch_monitor_internals(monkeypatch, on_register_filters)
    monkeypatch.chdir(tmpdir)

    result = clirunner.invoke(device_monitor_cmd, ["-d", "project"])
    validate_cliresult(result)

    # compare against the realpath, not the raw tmpdir string: `resolve_path`
    # also resolves symlinks, and some platforms put the temp dir behind one
    # (e.g. macOS `/tmp` -> `/private/tmp`)
    assert os.path.isabs(captured["project_dir"])
    assert captured["project_dir"] == project_dir
    assert captured["cwd_after_nested_cd"] == project_dir


def test_default_project_dir_without_flag_still_absolute(
    clirunner, validate_cliresult, monkeypatch, tmpdir
):
    captured = {}
    _patch_monitor_internals(
        monkeypatch,
        lambda platform, options: captured.update(project_dir=options["project_dir"]),
    )
    monkeypatch.chdir(tmpdir)

    result = clirunner.invoke(device_monitor_cmd, [])
    validate_cliresult(result)

    assert captured["project_dir"] == os.path.realpath(str(tmpdir))


def test_absolute_project_dir_passthrough(
    clirunner, validate_cliresult, monkeypatch, tmpdir
):
    captured = {}
    _patch_monitor_internals(
        monkeypatch,
        lambda platform, options: captured.update(project_dir=options["project_dir"]),
    )

    result = clirunner.invoke(device_monitor_cmd, ["-d", str(tmpdir)])
    validate_cliresult(result)

    assert captured["project_dir"] == os.path.realpath(str(tmpdir))


def test_new_terminal_rejects_non_tty_stdin(monkeypatch):
    # Regression test for https://github.com/platformio/platformio-core/issues/5113
    # `pio device monitor` used to crash with a raw termios traceback
    # ("Inappropriate ioctl for device") whenever stdin was piped instead of
    # a real terminal, e.g. `echo "" | pio device monitor`. It should fail
    # with a clear, actionable error instead.
    fake_stdin = MagicMock()
    fake_stdin.isatty.return_value = False
    monkeypatch.setattr(sys, "stdin", fake_stdin)

    with pytest.raises(UserSideException, match="interactive terminal"):
        new_terminal({})
