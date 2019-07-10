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
import json
import os
import re
from os.path import isfile

import click

from platformio import exception
from platformio.project.options import ProjectOptions

try:
    import ConfigParser as ConfigParser
except ImportError:
    import configparser as ConfigParser

CONFIG_HEADER = """;PlatformIO Project Configuration File
;
;   Build options: build flags, source filter
;   Upload options: custom upload port, speed and extra flags
;   Library options: dependencies, extra library storages
;   Advanced options: extra scripting
;
; Please visit documentation for the other options and examples
; https://docs.platformio.org/page/projectconf.html

"""


class ProjectConfig(object):

    INLINE_COMMENT_RE = re.compile(r"\s+;.*$")
    VARTPL_RE = re.compile(r"\$\{([^\.\}]+)\.([^\}]+)\}")

    expand_interpolations = True
    warnings = []

    _instances = {}
    _parser = None
    _parsed = []

    @staticmethod
    def parse_multi_values(items):
        result = []
        if not items:
            return result
        if not isinstance(items, (list, tuple)):
            items = items.split("\n" if "\n" in items else ", ")
        for item in items:
            item = item.strip()
            # comment
            if not item or item.startswith((";", "#")):
                continue
            if ";" in item:
                item = ProjectConfig.INLINE_COMMENT_RE.sub("", item).strip()
            result.append(item)
        return result

    @staticmethod
    def get_instance(path):
        if path not in ProjectConfig._instances:
            ProjectConfig._instances[path] = ProjectConfig(path)
        return ProjectConfig._instances[path]

    @staticmethod
    def reset_instances():
        ProjectConfig._instances = {}

    def __init__(self, path, parse_extra=True, expand_interpolations=True):
        self.path = path
        self.expand_interpolations = expand_interpolations
        self.warnings = []
        self._parsed = []
        self._parser = ConfigParser.ConfigParser()
        if isfile(path):
            self.read(path, parse_extra)

    def __getattr__(self, name):
        return getattr(self._parser, name)

    def read(self, path, parse_extra=True):
        if path in self._parsed:
            return
        self._parsed.append(path)
        try:
            self._parser.read(path)
        except ConfigParser.Error as e:
            raise exception.InvalidProjectConf(path, str(e))

        if not parse_extra:
            return

        # load extra configs
        for pattern in self.get("platformio", "extra_configs", []):
            for item in glob.glob(pattern):
                self.read(item)

        self._maintain_renaimed_options()

    def _maintain_renaimed_options(self):
        # legacy `lib_extra_dirs` in [platformio]
        if (self._parser.has_section("platformio")
                and self._parser.has_option("platformio", "lib_extra_dirs")):
            if not self._parser.has_section("env"):
                self._parser.add_section("env")
            self._parser.set("env", "lib_extra_dirs",
                             self._parser.get("platformio", "lib_extra_dirs"))
            self._parser.remove_option("platformio", "lib_extra_dirs")
            self.warnings.append(
                "`lib_extra_dirs` configuration option is deprecated in "
                "section [platformio]! Please move it to global `env` section")

        renamed_options = {}
        for option in ProjectOptions.values():
            if option.oldnames:
                renamed_options.update(
                    {name: option.name
                     for name in option.oldnames})

        for section in self._parser.sections():
            scope = section.split(":", 1)[0]
            if scope not in ("platformio", "env"):
                continue
            for option in self._parser.options(section):
                if option in renamed_options:
                    self.warnings.append(
                        "`%s` configuration option in section [%s] is "
                        "deprecated and will be removed in the next release! "
                        "Please use `%s` instead" %
                        (option, section, renamed_options[option]))
                    # rename on-the-fly
                    self._parser.set(section, renamed_options[option],
                                     self._parser.get(section, option))
                    self._parser.remove_option(section, option)
                    continue

                # unknown
                unknown_conditions = [
                    ("%s.%s" % (scope, option)) not in ProjectOptions,
                    scope != "env" or
                    not option.startswith(("custom_", "board_"))
                ]  # yapf: disable
                if all(unknown_conditions):
                    self.warnings.append(
                        "Ignore unknown configuration option `%s` "
                        "in section [%s]" % (option, section))
        return True

    def options(self, section=None, env=None):
        assert section or env
        if not section:
            section = "env:" + env
        options = self._parser.options(section)

        # handle global options from [env]
        if ((env or section.startswith("env:"))
                and self._parser.has_section("env")):
            for option in self._parser.options("env"):
                if option not in options:
                    options.append(option)

        # handle system environment variables
        scope = section.split(":", 1)[0]
        for option_meta in ProjectOptions.values():
            if option_meta.scope != scope or option_meta.name in options:
                continue
            if option_meta.sysenvvar and option_meta.sysenvvar in os.environ:
                options.append(option_meta.name)

        return options

    def has_option(self, section, option):
        if self._parser.has_option(section, option):
            return True
        return (section.startswith("env:") and self._parser.has_section("env")
                and self._parser.has_option("env", option))

    def items(self, section=None, env=None, as_dict=False):
        assert section or env
        if not section:
            section = "env:" + env
        if as_dict:
            return {
                option: self.get(section, option)
                for option in self.options(section)
            }
        return [(option, self.get(section, option))
                for option in self.options(section)]

    def set(self, section, option, value):
        if isinstance(value, (list, tuple)):
            value = "\n".join(value)
            if value:
                value = "\n" + value  # start from a new line
        self._parser.set(section, option, value)

    def getraw(self, section, option):
        if not self.expand_interpolations:
            return self._parser.get(section, option)

        try:
            value = self._parser.get(section, option)
        except ConfigParser.NoOptionError as e:
            if not section.startswith("env:"):
                raise e
            value = self._parser.get("env", option)

        if "${" not in value or "}" not in value:
            return value
        return self.VARTPL_RE.sub(self._re_interpolation_handler, value)

    def _re_interpolation_handler(self, match):
        section, option = match.group(1), match.group(2)
        if section == "sysenv":
            return os.getenv(option)
        return self.getraw(section, option)

    def get(self, section, option, default=None):
        value = None
        try:
            value = self.getraw(section, option)
        except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
            pass  # handle value from system environment
        except ConfigParser.Error as e:
            raise exception.InvalidProjectConf(self.path, str(e))

        option_meta = ProjectOptions.get("%s.%s" %
                                         (section.split(":", 1)[0], option))
        if not option_meta:
            return value or default

        if option_meta.multiple:
            value = self.parse_multi_values(value)

        if option_meta.sysenvvar:
            envvar_value = os.getenv(option_meta.sysenvvar)
            if not envvar_value and option_meta.oldnames:
                for oldoption in option_meta.oldnames:
                    envvar_value = os.getenv("PLATFORMIO_" + oldoption.upper())
                    if envvar_value:
                        break
            if envvar_value and option_meta.multiple:
                value = value or []
                value.extend(self.parse_multi_values(envvar_value))
            elif envvar_value and not value:
                value = envvar_value

        # option is not specified by user
        if value is None:
            return default

        try:
            return self._covert_value(value, option_meta.type)
        except click.BadParameter as e:
            raise exception.ProjectOptionValueError(e.format_message(), option,
                                                    section)

    @staticmethod
    def _covert_value(value, to_type):
        items = value
        if not isinstance(value, (list, tuple)):
            items = [value]
        items = [
            to_type(item) if isinstance(to_type, click.ParamType) else item
            for item in items
        ]
        return items if isinstance(value, (list, tuple)) else items[0]

    def envs(self):
        return [s[4:] for s in self._parser.sections() if s.startswith("env:")]

    def default_envs(self):
        return self.get("platformio", "default_envs", [])

    def validate(self, envs=None, silent=False):
        if not isfile(self.path):
            raise exception.NotPlatformIOProject(self.path)
        # check envs
        known = set(self.envs())
        if not known:
            raise exception.ProjectEnvsNotAvailable()
        unknown = set(list(envs or []) + self.default_envs()) - known
        if unknown:
            raise exception.UnknownEnvNames(", ".join(unknown),
                                            ", ".join(known))
        if not silent:
            for warning in self.warnings:
                click.secho("Warning! %s" % warning, fg="yellow")
        return True

    def to_json(self):
        result = {}
        for section in self.sections():
            result[section] = self.items(section, as_dict=True)
        return json.dumps(result)

    def save(self, path=None):
        with open(path or self.path, "w") as fp:
            fp.write(CONFIG_HEADER)
            self._parser.write(fp)
