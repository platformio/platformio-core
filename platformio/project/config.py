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

import os
import re
from os.path import isfile

from configobj import ConfigObj


class ProjectConfig(object):

    INITIAL_COMMENT = """# PlatformIO Project Configuration File
#
#   Build options: build flags, source filter
#   Upload options: custom upload port, speed and extra flags
#   Library options: dependencies, extra library storages
#   Advanced options: extra scripting
#
# Please visit documentation for the other options and examples
# http://docs.platformio.org/page/projectconf.html
"""

    SEMICOLON_TO_SHARP_RE = re.compile(r"((^|\s+);)", re.M)
    SHARP_TO_SEMICOLON_RE = re.compile(r"((^|\s+)#)", re.M)
    STRIP_INLINE_COMMENT_RE = re.compile(r"(^|\s+)#.*", re.M)
    MLOPTS_PRE_RE = re.compile(r"^([\w]+)(\s*=[ \t\r\f\v]*)(\n[ \t]+[^\n]+)+",
                               re.M)
    MLOPTS_POST_RE = re.compile(r"^([\w]+)\s*=[ \t\r\f\v]*(''')([^\2]+)\2",
                                re.M)
    VARTPL_RE = re.compile(r"\$\{([^\.\}]+)\.([^\}]+)\}")

    def __init__(self, path):
        self.path = path
        self._parser = ConfigObj(
            self._load_lines(),
            interpolation=False,
            list_values=False,
            raise_errors=True)
        self._modified = False

    def _load_lines(self):
        if not isfile(self.path):
            return []
        content = ""
        with open(self.path, "r") as fp:
            content = fp.read()
        # ConfigObj doesn't support semicolons
        content = self.SEMICOLON_TO_SHARP_RE.sub(r"\2#", content)
        # Convert Python's multi-lines to ConfigObj's
        if "'''" not in content:
            content = self.MLOPTS_PRE_RE.sub(self._re_sub_mloptspre_handler,
                                             content)
        return content.split("\n")

    @staticmethod
    def _re_sub_mloptspre_handler(match):
        name = match.group(1)
        value = match.string[match.end(2):match.end(3)].strip()
        return "%s = '''%s'''" % (name, value)

    def write(self):
        if not self._modified:
            return
        self._parser.initial_comment = self.INITIAL_COMMENT.split("\n")
        with open(self.path, "w") as fp:
            self._parser.write(fp)
        self._post_hooks()

    def _post_hooks(self):
        with open(self.path, "r+") as fp:
            content = fp.read()
            fp.seek(0)
            fp.truncate()
            # ConfigObj doesn't support semicolons
            content = self.SHARP_TO_SEMICOLON_RE.sub(r"\2;", content)
            # convert ConfigObj's multi-lines to Python's
            content = self.MLOPTS_POST_RE.sub(self._re_sub_mloptspost_handler,
                                              content)
            fp.write(content)

    @staticmethod
    def _re_sub_mloptspost_handler(match):
        name = match.group(1)
        items = [i.strip() for i in match.group(3).split("\n") if i.strip()]
        return "%s = \n  %s" % (name, "\n  ".join(items))

    @property
    def parser(self):
        return self._parser

    def sections(self):
        return self._parser.keys()

    def add_section(self, section):
        self._parser[section] = {}

    def delete_section(self, section):
        if self.has_section(section):
            self._modified = True
            del self._parser[section]

    def has_section(self, section):
        return section in self._parser

    def options(self, section):
        return self._parser[section]

    def items(self, section):
        items = []
        for option in self.options(section):
            items.append((option, self.get(section, option)))
        return items

    def get(self, section, option):
        value = self._parser[section][option]
        if "${" in value and "}" in value:
            value = self.VARTPL_RE.sub(self._re_sub_vartpl_handler, value)
        # make a list from multi-lie values or which are separated via ", "
        for separator in ("\n", ", "):
            if separator not in value:
                return value
            result = []
            for line in value.split(separator):
                if "#" in line:
                    line = self.STRIP_INLINE_COMMENT_RE.sub("", line)
                line = line.strip()
                if line:
                    result.append(line)
            return result

    def _re_sub_vartpl_handler(self, match):
        section, option = match.group(1), match.group(2)
        if section == "env" and not self.has_section(section):
            return os.getenv(option)
        return self.get(section, option)

    def set(self, section, option, value):
        if not self.has_section(section):
            self.add_section(section)
        if self._parser[section].get(option) != value:
            self._modified = True
        self._parser[section][option] = value

    def get_env_names(self):
        return [s[4:] for s in self.sections() if s.startswith("env:")]

    def env_get(self, name, option, default=None):
        section = "env:%s" % name
        if self.has_section(section) and option in self._parser[section]:
            return self.get(section, option)
        return default

    def env_update(self, name, options):
        for option, value in options:
            self.set("env:%s" % name, option, value)
        return True

    def env_replace(self, name, options):
        self.delete_section("env:%s" % name)
        return self.env_update(name, options)

    def dump_all_options(self):
        result = {}
        for section in self.sections():
            if not section.startswith("env:"):
                continue
            for option in self.options(section):
                if option not in result:
                    result[option] = []
                result[option].append(self.get(section, option))
        return result
