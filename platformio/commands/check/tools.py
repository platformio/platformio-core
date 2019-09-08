# Copyright (c) 2019-present PlatformIO <contact@platformio.org>
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

# pylint: disable=too-many-arguments,too-many-instance-attributes
# pylint: disable=redefined-builtin

import re
import sys
from os import remove
from os.path import isfile, join, relpath
from tempfile import NamedTemporaryFile

import click

from platformio import exception, fs, proc
from platformio.managers.core import get_core_package_dir
from platformio.project.helpers import (get_project_core_dir, get_project_dir,
                                        load_project_ide_data)


class DefectItem(object):

    SEVERITY_HIGH = 1
    SEVERITY_MEDIUM = 2
    SEVERITY_LOW = 4
    SEVERITY_LABELS = {4: "low", 2: "medium", 1: "high"}

    def __init__(self,
                 severity,
                 category,
                 message,
                 file="unknown",
                 line=0,
                 column=0,
                 id=None,
                 callstack=None,
                 cwe=None):
        assert severity in (self.SEVERITY_HIGH, self.SEVERITY_MEDIUM,
                            self.SEVERITY_LOW)
        self.severity = severity
        self.category = category
        self.message = message
        self.line = line
        self.column = column
        self.callstack = callstack
        self.cwe = cwe
        self.id = id
        self.file = file
        if file.startswith(get_project_dir()):
            self.file = relpath(file, get_project_dir())

    def __repr__(self):
        defect_color = None
        if self.severity == self.SEVERITY_HIGH:
            defect_color = "red"
        elif self.severity == self.SEVERITY_MEDIUM:
            defect_color = "yellow"

        format_str = "{file}:{line}: [{severity}:{category}] {message} {id}"
        return format_str.format(severity=click.style(
            self.SEVERITY_LABELS[self.severity], fg=defect_color),
                                 category=click.style(self.category.lower(),
                                                      fg=defect_color),
                                 file=click.style(self.file, bold=True),
                                 message=self.message,
                                 line=self.line,
                                 id="%s" % "[%s]" % self.id if self.id else "")

    def __or__(self, defect):
        return self.severity | defect.severity

    @staticmethod
    def severity_to_int(label):
        for key, value in DefectItem.SEVERITY_LABELS.items():
            if label == value:
                return key
        raise Exception("Unknown severity label -> %s" % label)

    def to_json(self):
        return {
            "severity": self.SEVERITY_LABELS[self.severity],
            "category": self.category,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "callstack": self.callstack,
            "id": self.id,
            "cwe": self.cwe
        }


class CheckToolFactory(object):

    @staticmethod
    def new(tool, project_dir, config, envname, options):
        clsname = "%sCheckTool" % tool.title()
        try:
            obj = getattr(sys.modules[__name__], clsname)(project_dir, config,
                                                          envname, options)
        except AttributeError:
            raise exception.PlatformioException("Unknown check tool `%s`" %
                                                tool)
        assert isinstance(obj, CheckToolBase)
        return obj


class CheckToolBase(object):

    def __init__(self, project_dir, config, envname, options):
        self.config = config
        self.envname = envname
        self.options = options
        self.cpp_defines = []
        self.cpp_includes = []
        self._bad_input = False
        self._load_cpp_data(project_dir, envname)

        self._defects = []
        self._on_defect_callback = None

    def _load_cpp_data(self, project_dir, envname):
        data = load_project_ide_data(project_dir, envname)
        if not data:
            return
        self.cpp_includes = data.get("includes", [])
        self.cpp_defines = data.get("defines", [])
        self.cpp_defines.extend(
            self._get_toolchain_defines(data.get("cc_path")))

    def get_flags(self, tool):
        result = []
        flags = self.options.get("flags", [])
        for flag in flags:
            if ":" not in flag:
                result.extend([f for f in flag.split(" ") if f])
            elif flag.startswith("%s:" % tool):
                result.extend(
                    [f for f in flag.split(":", 1)[1].split(" ") if f])

        return result

    @staticmethod
    def _get_toolchain_defines(cc_path):
        defines = []
        result = proc.exec_command(
            "echo | %s -dM -E -x c++ -" % cc_path, shell=True)

        for line in result['out'].split("\n"):
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
        if isinstance(defect, DefectItem):
            self._defects.append(defect)
            if self._on_defect_callback:
                self._on_defect_callback(defect)
        elif self.options.get("verbose"):
            click.echo(line)

    @staticmethod
    def tool_output_filter(line):
        return line

    @staticmethod
    def parse_defect(raw_line):
        return raw_line

    def clean_up(self):
        pass

    def exceeds_severity_threshold(self, severity):
        return severity <= DefectItem.severity_to_int(
            self.options.get("severity"))

    def get_project_src_files(self):
        file_extensions = ["h", "hpp", "c", "cc", "cpp", "ino"]
        return fs.match_src_files(get_project_dir(),
                                  self.options.get("filter"), file_extensions)

    def check(self, on_defect_callback=None):
        self._on_defect_callback = on_defect_callback
        cmd = self.configure_command()
        if self.options.get("verbose"):
            click.echo(" ".join(cmd))

        proc.exec_command(
            cmd,
            stdout=proc.LineBufferedAsyncPipe(self.on_tool_output),
            stderr=proc.LineBufferedAsyncPipe(self.on_tool_output))

        self.clean_up()

        return self._bad_input


