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
from os.path import isdir, isfile, join, normpath
from threading import Thread

from platformio import exception
from platformio.compat import (
    WINDOWS,
    get_filesystem_encoding,
    get_locale_encoding,
    string_types,
)


class AsyncPipeBase(object):
    def __init__(self):
        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(self._fd_read)
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
        super(BuildAsyncPipe, self).__init__()

    def do_reading(self):
        line = ""
        print_immediately = False

        for byte in iter(lambda: self._pipe_reader.read(1), ""):
            self._buffer += byte

            if line and byte.strip() and line[-3:] == (byte * 3):
                print_immediately = True

            if print_immediately:
                # leftover bytes
                if line:
                    self.data_callback(line)
                    line = ""
                self.data_callback(byte)
                if byte == "\n":
                    print_immediately = False
            else:
                line += byte
                if byte != "\n":
                    continue
                self.line_callback(line)
                line = ""

        self._pipe_reader.close()


class LineBufferedAsyncPipe(AsyncPipeBase):
    def __init__(self, line_callback):
        self.line_callback = line_callback
        super(LineBufferedAsyncPipe, self).__init__()

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

    p = subprocess.Popen(*args, **kwargs)
    try:
        result["out"], result["err"] = p.communicate()
        result["returncode"] = p.returncode
    except KeyboardInterrupt:
        raise exception.AbortedByUser()
    finally:
        for s in ("stdout", "stderr"):
            if isinstance(kwargs[s], AsyncPipeBase):
                kwargs[s].close()

    for s in ("stdout", "stderr"):
        if isinstance(kwargs[s], AsyncPipeBase):
            result[s[3:]] = kwargs[s].get_buffer()

    for k, v in result.items():
        if isinstance(result[k], bytes):
            try:
                result[k] = result[k].decode(
                    get_locale_encoding() or get_filesystem_encoding()
                )
            except UnicodeDecodeError:
                result[k] = result[k].decode("latin-1")
        if v and isinstance(v, string_types):
            result[k] = result[k].strip()

    return result


def is_ci():
    return os.getenv("CI", "").lower() == "true"


def is_container():
    if not isfile("/proc/1/cgroup"):
        return False
    with open("/proc/1/cgroup") as fp:
        for line in fp:
            line = line.strip()
            if ":" in line and not line.endswith(":/"):
                return True
    return False


def get_pythonexe_path():
    return os.environ.get("PYTHONEXEPATH", normpath(sys.executable))


def copy_pythonpath_to_osenv():
    _PYTHONPATH = []
    if "PYTHONPATH" in os.environ:
        _PYTHONPATH = os.environ.get("PYTHONPATH").split(os.pathsep)
    for p in os.sys.path:
        conditions = [p not in _PYTHONPATH]
        if not WINDOWS:
            conditions.append(isdir(join(p, "click")) or isdir(join(p, "platformio")))
        if all(conditions):
            _PYTHONPATH.append(p)
    os.environ["PYTHONPATH"] = os.pathsep.join(_PYTHONPATH)


def where_is_program(program, envpath=None):
    env = os.environ
    if envpath:
        env["PATH"] = envpath

    # try OS's built-in commands
    try:
        result = exec_command(["where" if WINDOWS else "which", program], env=env)
        if result["returncode"] == 0 and isfile(result["out"].strip()):
            return result["out"].strip()
    except OSError:
        pass

    # look up in $PATH
    for bin_dir in env.get("PATH", "").split(os.pathsep):
        if isfile(join(bin_dir, program)):
            return join(bin_dir, program)
        if isfile(join(bin_dir, "%s.exe" % program)):
            return join(bin_dir, "%s.exe" % program)

    return program
