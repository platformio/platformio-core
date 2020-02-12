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

import codecs
import os
import sys
from os.path import basename, isdir, isfile, join, realpath, relpath

import bottle

from platformio import fs, util
from platformio.proc import where_is_program
from platformio.project.config import ProjectConfig
from platformio.project.helpers import load_project_ide_data


class ProjectGenerator(object):
    def __init__(self, project_dir, ide, boards):
        self.config = ProjectConfig.get_instance(join(project_dir, "platformio.ini"))
        self.config.validate()
        self.project_dir = project_dir
        self.ide = str(ide)
        self.env_name = str(self.get_best_envname(boards))

    @staticmethod
    def get_supported_ides():
        tpls_dir = join(fs.get_source_dir(), "ide", "tpls")
        return sorted([d for d in os.listdir(tpls_dir) if isdir(join(tpls_dir, d))])

    def get_best_envname(self, boards=None):
        envname = None
        default_envs = self.config.default_envs()
        if default_envs:
            envname = default_envs[0]
            if not boards:
                return envname

        for env in self.config.envs():
            if not boards:
                return env
            if not envname:
                envname = env
            items = self.config.items(env=env, as_dict=True)
            if "board" in items and items.get("board") in boards:
                return env

        return envname

    def _load_tplvars(self):
        tpl_vars = {
            "config": self.config,
            "systype": util.get_systype(),
            "project_name": basename(self.project_dir),
            "project_dir": self.project_dir,
            "env_name": self.env_name,
            "user_home_dir": realpath(fs.expanduser("~")),
            "platformio_path": sys.argv[0]
            if isfile(sys.argv[0])
            else where_is_program("platformio"),
            "env_path": os.getenv("PATH"),
            "env_pathsep": os.pathsep,
        }

        # default env configuration
        tpl_vars.update(self.config.items(env=self.env_name, as_dict=True))
        # build data
        tpl_vars.update(load_project_ide_data(self.project_dir, self.env_name) or {})

        with fs.cd(self.project_dir):
            tpl_vars.update(
                {
                    "src_files": self.get_src_files(),
                    "project_src_dir": self.config.get_optional_dir("src"),
                    "project_lib_dir": self.config.get_optional_dir("lib"),
                    "project_libdeps_dir": join(
                        self.config.get_optional_dir("libdeps"), self.env_name
                    ),
                }
            )

        for key, value in tpl_vars.items():
            if key.endswith(("_path", "_dir")):
                tpl_vars[key] = fs.to_unix_path(value)
        for key in ("includes", "src_files", "libsource_dirs"):
            if key not in tpl_vars:
                continue
            tpl_vars[key] = [fs.to_unix_path(inc) for inc in tpl_vars[key]]

        tpl_vars["to_unix_path"] = fs.to_unix_path
        return tpl_vars

    def get_src_files(self):
        result = []
        with fs.cd(self.project_dir):
            for root, _, files in os.walk(self.config.get_optional_dir("src")):
                for f in files:
                    result.append(relpath(join(root, f)))
        return result

    def get_tpls(self):
        tpls = []
        tpls_dir = join(fs.get_source_dir(), "ide", "tpls", self.ide)
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
        tpl_vars = self._load_tplvars()
        for tpl_relpath, tpl_path in self.get_tpls():
            dst_dir = self.project_dir
            if tpl_relpath:
                dst_dir = join(self.project_dir, tpl_relpath)
                if not isdir(dst_dir):
                    os.makedirs(dst_dir)
            file_name = basename(tpl_path)[:-4]
            contents = self._render_tpl(tpl_path, tpl_vars)
            self._merge_contents(join(dst_dir, file_name), contents)

    @staticmethod
    def _render_tpl(tpl_path, tpl_vars):
        with codecs.open(tpl_path, "r", encoding="utf8") as fp:
            return bottle.SimpleTemplate(fp.read()).render(**tpl_vars)

    @staticmethod
    def _merge_contents(dst_path, contents):
        if basename(dst_path) == ".gitignore" and isfile(dst_path):
            return
        with codecs.open(dst_path, "w", encoding="utf8") as fp:
            fp.write(contents)
