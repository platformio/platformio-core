# Copyright 2014-present Ivan Kravets <me@ikravets.com>
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

import base64
import os
import re
import sys
from imp import load_source
from multiprocessing import cpu_count
from os.path import basename, dirname, isdir, isfile, join

import click
import semantic_version

from platformio import exception, util
from platformio.managers.package import PackageManager


class PlatformManager(PackageManager):

    def __init__(self):
        PackageManager.__init__(
            self,
            join(util.get_home_dir(), "platforms"),
            ["http://dl.platformio.org/platforms/manifest.json"]
        )

    @property
    def manifest_name(self):
        return "platform.json"

    def install(self,  # pylint: disable=too-many-arguments,arguments-differ
                name, requirements=None, with_packages=None,
                without_packages=None, skip_default_packages=False):
        manifest_path = PackageManager.install(self, name, requirements)
        PlatformFactory.newPlatform(
            manifest_path, requirements).install_packages(
                with_packages, without_packages, skip_default_packages)
        self.cleanup_packages()
        return True

    def uninstall(self,  # pylint: disable=arguments-differ
                  name, requirements=None):
        PackageManager.uninstall(self, name, requirements)
        self.cleanup_packages()
        return True

    def update(self,  # pylint: disable=arguments-differ
               name, requirements=None, only_packages=False):
        if not only_packages:
            PackageManager.update(self, name)
        PlatformFactory.newPlatform(
            name, requirements).update_packages()
        self.cleanup_packages()
        return True

    def is_outdated(self, name, requirements=None):
        p = PlatformFactory.newPlatform(name, requirements)
        return (p.are_outdated_packages() or
                p.version != self.get_latest_repo_version(name, requirements))

    def cleanup_packages(self):
        self.reset_cache()
        deppkgs = {}
        for manifest in PlatformManager().get_installed():
            p = PlatformFactory.newPlatform(
                manifest['name'], manifest['version'])
            for pkgname, pkgmanifest in p.get_installed_packages().items():
                if pkgname not in deppkgs:
                    deppkgs[pkgname] = set()
                deppkgs[pkgname].add(pkgmanifest['version'])

        pm = PackageManager()
        for manifest in pm.get_installed():
            if manifest['name'] not in deppkgs:
                continue
            if manifest['version'] not in deppkgs[manifest['name']]:
                pm.uninstall(
                    manifest['name'], manifest['version'], trigger_event=False)

        self.reset_cache()
        return True

    def get_installed_boards(self):
        boards = []
        for manifest in self.get_installed():
            p = PlatformFactory.newPlatform(manifest['_manifest_path'])
            for id_, config in p.get_boards().items():
                manifest = config.get_manifest().copy()
                manifest['id'] = id_
                manifest['platform'] = p.name
                boards.append(manifest)
        return boards

    @staticmethod
    @util.memoized
    def get_registered_boards():
        boards = util.get_api_result("/boards")
        for item in boards:
            # @TODO remove type from API
            item['id'] = item['type']
            del item['type']
        return boards


class PlatformFactory(object):

    @staticmethod
    def get_clsname(name):
        return "%s%sPlatform" % (name.upper()[0], name.lower()[1:])

    @staticmethod
    def load_module(name, path):
        module = None
        try:
            module = load_source(
                "platformio.managers.platform.%s" % name, path)
        except ImportError:
            raise exception.UnknownPlatform(name)
        return module

    @classmethod
    def newPlatform(cls, name, requirements=None):
        platform_dir = None
        if name.endswith("platform.json") and isfile(name):
            platform_dir = dirname(name)
            name = util.load_json(name)['name']
        else:
            _manifest = PlatformManager().max_satisfying_version(
                name, requirements)
            if _manifest:
                platform_dir = dirname(_manifest['_manifest_path'])

        if not platform_dir:
            raise exception.UnknownPlatform(
                name if not requirements else "%s@%s" % (name, requirements))

        platform_cls = None
        if isfile(join(platform_dir, "platform.py")):
            platform_cls = getattr(
                cls.load_module(name, join(platform_dir, "platform.py")),
                cls.get_clsname(name)
            )
        else:
            platform_cls = type(
                str(cls.get_clsname(name)), (PlatformBase,), {})

        _instance = platform_cls(join(platform_dir, "platform.json"))
        assert isinstance(_instance, PlatformBase)
        return _instance


