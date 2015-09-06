# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
import os
import re
from os.path import abspath, basename, expanduser, isdir, join, relpath

import bottle

from platformio import util


class ProjectGenerator(object):

    def __init__(self, project_dir, ide, board=None):
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
                if self.board and self.board == data.get("board"):
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
        result = util.exec_command(
            ["platformio", "-f", "run", "-t", "idedata",
             "-e", envdata['env_name'], "-d", self.project_dir]
        )
        if result['returncode'] != 0 or '"includes":' not in result['out']:
            return data

        output = result['out']
        try:
            start_index = output.index('\n{"')
            stop_index = output.rindex('}')
            data = json.loads(output[start_index + 1:stop_index + 1])
        except ValueError:
            pass

        return data

    def get_project_name(self):
        return basename(self.project_dir)

    def get_srcfiles(self):
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
        self._tplvars.update(self.get_project_env())
        self._tplvars.update(self.get_project_build_data())
        self._tplvars.update({
            "project_name": self.get_project_name(),
            "srcfiles": self.get_srcfiles(),
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
