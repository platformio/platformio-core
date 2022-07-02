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

import re
from os.path import join

from platformio.check.defect import DefectItem
from platformio.check.tools.base import CheckToolBase


class ClangtidyCheckTool(CheckToolBase):
    def tool_output_filter(self, line):  # pylint: disable=arguments-differ
        if not self.options.get("verbose") and "[clang-diagnostic-error]" in line:
            return ""

        if "[CommonOptionsParser]" in line:
            self._bad_input = True
            return line

        if any(d in line for d in ("note: ", "error: ", "warning: ")):
            return line

        return ""

    def parse_defect(self, raw_line):  # pylint: disable=arguments-differ
        match = re.match(r"^(.*):(\d+):(\d+):\s+([^:]+):\s(.+)\[([^]]+)\]$", raw_line)
        if not match:
            return raw_line

        file_, line, column, category, message, defect_id = match.groups()

        severity = DefectItem.SEVERITY_LOW
        if category == "error":
            severity = DefectItem.SEVERITY_HIGH
        elif category == "warning":
            severity = DefectItem.SEVERITY_MEDIUM

        return DefectItem(severity, category, message, file_, line, column, defect_id)

    @staticmethod
    def is_check_successful(cmd_result):
        # Note: Clang-Tidy returns 1 for not critical compilation errors,
        # so 0 and 1 are only acceptable values
        return cmd_result["returncode"] < 2

    def configure_command(self):
        tool_path = join(self.get_tool_dir("tool-clangtidy"), "clang-tidy")

        cmd = [tool_path, "--quiet"]
        flags = self.get_flags("clangtidy")
        if not (
            self.is_flag_set("--checks", flags) or self.is_flag_set("--config", flags)
        ):
            cmd.append("--checks=*")

        project_files = self.get_project_target_files(self.options["patterns"])

        src_files = []
        for items in project_files.values():
            src_files.extend(items)

        cmd.extend(flags + src_files + ["--"])
        cmd.extend(
            ["-D%s" % d for d in self.cpp_defines + self.toolchain_defines["c++"]]
        )

        includes = []
        for inc in self.cpp_includes:
            if self.options.get("skip_packages") and inc.lower().startswith(
                self.config.get("platformio", "packages_dir").lower()
            ):
                continue
            includes.append(inc)

        cmd.extend(["-I%s" % inc for inc in includes])

        return cmd
