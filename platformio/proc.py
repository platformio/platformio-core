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
import subprocess
import sys
from contextlib import contextmanager
from threading import Thread

from platformio import exception
from platformio.compat import (
    IS_WINDOWS,
    get_filesystem_encoding,
    get_locale_encoding,
    string_types,
)


class AsyncPipeBase:
    def __init__(self):
        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(
            self._fd_read, encoding="utf-8", errors="backslashreplace"
        )
        self._buffer = ""
        self._thread = Thread(target=self.run)
        self._thread.start()

    def get_buffer(self):
        return self._buffer

    def fileno(self):
        return self._fd_write

    def run(self):
        try:
            self.do_reading()
        except (KeyboardInterrupt, SystemExit, IOError):
            self.close()

    def do_reading(self):
        raise NotImplementedError()

    def close(self):
        self._buffer = ""
        os.close(self._fd_write)
        self._thread.join()


class BuildAsyncPipe(AsyncPipeBase):
    def __init__(self, line_callback, data_callback):
        self.line_callback = line_callback
        self.data_callback = data_callback
        super().__init__()

    def do_reading(self):
        line = ""
        print_immediately = False

        for char in iter(lambda: self._pipe_reader.read(1), ""):
            self._buffer += char

            if line and char.strip() and line[-3:] == (char * 3):
                print_immediately = True

            if print_immediately:
                # leftover bytes
                if line:
                    self.data_callback(line)
                    line = ""
                self.data_callback(char)
                if char == "\n":
                    print_immediately = False
            else:
                line += char
                if char != "\n":
                    continue
                self.line_callback(line)
                line = ""

        self._pipe_reader.close()


class LineBufferedAsyncPipe(AsyncPipeBase):
    def __init__(self, line_callback):
        self.line_callback = line_callback
        super().__init__()

    def do_reading(self):
        for line in iter(self._pipe_reader.readline, ""):
            self._buffer += line
            self.line_callback(line)
        self._pipe_reader.close()


def exec_command(*args, **kwargs):
    result = {"out": None, "err": None, "returncode": None}

    default = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    default.update(kwargs)
    kwargs = default

    with subprocess.Popen(*args, **kwargs) as p:
        try:
            result["out"], result["err"] = p.communicate()
            result["returncode"] = p.returncode
        except KeyboardInterrupt as exc:
            raise exception.AbortedByUser() from exc
        finally:
            for s in ("stdout", "stderr"):
                if isinstance(kwargs[s], AsyncPipeBase):
                    kwargs[s].close()  # pylint: disable=no-member

    for s in ("stdout", "stderr"):
        if isinstance(kwargs[s], AsyncPipeBase):
            result[s[3:]] = kwargs[s].get_buffer()  # pylint: disable=no-member

    for key, value in result.items():
        if isinstance(value, bytes):
            try:
                result[key] = value.decode(
                    get_locale_encoding() or get_filesystem_encoding()
                )
            except UnicodeDecodeError:
                result[key] = value.decode("latin-1")
        if value and isinstance(value, string_types):
            result[key] = value.strip()

    return result


@contextmanager
def capture_std_streams(stdout, stderr=None):
    _stdout = sys.stdout
    _stderr = sys.stderr
    sys.stdout = stdout
    sys.stderr = stderr or stdout
    yield
    sys.stdout = _stdout
    sys.stderr = _stderr


def is_ci():
    return os.getenv("CI", "").lower() == "true"


def is_container():
    if os.path.exists("/.dockerenv"):
        return True
    if not os.path.isfile("/proc/1/cgroup"):
        return False
    with open("/proc/1/cgroup", encoding="utf8") as fp:
        return ":/docker/" in fp.read()


def get_pythonexe_path():
    return os.environ.get("PYTHONEXEPATH", os.path.normpath(sys.executable))


def copy_pythonpath_to_osenv():
    _PYTHONPATH = []
    if "PYTHONPATH" in os.environ:
        _PYTHONPATH = os.environ.get("PYTHONPATH").split(os.pathsep)
    for p in os.sys.path:
        conditions = [p not in _PYTHONPATH]
        if not IS_WINDOWS:
            conditions.append(
                os.path.isdir(os.path.join(p, "click"))
                or os.path.isdir(os.path.join(p, "platformio"))
            )
        if all(conditions):
            _PYTHONPATH.append(p)
    os.environ["PYTHONPATH"] = os.pathsep.join(_PYTHONPATH)


def where_is_program(program, envpath=None):
    env = os.environ
    if envpath:
        env["PATH"] = envpath

    # try OS's built-in commands
    try:
        result = exec_command(["where" if IS_WINDOWS else "which", program], env=env)
        if result["returncode"] == 0 and os.path.isfile(result["out"].strip()):
            return result["out"].strip()
    except OSError:
        pass

    # look up in $PATH
    for bin_dir in env.get("PATH", "").split(os.pathsep):
        if os.path.isfile(os.path.join(bin_dir, program)):
            return os.path.join(bin_dir, program)
        if os.path.isfile(os.path.join(bin_dir, "%s.exe" % program)):
            return os.path.join(bin_dir, "%s.exe" % program)

    return program


def append_env_path(name, value):
    cur_value = os.environ.get(name) or ""
    if cur_value and value in cur_value.split(os.pathsep):
        return cur_value
    os.environ[name] = os.pathsep.join([cur_value, value])
    return os.environ[name]


def force_exit(code=0):
    os._exit(code)  # pylint: disable=protected-access
