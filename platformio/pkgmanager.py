# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

from os import makedirs, remove
from os.path import basename, isdir, isfile, join
from shutil import rmtree
from time import time

import click
import requests

from platformio import exception, telemetry, util
from platformio.app import get_state_item, set_state_item
from platformio.downloader import FileDownloader
from platformio.unpacker import FileUnpacker


class PackageManager(object):

    def __init__(self):
        self._package_dir = join(util.get_home_dir(), "packages")
        if not isdir(self._package_dir):
            makedirs(self._package_dir)
        assert isdir(self._package_dir)

    @classmethod
    @util.memoized
    def get_manifest(cls):
        return util.get_api_result("/packages/manifest")

    @staticmethod
    def download(url, dest_dir, sha1=None):
        fd = FileDownloader(url, dest_dir)
        fd.start()
        fd.verify(sha1)
        return fd.get_filepath()

    @staticmethod
    def unpack(pkgpath, dest_dir):
        fu = FileUnpacker(pkgpath, dest_dir)
        return fu.start()

    @staticmethod
    def get_installed():
        return get_state_item("installed_packages", {})

    def get_outdated(self):
        outdated = []
        for name, data in self.get_installed().items():
            if data['version'] != self.get_info(name)['version']:
                outdated.append(name)
        return outdated

    def is_installed(self, name):
        return name in self.get_installed()

    def get_info(self, name, version=None):
        manifest = self.get_manifest()
        if name not in manifest:
            raise exception.UnknownPackage(name)

        # check system platform
        systype = util.get_systype()
        builds = ([b for b in manifest[name] if b['system'] == "all" or systype
                   in b['system']])
        if not builds:
            raise exception.NonSystemPackage(name, systype)

        if version:
            for b in builds:
                if b['version'] == version:
                    return b
            raise exception.InvalidPackageVersion(name, version)
        else:
            return sorted(builds, key=lambda s: s['version'])[-1]

    def install(self, name):
        click.echo("Installing %s package:" % click.style(name, fg="cyan"))

        if self.is_installed(name):
            click.secho("Already installed", fg="yellow")
            return False

        info = self.get_info(name)
        pkg_dir = join(self._package_dir, name)
        if not isdir(pkg_dir):
            makedirs(pkg_dir)

        dlpath = None
        try:
            dlpath = self.download(info['url'], pkg_dir, info['sha1'])
        except (requests.exceptions.ConnectionError,
                exception.FDUnrecognizedStatusCode):
            if info['url'].startswith("http://sourceforge.net"):
                dlpath = self.download(
                    "http://dl.platformio.org/packages/%s" %
                    basename(info['url']), pkg_dir, info['sha1'])

        assert isfile(dlpath)

        if self.unpack(dlpath, pkg_dir):
            self._register(name, info['version'])
        # remove archive
        remove(dlpath)

        telemetry.on_event(
            category="PackageManager", action="Install", label=name)

    def uninstall(self, name):
        click.echo("Uninstalling %s package: \t" %
                   click.style(name, fg="cyan"), nl=False)

        if not self.is_installed(name):
            click.secho("Not installed", fg="yellow")
            return False

        rmtree(join(self._package_dir, name))
        self._unregister(name)
        click.echo("[%s]" % click.style("OK", fg="green"))

        # report usage
        telemetry.on_event(
            category="PackageManager", action="Uninstall", label=name)

    def update(self, name):
        click.echo("Updating %s package:" % click.style(name, fg="yellow"))

        installed = self.get_installed()
        current_version = installed[name]['version']
        latest_version = self.get_info(name)['version']

        click.echo("Versions: Current=%d, Latest=%d \t " %
                   (current_version, latest_version), nl=False)

        if current_version == latest_version:
            click.echo("[%s]" % (click.style("Up-to-date", fg="green")))
            return True
        else:
            click.echo("[%s]" % (click.style("Out-of-date", fg="red")))

        self.uninstall(name)
        self.install(name)

        telemetry.on_event(
            category="PackageManager", action="Update", label=name)

    def _register(self, name, version):
        data = self.get_installed()
        data[name] = {
            "version": version,
            "time": int(time())
        }
        set_state_item("installed_packages", data)

    def _unregister(self, name):
        data = self.get_installed()
        del data[name]
        set_state_item("installed_packages", data)
