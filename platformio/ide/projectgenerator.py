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
import re
import sys
from os.path import abspath, basename, expanduser, isdir, isfile, join, relpath

import bottle

from platformio import util
from platformio.compat import WINDOWS, get_file_contents
from platformio.proc import where_is_program
from platformio.project.config import ProjectConfig
from platformio.project.helpers import (get_project_lib_dir,
                                        get_project_libdeps_dir,
                                        get_project_src_dir,
                                        load_project_ide_data)


class ProjectGenerator(object):

    def __init__(self, project_dir, ide, env_name):
        self.project_dir = project_dir
        self.ide = str(ide)
        self.env_name = str(env_name)

    @staticmethod
    def get_supported_ides():
        tpls_dir = join(util.get_source_dir(), "ide", "tpls")
        return sorted(
            [d for d in os.listdir(tpls_dir) if isdir(join(tpls_dir, d))])

    def _load_tplvars(self):
        tpl_vars = {"env_name": self.env_name}
        # default env configuration
        tpl_vars.update(
            ProjectConfig.get_instance(join(
                self.project_dir, "platformio.ini")).items(env=self.env_name,
                                                           as_dict=True))
        # build data
        tpl_vars.update(
            load_project_ide_data(self.project_dir, self.env_name) or {})

        with util.cd(self.project_dir):
            tpl_vars.update({
                "project_name": basename(self.project_dir),
                "src_files": self.get_src_files(),
                "user_home_dir": abspath(expanduser("~")),
                "project_dir": self.project_dir,
                "project_src_dir": get_project_src_dir(),
                "project_lib_dir": get_project_lib_dir(),
                "project_libdeps_dir": join(
                    get_project_libdeps_dir(), self.env_name),
                "systype": util.get_systype(),
                "platformio_path": self._fix_os_path(
                    sys.argv[0] if isfile(sys.argv[0])
                    else where_is_program("platformio")),
                "env_pathsep": os.pathsep,
                "env_path": self._fix_os_path(os.getenv("PATH"))
            })  # yapf: disable
        return tpl_vars

    @staticmethod
    def _fix_os_path(path):
        return (re.sub(r"[\\]+", '\\' * 4, path) if WINDOWS else path)

    def get_src_files(self):
        result = []
        with util.cd(self.project_dir):
            for root, _, files in os.walk(get_project_src_dir()):
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
        return bottle.template(get_file_contents(tpl_path), **tpl_vars)

    @staticmethod
    def _merge_contents(dst_path, contents):
        if basename(dst_path) == ".gitignore" and isfile(dst_path):
            return
        with codecs.open(dst_path, "w", encoding="utf8") as fp:
            fp.write(contents)
