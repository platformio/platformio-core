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

import io

import serial
from serial.tools import miniterm

from platformio.device.monitor.terminal import NonInteractiveConsole, Terminal


def test_terminal_does_not_crash_when_stdin_is_not_a_tty(monkeypatch):
    # Regression test for https://github.com/platformio/platformio-core/issues/5113
    # `pio device monitor` used to crash with
    # `termios.error: (25, 'Inappropriate ioctl for device')` whenever stdin
    # was a pipe rather than a real terminal, because `miniterm.Miniterm`
    # unconditionally builds a `Console` that calls `termios.tcgetattr` on
    # stdin during construction.
    monkeypatch.setattr("sys.stdin", io.StringIO("hello"))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)

    ser = serial.serial_for_url("loop://", do_not_open=True)
    ser.open()
    try:
        term = Terminal(ser, echo=False, eol="crlf", filters=["default"])
        assert isinstance(term.console, NonInteractiveConsole)
    finally:
        ser.close()


def test_terminal_reads_piped_stdin_and_stops_cleanly_on_eof(monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("hi"))
    monkeypatch.setattr("sys.stdin.isatty", lambda: False, raising=False)

    ser = serial.serial_for_url("loop://", do_not_open=True)
    ser.open()
    term = None
    try:
        term = Terminal(ser, echo=False, eol="crlf", filters=["default"])
        term.set_rx_encoding("UTF-8")
        term.set_tx_encoding("UTF-8")
        term.start()
        term.join(True)
        term.join()

        assert term.alive is False
        assert term.pio_unexpected_exception is None
    finally:
        if term is not None:
            term.console.cleanup()
        ser.close()


def test_terminal_uses_real_console_when_stdin_is_a_tty(monkeypatch):
    # Non-regression: the fix must not change behavior for the normal,
    # interactive case. `Console.__init__` itself is stubbed out (rather
    # than calling the real termios-based one) because stdin under the
    # test runner is neither a pipe nor a real TTY, so there is no fd for
    # `termios.tcgetattr` to act on either way — this test only asserts
    # *which* console class gets selected, not termios behavior itself.
    monkeypatch.setattr("sys.stdin.isatty", lambda: True, raising=False)
    monkeypatch.setattr(miniterm.Console, "__init__", lambda self: None)
    monkeypatch.setattr(miniterm.Console, "cleanup", lambda self: None)

    ser = serial.serial_for_url("loop://", do_not_open=True)
    ser.open()
    term = None
    try:
        term = Terminal(ser, echo=False, eol="crlf", filters=["default"])
        assert isinstance(term.console, miniterm.Console)
        assert not isinstance(term.console, NonInteractiveConsole)
    finally:
        if term is not None:
            term.console.cleanup()
        ser.close()
