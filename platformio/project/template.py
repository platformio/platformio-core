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

import inspect
import os
from imp import load_source
from os.path import dirname, isdir, isfile, join, relpath, sep

import bottle

from platformio import exception, util
from platformio.managers.core import get_core_package_dir


class ProjectTemplateFactory(object):

    MANIFEST_NAME = "template.py"

    @classmethod
    @util.memoized
    def get_templates(cls):
        pkg_dir = get_core_package_dir("contrib-projecttpls")
        assert pkg_dir
        items = {}
        for root, _, _ in os.walk(pkg_dir):
            if isfile(join(root, cls.MANIFEST_NAME)):
                key = relpath(root, pkg_dir).replace(sep, ".")
                items[key] = root
        return items

    @staticmethod
    def load_module(key, path):
        module = None
        try:
            module = load_source(
                "platformio.project.template.%s" % key.replace(".", "_"), path)
        except ImportError:
            raise exception.UnknownProjectTemplate(key)
        return module

    @classmethod
    def new(cls, key, project_config):
        if key not in cls.get_templates():
            raise exception.UnknownProjectTemplate(key)
        template_py = join(cls.get_templates()[key], cls.MANIFEST_NAME)
        for _, _class in inspect.getmembers(
                cls.load_module(key, template_py), inspect.isclass):
            if issubclass(_class, ProjectTemplateBase):
                return _class(project_config)

        raise exception.UnknownProjectTemplate(key)


class ProjectTemplateBase(object):

    TITLE = None
    DESCRIPTION = None

    COMPATIBLE_PLATFORMS = None
    COMPATIBLE_BOARDS = None
    COMPATIBLE_FRAMEWORKS = None

    VARIABLES = None
    CONTENTS = None

    def __init__(self, project_config):
        self.project_config = project_config
        self.project_dir = dirname(project_config.path)

    def get_title(self):
        return self.TITLE or self.__class__.__name__

    def get_description(self):
        return self.DESCRIPTION or self.get_title()

    def get_compatible_platforms(self):
        return self.COMPATIBLE_PLATFORMS or []

    def get_compatible_boards(self):
        return self.COMPATIBLE_BOARDS or []

    def get_compatible_frameworks(self):
        return self.COMPATIBLE_FRAMEWORKS or []

    def get_variables(self):
        return self.VARIABLES or []

    def get_contents(self):
        return self.CONTENTS or []

    def assign(self, name, value):
        found = False
        for var in self.get_variables():
            if var.name == name:
                var.set_value(value)
                found = True
        if not found:
            raise exception.UnknownProjectTplVar(name)

    def is_compatible(self, raise_errors=False):
        options = self.project_config.dump_all_options()
        name_candidates = dict(
            platform=set(self.get_compatible_platforms()),
            board=set(self.get_compatible_boards()),
            framework=set(self.get_compatible_frameworks()))
        for name, candidates in name_candidates.items():
            if not candidates:
                continue
            diff = set(options.get(name, [])) - candidates
            if name not in options or diff:
                if raise_errors:
                    raise exception.IncompatbileProjectTemplate(
                        self.get_title(), name, ", ".join(diff),
                        ", ".join(candidates))
                return False
        return True

    def validate_variables(self):
        return all([v.validate() for v in self.get_variables()])

    def render(self):
        items = []
        data = dict(__project_config=self.project_config)
        data.update({v.name: v.get_value() for v in self.get_variables()})
        for item in self.get_contents():
            result = self.render_content(item, data)
            if result:
                items.append(result)
        return items

    @staticmethod
    def render_content(item, data):
        return (item.location, item.render(data))


#
# Template Contents
#


class ProjectTplContentBase(object):

    def __init__(self, content, location):
        self.content = content
        self.location = location

    def render(self, data):
        content = self.content
        if isfile(content):
            with open(content) as fp:
                content = fp.read()
        return bottle.template(self.content, **data)


class ProjectTplRootContent(ProjectTplContentBase):

    def __init__(self, content, location):
        super(ProjectTplRootContent,
              self).__init__(content, join("%project_dir%", location))


class ProjectTplSrcContent(ProjectTplContentBase):

    def __init__(self, content, location):
        super(ProjectTplSrcContent, self).__init__(content,
                                                   join("%src_dir%", location))


class ProjectTplLibContent(ProjectTplContentBase):

    def __init__(self, content, location):
        super(ProjectTplLibContent, self).__init__(content,
                                                   join("%lib_dir%", location))


#
# Template Variables
#


