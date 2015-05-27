# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import json
from glob import glob
from os import listdir, walk
from os.path import basename, isdir, join

import bottle

from platformio import util


class ProjectGenerator(object):

    def __init__(self, project_dir, ide):
        self.project_dir = project_dir
        self.ide = ide
        self._tplvars = {}

        self._gather_tplvars()

    @staticmethod
    def get_supported_ides():
        tpls_dir = join(util.get_source_dir(), "ide", "tpls")
        return sorted([d for d in listdir(tpls_dir)
                       if isdir(join(tpls_dir, d))])

    def get_project_env(self):
        data = {"env_name": "PlatformIO"}
        with util.cd(self.project_dir):
            config = util.get_project_config()
            for section in config.sections():
                if not section.startswith("env:"):
                    continue
                data['env_name'] = section[4:]
                for k, v in config.items(section):
                    data[k] = v
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

    @staticmethod
    def get_srcfiles():
        result = []
        for root, _, files in walk(util.get_projectsrc_dir()):
            for f in files:
                result.append(join(root, f))
        return result

    def get_tpls(self):
        tpls_dir = join(util.get_source_dir(), "ide", "tpls", self.ide)
        return glob(join(tpls_dir, ".*.tpl")) + glob(join(tpls_dir, "*.tpl"))

    def generate(self):
        for tpl_path in self.get_tpls():
            file_name = basename(tpl_path)[:-4]
            with open(join(self.project_dir, file_name), "w") as f:
                f.write(self._render_tpl(tpl_path).encode("utf8"))

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
            "project_dir": self.project_dir
        })
