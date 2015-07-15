# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from os import listdir, makedirs, walk
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
        return sorted([d for d in listdir(tpls_dir)
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
        envdata = self.get_project_env()
        if "env_name" not in envdata:
            return None
        result = util.exec_command(
            ["platformio", "run", "-t", "idedata", "-e", envdata['env_name'],
             "--project-dir", self.project_dir]
        )
        if result['returncode'] != 0 or '{"includes":' not in result['out']:
            return None

        output = result['out']
        try:
            start_index = output.index('\n{"includes":')
            stop_index = output.rindex('}')
            return json.loads(output[start_index + 1:stop_index + 1])
        except ValueError:
            pass

        return None

    def get_project_name(self):
        return basename(self.project_dir)

    def get_srcfiles(self):
        result = []
        with util.cd(self.project_dir):
            for root, _, files in walk(util.get_projectsrc_dir()):
                for f in files:
                    result.append(relpath(join(root, f)))
        return result

    def get_tpls(self):
        tpls = []
        tpls_dir = join(util.get_source_dir(), "ide", "tpls", self.ide)
        for root, _, files in walk(tpls_dir):
            for f in files:
                if f.endswith(".tpl"):
                    tpls.append((
                        root.replace(tpls_dir, ""), join(root, f)))
        return tpls

    def generate(self):
        for _relpath, _path in self.get_tpls():
            tpl_dir = self.project_dir
            if _relpath:
                tpl_dir = join(self.project_dir, _relpath)[1:]
                if not isdir(tpl_dir):
                    makedirs(tpl_dir)

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

        build_data = self.get_project_build_data()

        self._tplvars.update({
            "project_name": self.get_project_name(),
            "includes": (build_data['includes']
                         if build_data and "includes" in build_data else []),
            "defines": (build_data['defines']
                        if build_data and "defines" in build_data else []),
            "srcfiles": self.get_srcfiles(),
            "user_home_dir": abspath(expanduser("~")),
            "project_dir": self.project_dir
        })
