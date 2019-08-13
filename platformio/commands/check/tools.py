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

# pylint: disable=too-many-arguments

import subprocess
import sys
from os import remove
from os.path import isfile, join
from tempfile import NamedTemporaryFile

import click

from platformio import app, exception, fs, proc
from platformio.commands.platform import \
    platform_install as cmd_platform_install
from platformio.managers.core import get_core_package_dir
from platformio.managers.platform import PlatformFactory
from platformio.project.helpers import (get_project_dir,
                                        get_project_include_dir,
                                        get_project_lib_dir,
                                        get_project_src_dir,
                                        load_project_ide_data)


class CheckToolFactory(object):

    @staticmethod
    def new(tool, project_dir, config, envname, verbose, silent):
        clsname = "%sCheckTool" % tool.title()
        try:
            obj = getattr(sys.modules[__name__],
                          clsname)(project_dir, config, envname, verbose,
                                   silent)
        except AttributeError:
            raise exception.PlatformioException("Unknown check tool `%s`" %
                                                tool)
        assert isinstance(obj, CheckToolBase)
        return obj


class CheckToolBase(object):

    def __init__(self, project_dir, config, envname, verbose, silent):
        self.config = config
        self.envname = envname
        self.verbose = verbose
        self.silent = silent

        self.platform = self._init_platform(
            self.config.get("env:" + self.envname, "platform"))

        self._cpp_defines = []
        self._cpp_includes = []
        self._load_cpp_data(project_dir, envname)

    @staticmethod
    def _init_platform(platform):
        try:
            return PlatformFactory.newPlatform(platform)
        except exception.UnknownPlatform:
            app.get_session_var("command_ctx").invoke(
                cmd_platform_install,
                platforms=[platform],
                skip_default_package=True)
            return PlatformFactory.newPlatform(platform)

    def _load_cpp_data(self, project_dir, envname):
        data = load_project_ide_data(project_dir, envname)
        if not data:
            return

        for inc in data.get("includes", []):
            self._cpp_includes.append(inc)

        self._cpp_defines = data.get("defines", [])
        self._cpp_defines.extend(
            self._get_toolchain_defines(data.get("cc_path")))

    @staticmethod
    def _get_toolchain_defines(cc_path):
        defines = []
        result = proc.exec_command(["echo", "|", cc_path, "-dM", "-E", "-"],
                                   shell=True)

        for line in result['out'].split("\n"):
            tokens = line.strip().split(" ", 2)
            if not tokens or tokens[0] != "#define":
                continue
            if len(tokens) > 2:
                defines.append("%s=%s" % (tokens[1], tokens[2]))
            else:
                defines.append(tokens[1])

        return defines

    def prepare_command(self):
        raise NotImplementedError

    def clean_up(self):
        pass

    def check(self):
        cmd = self.prepare_command()
        if self.verbose:
            click.echo(" ".join(cmd))

        return_code = subprocess.call(cmd)
        self.clean_up()

        return return_code


class CppcheckCheckTool(CheckToolBase):

    def __init__(self, *args, **kwargs):
        self._tmp_files = []
        super(CppcheckCheckTool, self).__init__(*args, **kwargs)

    @staticmethod
    def is_flag_set(flag, flags):
        return any(flag in f for f in flags)

    def prepare_command(self):
        tool_path = join(get_core_package_dir("tool-cppcheck"), "bin",
                         "cppcheck")
        extra_flags = self.config.get("env:" + self.envname, "check_flags", [])

        cmd = [tool_path, "--error-exitcode=1"]
        if self.verbose:
            cmd.append("--verbose")
        else:
            cmd.append("--quiet")

        if not self.is_flag_set("--platform", extra_flags):
            cmd.append("--platform=unspecified")
        if not self.is_flag_set("--enable", extra_flags):
            cmd.append("--enable=all")

        for define in self._cpp_defines:
            cmd.append("-D%s" % define)

        cmd.extend(extra_flags)

        cmd.append("--file-list=%s" % self._generate_src_file())
        cmd.append("--includes-file=%s" % self._generate_inc_file())

        for package in self._get_ignored_packages():
            cmd.append("--suppress=*:*%s*" % package)
            cmd.append("--suppress=unmatchedSuppression:*%s*" % package)

        return cmd

    def _get_ignored_packages(self):
        ignore_packages = []
        env_framework = self.config.get("env:" + self.envname, "framework", [])
        for package, description in self.platform.packages.items():
            if (any("framework-%s" % f in package for f in env_framework)
                    or description.get("type") == "toolchain"):
                ignore_packages.append(package)

        return ignore_packages

    def _create_tmp_file(self, data):
        with NamedTemporaryFile("w", delete=False) as fp:
            fp.write(data)
            self._tmp_files.append(fp.name)
            return fp.name

    def _generate_src_file(self):
        check_filter = self.config.get("env:" + self.envname, "check_filter")
        if not check_filter:
            check_filter = [
                "+<%s/>" % p
                for p in (get_project_src_dir(), get_project_include_dir(),
                          get_project_lib_dir())
            ]

        file_extensions = ["h", "hpp", "c", "cc", "cpp", "ino"]
        src_files = fs.match_src_files(get_project_dir(), check_filter,
                                       file_extensions)

        return self._create_tmp_file("\n".join(src_files))

    def _generate_inc_file(self):
        return self._create_tmp_file("\n".join(self._cpp_includes))

    def clean_up(self):
        for f in self._tmp_files:
            if isfile(f):
                remove(f)


class CustomCheckTool(CheckToolBase):

    def prepare_command(self):
        return self.config.get("env:" + self.envname, "check_flags")