class PlatformPackagesMixin(object):

    def get_installed_packages(self):
        items = {}
        installed = self.pm.get_installed()
        for name, opts in self.packages.items():
            manifest = None
            for p in installed:
                if (p['name'] != name or not semantic_version.match(
                        opts['version'], p['version'])):
                    continue
                elif (not manifest or semantic_version.compare(
                        p['version'], manifest['version']) == 1):
                    manifest = p
            if manifest:
                items[name] = manifest
        return items

    def install_packages(self, with_packages=None, without_packages=None,
                         skip_default_packages=False, silent=False):
        with_packages = set(
            self.pkg_types_to_names(with_packages or []))
        without_packages = set(
            self.pkg_types_to_names(without_packages or []))

        upkgs = with_packages | without_packages
        ppkgs = set(self.packages.keys())
        if not upkgs.issubset(ppkgs):
            raise exception.UnknownPackage(", ".join(upkgs - ppkgs))

        for name, opts in self.packages.items():
            if name in without_packages:
                continue
            elif (name in with_packages or
                  not (skip_default_packages or opts.get("optional", False))):
                self.pm.install(name, opts.get("version"), silent=silent)

        return True

    def update_packages(self):
        for name in self.get_installed_packages().keys():
            self.pm.update(name, self.packages[name]['version'])

    def are_outdated_packages(self):
        for name, opts in self.get_installed_packages().items():
            if (opts['version'] != self.pm.get_latest_repo_version(
                    name, self.packages[name].get("version"))):
                return True
        return False


class PlatformRunMixin(object):

    LINE_ERROR_RE = re.compile(r"(\s+error|error[:\s]+)", re.I)

    def run(self, variables, targets, verbose):
        assert isinstance(variables, dict)
        assert isinstance(targets, list)

        self.configure_default_packages(variables, targets)
        self.install_packages(silent=True)

        self._verbose_level = int(verbose)

        if "clean" in targets:
            targets.remove("clean")
            targets.append("-c")

        variables['platform_manifest'] = self.manifest_path

        if "build_script" not in variables:
            variables['build_script'] = self.get_build_script()
        if not isfile(variables['build_script']):
            raise exception.BuildScriptNotFound(variables['build_script'])

        self._found_error = False
        result = self._run_scons(variables, targets)
        assert "returncode" in result
        # if self._found_error:
        #     result['returncode'] = 1

        if self._last_echo_line == ".":
            click.echo("")

        return result

    def _run_scons(self, variables, targets):
        # pass current PYTHONPATH to SCons
        if "PYTHONPATH" in os.environ:
            _PYTHONPATH = os.environ.get("PYTHONPATH").split(os.pathsep)
        else:
            _PYTHONPATH = []
        for p in os.sys.path:
            if p not in _PYTHONPATH:
                _PYTHONPATH.append(p)
        os.environ['PYTHONPATH'] = os.pathsep.join(_PYTHONPATH)

        cmd = [
            os.path.normpath(sys.executable),
            join(self.get_package_dir("tool-scons"), "script", "scons"),
            "-Q",
            "-j %d" % self.get_job_nums(),
            "--warn=no-no-parallel-support",
            "-f", join(util.get_source_dir(), "builder", "main.py")
        ] + targets

        # encode and append variables
        for key, value in variables.items():
            cmd.append("%s=%s" % (key.upper(), base64.b64encode(value)))

        result = util.exec_command(
            cmd,
            stdout=util.AsyncPipe(self.on_run_out),
            stderr=util.AsyncPipe(self.on_run_err)
        )
        return result

    def on_run_out(self, line):
        self._echo_line(line, level=3)

    def on_run_err(self, line):
        is_error = self.LINE_ERROR_RE.search(line) is not None
        if is_error:
            self._found_error = True
        self._echo_line(line, level=1 if is_error else 2)

    def _echo_line(self, line, level):
        assert 1 <= level <= 3

        fg = ("red", "yellow", None)[level - 1]
        if level == 3 and "is up to date" in line:
            fg = "green"

        if level > self._verbose_level:
            click.secho(".", fg=fg, err=level < 3, nl=False)
            self._last_echo_line = "."
            return

        if self._last_echo_line == ".":
            click.echo("")
        self._last_echo_line = line

        click.secho(line, fg=fg, err=level < 3)

    @staticmethod
    def get_job_nums():
        try:
            return cpu_count()
        except NotImplementedError:
            return 1


