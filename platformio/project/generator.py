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
from os.path import (abspath, basename, dirname, expanduser, isdir, isfile,
                     join, relpath)

from platformio import app, exception, util
from platformio.managers.platform import PlatformManager
from platformio.project.config import ProjectConfig
from platformio.project.template import ProjectTemplateFactory


class ProjectGenerator(object):

    CONFIG_NAME = "platformio.ini"

    def __init__(self, project_dir, options=None):
        self.project_dir = project_dir
        self.options = options or {}

        self._project_lib_dir = None
        self._project_src_dir = None

        # Will be set to the first used env name
        # Can be used later for IDE Generator
        self._main_env_name = None

        self.project_config = self.init_config()

    def init_config(self):
        config = ProjectConfig(join(self.project_dir, self.CONFIG_NAME))
        pm = PlatformManager()
        env_prefix = str(self.options['env_prefix'] or "")

        for bid in self.options['boards']:
            env_name = "%s%s" % (env_prefix, bid)
            board_config = pm.board_config(bid, self.options['platform'])
            env_options = [("platform", self.options['platform']
                            or board_config['platform'])]
            board_frameworks = board_config.get("frameworks", [])
            env_framework = self.options['framework']
            if env_framework is None and board_frameworks:
                env_framework = board_frameworks[0]
            if env_framework and env_framework not in board_frameworks:
                raise exception.PlatformioException(
                    "Board `%s` is not compatible with framework %s" %
                    (bid, env_framework))
            if env_framework:
                env_options.append(("framework", env_framework))
            env_options.append(("board", bid))

            # extra env options
            for item in self.options['env_options']:
                _name, _value = item.split("=", 1)
                env_options.append((_name.strip(), _value.strip()))

            # FIXME: Check [platformio] -> env_default
            if not self._main_env_name:
                self._main_env_name = env_name

            config.env_update(env_name, env_options)

        if not self._main_env_name:
            env_names = config.get_env_names()
            if env_names:
                self._main_env_name = env_names[0]

        return config

    @staticmethod
    def get_supported_ide():
        return sorted([
            key[4:] for key in ProjectTemplateFactory.get_templates()
            if key.startswith("ide.")
        ])

    @staticmethod
    def get_supported_vcs():
        return sorted([
            key[4:] for key in ProjectTemplateFactory.get_templates()
            if key.startswith("vcs.")
        ])

    @staticmethod
    def get_supported_ci():
        return sorted([
            key[3:] for key in ProjectTemplateFactory.get_templates()
            if key.startswith("ci.")
        ])

    @staticmethod
    def fix_os_path(path):
        return (re.sub(r"[\\]+", '\\' * 4, path)
                if "windows" in util.get_systype() else path)

    def get_src_files(self):
        assert self._project_src_dir
        result = []
        with util.cd(self.project_dir):
            for root, _, files in os.walk(self._project_src_dir):
                for f in files:
                    result.append(relpath(join(root, f)))

    def generate(self):
        lib_dir, src_dir = self._init_file_structure()
        self._project_lib_dir = lib_dir
        self._project_src_dir = src_dir

        self._init_lib_readme(lib_dir)

        if self.options['template']:
            self._process_user_template(self.options['template'],
                                        self.options['template_vars'])

        self.project_config.write()

        if self.options['vcs']:
            self._process_vcs_template(self.options['vcs'])
        if self.options['ci']:
            self._process_ci_template(self.options['ci'])
        if self.options['ide']:
            self._process_ide_template(self.options['ide'])

    def _init_file_structure(self):
        with util.cd(self.project_dir):
            result = (util.get_projectlib_dir(), util.get_projectsrc_dir())
            for d in result:
                if not isdir(d):
                    os.makedirs(d)
            return result

    def _process_user_template(self, name, variables):
        pt = ProjectTemplateFactory.new("src.%s" % name, self.project_config)
        for variable in variables:
            assert "=" in variable, \
                "Template Variable format is `name=value` pair"
            pt.assign(*variable.split("=", 1))

        assert pt.is_compatible(raise_errors=True)
        assert pt.validate_variables()

        for location, content in pt.render():
            self.write_content(location, content)

        return True

    def _process_vcs_template(self, name):
        pt = ProjectTemplateFactory.new("vcs.%s" % name, self.project_config)
        assert pt.is_compatible(raise_errors=True)
        for location, content in pt.render():
            self.write_content(location, content)
        return True

    def _process_ci_template(self, name):
        pt = ProjectTemplateFactory.new("ci.%s" % name, self.project_config)
        assert pt.is_compatible(raise_errors=True)
        for location, content in pt.render():
            self.write_content(location, content)
        return True

    def _process_ide_template(self, ide):
        if not self._main_env_name:
            raise exception.BoardNotDefined()

        pt = ProjectTemplateFactory.new("ide.%s" % ide, self.project_config)

        # system
        pt.assign("systype", util.get_systype())
        pt.assign("env_pathsep", os.pathsep)
        pt.assign("env_path", self.fix_os_path(os.getenv("PATH")))
        pt.assign("user_home_dir", abspath(expanduser("~")))
        pt.assign("platformio_path",
                  self.fix_os_path(util.where_is_program("platformio")))
        # project
        pt.assign("project_name", basename(self.project_dir))
        pt.assign("project_dir", self.project_dir)
        pt.assign("project_src_dir", self._project_src_dir)
        pt.assign("src_files", self.get_src_files())

        # project build environment
        for name, value in self._dump_build_env(self._main_env_name).items():
            pt.assign(name, value)

        assert pt.is_compatible(raise_errors=True)
        assert pt.validate_variables()

        for location, content in pt.render():
            self.write_content(location, content)

        return True

    def _dump_build_env(self, env_name):
        data = {"defines": [], "includes": [], "cxx_path": None}
        cmd = [util.get_pythonexe_path(), "-m", "platformio", "-f"]
        if app.get_session_var("caller_id"):
            cmd.extend(["-c", app.get_session_var("caller_id")])
        cmd.extend(["run", "-t", "idedata", "-e", env_name])
        cmd.extend(["-d", self.project_dir])
        result = util.exec_command(cmd)

        if result['returncode'] != 0 or '"includes":' not in result['out']:
            raise exception.PlatformioException(
                "\n".join([result['out'], result['err']]))

        for line in result['out'].split("\n"):
            line = line.strip()
            if line.startswith('{"') and '"cxx_path"' in line:
                data = json.loads(line[:line.rindex("}") + 1])
        return data

    def write_content(self, location, content):
        for name in ("project_dir", "lib_dir", "src_dir"):
            pattern = "%%%s%%" % name
            if pattern not in location:
                continue
            location = location.replace(pattern, self.project_dir
                                        if name == "project_dir" else getattr(
                                            self, "_project_%s" % name))
        if not isdir(dirname(location)):
            os.makedirs(dirname(location))
        with open(join(location), "w") as fp:
            fp.write(content.encode("utf8"))

    @staticmethod
    def _init_lib_readme(lib_dir):
        if isfile(join(lib_dir, "readme.txt")):
            return
        with open(join(lib_dir, "readme.txt"), "w") as f:
            f.write(
                """This directory is intended for the project specific (private) libraries.
PlatformIO will compile them to static libraries and link to executable file.

The source code of each library should be placed in separate directory, like
"lib/private_lib/[here are source files]".

For example, see how can be organized `Foo` and `Bar` libraries:

|--lib
|  |--Bar
|  |  |--docs
|  |  |--examples
|  |  |--src
|  |     |- Bar.c
|  |     |- Bar.h
|  |--Foo
|  |  |- Foo.c
|  |  |- Foo.h
|  |- readme.txt --> THIS FILE
|- platformio.ini
|--src
   |- main.cpp

Then in `src/main.cpp` you should use:

#include <Foo.h>
#include <Bar.h>

// rest H/C/CPP code

PlatformIO will find your libraries automatically, configure preprocessor's
include paths and build them.

More information about PlatformIO Library Dependency Finder
- http://docs.platformio.org/page/librarymanager/ldf.html
""")
