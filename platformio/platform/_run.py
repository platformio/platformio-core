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

import base64
import json
import os
import re
import sys
from urllib.parse import quote

import click

from platformio import app, fs, proc, telemetry
from platformio.compat import hashlib_encode_data
from platformio.package.manager.core import get_core_package_dir
from platformio.platform.exception import BuildScriptNotFound
from platformio.run.helpers import KNOWN_CLEAN_TARGETS, KNOWN_FULLCLEAN_TARGETS


class PlatformRunMixin:
    LINE_ERROR_RE = re.compile(r"(^|\s+)error:?\s+", re.I)

    @staticmethod
    def encode_scons_arg(value):
        if isinstance(value, (list, tuple, dict)):
            value = json.dumps(value)
        return base64.urlsafe_b64encode(hashlib_encode_data(value)).decode()

    @staticmethod
    def decode_scons_arg(data):
        value = base64.urlsafe_b64decode(data).decode()
        if value.startswith(("[", "{")):
            value = json.loads(value)
        return value

    def run(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, variables, targets, silent, verbose, jobs
    ):
        assert isinstance(variables, dict)
        assert isinstance(targets, list)

        self.ensure_engine_compatible()

        self.silent = silent
        self.verbose = verbose or app.get_setting("force_verbose")

        if "build_script" not in variables:
            variables["build_script"] = self.get_build_script()
        if not os.path.isfile(variables["build_script"]):
            raise BuildScriptNotFound(variables["build_script"])

        telemetry.log_platform_run(self, self.config, variables["pioenv"], targets)
        result = self._run_scons(variables, targets, jobs)

        assert "returncode" in result

        return result

    def _run_scons(self, variables, targets, jobs):
        scons_dir = get_core_package_dir("tool-scons")
        args = [
            proc.get_pythonexe_path(),
            os.path.join(scons_dir, "scons.py"),
            "-Q",
            "--warn=no-no-parallel-support",
            "--jobs",
            str(jobs),
            "--sconstruct",
            os.path.join(fs.get_source_dir(), "builder", "main.py"),
        ]
        args.append("PIOVERBOSE=%d" % int(self.verbose))
        # pylint: disable=protected-access
        args.append("ISATTY=%d" % int(click._compat.isatty(sys.stdout)))
        # encode and append variables
        for key, value in variables.items():
            args.append("%s=%s" % (key.upper(), self.encode_scons_arg(value)))

        if set(KNOWN_CLEAN_TARGETS + KNOWN_FULLCLEAN_TARGETS) & set(targets):
            args.append("--clean")
            args.append(
                "FULLCLEAN=%d"
                % (1 if set(KNOWN_FULLCLEAN_TARGETS) & set(targets) else 0)
            )
        elif targets:
            args.extend(targets)

        # force SCons output to Unicode
        os.environ["PYTHONIOENCODING"] = "utf-8"

        if targets and "menuconfig" in targets:
            return proc.exec_command(
                args, stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin
            )

        if click._compat.isatty(sys.stdout):

            def _write_and_flush(stream, data):
                try:
                    stream.write(data)
                    stream.flush()
                except IOError:
                    pass

            return proc.exec_command(
                args,
                stdout=proc.BuildAsyncPipe(
                    line_callback=self._on_stdout_line,
                    data_callback=lambda data: (
                        None if self.silent else _write_and_flush(sys.stdout, data)
                    ),
                ),
                stderr=proc.BuildAsyncPipe(
                    line_callback=self._on_stderr_line,
                    data_callback=lambda data: _write_and_flush(sys.stderr, data),
                ),
            )

        return proc.exec_command(
            args,
            stdout=proc.LineBufferedAsyncPipe(line_callback=self._on_stdout_line),
            stderr=proc.LineBufferedAsyncPipe(line_callback=self._on_stderr_line),
        )

    def _on_stdout_line(self, line):
        if "`buildprog' is up to date." in line:
            return
        self._echo_line(line, level=1)

    def _on_stderr_line(self, line):
        is_error = self.LINE_ERROR_RE.search(line) is not None
        self._echo_line(line, level=3 if is_error else 2)

        a_pos = line.find("fatal error:")
        b_pos = line.rfind(": No such file or directory")
        if a_pos == -1 or b_pos == -1:
            return
        self._echo_missed_dependency(line[a_pos + 12 : b_pos].strip())

    def _echo_line(self, line, level):
        if line.startswith("scons: "):
            line = line[7:]
        assert 1 <= level <= 3
        if self.silent and (level < 2 or not line):
            return
        fg = (None, "yellow", "red")[level - 1]
        if level == 1 and "is up to date" in line:
            fg = "green"
        click.secho(line, fg=fg, err=level > 1, nl=False)

    @staticmethod
    def _echo_missed_dependency(filename):
        if "/" in filename or not filename.endswith((".h", ".hpp")):
            return
        banner = """
{dots}
* Looking for {filename_styled} dependency? Check our library registry!
*
* CLI  > platformio lib search "header:{filename}"
* Web  > {link}
*
{dots}
""".format(
            filename=filename,
            filename_styled=click.style(filename, fg="cyan"),
            link=click.style(
                "https://registry.platformio.org/search?q=header:%s"
                % quote(filename, safe=""),
                fg="blue",
            ),
            dots="*" * (56 + len(filename)),
        )
        click.echo(banner, err=True)
