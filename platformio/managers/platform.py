# Copyright 2014-present PlatformIO <contact@platformio.org>
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
from imp import load_source
from multiprocessing import cpu_count
from os.path import basename, dirname, isdir, isfile, join

import click

from platformio import app, exception, util
from platformio.managers.package import BasePkgManager, PackageManager


class PlatformManager(BasePkgManager):

    FILE_CACHE_VALID = None  # disable platform caching

    def __init__(self, package_dir=None, repositories=None):
        if not repositories:
            repositories = [
                "https://dl.bintray.com/platformio/dl-platforms/manifest.json",
                "{0}://dl.platformio.org/platforms/manifest.json".format(
                    "https" if app.get_setting("enable_ssl") else "http")
            ]
        BasePkgManager.__init__(self, package_dir or
                                join(util.get_home_dir(), "platforms"),
                                repositories)

    @property
    def manifest_name(self):
        return "platform.json"

    def install(self,
                name,
                requirements=None,
                with_packages=None,
                without_packages=None,
                skip_default_package=False,
                **_):  # pylint: disable=too-many-arguments
        platform_dir = BasePkgManager.install(self, name, requirements)
        p = PlatformFactory.newPlatform(self.get_manifest_path(platform_dir))
        p.install_packages(with_packages, without_packages,
                           skip_default_package)
        self.cleanup_packages(p.packages.keys())
        return True

    def uninstall(self, name, requirements=None, trigger_event=True):
        name, requirements, _ = self.parse_pkg_name(name, requirements)
        p = PlatformFactory.newPlatform(name, requirements)
        BasePkgManager.uninstall(self, name, requirements)
        # trigger event is disabled when upgrading operation
        # don't cleanup packages, "install" will do that
        if trigger_event:
            self.cleanup_packages(p.packages.keys())
        return True

    def update(  # pylint: disable=arguments-differ
            self,
            name,
            requirements=None,
            only_packages=False,
            only_check=False):
        name, requirements, _ = self.parse_pkg_name(name, requirements)
        if not only_packages:
            BasePkgManager.update(self, name, requirements, only_check)
        p = PlatformFactory.newPlatform(name, requirements)
        p.update_packages(only_check)
        self.cleanup_packages(p.packages.keys())
        return True

    def is_outdated(self, name, requirements=None):
        if BasePkgManager.is_outdated(self, name, requirements):
            return True
        p = PlatformFactory.newPlatform(name, requirements)
        return p.are_outdated_packages()

    def cleanup_packages(self, names):
        self.reset_cache()
        deppkgs = {}
        for manifest in PlatformManager().get_installed():
            p = PlatformFactory.newPlatform(manifest['name'],
                                            manifest['version'])
            for pkgname, pkgmanifest in p.get_installed_packages().items():
                if pkgname not in deppkgs:
                    deppkgs[pkgname] = set()
                deppkgs[pkgname].add(pkgmanifest['version'])

        pm = PackageManager(join(util.get_home_dir(), "packages"))
        for manifest in pm.get_installed():
            if manifest['name'] not in names:
                continue
            if (manifest['name'] not in deppkgs or
                    manifest['version'] not in deppkgs[manifest['name']]):
                pm.uninstall(
                    manifest['name'], manifest['version'], trigger_event=False)

        self.reset_cache()
        return True

    def get_installed_boards(self):
        boards = []
        for manifest in self.get_installed():
            p = PlatformFactory.newPlatform(
                self.get_manifest_path(manifest['__pkg_dir']))
            for config in p.get_boards().values():
                boards.append(config.get_brief_data())
        return boards

    @staticmethod
    @util.memoized
    def get_registered_boards():
        return util.get_api_result("/boards", cache_valid="365d")

    def board_config(self, id_):
        for manifest in self.get_installed_boards():
            if manifest['id'] == id_:
                return manifest
        for manifest in self.get_registered_boards():
            if manifest['id'] == id_:
                return manifest
        raise exception.UnknownBoard(id_)


