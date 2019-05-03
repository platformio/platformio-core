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

import glob
import os
import re

import click

from platformio import exception

try:
    import ConfigParser as ConfigParser
except ImportError:
    import configparser as ConfigParser


class ProjectConfig(object):

    VARTPL_RE = re.compile(r"\$\{([^\.\}]+)\.([^\}]+)\}")

    _parser = None
    _parsed = []

    @staticmethod
    def parse_multi_values(items):
        result = []
        if not items:
            return result
        inline_comment_re = re.compile(r"\s+;.*$")
        for item in items.split("\n" if "\n" in items else ", "):
            item = item.strip()
            # comment
            if not item or item.startswith((";", "#")):
                continue
            if ";" in item:
                item = inline_comment_re.sub("", item).strip()
            result.append(item)
        return result

    def __init__(self, path):
        self.path = path
        self._parsed = []
        self._parser = ConfigParser.ConfigParser()
        self.read(path)

    def read(self, path):
        if path in self._parsed:
            return
        self._parsed.append(path)
        try:
            self._parser.read(path)
        except ConfigParser.Error as e:
            raise exception.InvalidProjectConf(path, str(e))

        # load extra configs
        if (not self._parser.has_section("platformio")
                or not self._parser.has_option("platformio", "extra_configs")):
            return
        extra_configs = self.parse_multi_values(
            self.get("platformio", "extra_configs"))
        for pattern in extra_configs:
            for item in glob.glob(pattern):
                self.read(item)

    def __getattr__(self, name):
        return getattr(self._parser, name)

    def items(self, section):
        items = []
        for option in self._parser.options(section):
            items.append((option, self._parser.get(section, option)))
        return items

    def get(self, section, option):
        try:
            value = self._parser.get(section, option)
        except ConfigParser.Error as e:
            raise exception.InvalidProjectConf(self.path, str(e))
        if "${" not in value or "}" not in value:
            return value
        return self.VARTPL_RE.sub(self._re_sub_handler, value)

    def _re_sub_handler(self, match):
        section, option = match.group(1), match.group(2)
        if section in ("env",
                       "sysenv") and not self._parser.has_section(section):
            if section == "env":
                click.secho(
                    "Warning! Access to system environment variable via "
                    "`${{env.{0}}}` is deprecated. Please use "
                    "`${{sysenv.{0}}}` instead".format(option),
                    fg="yellow")
            return os.getenv(option)
        return self._parser.get(section, option)
