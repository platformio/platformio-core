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

import glob
import os

import click

from platformio import fs, proc
from platformio.commands.check.defect import DefectItem
from platformio.project.helpers import get_project_dir, load_project_ide_data


class CheckToolBase(object):  # pylint: disable=too-many-instance-attributes
    def __init__(self, project_dir, config, envname, options):
        self.config = config
        self.envname = envname
        self.options = options
        self.cc_flags = []
        self.cxx_flags = []
        self.cpp_includes = []
        self.cpp_defines = []
        self.toolchain_defines = []
        self.cc_path = None
        self.cxx_path = None
        self._defects = []
        self._on_defect_callback = None
        self._bad_input = False
        self._load_cpp_data(project_dir, envname)

        # detect all defects by default
        if not self.options.get("severity"):
            self.options["severity"] = [
                DefectItem.SEVERITY_LOW,
                DefectItem.SEVERITY_MEDIUM,
                DefectItem.SEVERITY_HIGH,
            ]
        # cast to severity by ids
        self.options["severity"] = [
            s if isinstance(s, int) else DefectItem.severity_to_int(s)
            for s in self.options["severity"]
        ]

    def _load_cpp_data(self, project_dir, envname):
        data = load_project_ide_data(project_dir, envname)
        if not data:
            return
        self.cc_flags = data.get("cc_flags", "").split(" ")
        self.cxx_flags = data.get("cxx_flags", "").split(" ")
        self.cpp_includes = data.get("includes", [])
        self.cpp_defines = data.get("defines", [])
        self.cc_path = data.get("cc_path")
        self.cxx_path = data.get("cxx_path")
        self.toolchain_defines = self._get_toolchain_defines(self.cc_path)

    def get_flags(self, tool):
        result = []
        flags = self.options.get("flags") or []
        for flag in flags:
            if ":" not in flag or flag.startswith("-"):
                result.extend([f for f in flag.split(" ") if f])
            elif flag.startswith("%s:" % tool):
                result.extend([f for f in flag.split(":", 1)[1].split(" ") if f])

        return result

    @staticmethod
    def _get_toolchain_defines(cc_path):
        defines = []
        result = proc.exec_command("echo | %s -dM -E -x c++ -" % cc_path, shell=True)

        for line in result["out"].split("\n"):
            tokens = line.strip().split(" ", 2)
            if not tokens or tokens[0] != "#define":
                continue
            if len(tokens) > 2:
                defines.append("%s=%s" % (tokens[1], tokens[2]))
            else:
                defines.append(tokens[1])

        return defines

    @staticmethod
    def is_flag_set(flag, flags):
        return any(flag in f for f in flags)

    def get_defects(self):
        return self._defects

    def configure_command(self):
        raise NotImplementedError

    def on_tool_output(self, line):
        line = self.tool_output_filter(line)
        if not line:
            return

        defect = self.parse_defect(line)

        if not isinstance(defect, DefectItem):
            if self.options.get("verbose"):
                click.echo(line)
            return

        if defect.severity not in self.options["severity"]:
            return

        self._defects.append(defect)
        if self._on_defect_callback:
            self._on_defect_callback(defect)

    @staticmethod
    def tool_output_filter(line):
        return line

    @staticmethod
    def parse_defect(raw_line):
        return raw_line

    def clean_up(self):
        pass

    def get_project_target_files(self):
        allowed_extensions = (".h", ".hpp", ".c", ".cc", ".cpp", ".ino")
        result = []

        def _add_file(path):
            if not path.endswith(allowed_extensions):
                return
            result.append(os.path.realpath(path))

        for pattern in self.options["patterns"]:
            for item in glob.glob(pattern):
                if not os.path.isdir(item):
                    _add_file(item)
                for root, _, files in os.walk(item, followlinks=True):
                    for f in files:
                        _add_file(os.path.join(root, f))

        return result

    def get_source_language(self):
        with fs.cd(get_project_dir()):
            for _, __, files in os.walk(self.config.get_optional_dir("src")):
                for name in files:
                    if "." not in name:
                        continue
                    if os.path.splitext(name)[1].lower() in (".cpp", ".cxx", ".ino"):
                        return "c++"
            return "c"

    def check(self, on_defect_callback=None):
        self._on_defect_callback = on_defect_callback
        cmd = self.configure_command()
        if self.options.get("verbose"):
            click.echo(" ".join(cmd))

        proc.exec_command(
            cmd,
            stdout=proc.LineBufferedAsyncPipe(self.on_tool_output),
            stderr=proc.LineBufferedAsyncPipe(self.on_tool_output),
        )

        self.clean_up()

        return self._bad_input