class PlatformFactory(object):

    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_]+", "", name, flags=re.I)
        return "%s%sPlatform" % (name.upper()[0], name.lower()[1:])

    @staticmethod
    def load_module(name, path):
        module = None
        try:
            module = load_source("platformio.managers.platform.%s" % name,
                                 path)
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
            if not requirements and "@" in name:
                name, requirements = name.rsplit("@", 1)
            platform_dir = PlatformManager().get_package_dir(name,
                                                             requirements)

        if not platform_dir:
            raise exception.UnknownPlatform(name if not requirements else
                                            "%s@%s" % (name, requirements))

        platform_cls = None
        if isfile(join(platform_dir, "platform.py")):
            platform_cls = getattr(
                cls.load_module(name, join(platform_dir, "platform.py")),
                cls.get_clsname(name))
        else:
            platform_cls = type(
                str(cls.get_clsname(name)), (PlatformBase, ), {})

        _instance = platform_cls(join(platform_dir, "platform.json"))
        assert isinstance(_instance, PlatformBase)
        return _instance


class PlatformPackagesMixin(object):

    def install_packages(self,
                         with_packages=None,
                         without_packages=None,
                         skip_default_package=False,
                         silent=False):
        with_packages = set(self.pkg_types_to_names(with_packages or []))
        without_packages = set(self.pkg_types_to_names(without_packages or []))

        upkgs = with_packages | without_packages
        ppkgs = set(self.packages.keys())
        if not upkgs.issubset(ppkgs):
            raise exception.UnknownPackage(", ".join(upkgs - ppkgs))

        for name, opts in self.packages.items():
            if name in without_packages:
                continue
            elif (name in with_packages or
                  not (skip_default_package or opts.get("optional", False))):
                if any([s in opts.get("version", "") for s in ("\\", "/")]):
                    self.pm.install(
                        "%s=%s" % (name, opts['version']), silent=silent)
                else:
                    self.pm.install(name, opts.get("version"), silent=silent)

        return True

    def get_installed_packages(self):
        items = {}
        for name, opts in self.packages.items():
            package = self.pm.get_package(name, opts['version'])
            if package:
                items[name] = package
        return items

    def update_packages(self, only_check=False):
        for name in self.get_installed_packages():
            self.pm.update(name, self.packages[name]['version'], only_check)

    def are_outdated_packages(self):
        for name, opts in self.get_installed_packages().items():
            if (opts['version'] != self.pm.get_latest_repo_version(
                    name, self.packages[name].get("version"))):
                return True
        return False

    def get_package_dir(self, name):
        return self.pm.get_package_dir(name,
                                       self.packages[name].get("version"))

    def get_package_version(self, name):
        package = self.pm.get_package(name, self.packages[name].get("version"))
        return package['version'] if package else None