class PlatformBase(PlatformPackagesMixin, PlatformRunMixin):

    _BOARDS_CACHE = {}

    def __init__(self, manifest_path):
        self._BOARDS_CACHE = {}
        self.manifest_path = manifest_path
        self._manifest = util.load_json(manifest_path)

        self.pm = PackageManager(
            repositories=self._manifest.get("packageRepositories"))

        self._found_error = False
        self._last_echo_line = None

        # 1 = errors
        # 2 = 1 + warnings
        # 3 = 2 + others
        self._verbose_level = 3

    @property
    def name(self):
        return self._manifest['name']

    @property
    def title(self):
        return self._manifest['title']

    @property
    def description(self):
        return self._manifest['description']

    @property
    def version(self):
        return self._manifest['version']

    @property
    def homepage(self):
        return self._manifest.get("homepage")

    @property
    def license(self):
        return self._manifest.get("license")

    @property
    def frameworks(self):
        return self._manifest.get("frameworks")

    @property
    def manifest(self):
        return self._manifest

    @property
    def packages(self):
        packages = self._manifest.get("packages", {})
        if "tool-scons" not in packages:
            packages['tool-scons'] = {
                "version": self._manifest.get("engines", {}).get(
                    "scons", ">=2.3.0,<2.6.0"),
                "optional": False
            }
        return packages

    def get_dir(self):
        return dirname(self.manifest_path)

    def get_build_script(self):
        main_script = join(self.get_dir(), "builder", "main.py")
        if isfile(main_script):
            return main_script
        raise NotImplementedError()

    def is_embedded(self):
        for opts in self.packages.values():
            if opts.get("type") == "uploader":
                return True
        return False

    def get_boards(self, id_=None):
        if id_ is None:
            boards_dir = join(self.get_dir(), "boards")
            if not isdir(boards_dir):
                return {}
            for item in sorted(os.listdir(boards_dir)):
                _id = item[:-5]
                if _id in self._BOARDS_CACHE:
                    continue
                self._BOARDS_CACHE[_id] = PlatformBoardConfig(
                    join(self.get_dir(), "boards", item)
                )
        else:
            if id_ not in self._BOARDS_CACHE:
                self._BOARDS_CACHE[id_] = PlatformBoardConfig(
                    join(self.get_dir(), "boards", "%s.json" % id_)
                )
        return self._BOARDS_CACHE[id_] if id_ else self._BOARDS_CACHE

    def board_config(self, id_):
        return self.get_boards(id_)

    def get_package_dir(self, name):
        packages = self.get_installed_packages()
        if name not in packages:
            return None
        return dirname(packages[name]['_manifest_path'])

    def get_package_version(self, name):
        packages = self.get_installed_packages()
        if name not in packages:
            return None
        return packages[name]['version']

    def get_package_type(self, name):
        return self.packages[name].get("type")

    def pkg_types_to_names(self, types):
        names = []
        for type_ in types:
            name = type_
            # lookup by package types
            for _name, _opts in self.packages.items():
                if _opts.get("type") == type_:
                    name = None
                    names.append(_name)
            # if type is the right name
            if name:
                names.append(name)
        return names

    def configure_default_packages(self, variables, targets):
        # enbale used frameworks
        for framework in variables.get("framework", "").split(","):
            framework = framework.lower().strip()
            if not framework or framework not in self.frameworks:
                continue
            _pkg_name = self.frameworks[framework]['package']
            self.packages[_pkg_name]['optional'] = False

        # enable upload tools for upload targets
        if any(["upload" in t for t in targets] + ["program" in targets]):
            for _name, _opts in self.packages.iteritems():
                if _opts.get("type") == "uploader":
                    self.packages[_name]['optional'] = False
                elif "uploadlazy" in targets:
                    # skip all packages, allow only upload tools
                    self.packages[_name]['optional'] = True

        if "test" in targets and "tool-unity" not in self.packages:
            self.packages['tool-unity'] = {
                "version": "~1.20302.0",
                "optional": False
            }


class PlatformBoardConfig(object):

    def __init__(self, manifest_path):
        if not isfile(manifest_path):
            raise exception.UnknownBoard(basename(manifest_path[:-5]))
        self.manifest_path = manifest_path
        self._manifest = util.load_json(manifest_path)

    def get(self, path, default=None):
        try:
            value = self._manifest
            for k in path.split("."):
                value = value[k]
            return value
        except KeyError:
            if default is not None:
                return default
            else:
                raise KeyError("Invalid board option '%s'" % path)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except KeyError:
            return False

    def get_manifest(self):
        return self._manifest
