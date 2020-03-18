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

import signal
import time

import click
from twisted.internet import protocol  # pylint: disable=import-error

from platformio import fs
from platformio.compat import string_types
from platformio.proc import get_pythonexe_path
from platformio.project.helpers import get_project_core_dir


class BaseProcess(protocol.ProcessProtocol, object):

    STDOUT_CHUNK_SIZE = 2048
    LOG_FILE = None

    COMMON_PATTERNS = {
        "PLATFORMIO_HOME_DIR": get_project_core_dir(),
        "PLATFORMIO_CORE_DIR": get_project_core_dir(),
        "PYTHONEXE": get_pythonexe_path(),
    }

    def __init__(self):
        self._last_activity = 0

    def apply_patterns(self, source, patterns=None):
        _patterns = self.COMMON_PATTERNS.copy()
        _patterns.update(patterns or {})

        for key, value in _patterns.items():
            if key.endswith(("_DIR", "_PATH")):
                _patterns[key] = fs.to_unix_path(value)

        def _replace(text):
            for key, value in _patterns.items():
                pattern = "$%s" % key
                text = text.replace(pattern, value or "")
            return text

        if isinstance(source, string_types):
            source = _replace(source)
        elif isinstance(source, (list, dict)):
            items = enumerate(source) if isinstance(source, list) else source.items()
            for key, value in items:
                if isinstance(value, string_types):
                    source[key] = _replace(value)
                elif isinstance(value, (list, dict)):
                    source[key] = self.apply_patterns(value, patterns)

        return source

    def onStdInData(self, data):
        self._last_activity = time.time()
        if self.LOG_FILE:
            with open(self.LOG_FILE, "ab") as fp:
                fp.write(data)

    def outReceived(self, data):
        self._last_activity = time.time()
        if self.LOG_FILE:
            with open(self.LOG_FILE, "ab") as fp:
                fp.write(data)
        while data:
            chunk = data[: self.STDOUT_CHUNK_SIZE]
            click.echo(chunk, nl=False)
            data = data[self.STDOUT_CHUNK_SIZE :]

    def errReceived(self, data):
        self._last_activity = time.time()
        if self.LOG_FILE:
            with open(self.LOG_FILE, "ab") as fp:
                fp.write(data)
        click.echo(data, nl=False, err=True)

    def processEnded(self, _):
        self._last_activity = time.time()
        # Allow terminating via SIGINT/CTRL+C
        signal.signal(signal.SIGINT, signal.default_int_handler)
