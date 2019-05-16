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
from platformio.compat import PY2, WINDOWS, string_types


class AsyncPipe(Thread):

    def __init__(self, outcallback=None):
        super(AsyncPipe, self).__init__()
        self.outcallback = outcallback

        self._fd_read, self._fd_write = os.pipe()
        self._pipe_reader = os.fdopen(self._fd_read)
        self._buffer = []

        self.start()

    def get_buffer(self):
        return self._buffer

    def fileno(self):
        return self._fd_write

    def run(self):
        for line in iter(self._pipe_reader.readline, ""):
            line = line.strip()
            self._buffer.append(line)
            if self.outcallback:
                self.outcallback(line)
            else:
                print(line)
        self._pipe_reader.close()

    def close(self):
        os.close(self._fd_write)
        self.join()


def exec_command(*args, **kwargs):
    result = {"out": None, "err": None, "returncode": None}

    default = dict(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    default.update(kwargs)
    kwargs = default

    p = subprocess.Popen(*args, **kwargs)
    try:
        result['out'], result['err'] = p.communicate()
        result['returncode'] = p.returncode
    except KeyboardInterrupt:
        raise exception.AbortedByUser()
    finally:
        for s in ("stdout", "stderr"):
            if isinstance(kwargs[s], AsyncPipe):
                kwargs[s].close()

    for s in ("stdout", "stderr"):
        if isinstance(kwargs[s], AsyncPipe):
            result[s[3:]] = "\n".join(kwargs[s].get_buffer())

    for k, v in result.items():
        if not PY2 and isinstance(result[k], bytes):
            result[k] = result[k].decode()
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
            conditions.append(
                isdir(join(p, "click")) or isdir(join(p, "platformio")))
        if all(conditions):
            _PYTHONPATH.append(p)
    os.environ['PYTHONPATH'] = os.pathsep.join(_PYTHONPATH)


def where_is_program(program, envpath=None):
    env = os.environ
    if envpath:
        env['PATH'] = envpath

    # try OS's built-in commands
    try:
        result = exec_command(["where" if WINDOWS else "which", program],
                              env=env)
        if result['returncode'] == 0 and isfile(result['out'].strip()):
            return result['out'].strip()
    except OSError:
        pass

    # look up in $PATH
    for bin_dir in env.get("PATH", "").split(os.pathsep):
        if isfile(join(bin_dir, program)):
            return join(bin_dir, program)
        if isfile(join(bin_dir, "%s.exe" % program)):
            return join(bin_dir, "%s.exe" % program)

    return program