class ProjectTplVarBase(object):

    TYPE = None

    def __init__(self,  # pylint: disable=too-many-arguments
                 name,
                 title=None,
                 description=None,
                 default=None,
                 options=None):
        self.name = name
        self.title = title
        self.description = description
        self.default = default
        self.options = options or {}
        self._value = None

    @property
    def type(self):
        return self.TYPE

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value or self.default

    def validate(self):
        try:
            value = self.get_value()
            if "min" in self.options:
                assert value >= self.options['min']
            if "max" in self.options:
                assert value <= self.options['max']
            if "enum" in self.options:
                assert value in self.options['enum']
        except AssertionError:
            raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                                 self.type, self.options)


class ProjectTplVarString(ProjectTplVarBase):

    TYPE = "string"

    def validate(self):
        try:
            self.set_value(str(self.get_value()))
            super(ProjectTplVarString, self).validate()
        except ValueError:
            raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                                 self.type, self.options)
        return True


class ProjectTplVarInteger(ProjectTplVarBase):

    TYPE = "integer"

    def validate(self):
        try:
            self.set_value(int(self.get_value()))
            super(ProjectTplVarInteger, self).validate()
        except ValueError:
            raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                                 self.type, self.options)
        return True


class ProjectTplVarNumber(ProjectTplVarBase):

    TYPE = "number"

    def validate(self):
        try:
            self.set_value(float(self.get_value()))
            super(ProjectTplVarNumber, self).validate()
        except ValueError:
            raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                                 self.type, self.options)
        return True


class ProjectTplVarBoolean(ProjectTplVarBase):

    TYPE = "boolean"

    def validate(self):
        try:
            value = self.get_value()
            if not isinstance(value, bool):
                value = str(value).lower()
                assert value in ("1", "0", "true", "false", "yes", "no")
                value = bool(value in ("1", "true", "yes"))
                self.set_value(value)
            super(ProjectTplVarBoolean, self).validate()
        except (AssertionError, ValueError):
            raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                                 self.type, self.options)
        return True


class ProjectTplVarArray(ProjectTplVarBase):

    TYPE = "array"

    def validate(self):
        try:
            value = self.get_value()
            if not isinstance(value, list):
                value = str(value).split(", ")
                self.set_value(value)
            if "enum" in self.options:
                assert set(self.options['enum']) >= set(value)
        except (AssertionError, ValueError):
            raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                                 self.type, self.options)
        return True


class ProjectTplVarFilePath(ProjectTplVarBase):

    TYPE = "file"

    def validate(self):
        if isfile(self.get_value()):
            return True
        raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                             self.type, self.options)


class ProjectTplVarDirPath(ProjectTplVarBase):

    TYPE = "directory"

    def validate(self):
        if isdir(self.get_value()):
            return True
        raise exception.InvalidProjectTplVar(self.get_value(), self.name,
                                             self.type, self.options)


#
# Base IDE template
#


class IDEProjectTemplateBase(ProjectTemplateBase):

    VARIABLES = [
        # system
        ProjectTplVarString("systype"),
        ProjectTplVarString("env_pathsep"),
        ProjectTplVarString("env_path"),
        ProjectTplVarDirPath("user_home_dir"),
        ProjectTplVarFilePath("platformio_path"),

        # project
        ProjectTplVarString("project_name"),
        ProjectTplVarDirPath("project_dir"),
        ProjectTplVarDirPath("project_src_dir"),
        ProjectTplVarArray("src_files"),

        # project build environment
        ProjectTplVarString("prog_path"),
        ProjectTplVarFilePath("cc_path"),
        ProjectTplVarFilePath("cxx_path"),
        ProjectTplVarFilePath("gdb_path"),
        ProjectTplVarArray("defines"),
        ProjectTplVarArray("libsource_dirs"),
        ProjectTplVarArray("includes"),
        ProjectTplVarString("cc_flags"),
        ProjectTplVarString("cxx_flags")
    ]

    def render_content(self, item, data):
        dst_path = item.location.replace("%project_dir%", self.project_dir)
        conds = [
            item.location.endswith(".gitignore"),
            isfile(item.content),
            isfile(dst_path)
        ]
        if not all(conds):
            return super(IDEProjectTemplateBase, self).render_content(
                item, data)
        # merge .gitignore
        assert isfile(item.content)
        with open(item.content) as fp:
            content = fp.read()
        modified = False
        default = [l.strip() for l in content.split("\n")]
        with open(dst_path) as fp:
            current = [l.strip() for l in fp.readlines()]
        for d in default:
            if d and d not in current:
                modified = True
                current.append(d)
        if not modified:
            return
        return (item.location, "\n".join(current) + "\n")
