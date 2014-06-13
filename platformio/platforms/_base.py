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

    def install(self, with_packages, without_packages):
        requirements = []
        pm = PackageManager(self.get_name())

        upkgs = set(with_packages + without_packages)
        ppkgs = set(self.PACKAGES.keys())
        if not upkgs.issubset(ppkgs):
            raise UnknownPackage(", ".join(upkgs - ppkgs))

        for name, opts in self.PACKAGES.iteritems():
            if name in without_packages:
                continue
            elif name in with_packages or opts["default"]:
                requirements.append((name, opts["path"]))

        for (package, path) in requirements:
            pm.install(package, path)
        return True

    def uninstall(self):
        platform = self.get_name()
        pm = PackageManager(platform)

        for package, data in pm.get_installed(platform).iteritems():
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
