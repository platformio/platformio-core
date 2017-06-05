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

import json
import os
import re
from cStringIO import StringIO
from os.path import abspath, basename, expanduser, isdir, isfile, join, relpath

import bottle
import click

from platformio import exception, util
from platformio.commands.run import cli as cmd_run


class ProjectGenerator(object):

    def __init__(self, project_dir, ide, env_name):
        self.project_dir = project_dir
        self.ide = ide
        self.env_name = env_name
        self._tplvars = {}

        with util.cd(self.project_dir):
            self.project_src_dir = util.get_projectsrc_dir()

        self._gather_tplvars()

    @staticmethod
    def get_supported_ides():
        tpls_dir = join(util.get_source_dir(), "ide", "tpls")
        return sorted(
            [d for d in os.listdir(tpls_dir) if isdir(join(tpls_dir, d))])

    @util.memoized
    def get_project_env(self):
        data = None
        config = util.load_project_config(self.project_dir)
        for section in config.sections():
            if not section.startswith("env:"):
                continue
            if self.env_name != section[4:]:
                continue
            data = {"env_name": section[4:]}
            for k, v in config.items(section):
                data[k] = v
        return data

    @util.memoized
    def get_project_build_data(self):
        data = {"defines": [], "includes": [], "cxx_path": None}
        envdata = self.get_project_env()
        if not envdata:
            return data

        out = StringIO()
        with util.capture_stdout(out):
            click.get_current_context().invoke(
                cmd_run,
                project_dir=self.project_dir,
                environment=[envdata['env_name']],
                target=["idedata"])
        result = out.getvalue()

        if '"includes":' not in result:
            raise exception.PlatformioException(result)

        for line in result.split("\n"):
            line = line.strip()
            if line.startswith('{"') and line.endswith("}"):
                data = json.loads(line)
        return data

    def get_project_name(self):
        return basename(self.project_dir)

    def get_src_files(self):
        result = []
        with util.cd(self.project_dir):
            for root, _, files in os.walk(self.project_src_dir):
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
        for tpl_relpath, tpl_path in self.get_tpls():
            dst_dir = self.project_dir
            if tpl_relpath:
                dst_dir = join(self.project_dir, tpl_relpath)
                if not isdir(dst_dir):
                    os.makedirs(dst_dir)

            file_name = basename(tpl_path)[:-4]
            self._merge_contents(
                join(dst_dir, file_name),
                self._render_tpl(tpl_path).encode("utf8"))

    def _render_tpl(self, tpl_path):
        content = ""
        with open(tpl_path) as f:
            content = f.read()
        return bottle.template(content, **self._tplvars)

    @staticmethod
    def _merge_contents(dst_path, contents):
        file_name = basename(dst_path)

        # merge .gitignore
        if file_name == ".gitignore" and isfile(dst_path):
            modified = False
            default = [l.strip() for l in contents.split("\n")]
            with open(dst_path) as fp:
                current = [l.strip() for l in fp.readlines()]
            for d in default:
                if d and d not in current:
                    modified = True
                    current.append(d)
            if not modified:
                return
            contents = "\n".join(current) + "\n"

        with open(dst_path, "w") as f:
            f.write(contents)

    def _gather_tplvars(self):
        self._tplvars.update(self.get_project_env())
        self._tplvars.update(self.get_project_build_data())
        self._tplvars.update({
            "project_name":
            self.get_project_name(),
            "src_files":
            self.get_src_files(),
            "user_home_dir":
            abspath(expanduser("~")),
            "project_dir":
            self.project_dir,
            "project_src_dir":
            self.project_src_dir,
            "systype":
            util.get_systype(),
            "platformio_path":
            self._fix_os_path(util.where_is_program("platformio")),
            "env_pathsep":
            os.pathsep,
            "env_path":
            self._fix_os_path(os.getenv("PATH"))
        })

    @staticmethod
    def _fix_os_path(path):
        return (re.sub(r"[\\]+", '\\' * 4, path)
                if "windows" in util.get_systype() else path)
