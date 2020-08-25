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

import click

from platformio import proc
from platformio.commands.check.defect import DefectItem
from platformio.commands.check.tools.base import CheckToolBase
from platformio.package.manager.core import get_core_package_dir


class CppcheckCheckTool(CheckToolBase):
    def __init__(self, *args, **kwargs):
        self._field_delimiter = "<&PIO&>"
        self._buffer = ""
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
        if self._field_delimiter not in raw_line:
            return None

        self._buffer += raw_line
        if any(f not in self._buffer for f in self.defect_fields):
            return None

        args = dict()
        for field in self._buffer.split(self._field_delimiter):
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

        # Skip defects found in third-party software, but keep in mind that such defects
        # might break checking process so defects from project files are not reported
        breaking_defect_ids = ("preprocessorErrorDirective", "syntaxError")
        if (
            args.get("file", "")
            .lower()
            .startswith(self.config.get_optional_dir("packages").lower())
        ):
            if args["id"] in breaking_defect_ids:
                if self.options.get("verbose"):
                    click.echo(
                        "Error: Found a breaking defect '%s' in %s:%s\n"
                        "Please note: check results might not be valid!\n"
                        "Try adding --skip-packages"
                        % (args.get("message"), args.get("file"), args.get("line"))
                    )
                    click.echo()
                self._bad_input = True
            return None

        self._buffer = ""
        return DefectItem(**args)

    def configure_command(
        self, language, src_files
    ):  # pylint: disable=arguments-differ
        tool_path = os.path.join(get_core_package_dir("tool-cppcheck"), "cppcheck")

        cmd = [
            tool_path,
            "--addon-python=%s" % proc.get_pythonexe_path(),
            "--error-exitcode=1",
            "--verbose" if self.options.get("verbose") else "--quiet",
        ]

        cmd.append(
            '--template="%s"'
            % self._field_delimiter.join(
                ["{0}={{{0}}}".format(f) for f in self.defect_fields]
            )
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
            cmd.append("--language=" + language)

        build_flags = self.cxx_flags if language == "c++" else self.cc_flags

        for flag in build_flags:
            if "-std" in flag:
                # Standards with GNU extensions are not allowed
                cmd.append("-" + flag.replace("gnu", "c"))

        cmd.extend(
            ["-D%s" % d for d in self.cpp_defines + self.toolchain_defines[language]]
        )

        cmd.extend(flags)

        cmd.extend(
            "--include=" + inc
            for inc in self.get_forced_includes(build_flags, self.cpp_includes)
        )
        cmd.append("--file-list=%s" % self._generate_src_file(src_files))
        cmd.append("--includes-file=%s" % self._generate_inc_file())

        return cmd

    @staticmethod
    def get_forced_includes(build_flags, includes):
        def _extract_filepath(flag, include_options, build_flags):
            path = ""
            for option in include_options:
                if not flag.startswith(option):
                    continue
                if flag.split(option)[1].strip():
                    path = flag.split(option)[1].strip()
                elif build_flags.index(flag) + 1 < len(build_flags):
                    path = build_flags[build_flags.index(flag) + 1]
            return path

        def _search_include_dir(filepath, include_paths):
            for inc_path in include_paths:
                path = os.path.join(inc_path, filepath)
                if os.path.isfile(path):
                    return path
            return ""

        result = []
        include_options = ("-include", "-imacros")
        for f in build_flags:
            if f.startswith(include_options):
                filepath = _extract_filepath(f, include_options, build_flags)
                if not os.path.isabs(filepath):
                    filepath = _search_include_dir(filepath, includes)
                if os.path.isfile(filepath):
                    result.append(filepath)

        return result

    def _generate_src_file(self, src_files):
        return self._create_tmp_file("\n".join(src_files))

    def _generate_inc_file(self):
        result = []
        for inc in self.cpp_includes:
            if self.options.get("skip_packages") and inc.lower().startswith(
                self.config.get_optional_dir("packages").lower()
            ):
                continue
            result.append(inc)
        return self._create_tmp_file("\n".join(result))

    def clean_up(self):
        super(CppcheckCheckTool, self).clean_up()

        # delete temporary dump files generated by addons
        if not self.is_flag_set("--addon", self.get_flags("cppcheck")):
            return

        for files in self.get_project_target_files(self.options["patterns"]).values():
            for f in files:
                dump_file = f + ".dump"
                if os.path.isfile(dump_file):
                    os.remove(dump_file)

    def check(self, on_defect_callback=None):
        self._on_defect_callback = on_defect_callback
        project_files = self.get_project_target_files(self.options["patterns"])

        languages = ("c", "c++")
        if not any([project_files[t] for t in languages]):
            click.echo("Error: Nothing to check.")
            return True
        for language in languages:
            if not project_files[language]:
                continue
            cmd = self.configure_command(language, project_files[language])
            if not cmd:
                self._bad_input = True
                continue
            if self.options.get("verbose"):
                click.echo(" ".join(cmd))

            proc.exec_command(
                cmd,
                stdout=proc.LineBufferedAsyncPipe(self.on_tool_output),
                stderr=proc.LineBufferedAsyncPipe(self.on_tool_output),
            )

        self.clean_up()

        return self._bad_input
