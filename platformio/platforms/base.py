# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import join
from shutil import rmtree

from platformio.exception import UnknownPackage, UnknownPlatform
from platformio.pkgmanager import PackageManager
from platformio.util import exec_command, get_platforms, get_source_dir


class PlatformFactory(object):

    @staticmethod
    def newPlatform(name):
        clsname = "%sPlatform" % name.title()
        try:
            assert name in get_platforms()
            mod = __import__("platformio.platforms." + name.lower(),
                             None, None, [clsname])
        except (AssertionError, ImportError):
            raise UnknownPlatform(name)

        obj = getattr(mod, clsname)()
        assert isinstance(obj, BasePlatform)
        return obj


class BasePlatform(object):

    PACKAGES = {}

    def get_name(self):
        raise NotImplementedError()

    def get_short_info(self):
        if self.__doc__:
            doclines = [l.strip() for l in self.__doc__.splitlines()]
            return " ".join(doclines).strip()
        else:
            raise NotImplementedError()

    def get_pkg_alias(self, pkgname):
        return self.PACKAGES[pkgname].get("alias", None)

    def pkg_aliases_to_names(self, aliases):
        names = []
        for alias in aliases:
            name = alias
            # lookup by packages alias
            if name not in self.PACKAGES:
                for _name, _opts in self.PACKAGES.items():
                    if _opts.get("alias", None) == alias:
                        name = _name
                        break
            names.append(name)
        return names

    def install(self, with_packages, without_packages, skip_default_packages):
        with_packages = set(self.pkg_aliases_to_names(with_packages))
        without_packages = set(self.pkg_aliases_to_names(without_packages))

        upkgs = with_packages | without_packages
        ppkgs = set(self.PACKAGES.keys())
        if not upkgs.issubset(ppkgs):
            raise UnknownPackage(", ".join(upkgs - ppkgs))

        requirements = []
        for name, opts in self.PACKAGES.items():
            if name in without_packages:
                continue
            elif (name in with_packages or (not skip_default_packages and
                                            opts['default'])):
                requirements.append((name, opts['path']))

        pm = PackageManager(self.get_name())
        for (package, path) in requirements:
            pm.install(package, path)
        return len(requirements)

    def uninstall(self):
        platform = self.get_name()
        pm = PackageManager(platform)

        for package, data in pm.get_installed(platform).items():
            pm.uninstall(package, data['path'])

        pm.unregister_platform(platform)
        rmtree(pm.get_platform_dir())
        return True

    def update(self):
        platform = self.get_name()
        pm = PackageManager(platform)
        for package in pm.get_installed(platform).keys():
            pm.update(package)

    def run(self, variables, targets):
        assert isinstance(variables, list)
        assert isinstance(targets, list)

        if "clean" in targets:
            targets.remove("clean")
            targets.append("-c")

        result = exec_command([
            "scons",
            "-Q",
            "-f", join(get_source_dir(), "builder", "main.py")
        ] + variables + targets)

        return self.after_run(result)

    def after_run(self, result):  # pylint: disable=R0201
        return result
