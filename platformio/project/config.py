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

import configparser
import glob
import hashlib
import json
import os
import re
import time

import click

from platformio import fs
from platformio.compat import MISSING, hashlib_encode_data, string_types
from platformio.project import exception
from platformio.project.options import ProjectOptions

CONFIG_HEADER = """
; PlatformIO Project Configuration File
;
;   Build options: build flags, source filter
;   Upload options: custom upload port, speed and extra flags
;   Library options: dependencies, extra library storages
;   Advanced options: extra scripting
;
; Please visit documentation for the other options and examples
; https://docs.platformio.org/page/projectconf.html
"""


class ProjectConfigBase:
    ENVNAME_RE = re.compile(r"^[a-z\d\_\-]+$", flags=re.I)
    INLINE_COMMENT_RE = re.compile(r"\s+;.*$")
    VARTPL_RE = re.compile(r"\$\{(?:([^\.\}\()]+)\.)?([^\}]+)\}")

    BUILTIN_VARS = {
        "PROJECT_DIR": lambda: os.getcwd(),  # pylint: disable=unnecessary-lambda
        "PROJECT_HASH": lambda: "%s-%s"
        % (
            os.path.basename(os.getcwd()),
            hashlib.sha1(hashlib_encode_data(os.getcwd())).hexdigest()[:10],
        ),
        "UNIX_TIME": lambda: str(int(time.time())),
    }

    CUSTOM_OPTION_PREFIXES = ("custom_", "board_")

    expand_interpolations = True
    warnings = []

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
                item = ProjectConfigBase.INLINE_COMMENT_RE.sub("", item).strip()
            result.append(item)
        return result

    @staticmethod
    def get_default_path():
        from platformio import app  # pylint: disable=import-outside-toplevel

        return app.get_session_var("custom_project_conf") or os.path.join(
            os.getcwd(), "platformio.ini"
        )

    def __init__(self, path=None, parse_extra=True, expand_interpolations=True):
        path = self.get_default_path() if path is None else path
        self.path = path
        self.expand_interpolations = expand_interpolations
        self.warnings = []
        self._parsed = []
        self._parser = configparser.ConfigParser(inline_comment_prefixes=("#", ";"))
        if path and os.path.isfile(path):
            self.read(path, parse_extra)

        self._maintain_renamed_options()

    def __getattr__(self, name):
        return getattr(self._parser, name)

    def read(self, path, parse_extra=True):
        if path in self._parsed:
            return
        self._parsed.append(path)
        try:
            self._parser.read(path, "utf-8")
        except configparser.Error as exc:
            raise exception.InvalidProjectConfError(path, str(exc)) from exc

        if not parse_extra:
            return

        # load extra configs
        for pattern in self.get("platformio", "extra_configs", []):
            if pattern.startswith("~"):
                pattern = fs.expanduser(pattern)
            for item in glob.glob(pattern, recursive=True):
                self.read(item)

    def _maintain_renamed_options(self):
        renamed_options = {}
        for option in ProjectOptions.values():
            if option.oldnames:
                renamed_options.update({name: option.name for name in option.oldnames})

        for section in self._parser.sections():
            scope = self.get_section_scope(section)
            if scope not in ("platformio", "env"):
                continue
            for option in self._parser.options(section):
                if option in renamed_options:
                    self.warnings.append(
                        "`%s` configuration option in section [%s] is "
                        "deprecated and will be removed in the next release! "
                        "Please use `%s` instead"
                        % (option, section, renamed_options[option])
                    )
                    # # rename on-the-fly
                    # self._parser.set(
                    #     section,
                    #     renamed_options[option],
                    #     self._parser.get(section, option),
                    # )
                    # self._parser.remove_option(section, option)
                    continue

                # unknown
                unknown_conditions = [
                    ("%s.%s" % (scope, option)) not in ProjectOptions,
                    scope != "env"
                    or not option.startswith(self.CUSTOM_OPTION_PREFIXES),
                ]
                if all(unknown_conditions):
                    self.warnings.append(
                        "Ignore unknown configuration option `%s` "
                        "in section [%s]" % (option, section)
                    )
        return True

    @staticmethod
    def get_section_scope(section):
        assert section
        return section.split(":", 1)[0] if ":" in section else section

    def walk_options(self, root_section):
        extends_queue = (
            ["env", root_section] if root_section.startswith("env:") else [root_section]
        )
        extends_done = []
        while extends_queue:
            section = extends_queue.pop()
            extends_done.append(section)
            if not self._parser.has_section(section):
                continue
            for option in self._parser.options(section):
                yield (section, option)
            if self._parser.has_option(section, "extends"):
                extends_queue.extend(
                    self.parse_multi_values(self._parser.get(section, "extends"))
                )

    def options(self, section=None, env=None):
        result = []
        assert section or env
        if not section:
            section = "env:" + env

        if not self.expand_interpolations:
            return self._parser.options(section)

        for _, option in self.walk_options(section):
            if option not in result:
                result.append(option)

        # handle system environment variables
        scope = self.get_section_scope(section)
        for option_meta in ProjectOptions.values():
            if option_meta.scope != scope or option_meta.name in result:
                continue
            if option_meta.sysenvvar and option_meta.sysenvvar in os.environ:
                result.append(option_meta.name)

        return result

    def has_option(self, section, option):
        if self._parser.has_option(section, option):
            return True
        return option in self.options(section)

    def items(self, section=None, env=None, as_dict=False):
        assert section or env
        if not section:
            section = "env:" + env
        if as_dict:
            return {
                option: self.get(section, option) for option in self.options(section)
            }
        return [(option, self.get(section, option)) for option in self.options(section)]

    def set(self, section, option, value):
        if value is None:
            value = ""
        if isinstance(value, (list, tuple)):
            value = "\n".join(value)
        elif isinstance(value, bool):
            value = "yes" if value else "no"
        elif isinstance(value, (int, float)):
            value = str(value)
        # start multi-line value from a new line
        if "\n" in value and not value.startswith("\n"):
            value = "\n" + value
        self._parser.set(section, option, value)

    def resolve_renamed_option(self, section, old_name):
        scope = self.get_section_scope(section)
        if scope not in ("platformio", "env"):
            return None
        for option_meta in ProjectOptions.values():
            if (
                option_meta.oldnames
                and option_meta.scope == scope
                and old_name in option_meta.oldnames
            ):
                return option_meta.name
        return None

    def find_option_meta(self, section, option):
        scope = self.get_section_scope(section)
        if scope not in ("platformio", "env"):
            return None
        option_meta = ProjectOptions.get("%s.%s" % (scope, option))
        if option_meta:
            return option_meta
        for option_meta in ProjectOptions.values():
            if option_meta.scope == scope and option in (option_meta.oldnames or []):
                return option_meta
        return None

    def _traverse_for_value(self, section, option, option_meta=None):
        for _section, _option in self.walk_options(section):
            if _option == option or (
                option_meta
                and (
                    option_meta.name == _option
                    or _option in (option_meta.oldnames or [])
                )
            ):
                return self._parser.get(_section, _option)
        return MISSING

    def getraw(
        self, section, option, default=MISSING
    ):  # pylint: disable=too-many-branches
        if not self.expand_interpolations:
            return self._parser.get(section, option)

        option_meta = self.find_option_meta(section, option)
        value = self._traverse_for_value(section, option, option_meta)

        if not option_meta:
            if value == MISSING:
                value = (
                    default if default != MISSING else self._parser.get(section, option)
                )
            return self._expand_interpolations(section, option, value)

        if option_meta.sysenvvar:
            envvar_value = os.getenv(option_meta.sysenvvar)
            if not envvar_value and option_meta.oldnames:
                for oldoption in option_meta.oldnames:
                    envvar_value = os.getenv("PLATFORMIO_" + oldoption.upper())
                    if envvar_value:
                        break
            if envvar_value and option_meta.multiple:
                if value == MISSING:
                    value = ""
                value += ("\n" if value else "") + envvar_value
            elif envvar_value:
                value = envvar_value

        if value == MISSING:
            value = default if default != MISSING else option_meta.default
        if callable(value):
            value = value()
        if value == MISSING:
            return None

        return self._expand_interpolations(section, option, value)

    def _expand_interpolations(self, section, option, value):
        if not value or not isinstance(value, string_types) or not "$" in value:
            return value

        # legacy support for variables delclared without "${}"
        legacy_vars = ["PROJECT_HASH"]
        stop = False
        while not stop:
            stop = True
            for name in legacy_vars:
                x = value.find(f"${name}")
                if x < 0 or value[x - 1] == "$":
                    continue
                value = "%s${%s}%s" % (value[:x], name, value[x + len(name) + 1 :])
                stop = False
                warn_msg = (
                    "Invalid variable declaration. Please use "
                    f"`${{{name}}}` instead of `${name}`"
                )
                if warn_msg not in self.warnings:
                    self.warnings.append(warn_msg)

        if not all(["${" in value, "}" in value]):
            return value
        return self.VARTPL_RE.sub(
            lambda match: self._re_interpolation_handler(section, option, match), value
        )

    def _re_interpolation_handler(self, parent_section, parent_option, match):
        section, option = match.group(1), match.group(2)

        # handle built-in variables
        if section is None:
            if option in self.BUILTIN_VARS:
                return self.BUILTIN_VARS[option]()
            # SCons varaibles
            return f"${{{option}}}"

        # handle system environment variables
        if section == "sysenv":
            return os.getenv(option)

        # handle ${this.*}
        if section == "this":
            section = parent_section
            if option == "__env__":
                if not parent_section.startswith("env:"):
                    raise exception.ProjectOptionValueError(
                        f"`${{this.__env__}}` is called from the `{parent_section}` "
                        "section that is not valid PlatformIO environment. Please "
                        f"check `{parent_option}` option in the `{section}` section"
                    )
                return parent_section[4:]

        # handle nested calls
        try:
            value = self.get(section, option)
        except RecursionError as exc:
            raise exception.ProjectOptionValueError(
                f"Infinite recursion has been detected for `{option}` "
                f"option in the `{section}` section"
            ) from exc
        if isinstance(value, list):
            return "\n".join(value)
        return str(value)

    def get(self, section, option, default=MISSING):
        value = None
        try:
            value = self.getraw(section, option, default)
        except configparser.Error as exc:
            raise exception.InvalidProjectConfError(self.path, str(exc))

        option_meta = self.find_option_meta(section, option)
        if not option_meta:
            return value

        if option_meta.validate:
            value = option_meta.validate(value)
        if option_meta.multiple:
            value = self.parse_multi_values(value or [])
        try:
            return self.cast_to(value, option_meta.type)
        except click.BadParameter as exc:
            if not self.expand_interpolations:
                return value
            raise exception.ProjectOptionValueError(
                "%s for `%s` option in the `%s` section (%s)"
                % (exc.format_message(), option, section, option_meta.description)
            )

    @staticmethod
    def cast_to(value, to_type):
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

    def get_default_env(self):
        default_envs = self.default_envs()
        if default_envs:
            return default_envs[0]
        envs = self.envs()
        return envs[0] if envs else None

    def validate(self, envs=None, silent=False):
        if not os.path.isfile(self.path):
            raise exception.NotPlatformIOProjectError(os.path.dirname(self.path))

        known_envs = set(self.envs())

        # check envs
        if not known_envs:
            raise exception.ProjectEnvsNotAvailableError()
        unknown_envs = set(list(envs or []) + self.default_envs()) - known_envs
        if unknown_envs:
            raise exception.UnknownEnvNamesError(
                ", ".join(unknown_envs), ", ".join(known_envs)
            )

        for env in known_envs:
            # check envs names
            if not self.ENVNAME_RE.match(env):
                raise exception.InvalidEnvNameError(env)

            # check simultaneous use of `monitor_raw` and `monitor_filters`
            if self.get(f"env:{env}", "monitor_raw", False) and self.get(
                f"env:{env}", "monitor_filters", None
            ):
                self.warnings.append(
                    "The `monitor_raw` and `monitor_filters` options cannot be "
                    f"used simultaneously for the `{env}` environment in the "
                    "`platformio.ini` file. The `monitor_filters` option will "
                    "be disabled to avoid conflicts."
                )

        if not silent:
            for warning in self.warnings:
                click.secho("Warning! %s" % warning, fg="yellow")

        return True


