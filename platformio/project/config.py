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

KNOWN_PLATFORMIO_OPTIONS = [
    "description",
    "env_default",
    "extra_configs",

    # Dirs
    "core_dir",
    "globallib_dir",
    "platforms_dir",
    "packages_dir",
    "cache_dir",
    "workspace_dir",
    "build_dir",
    "libdeps_dir",
    "lib_dir",
    "include_dir",
    "src_dir",
    "test_dir",
    "boards_dir",
    "data_dir"
]

KNOWN_ENV_OPTIONS = [
    # Generic
    "platform",
    "framework",
    "board",
    "targets",

    # Build
    "build_flags",
    "src_build_flags",
    "build_unflags",
    "src_filter",

    # Upload
    "upload_port",
    "upload_protocol",
    "upload_speed",
    "upload_flags",
    "upload_resetmethod",

    # Monitor
    "monitor_port",
    "monitor_speed",
    "monitor_rts",
    "monitor_dtr",
    "monitor_flags",

    # Library
    "lib_deps",
    "lib_ignore",
    "lib_extra_dirs",
    "lib_ldf_mode",
    "lib_compat_mode",
    "lib_archive",

    # Test
    "piotest",
    "test_filter",
    "test_ignore",
    "test_port",
    "test_speed",
    "test_transport",
    "test_build_project_src",

    # Debug
    "debug_tool",
    "debug_init_break",
    "debug_init_cmds",
    "debug_extra_cmds",
    "debug_load_cmd",
    "debug_load_mode",
    "debug_server",
    "debug_port",
    "debug_svd_path",

    # Other
    "extra_scripts"
]

RENAMED_OPTIONS = {
    "lib_use": "lib_deps",
    "lib_force": "lib_deps",
    "extra_script": "extra_scripts",
    "monitor_baud": "monitor_speed",
    "board_mcu": "board_build.mcu",
    "board_f_cpu": "board_build.f_cpu",
    "board_f_flash": "board_build.f_flash",
    "board_flash_mode": "board_build.flash_mode"
}


class ProjectConfig(object):

    VARTPL_RE = re.compile(r"\$\{([^\.\}]+)\.([^\}]+)\}")

    expand_interpolations = True
    _instances = {}
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
        if (not self._parser.has_section("platformio")
                or not self._parser.has_option("platformio", "extra_configs")):
            return
        extra_configs = self.getlist("platformio", "extra_configs")
        for pattern in extra_configs:
            for item in glob.glob(pattern):
                self.read(item)

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

    def get(self, section, option):
        if not self.expand_interpolations:
            return self._parser.get(section, option)

        try:
            value = self._parser.get(section, option)
        except ConfigParser.NoOptionError:
            value = self._parser.get("env", option)
        except ConfigParser.Error as e:
            raise exception.InvalidProjectConf(self.path, str(e))

        if "${" not in value or "}" not in value:
            return value
        return self.VARTPL_RE.sub(self._re_sub_handler, value)

    def _re_sub_handler(self, match):
        section, option = match.group(1), match.group(2)
        if section == "sysenv":
            return os.getenv(option)
        return self.get(section, option)

    def getlist(self, section, option):
        return self.parse_multi_values(self.get(section, option))

    def envs(self):
        return [s[4:] for s in self._parser.sections() if s.startswith("env:")]

    def default_envs(self):
        if not self._parser.has_option("platformio", "env_default"):
            return []
        return self.getlist("platformio", "env_default")

    def validate(self, envs=None, validate_options=True):
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
        return self.validate_options() if validate_options else True

    def validate_options(self):
        return (self._validate_platformio_options()
                and self._validate_env_options())

    def _validate_platformio_options(self):
        if not self._parser.has_section("platformio"):
            return True
        warnings = set()

        # legacy `lib_extra_dirs`
        if self._parser.has_option("platformio", "lib_extra_dirs"):
            if not self._parser.has_section("env"):
                self._parser.add_section("env")
            self._parser.set("env", "lib_extra_dirs",
                             self._parser.get("platformio", "lib_extra_dirs"))
            self._parser.remove_option("platformio", "lib_extra_dirs")
            warnings.add(
                "`lib_extra_dirs` option is deprecated in section "
                "`platformio`! Please move it to global `env` section")

        unknown = set(k for k, _ in self.items("platformio")) - set(
            KNOWN_PLATFORMIO_OPTIONS)
        if unknown:
            warnings.add(
                "Ignore unknown `%s` options in section `[platformio]`" %
                ", ".join(unknown))

        for warning in warnings:
            click.secho("Warning! %s" % warning, fg="yellow")

        return True

    def _validate_env_options(self):
        warnings = set()

        for section in self._parser.sections():
            if section != "env" and not section.startswith("env:"):
                continue
            for option in self._parser.options(section):
                # obsolete
                if option in RENAMED_OPTIONS:
                    warnings.add(
                        "`%s` option in section `[%s]` is deprecated and will "
                        "be removed in the next release! Please use `%s` "
                        "instead" % (option, section, RENAMED_OPTIONS[option]))
                    # rename on-the-fly
                    self._parser.set(section, RENAMED_OPTIONS[option],
                                     self._parser.get(section, option))
                    self._parser.remove_option(section, option)
                    continue

                # unknown
                unknown_conditions = [
                    option not in KNOWN_ENV_OPTIONS,
                    not option.startswith("custom_"),
                    not option.startswith("board_")
                ]  # yapf: disable
                if all(unknown_conditions):
                    warnings.add(
                        "Detected non-PlatformIO `%s` option in `[%s]` section"
                        % (option, section))

        for warning in warnings:
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
