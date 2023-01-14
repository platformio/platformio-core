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

import bottle

from platformio import fs, util
from platformio.proc import where_is_program
from platformio.project.helpers import load_build_metadata


class ProjectGenerator:
    def __init__(self, config, env_name, ide, board_ids=None):
        self.config = config
        self.project_dir = os.path.dirname(config.path)
        self.original_env_name = env_name
        self.env_name = str(env_name or self.get_best_envname(board_ids))
        self.ide = str(ide)

    def get_best_envname(self, board_ids=None):
        envname = None
        default_envs = self.config.default_envs()
        if default_envs:
            envname = default_envs[0]
            if not board_ids:
                return envname

        for env in self.config.envs():
            if not board_ids:
                return env
            if not envname:
                envname = env
            items = self.config.items(env=env, as_dict=True)
            if "board" in items and items.get("board") in board_ids:
                return env
        return envname

    @staticmethod
    def get_ide_tpls_dir():
        return os.path.join(fs.get_assets_dir(), "templates", "ide-projects")

    @classmethod
    def get_supported_ides(cls):
        tpls_dir = cls.get_ide_tpls_dir()
        return sorted(
            [
                name
                for name in os.listdir(tpls_dir)
                if os.path.isdir(os.path.join(tpls_dir, name))
            ]
        )

    @staticmethod
    def filter_includes(includes_map, ignore_scopes=None, to_unix_path=True):
        ignore_scopes = ignore_scopes or []
        result = []
        for scope, includes in includes_map.items():
            if scope in ignore_scopes:
                continue
            for include in includes:
                if to_unix_path:
                    include = fs.to_unix_path(include)
                if include not in result:
                    result.append(include)
        return result

    def _load_tplvars(self):
        tpl_vars = {
            "config": self.config,
            "systype": util.get_systype(),
            "project_name": self.config.get(
                "platformio", "name", os.path.basename(self.project_dir)
            ),
            "project_dir": self.project_dir,
            "original_env_name": self.original_env_name,
            "env_name": self.env_name,
            "user_home_dir": os.path.abspath(fs.expanduser("~")),
            "platformio_path": sys.argv[0]
            if os.path.isfile(sys.argv[0])
            else where_is_program("platformio"),
            "env_path": os.getenv("PATH"),
            "env_pathsep": os.pathsep,
        }

        # default env configuration
        tpl_vars.update(self.config.items(env=self.env_name, as_dict=True))
        # build data
        tpl_vars.update(load_build_metadata(self.project_dir, self.env_name) or {})

        with fs.cd(self.project_dir):
            tpl_vars.update(
                {
                    "src_files": self.get_src_files(),
                    "project_src_dir": self.config.get("platformio", "src_dir"),
                    "project_lib_dir": self.config.get("platformio", "lib_dir"),
                    "project_test_dir": self.config.get("platformio", "test_dir"),
                    "project_libdeps_dir": os.path.join(
                        self.config.get("platformio", "libdeps_dir"), self.env_name
                    ),
                }
            )

        for key, value in tpl_vars.items():
            if key.endswith(("_path", "_dir")):
                tpl_vars[key] = fs.to_unix_path(value)
        for key in ("src_files", "libsource_dirs"):
            if key not in tpl_vars:
                continue
            tpl_vars[key] = [fs.to_unix_path(inc) for inc in tpl_vars[key]]

        tpl_vars["to_unix_path"] = fs.to_unix_path
        tpl_vars["filter_includes"] = self.filter_includes
        return tpl_vars

    def get_src_files(self):
        result = []
        with fs.cd(self.project_dir):
            for root, _, files in os.walk(self.config.get("platformio", "src_dir")):
                for f in files:
                    result.append(
                        os.path.relpath(os.path.join(os.path.realpath(root), f))
                    )
        return result

    def get_tpls(self):
        tpls = []
        ide_tpls_dir = os.path.join(self.get_ide_tpls_dir(), self.ide)
        for root, _, files in os.walk(ide_tpls_dir):
            for f in files:
                if not f.endswith(".tpl"):
                    continue
                _relpath = root.replace(ide_tpls_dir, "")
                if _relpath.startswith(os.sep):
                    _relpath = _relpath[1:]
                tpls.append((_relpath, os.path.join(root, f)))
        return tpls

    def generate(self):
        tpl_vars = self._load_tplvars()
        for tpl_relpath, tpl_path in self.get_tpls():
            dst_dir = self.project_dir
            if tpl_relpath:
                dst_dir = os.path.join(self.project_dir, tpl_relpath)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
            file_name = os.path.basename(tpl_path)[:-4]
            contents = self._render_tpl(tpl_path, tpl_vars)
            self._merge_contents(os.path.join(dst_dir, file_name), contents)

    @staticmethod
    def _render_tpl(tpl_path, tpl_vars):
        with codecs.open(tpl_path, "r", encoding="utf8") as fp:
            return bottle.template(fp.read(), **tpl_vars)

    @staticmethod
    def _merge_contents(dst_path, contents):
        if os.path.basename(dst_path) == ".gitignore" and os.path.isfile(dst_path):
            return
        with codecs.open(dst_path, "w", encoding="utf8") as fp:
            fp.write(contents)
