# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import re
from imp import load_source
from os import listdir
from os.path import isdir, isfile, join

import click

from platformio import exception, util
from platformio.app import get_state_item, set_state_item
from platformio.pkgmanager import PackageManager


class PlatformFactory(object):

    @staticmethod
    def get_clsname(name):
        return "%sPlatform" % name.title()

    @staticmethod
    def load_module(name, path):
        module = None
        try:
            module = load_source(
                "platformio.platforms.%s" % name, path)
        except ImportError:
            raise exception.UnknownPlatform(name)
        return module

    @classmethod
    def get_platforms(cls, installed=False):
        platforms = {}
        for d in (util.get_home_dir(), util.get_source_dir()):
            pdir = join(d, "platforms")
            if not isdir(pdir):
                continue
            for p in listdir(pdir):
                if p in ("__init__.py", "base.py") or not p.endswith(".py"):
                    continue
                name = p[:-3]
                path = join(pdir, p)
                try:
                    isplatform = hasattr(
                        cls.load_module(name, path),
                        cls.get_clsname(name)
                    )
                    if isplatform:
                        platforms[name] = path
                except exception.UnknownPlatform:
                    pass

        if not installed:
            return platforms

        installed_platforms = {}
        for name in get_state_item("installed_platforms", []):
            if name in platforms:
                installed_platforms[name] = platforms[name]
        return installed_platforms

    @classmethod
    def newPlatform(cls, name):
        platforms = cls.get_platforms()
        if name not in platforms:
            raise exception.UnknownPlatform(name)

        _instance = getattr(
            cls.load_module(name, platforms[name]),
            cls.get_clsname(name)
        )()
        assert isinstance(_instance, BasePlatform)
        return _instance


class BasePlatform(object):

    PACKAGES = {}
    LINE_ERROR_RE = re.compile(r"(\s+error|error[:\s]+)", re.I)

    def __init__(self):
        self._found_error = False

    def get_name(self):
        return self.__class__.__name__[:-8].lower()

    def get_build_script(self):
        builtin = join(util.get_source_dir(), "builder", "scripts", "%s.py" %
                       self.get_name())
        if isfile(builtin):
            return builtin
        raise NotImplementedError()

    def get_short_info(self):
        if self.__doc__:
            doclines = [l.strip() for l in self.__doc__.splitlines()]
            return " ".join(doclines).strip()
        else:
            raise NotImplementedError()

    def get_packages(self):
        return self.PACKAGES

    def get_pkg_alias(self, pkgname):
        return self.PACKAGES[pkgname].get("alias", None)

    def pkg_aliases_to_names(self, aliases):
        names = []
        for alias in aliases:
            name = alias
            # lookup by package aliases
            for _name, _opts in self.get_packages().items():
                if _opts.get("alias", None) == alias:
                    name = _name
                    break
            names.append(name)
        return names

    def get_installed_packages(self):
        pm = PackageManager()
        return [n for n in self.get_packages().keys() if pm.is_installed(n)]

    def install(self, with_packages, without_packages, skip_default_packages):
        with_packages = set(self.pkg_aliases_to_names(with_packages))
        without_packages = set(self.pkg_aliases_to_names(without_packages))

        upkgs = with_packages | without_packages
        ppkgs = set(self.get_packages().keys())
        if not upkgs.issubset(ppkgs):
            raise exception.UnknownPackage(", ".join(upkgs - ppkgs))

        requirements = []
        for name, opts in self.get_packages().items():
            if name in without_packages:
                continue
            elif (name in with_packages or (not skip_default_packages and
                                            opts['default'])):
                requirements.append(name)

        pm = PackageManager()
        for name in requirements:
            pm.install(name)

        # register installed platform
        data = get_state_item("installed_platforms", [])
        if self.get_name() not in data:
            data.append(self.get_name())
            set_state_item("installed_platforms", data)

        return len(requirements)

    def uninstall(self):
        platform = self.get_name()
        installed_platforms = PlatformFactory.get_platforms(
            installed=True).keys()

        if platform not in installed_platforms:
            raise exception.PlatformNotInstalledYet(platform)

        deppkgs = set()
        for item in installed_platforms:
            if item == platform:
                continue
            p = PlatformFactory.newPlatform(item)
            deppkgs = deppkgs.union(set(p.get_packages().keys()))

        pm = PackageManager()
        for name in self.get_packages().keys():
            if not pm.is_installed(name) or name in deppkgs:
                continue
            pm.uninstall(name)

        # unregister installed platform
        installed_platforms.remove(platform)
        set_state_item("installed_platforms", installed_platforms)

        return True

    def update(self):
        pm = PackageManager()
        for name in self.get_installed_packages():
            pm.update(name)

    def is_outdated(self):
        pm = PackageManager()
        obsolated = pm.get_outdated()
        return not set(self.get_packages().keys()).isdisjoint(set(obsolated))

    def run(self, variables, targets):
        assert isinstance(variables, list)
        assert isinstance(targets, list)

        installed_platforms = PlatformFactory.get_platforms(
            installed=True).keys()
        installed_packages = PackageManager.get_installed()

        if self.get_name() not in installed_platforms:
            raise exception.PlatformNotInstalledYet(self.get_name())

        if "clean" in targets:
            targets.remove("clean")
            targets.append("-c")

        if not any([v.startswith("BUILD_SCRIPT=") for v in variables]):
            variables.append("BUILD_SCRIPT=%s" % self.get_build_script())

        for v in variables:
            if not v.startswith("BUILD_SCRIPT="):
                continue
            _, path = v.split("=", 2)
            if not isfile(path):
                raise exception.BuildScriptNotFound(path)

        # append aliases of the installed packages
        for name, options in self.get_packages().items():
            if "alias" not in options or name not in installed_packages:
                continue
            variables.append(
                "PIOPACKAGE_%s=%s" % (options['alias'].upper(), name))

        self._found_error = False
        try:
            result = util.exec_command(
                [
                    "scons",
                    "-Q",
                    "-f", join(util.get_source_dir(), "builder", "main.py")
                ] + variables + targets,
                stdout=util.AsyncPipe(self.on_run_out),
                stderr=util.AsyncPipe(self.on_run_err)
            )
        except OSError:
            raise exception.SConsNotInstalled()

        assert "returncode" in result
        if self._found_error:
            result['returncode'] = 1

        return result

    def on_run_out(self, line):  # pylint: disable=R0201
        fg = None
        if "is up to date" in line:
            fg = "green"
        click.secho(line, fg=fg)

    def on_run_err(self, line):  # pylint: disable=R0201
        is_error = self.LINE_ERROR_RE.search(line) is not None
        if is_error:
            self._found_error = True
        click.secho(line, err=True, fg="red" if is_error else "yellow")