class ProjectConfigLintMixin:
    @classmethod
    def lint(cls, path=None):
        errors = []
        warnings = []
        try:
            config = cls.get_instance(path)
            config.validate(silent=True)
            warnings = config.warnings  # in case "as_tuple" fails
            config.as_tuple()
            warnings = config.warnings
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if exc.__cause__ is not None:
                exc = exc.__cause__

            item = {"type": exc.__class__.__name__, "message": str(exc)}
            for attr in ("lineno", "source"):
                if hasattr(exc, attr):
                    item[attr] = getattr(exc, attr)

            if item["type"] == "ParsingError" and hasattr(exc, "errors"):
                for lineno, line in getattr(exc, "errors"):
                    errors.append(
                        {
                            "type": item["type"],
                            "message": f"Parsing error: {line}",
                            "lineno": lineno,
                            "source": item["source"],
                        }
                    )
            else:
                errors.append(item)
        return {"errors": errors, "warnings": warnings}


class ProjectConfigDirsMixin:
    def get_optional_dir(self, name):
        """
        Deprecated, used by platformio-node-helpers.project.observer.fetchLibDirs
        PlatformIO IDE for Atom depends on platformio-node-helpers@~7.2.0
        PIO Home 3.0 Project Inspection depends on it
        """
        return self.get("platformio", f"{name}_dir")