class CppcheckCheckTool(CheckToolBase):

    def __init__(self, *args, **kwargs):
        self._tmp_files = []
        self.defect_fields = [
            "severity", "message", "file", "line", "column", "callstack",
            "cwe", "id"
        ]
        super(CppcheckCheckTool, self).__init__(*args, **kwargs)

    def tool_output_filter(self, line):
        if not self.options.get(
                "verbose") and "--suppress=unmatchedSuppression:" in line:
            return ""

        if any(msg in line for msg in ("No C or C++ source files found",
                                       "unrecognized command line option")):
            self._bad_input = True

        return line

    def parse_defect(self, raw_line):
        if "<&PIO&>" not in raw_line or any(f not in raw_line
                                            for f in self.defect_fields):
            return None

        args = dict()
        for field in raw_line.split("<&PIO&>"):
            field = field.strip().replace('"', "")
            name, value = field.split("=", 1)
            args[name] = value

        args['category'] = args['severity']
        if args['severity'] == "error":
            args['severity'] = DefectItem.SEVERITY_HIGH
        elif args['severity'] == "warning":
            args['severity'] = DefectItem.SEVERITY_MEDIUM
        else:
            args['severity'] = DefectItem.SEVERITY_LOW

        if self.exceeds_severity_threshold(args['severity']):
            return DefectItem(**args)

        return None

    def configure_command(self):
        tool_path = join(get_core_package_dir("tool-cppcheck"), "cppcheck")

        cmd = [
            tool_path, "--error-exitcode=1",
            "--verbose" if self.options.get("verbose") else "--quiet"
        ]

        cmd.append('--template="%s"' % "<&PIO&>".join(
            ["{0}={{{0}}}".format(f) for f in self.defect_fields]))

        flags = self.get_flags("cppcheck")
        if not self.is_flag_set("--platform", flags):
            cmd.append("--platform=unspecified")
        if not self.is_flag_set("--enable", flags):
            enabled_checks = [
                "warning", "style", "performance", "portability",
                "unusedFunction"
            ]
            cmd.append("--enable=%s" % ",".join(enabled_checks))

        cmd.extend(["-D%s" % d for d in self.cpp_defines])
        cmd.extend(flags)

        cmd.append("--file-list=%s" % self._generate_src_file())
        cmd.append("--includes-file=%s" % self._generate_inc_file())

        core_dir = get_project_core_dir()
        cmd.append("--suppress=*:%s*" % core_dir)
        cmd.append("--suppress=unmatchedSuppression:%s*" % core_dir)

        return cmd

    def _create_tmp_file(self, data):
        with NamedTemporaryFile("w", delete=False) as fp:
            fp.write(data)
            self._tmp_files.append(fp.name)
            return fp.name

    def _generate_src_file(self):
        return self._create_tmp_file("\n".join(self.get_project_src_files()))

    def _generate_inc_file(self):
        return self._create_tmp_file("\n".join(self.cpp_includes))

    def clean_up(self):
        for f in self._tmp_files:
            if isfile(f):
                remove(f)

        # delete temporary dump files generated by addons
        if not self.is_flag_set("--addon", self.get_flags("cppcheck")):
            return
        for f in self.get_project_src_files():
            dump_file = f + ".dump"
            if isfile(dump_file):
                remove(dump_file)


class ClangtidyCheckTool(CheckToolBase):

    def tool_output_filter(self, line):
        if not self.options.get(
                "verbose") and "[clang-diagnostic-error]" in line:
            return ""

        if "[CommonOptionsParser]" in line:
            self._bad_input = True
            return line

        if any(d in line for d in ("note: ", "error: ", "warning: ")):
            return line

        return ""

    def parse_defect(self, raw_line):
        match = re.match(r"^(.*):(\d+):(\d+):\s+([^:]+):\s(.+)\[([^]]+)\]$",
                         raw_line)
        if not match:
            return raw_line

        file, line, column, category, message, defect_id = match.groups()

        severity = DefectItem.SEVERITY_LOW
        if category == "error":
            severity = DefectItem.SEVERITY_HIGH
        elif category == "warning":
            severity = DefectItem.SEVERITY_MEDIUM

        if self.exceeds_severity_threshold(severity):
            return DefectItem(severity, category, message, file, line, column,
                              defect_id)

        return None

    def configure_command(self):
        tool_path = join(get_core_package_dir("tool-clangtidy"), "clang-tidy")

        cmd = [tool_path, "--quiet"]
        flags = self.get_flags("clangtidy")
        if not self.is_flag_set("--checks", flags):
            cmd.append("--checks=*")

        cmd.extend(flags)
        cmd.extend(self.get_project_src_files())
        cmd.append("--")

        cmd.extend(["-D%s" % d for d in self.cpp_defines])
        cmd.extend(["-I%s" % inc for inc in self.cpp_includes])

        return cmd
