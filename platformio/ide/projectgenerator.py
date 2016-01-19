# Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

import json
import os
import re
import sys
from os.path import (abspath, basename, expanduser, isdir, join, normpath,
                     relpath)

import bottle
import click  # pylint: disable=wrong-import-order

from platformio import app, exception, util


class ProjectGenerator(object):

    def __init__(self, project_dir, ide, board):
        self.project_dir = project_dir
        self.ide = ide
        self.board = board
        self._tplvars = {}

        self._gather_tplvars()

    @staticmethod
    def get_supported_ides():
        tpls_dir = join(util.get_source_dir(), "ide", "tpls")
        return sorted([d for d in os.listdir(tpls_dir)
                       if isdir(join(tpls_dir, d))])

    @util.memoized
    def get_project_env(self):
        data = {"env_name": "PlatformIO"}
        with util.cd(self.project_dir):
            config = util.get_project_config()
            for section in config.sections():
                if not section.startswith("env:"):
                    continue
                data = {"env_name": section[4:]}
                for k, v in config.items(section):
                    data[k] = v
                if self.board == data.get("board"):
                    break
        return data

    @util.memoized
    def get_project_build_data(self):
        data = {
            "defines": [],
            "includes": [],
            "cxx_path": None
        }
        envdata = self.get_project_env()
        if "env_name" not in envdata:
            return data
        cmd = [normpath(sys.executable), "-m", "platformio", "-f"]
        if app.get_session_var("caller_id"):
            cmd.extend(["-c", app.get_session_var("caller_id")])
        cmd.extend(["run", "-t", "idedata", "-e", envdata['env_name']])
        cmd.extend(["-d", self.project_dir])
        result = util.exec_command(cmd)

        if result['returncode'] != 0 or '"includes":' not in result['out']:
            raise exception.PlatformioException(
                "\n".join([result['out'], result['err']]))

        output = result['out']
        start_index = output.index('{"')
        stop_index = output.rindex('}')
        data = json.loads(output[start_index:stop_index + 1])

        return data

    def get_project_name(self):
        return basename(self.project_dir)

    def get_src_files(self):
        result = []
        with util.cd(self.project_dir):
            for root, _, files in os.walk(util.get_projectsrc_dir()):
                for f in files:
                    result.append(relpath(join(root, f)))
        return result

    def get_tpls(self):
        tpls = []
        tpls_dir = join(util.get_source_dir(), "ide", "tpls", self.ide)
        for root, _, files in os.walk(tpls_dir):
            for f in files:
                if not f.endswith(".tpl"):
                    continue
                _relpath = root.replace(tpls_dir, "")
                if _relpath.startswith(os.sep):
                    _relpath = _relpath[1:]
                tpls.append((_relpath, join(root, f)))
        return tpls

    def generate(self):
        for _relpath, _path in self.get_tpls():
            tpl_dir = self.project_dir
            if _relpath:
                tpl_dir = join(self.project_dir, _relpath)
                if not isdir(tpl_dir):
                    os.makedirs(tpl_dir)

            file_name = basename(_path)[:-4]
            with open(join(tpl_dir, file_name), "w") as f:
                f.write(self._render_tpl(_path).encode("utf8"))

    def _render_tpl(self, tpl_path):
        content = ""
        with open(tpl_path) as f:
            content = f.read()
        return bottle.template(content, **self._tplvars)

    def _gather_tplvars(self):
        src_files = self.get_src_files()

        if (not any([f.endswith((".c", ".cpp")) for f in src_files]) and
                self.ide == "clion"):
            click.secho(
                "Warning! Can not find main source file (*.c, *.cpp). So, "
                "code auto-completion is disabled. Please add source files "
                "to `src` directory and re-initialize project or edit "
                "`CMakeLists.txt` file manually (`add_executable` command).",
                fg="yellow")

        self._tplvars.update(self.get_project_env())
        self._tplvars.update(self.get_project_build_data())
        self._tplvars.update({
            "project_name": self.get_project_name(),
            "src_files": src_files,
            "user_home_dir": abspath(expanduser("~")),
            "project_dir": self.project_dir,
            "systype": util.get_systype(),
            "platformio_path": self._fix_os_path(
                util.where_is_program("platformio")),
            "env_pathsep": os.pathsep,
            "env_path": self._fix_os_path(os.getenv("PATH"))
        })

    @staticmethod
    def _fix_os_path(path):
        return (re.sub(r"[\\]+", '\\' * 4, path) if "windows" in
                util.get_systype() else path)