class PlatformRunMixin(object):

    LINE_ERROR_RE = re.compile(r"(^|\s+)error:?\s+", re.I)

    def run(self, variables, targets, silent, verbose):
        assert isinstance(variables, dict)
        assert isinstance(targets, list)

        self.configure_default_packages(variables, targets)
        self.install_packages(silent=True)

        self.silent = silent
        self.verbose = verbose or app.get_setting("force_verbose")

        if "clean" in targets:
            targets = ["-c", "."]

        variables['platform_manifest'] = self.manifest_path

        if "build_script" not in variables:
            variables['build_script'] = self.get_build_script()
        if not isfile(variables['build_script']):
            raise exception.BuildScriptNotFound(variables['build_script'])

        result = self._run_scons(variables, targets)
        assert "returncode" in result

        return result

    def _run_scons(self, variables, targets):
        cmd = [
            util.get_pythonexe_path(),
            join(self.get_package_dir("tool-scons"), "script", "scons"), "-Q",
            "-j %d" % self.get_job_nums(), "--warn=no-no-parallel-support",
            "-f", join(util.get_source_dir(), "builder", "main.py")
        ]
        cmd.append("PIOVERBOSE=%d" % (1 if self.verbose else 0))
        cmd += targets

        # encode and append variables
        for key, value in variables.items():
            cmd.append("%s=%s" % (key.upper(), base64.b64encode(value)))

        util.copy_pythonpath_to_osenv()
        result = util.exec_command(
            cmd,
            stdout=util.AsyncPipe(self.on_run_out),
            stderr=util.AsyncPipe(self.on_run_err))
        return result

    def on_run_out(self, line):
        if "`buildprog' is up to date." in line:
            return
        self._echo_line(line, level=1)

    def on_run_err(self, line):
        is_error = self.LINE_ERROR_RE.search(line) is not None
        self._echo_line(line, level=3 if is_error else 2)

    def _echo_line(self, line, level):
        if line.startswith("scons: "):
            line = line[7:]
        assert 1 <= level <= 3
        if self.silent and (level < 2 or not line):
            return
        fg = (None, "yellow", "red")[level - 1]
        if level == 1 and "is up to date" in line:
            fg = "green"
        click.secho(line, fg=fg, err=level > 1)

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
            join(util.get_home_dir(), "packages"),
            self._manifest.get("packageRepositories"))

        self.silent = False
        self.verbose = False

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
    def vendor_url(self):
        return self._manifest.get("url")

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
        if "packages" not in self._manifest:
            self._manifest['packages'] = {}
        return self._manifest['packages']

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

        def _append_board(board_id, manifest_path):
            config = PlatformBoardConfig(manifest_path)
            if "platform" in config and config.get("platform") != self.name:
                return
            elif ("platforms" in config and
                  self.name not in config.get("platforms")):
                return
            config.manifest['platform'] = self.name
            self._BOARDS_CACHE[board_id] = config

        bdirs = [
            util.get_projectboards_dir(),
            join(util.get_home_dir(), "boards"),
            join(self.get_dir(), "boards"),
        ]

        if id_ is None:
            for boards_dir in bdirs:
                if not isdir(boards_dir):
                    continue
                for item in sorted(os.listdir(boards_dir)):
                    _id = item[:-5]
                    if not item.endswith(".json") or _id in self._BOARDS_CACHE:
                        continue
                    _append_board(_id, join(boards_dir, item))
        else:
            if id_ not in self._BOARDS_CACHE:
                for boards_dir in bdirs:
                    if not isdir(boards_dir):
                        continue
                    manifest_path = join(boards_dir, "%s.json" % id_)
                    if not isfile(manifest_path):
                        continue
                    _append_board(id_, manifest_path)
            if id_ not in self._BOARDS_CACHE:
                raise exception.UnknownBoard(id_)
        return self._BOARDS_CACHE[id_] if id_ else self._BOARDS_CACHE

    def board_config(self, id_):
        return self.get_boards(id_)

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
        # enable used frameworks
        frameworks = variables.get("pioframework", [])
        if not isinstance(frameworks, list):
            frameworks = frameworks.split(", ")
        for framework in frameworks:
            if not self.frameworks:
                continue
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
                elif "nobuild" in targets:
                    # skip all packages, allow only upload tools
                    self.packages[_name]['optional'] = True

        if "__test" in targets and "tool-unity" not in self.packages:
            self.packages['tool-unity'] = {
                "version": "~1.20302.1",
                "optional": False
            }
        if "tool-scons" not in self.packages:
            self.packages['tool-scons'] = {
                "version": "~3.20501.2",
                "optional": False
            }


class PlatformBoardConfig(object):

    def __init__(self, manifest_path):
        self._id = basename(manifest_path)[:-5]
        assert isfile(manifest_path)
        self.manifest_path = manifest_path
        try:
            self._manifest = util.load_json(manifest_path)
        except ValueError:
            raise exception.InvalidBoardManifest(manifest_path)
        if not set(["name", "url", "vendor"]) <= set(self._manifest.keys()):
            raise exception.PlatformioException(
                "Please specify name, url and vendor fields for " +
                manifest_path)

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

    @property
    def id(self):
        return self._id

    @property
    def id_(self):
        return self.id

    @property
    def manifest(self):
        return self._manifest

    def get_brief_data(self):
        return {
            "id": self.id,
            "name": self._manifest['name'],
            "platform": self._manifest.get("platform"),
            "mcu": self._manifest.get("build", {}).get("mcu", "").upper(),
            "fcpu":
            int(self._manifest.get("build", {}).get("f_cpu", "0L")[:-1]),
            "ram": self._manifest.get("upload", {}).get("maximum_ram_size", 0),
            "rom": self._manifest.get("upload", {}).get("maximum_size", 0),
            "frameworks": self._manifest.get("frameworks"),
            "vendor": self._manifest['vendor'],
            "url": self._manifest['url']
        }
