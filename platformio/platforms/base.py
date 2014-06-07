# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os.path import join

from click import echo, secho, style

from platformio.exception import (PackageInstalled, UnknownPackage,
                                  UnknownPlatform)
from platformio.pkgmanager import PackageManager
from platformio.util import exec_command, get_source_dir


class PlatformFactory(object):

    @staticmethod
    def newPlatform(name):
        clsname = "%sPlatform" % name.title()
        try:
            mod = __import__("platformio.platforms." + name.lower(),
                             None, None, [clsname])
        except ImportError:
            raise UnknownPlatform(name)

        obj = getattr(mod, clsname)()
        assert isinstance(obj, BasePlatform)
        return obj


class BasePlatform(object):

    PACKAGES = {}

    def get_name(self):
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

        for (name, path) in requirements:
            echo("Installing %s package:" % style(name, fg="cyan"))
            try:
                pm.install(name, path)
            except PackageInstalled:
                secho("Already installed", fg="yellow")

        return True

    def after_run(self, result):  # pylint: disable=R0201
        return result

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
