# Copyright (c) 2020-present PlatformIO <contact@platformio.org>
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
import shutil
import tempfile
from xml.etree.ElementTree import fromstring

import click

from platformio import proc, util
from platformio.commands.check.defect import DefectItem
from platformio.commands.check.tools.base import CheckToolBase
from platformio.managers.core import get_core_package_dir


class PvsStudioCheckTool(CheckToolBase):  # pylint: disable=too-many-instance-attributes
    def __init__(self, *args, **kwargs):
        self._tmp_dir = tempfile.mkdtemp(prefix="piocheck")
        self._tmp_preprocessed_file = self._generate_tmp_file_path() + ".i"
        self._tmp_output_file = self._generate_tmp_file_path() + ".pvs"
        self._tmp_cfg_file = self._generate_tmp_file_path() + ".cfg"
        self._tmp_cmd_file = self._generate_tmp_file_path() + ".cmd"
        self.tool_path = os.path.join(
            get_core_package_dir("tool-pvs-studio"),
            "x64" if "windows" in util.get_systype() else "bin",
            "pvs-studio",
        )
        super(PvsStudioCheckTool, self).__init__(*args, **kwargs)

        with open(self._tmp_cfg_file, "w") as fp:
            fp.write(
                "exclude-path = "
                + self.config.get_optional_dir("packages").replace("\\", "/")
            )

        with open(self._tmp_cmd_file, "w") as fp:
            fp.write(
                " ".join(
                    ['-I"%s"' % inc.replace("\\", "/") for inc in self.cpp_includes]
                )
            )

    def _process_defects(self, defects):
        for defect in defects:
            if not isinstance(defect, DefectItem):
                return
            if defect.severity not in self.options["severity"]:
                return
            self._defects.append(defect)
            if self._on_defect_callback:
                self._on_defect_callback(defect)

    def _demangle_report(self, output_file):
        converter_tool = os.path.join(
            get_core_package_dir("tool-pvs-studio"),
            "HtmlGenerator"
            if "windows" in util.get_systype()
            else os.path.join("bin", "plog-converter"),
        )

        cmd = (
            converter_tool,
            "-t",
            "xml",
            output_file,
            "-m",
            "cwe",
            "-m",
            "misra",
            "-a",
            # Enable all possible analyzers and defect levels
            "GA:1,2,3;64:1,2,3;OP:1,2,3;CS:1,2,3;MISRA:1,2,3",
            "--cerr",
        )

        result = proc.exec_command(cmd)
        if result["returncode"] != 0:
            click.echo(result["err"])
            self._bad_input = True

        return result["err"]

    def parse_defects(self, output_file):
        defects = []

        report = self._demangle_report(output_file)
        if not report:
            self._bad_input = True
            return []

        try:
            defects_data = fromstring(report)
        except:  # pylint: disable=bare-except
            click.echo("Error: Couldn't decode generated report!")
            self._bad_input = True
            return []

        for table in defects_data.iter("PVS-Studio_Analysis_Log"):
            message = table.find("Message").text
            category = table.find("ErrorType").text
            line = table.find("Line").text
            file_ = table.find("File").text
            defect_id = table.find("ErrorCode").text
            cwe = table.find("CWECode")
            cwe_id = None
            if cwe is not None:
                cwe_id = cwe.text.lower().replace("cwe-", "")
            misra = table.find("MISRA")
            if misra is not None:
                message += " [%s]" % misra.text

            severity = DefectItem.SEVERITY_LOW
            if category == "error":
                severity = DefectItem.SEVERITY_HIGH
            elif category == "warning":
                severity = DefectItem.SEVERITY_MEDIUM

            defects.append(
                DefectItem(
                    severity, category, message, file_, line, id=defect_id, cwe=cwe_id
                )
            )

        return defects

    def configure_command(self, src_file):  # pylint: disable=arguments-differ
        if os.path.isfile(self._tmp_output_file):
            os.remove(self._tmp_output_file)

        if not os.path.isfile(self._tmp_preprocessed_file):
            click.echo(
                "Error: Missing preprocessed file '%s'" % (self._tmp_preprocessed_file)
            )
            return ""

        cmd = [
            self.tool_path,
            "--skip-cl-exe",
            "yes",
            "--language",
            "C" if src_file.endswith(".c") else "C++",
            "--preprocessor",
            "gcc",
            "--cfg",
            self._tmp_cfg_file,
            "--source-file",
            src_file,
            "--i-file",
            self._tmp_preprocessed_file,
            "--output-file",
            self._tmp_output_file,
        ]

        flags = self.get_flags("pvs-studio")
        if not self.is_flag_set("--platform", flags):
            cmd.append("--platform=arm")
        cmd.extend(flags)

        return cmd

    def _generate_tmp_file_path(self):
        # pylint: disable=protected-access
        return os.path.join(self._tmp_dir, next(tempfile._get_candidate_names()))

    def _prepare_preprocessed_file(self, src_file):
        flags = self.cxx_flags
        compiler = self.cxx_path
        if src_file.endswith(".c"):
            flags = self.cc_flags
            compiler = self.cc_path

        cmd = [compiler, src_file, "-E", "-o", self._tmp_preprocessed_file]
        cmd.extend([f for f in flags if f])
        cmd.extend(["-D%s" % d for d in self.cpp_defines])
        cmd.append('@"%s"' % self._tmp_cmd_file)

        result = proc.exec_command(" ".join(cmd), shell=True)
        if result["returncode"] != 0:
            if self.options.get("verbose"):
                click.echo(" ".join(cmd))
            click.echo(result["err"])
            self._bad_input = True

    def clean_up(self):
        if os.path.isdir(self._tmp_dir):
            shutil.rmtree(self._tmp_dir)

    def check(self, on_defect_callback=None):
        self._on_defect_callback = on_defect_callback
        src_files = [
            f for f in self.get_project_target_files() if not f.endswith((".h", ".hpp"))
        ]

        for src_file in src_files:
            self._prepare_preprocessed_file(src_file)
            cmd = self.configure_command(src_file)
            if self.options.get("verbose"):
                click.echo(" ".join(cmd))
            if not cmd:
                self._bad_input = True
                continue

            result = proc.exec_command(cmd)
            # pylint: disable=unsupported-membership-test
            if result["returncode"] != 0 or "License was not entered" in result["err"]:
                self._bad_input = True
                click.echo(result["err"])
                continue

            self._process_defects(self.parse_defects(self._tmp_output_file))

        self.clean_up()

        return self._bad_input
