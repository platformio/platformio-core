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

from os import remove
from os.path import isfile, join
from tempfile import NamedTemporaryFile

from platformio.commands.check.defect import DefectItem
from platformio.commands.check.tools.base import CheckToolBase
from platformio.managers.core import get_core_package_dir


class CppcheckCheckTool(CheckToolBase):
    def __init__(self, *args, **kwargs):
        self._tmp_files = []
        self.defect_fields = [
            "severity",
            "message",
            "file",
            "line",
            "column",
            "callstack",
            "cwe",
            "id",
        ]
        super(CppcheckCheckTool, self).__init__(*args, **kwargs)

    def tool_output_filter(self, line):
        if (
            not self.options.get("verbose")
            and "--suppress=unmatchedSuppression:" in line
        ):
            return ""

        if any(
            msg in line
            for msg in (
                "No C or C++ source files found",
                "unrecognized command line option",
            )
        ):
            self._bad_input = True

        return line

    def parse_defect(self, raw_line):
        if "<&PIO&>" not in raw_line or any(
            f not in raw_line for f in self.defect_fields
        ):
            return None

        args = dict()
        for field in raw_line.split("<&PIO&>"):
            field = field.strip().replace('"', "")
            name, value = field.split("=", 1)
            args[name] = value

        args["category"] = args["severity"]
        if args["severity"] == "error":
            args["severity"] = DefectItem.SEVERITY_HIGH
        elif args["severity"] == "warning":
            args["severity"] = DefectItem.SEVERITY_MEDIUM
        else:
            args["severity"] = DefectItem.SEVERITY_LOW

        return DefectItem(**args)

    def configure_command(self):
        tool_path = join(get_core_package_dir("tool-cppcheck"), "cppcheck")

        cmd = [
            tool_path,
            "--error-exitcode=1",
            "--verbose" if self.options.get("verbose") else "--quiet",
        ]

        cmd.append(
            '--template="%s"'
            % "<&PIO&>".join(["{0}={{{0}}}".format(f) for f in self.defect_fields])
        )

        flags = self.get_flags("cppcheck")
        if not flags:
            # by default user can suppress reporting individual defects
            # directly in code // cppcheck-suppress warningID
            cmd.append("--inline-suppr")
        if not self.is_flag_set("--platform", flags):
            cmd.append("--platform=unspecified")
        if not self.is_flag_set("--enable", flags):
            enabled_checks = [
                "warning",
                "style",
                "performance",
                "portability",
                "unusedFunction",
            ]
            cmd.append("--enable=%s" % ",".join(enabled_checks))

        if not self.is_flag_set("--language", flags):
            if self.get_source_language() == "c++":
                cmd.append("--language=c++")

                if not self.is_flag_set("--std", flags):
                    for f in self.cxx_flags + self.cc_flags:
                        if "-std" in f:
                            # Standards with GNU extensions are not allowed
                            cmd.append("-" + f.replace("gnu", "c"))

        cmd.extend(["-D%s" % d for d in self.cpp_defines + self.toolchain_defines])
        cmd.extend(flags)

        cmd.append("--file-list=%s" % self._generate_src_file())
        cmd.append("--includes-file=%s" % self._generate_inc_file())

        core_dir = self.config.get_optional_dir("packages")
        cmd.append("--suppress=*:%s*" % core_dir)
        cmd.append("--suppress=unmatchedSuppression:%s*" % core_dir)

        return cmd

    def _create_tmp_file(self, data):
        with NamedTemporaryFile("w", delete=False) as fp:
            fp.write(data)
            self._tmp_files.append(fp.name)
            return fp.name

    def _generate_src_file(self):
        src_files = [
            f for f in self.get_project_target_files() if not f.endswith((".h", ".hpp"))
        ]
        return self._create_tmp_file("\n".join(src_files))

    def _generate_inc_file(self):
        return self._create_tmp_file("\n".join(self.cpp_includes))

    def clean_up(self):
        for f in self._tmp_files:
            if isfile(f):
                remove(f)

        # delete temporary dump files generated by addons
        if not self.is_flag_set("--addon", self.get_flags("cppcheck")):
            return
        for f in self.get_project_target_files():
            dump_file = f + ".dump"
            if isfile(dump_file):
                remove(dump_file)