class ProjectConfig(ProjectConfigBase, ProjectConfigLintMixin, ProjectConfigDirsMixin):
    _instances = {}

    @staticmethod
    def get_instance(path=None):
        path = ProjectConfig.get_default_path() if path is None else path
        mtime = os.path.getmtime(path) if os.path.isfile(path) else 0
        instance = ProjectConfig._instances.get(path)
        if instance and instance["mtime"] != mtime:
            instance = None
        if not instance:
            instance = {"mtime": mtime, "config": ProjectConfig(path)}
            ProjectConfig._instances[path] = instance
        return instance["config"]

    def __repr__(self):
        return "<ProjectConfig %s>" % (self.path or "in-memory")

    def as_tuple(self):
        return [(s, self.items(s)) for s in self.sections()]

    def to_json(self):
        return json.dumps(self.as_tuple())

    def update(self, data, clear=False):
        assert isinstance(data, list)
        if clear:
            self._parser = configparser.ConfigParser()
        for section, options in data:
            if not self._parser.has_section(section):
                self._parser.add_section(section)
            for option, value in options:
                self.set(section, option, value)

    def save(self, path=None):
        path = path or self.path
        if path in self._instances:
            del self._instances[path]
        with open(path or self.path, mode="w+", encoding="utf8") as fp:
            fp.write(CONFIG_HEADER.strip() + "\n\n")
            self._parser.write(fp)
            fp.seek(0)
            contents = fp.read()
            fp.seek(0)
            fp.truncate()
            fp.write(contents.strip() + "\n")
        return True
