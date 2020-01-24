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

# pylint: disable=too-many-public-methods, too-many-instance-attributes

import base64
import os
import re
import subprocess
import sys
from os.path import basename, dirname, isdir, isfile, join

import click
import semantic_version

from platformio import __version__, app, exception, fs, proc, telemetry, util
from platformio.commands.debug.exception import (
    DebugInvalidOptionsError,
    DebugSupportError,
)
from platformio.compat import PY2, hashlib_encode_data, is_bytes, load_python_module
from platformio.managers.core import get_core_package_dir
from platformio.managers.package import BasePkgManager, PackageManager
from platformio.project.config import ProjectConfig

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


class PlatformManager(BasePkgManager):
    def __init__(self, package_dir=None, repositories=None):
        if not repositories:
            repositories = [
                "https://dl.bintray.com/platformio/dl-platforms/manifest.json",
                "{0}://dl.platformio.org/platforms/manifest.json".format(
                    "https" if app.get_setting("strict_ssl") else "http"
                ),
            ]
        self.config = ProjectConfig.get_instance()
        BasePkgManager.__init__(
            self, package_dir or self.config.get_optional_dir("platforms"), repositories
        )

    @property
    def manifest_names(self):
        return ["platform.json"]

    def get_manifest_path(self, pkg_dir):
        if not isdir(pkg_dir):
            return None
        for name in self.manifest_names:
            manifest_path = join(pkg_dir, name)
            if isfile(manifest_path):
                return manifest_path
        return None

    def install(
        self,
        name,
        requirements=None,
        with_packages=None,
        without_packages=None,
        skip_default_package=False,
        with_all_packages=False,
        after_update=False,
        silent=False,
        force=False,
        **_
    ):  # pylint: disable=too-many-arguments, arguments-differ
        platform_dir = BasePkgManager.install(
            self, name, requirements, silent=silent, force=force
        )
        p = PlatformFactory.newPlatform(platform_dir)

        if with_all_packages:
            with_packages = list(p.packages.keys())

        # don't cleanup packages or install them after update
        # we check packages for updates in def update()
        if after_update:
            p.install_python_packages()
            p.on_installed()
            return True

        p.install_packages(
            with_packages,
            without_packages,
            skip_default_package,
            silent=silent,
            force=force,
        )
        p.install_python_packages()
        p.on_installed()
        return self.cleanup_packages(list(p.packages))

    def uninstall(self, package, requirements=None, after_update=False):
        if isdir(package):
            pkg_dir = package
        else:
            name, requirements, url = self.parse_pkg_uri(package, requirements)
            pkg_dir = self.get_package_dir(name, requirements, url)

        if not pkg_dir:
            raise exception.UnknownPlatform(package)

        p = PlatformFactory.newPlatform(pkg_dir)
        BasePkgManager.uninstall(self, pkg_dir, requirements)
        p.uninstall_python_packages()
        p.on_uninstalled()

        # don't cleanup packages or install them after update
        # we check packages for updates in def update()
        if after_update:
            return True

        return self.cleanup_packages(list(p.packages))

    def update(  # pylint: disable=arguments-differ
        self, package, requirements=None, only_check=False, only_packages=False
    ):
        if isdir(package):
            pkg_dir = package
        else:
            name, requirements, url = self.parse_pkg_uri(package, requirements)
            pkg_dir = self.get_package_dir(name, requirements, url)

        if not pkg_dir:
            raise exception.UnknownPlatform(package)

        p = PlatformFactory.newPlatform(pkg_dir)
        pkgs_before = list(p.get_installed_packages())

        missed_pkgs = set()
        if not only_packages:
            BasePkgManager.update(self, pkg_dir, requirements, only_check)
            p = PlatformFactory.newPlatform(pkg_dir)
            missed_pkgs = set(pkgs_before) & set(p.packages)
            missed_pkgs -= set(p.get_installed_packages())

        p.update_packages(only_check)
        self.cleanup_packages(list(p.packages))

        if missed_pkgs:
            p.install_packages(
                with_packages=list(missed_pkgs), skip_default_package=True
            )

        return True

    def cleanup_packages(self, names):
        self.cache_reset()
        deppkgs = {}
        for manifest in PlatformManager().get_installed():
            p = PlatformFactory.newPlatform(manifest["__pkg_dir"])
            for pkgname, pkgmanifest in p.get_installed_packages().items():
                if pkgname not in deppkgs:
                    deppkgs[pkgname] = set()
                deppkgs[pkgname].add(pkgmanifest["version"])

        pm = PackageManager(self.config.get_optional_dir("packages"))
        for manifest in pm.get_installed():
            if manifest["name"] not in names:
                continue
            if (
                manifest["name"] not in deppkgs
                or manifest["version"] not in deppkgs[manifest["name"]]
            ):
                try:
                    pm.uninstall(manifest["__pkg_dir"], after_update=True)
                except exception.UnknownPackage:
                    pass

        self.cache_reset()
        return True

    @util.memoized(expire="5s")
    def get_installed_boards(self):
        boards = []
        for manifest in self.get_installed():
            p = PlatformFactory.newPlatform(manifest["__pkg_dir"])
            for config in p.get_boards().values():
                board = config.get_brief_data()
                if board not in boards:
                    boards.append(board)
        return boards

    @staticmethod
    def get_registered_boards():
        return util.get_api_result("/boards", cache_valid="7d")

    def get_all_boards(self):
        boards = self.get_installed_boards()
        know_boards = ["%s:%s" % (b["platform"], b["id"]) for b in boards]
        try:
            for board in self.get_registered_boards():
                key = "%s:%s" % (board["platform"], board["id"])
                if key not in know_boards:
                    boards.append(board)
        except (exception.APIRequestError, exception.InternetIsOffline):
            pass
        return sorted(boards, key=lambda b: b["name"])

    def board_config(self, id_, platform=None):
        for manifest in self.get_installed_boards():
            if manifest["id"] == id_ and (
                not platform or manifest["platform"] == platform
            ):
                return manifest
        for manifest in self.get_registered_boards():
            if manifest["id"] == id_ and (
                not platform or manifest["platform"] == platform
            ):
                return manifest
        raise exception.UnknownBoard(id_)


class PlatformFactory(object):
    @staticmethod
    def get_clsname(name):
        name = re.sub(r"[^\da-z\_]+", "", name, flags=re.I)
        return "%s%sPlatform" % (name.upper()[0], name.lower()[1:])

    @staticmethod
    def load_module(name, path):
        try:
            return load_python_module("platformio.managers.platform.%s" % name, path)
        except ImportError:
            raise exception.UnknownPlatform(name)

    @classmethod
    def newPlatform(cls, name, requirements=None):
        pm = PlatformManager()
        platform_dir = None
        if isdir(name):
            platform_dir = name
            name = pm.load_manifest(platform_dir)["name"]
        elif name.endswith("platform.json") and isfile(name):
            platform_dir = dirname(name)
            name = fs.load_json(name)["name"]
        else:
            name, requirements, url = pm.parse_pkg_uri(name, requirements)
            platform_dir = pm.get_package_dir(name, requirements, url)
            if platform_dir:
                name = pm.load_manifest(platform_dir)["name"]

        if not platform_dir:
            raise exception.UnknownPlatform(
                name if not requirements else "%s@%s" % (name, requirements)
            )

        platform_cls = None
        if isfile(join(platform_dir, "platform.py")):
            platform_cls = getattr(
                cls.load_module(name, join(platform_dir, "platform.py")),
                cls.get_clsname(name),
            )
        else:
            platform_cls = type(str(cls.get_clsname(name)), (PlatformBase,), {})

        _instance = platform_cls(join(platform_dir, "platform.json"))
        assert isinstance(_instance, PlatformBase)
        return _instance


class PlatformPackagesMixin(object):
    def install_packages(  # pylint: disable=too-many-arguments
        self,
        with_packages=None,
        without_packages=None,
        skip_default_package=False,
        silent=False,
        force=False,
    ):
        with_packages = set(self.find_pkg_names(with_packages or []))
        without_packages = set(self.find_pkg_names(without_packages or []))

        upkgs = with_packages | without_packages
        ppkgs = set(self.packages)
        if not upkgs.issubset(ppkgs):
            raise exception.UnknownPackage(", ".join(upkgs - ppkgs))

        for name, opts in self.packages.items():
            version = opts.get("version", "")
            if name in without_packages:
                continue
            if name in with_packages or not (
                skip_default_package or opts.get("optional", False)
            ):
                if ":" in version:
                    self.pm.install(
                        "%s=%s" % (name, version), silent=silent, force=force
                    )
                else:
                    self.pm.install(name, version, silent=silent, force=force)

        return True

    def find_pkg_names(self, candidates):
        result = []
        for candidate in candidates:
            found = False

            # lookup by package types
            for _name, _opts in self.packages.items():
                if _opts.get("type") == candidate:
                    result.append(_name)
                    found = True

            if (
                self.frameworks
                and candidate.startswith("framework-")
                and candidate[10:] in self.frameworks
            ):
                result.append(self.frameworks[candidate[10:]]["package"])
                found = True

            if not found:
                result.append(candidate)

        return result

    def update_packages(self, only_check=False):
        for name, manifest in self.get_installed_packages().items():
            requirements = self.packages[name].get("version", "")
            if ":" in requirements:
                _, requirements, __ = self.pm.parse_pkg_uri(requirements)
            self.pm.update(manifest["__pkg_dir"], requirements, only_check)

    def get_installed_packages(self):
        items = {}
        for name in self.packages:
            pkg_dir = self.get_package_dir(name)
            if pkg_dir:
                items[name] = self.pm.load_manifest(pkg_dir)
        return items

    def are_outdated_packages(self):
        for name, manifest in self.get_installed_packages().items():
            requirements = self.packages[name].get("version", "")
            if ":" in requirements:
                _, requirements, __ = self.pm.parse_pkg_uri(requirements)
            if self.pm.outdated(manifest["__pkg_dir"], requirements):
                return True
        return False

    def get_package_dir(self, name):
        version = self.packages[name].get("version", "")
        if ":" in version:
            return self.pm.get_package_dir(
                *self.pm.parse_pkg_uri("%s=%s" % (name, version))
            )
        return self.pm.get_package_dir(name, version)

    def get_package_version(self, name):
        pkg_dir = self.get_package_dir(name)
        if not pkg_dir:
            return None
        return self.pm.load_manifest(pkg_dir).get("version")


class PlatformRunMixin(object):

    LINE_ERROR_RE = re.compile(r"(^|\s+)error:?\s+", re.I)

    @staticmethod
    def encode_scons_arg(value):
        data = base64.urlsafe_b64encode(hashlib_encode_data(value))
        return data.decode() if is_bytes(data) else data

    @staticmethod
    def decode_scons_arg(data):
        value = base64.urlsafe_b64decode(data)
        return value.decode() if is_bytes(value) else value

    def run(  # pylint: disable=too-many-arguments
        self, variables, targets, silent, verbose, jobs
    ):
        assert isinstance(variables, dict)
        assert isinstance(targets, list)

        options = self.config.items(env=variables["pioenv"], as_dict=True)
        if "framework" in options:
            # support PIO Core 3.0 dev/platforms
            options["pioframework"] = options["framework"]
        self.configure_default_packages(options, targets)
        self.install_packages(silent=True)

        self.silent = silent
        self.verbose = verbose or app.get_setting("force_verbose")

        if "clean" in targets:
            targets = ["-c", "."]

        variables["platform_manifest"] = self.manifest_path

        if "build_script" not in variables:
            variables["build_script"] = self.get_build_script()
        if not isfile(variables["build_script"]):
            raise exception.BuildScriptNotFound(variables["build_script"])

        result = self._run_scons(variables, targets, jobs)
        assert "returncode" in result

        return result

    def _run_scons(self, variables, targets, jobs):
        args = [
            proc.get_pythonexe_path(),
            join(get_core_package_dir("tool-scons"), "script", "scons"),
            "-Q",
            "--warn=no-no-parallel-support",
            "--jobs",
            str(jobs),
            "--sconstruct",
            join(fs.get_source_dir(), "builder", "main.py"),
        ]
        args.append("PIOVERBOSE=%d" % (1 if self.verbose else 0))
        # pylint: disable=protected-access
        args.append("ISATTY=%d" % (1 if click._compat.isatty(sys.stdout) else 0))
        args += targets

        # encode and append variables
        for key, value in variables.items():
            args.append("%s=%s" % (key.upper(), self.encode_scons_arg(value)))

        def _write_and_flush(stream, data):
            try:
                stream.write(data)
                stream.flush()
            except IOError:
                pass

        proc.copy_pythonpath_to_osenv()
        if click._compat.isatty(sys.stdout):
            result = proc.exec_command(
                args,
                stdout=proc.BuildAsyncPipe(
                    line_callback=self._on_stdout_line,
                    data_callback=lambda data: _write_and_flush(sys.stdout, data),
                ),
                stderr=proc.BuildAsyncPipe(
                    line_callback=self._on_stderr_line,
                    data_callback=lambda data: _write_and_flush(sys.stderr, data),
                ),
            )
        else:
            result = proc.exec_command(
                args,
                stdout=proc.LineBufferedAsyncPipe(line_callback=self._on_stdout_line),
                stderr=proc.LineBufferedAsyncPipe(line_callback=self._on_stderr_line),
            )
        return result

    def _on_stdout_line(self, line):
        if "`buildprog' is up to date." in line:
            return
        self._echo_line(line, level=1)

    def _on_stderr_line(self, line):
        is_error = self.LINE_ERROR_RE.search(line) is not None
        self._echo_line(line, level=3 if is_error else 2)

        a_pos = line.find("fatal error:")
        b_pos = line.rfind(": No such file or directory")
        if a_pos == -1 or b_pos == -1:
            return
        self._echo_missed_dependency(line[a_pos + 12 : b_pos].strip())

    def _echo_line(self, line, level):
        if line.startswith("scons: "):
            line = line[7:]
        assert 1 <= level <= 3
        if self.silent and (level < 2 or not line):
            return
        fg = (None, "yellow", "red")[level - 1]
        if level == 1 and "is up to date" in line:
            fg = "green"
        click.secho(line, fg=fg, err=level > 1, nl=False)

    @staticmethod
    def _echo_missed_dependency(filename):
        if "/" in filename or not filename.endswith((".h", ".hpp")):
            return
        banner = """
{dots}
* Looking for {filename_styled} dependency? Check our library registry!
*
* CLI  > platformio lib search "header:{filename}"
* Web  > {link}
*
{dots}
""".format(
            filename=filename,
            filename_styled=click.style(filename, fg="cyan"),
            link=click.style(
                "https://platformio.org/lib/search?query=header:%s"
                % quote(filename, safe=""),
                fg="blue",
            ),
            dots="*" * (56 + len(filename)),
        )
        click.echo(banner, err=True)


class PlatformBase(PlatformPackagesMixin, PlatformRunMixin):

    PIO_VERSION = semantic_version.Version(util.pepver_to_semver(__version__))
    _BOARDS_CACHE = {}

    def __init__(self, manifest_path):
        self.manifest_path = manifest_path
        self.silent = False
        self.verbose = False

        self._BOARDS_CACHE = {}
        self._manifest = fs.load_json(manifest_path)
        self._custom_packages = None

        self.config = ProjectConfig.get_instance()
        self.pm = PackageManager(
            self.config.get_optional_dir("packages"), self.package_repositories
        )
        # if self.engines and "platformio" in self.engines:
        #     if self.PIO_VERSION not in semantic_version.SimpleSpec(
        #             self.engines['platformio']):
        #         raise exception.IncompatiblePlatform(self.name,
        #                                              str(self.PIO_VERSION))

    @property
    def name(self):
        return self._manifest["name"]

    @property
    def title(self):
        return self._manifest["title"]

    @property
    def description(self):
        return self._manifest["description"]

    @property
    def version(self):
        return self._manifest["version"]

    @property
    def homepage(self):
        return self._manifest.get("homepage")

    @property
    def vendor_url(self):
        return self._manifest.get("url")

    @property
    def docs_url(self):
        return self._manifest.get("docs")

    @property
    def repository_url(self):
        return self._manifest.get("repository", {}).get("url")

    @property
    def license(self):
        return self._manifest.get("license")

    @property
    def frameworks(self):
        return self._manifest.get("frameworks")

    @property
    def engines(self):
        return self._manifest.get("engines")

    @property
    def package_repositories(self):
        return self._manifest.get("packageRepositories")

    @property
    def manifest(self):
        return self._manifest

    @property
    def packages(self):
        packages = self._manifest.get("packages", {})
        for item in self._custom_packages or []:
            name = item
            version = "*"
            if "@" in item:
                name, version = item.split("@", 2)
            name = name.strip()
            if name not in packages:
                packages[name] = {}
            packages[name].update({"version": version.strip(), "optional": False})
        return packages

    @property
    def python_packages(self):
        return self._manifest.get("pythonPackages")

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
            if "platforms" in config and self.name not in config.get("platforms"):
                return
            config.manifest["platform"] = self.name
            self._BOARDS_CACHE[board_id] = config

        bdirs = [
            self.config.get_optional_dir("boards"),
            join(self.config.get_optional_dir("core"), "boards"),
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
                    if isfile(manifest_path):
                        _append_board(id_, manifest_path)
                        break
            if id_ not in self._BOARDS_CACHE:
                raise exception.UnknownBoard(id_)
        return self._BOARDS_CACHE[id_] if id_ else self._BOARDS_CACHE

    def board_config(self, id_):
        return self.get_boards(id_)

    def get_package_type(self, name):
        return self.packages[name].get("type")

    def configure_default_packages(self, options, targets):
        # override user custom packages
        self._custom_packages = options.get("platform_packages")

        # enable used frameworks
        for framework in options.get("framework", []):
            if not self.frameworks:
                continue
            framework = framework.lower().strip()
            if not framework or framework not in self.frameworks:
                continue
            _pkg_name = self.frameworks[framework].get("package")
            if _pkg_name:
                self.packages[_pkg_name]["optional"] = False

        # enable upload tools for upload targets
        if any(["upload" in t for t in targets] + ["program" in targets]):
            for name, opts in self.packages.items():
                if opts.get("type") == "uploader":
                    self.packages[name]["optional"] = False
                # skip all packages in "nobuild" mode
                # allow only upload tools and frameworks
                elif "nobuild" in targets and opts.get("type") != "framework":
                    self.packages[name]["optional"] = True

    def get_lib_storages(self):
        storages = {}
        for opts in (self.frameworks or {}).values():
            if "package" not in opts:
                continue
            pkg_dir = self.get_package_dir(opts["package"])
            if not pkg_dir or not isdir(join(pkg_dir, "libraries")):
                continue
            libs_dir = join(pkg_dir, "libraries")
            storages[libs_dir] = opts["package"]
            libcores_dir = join(libs_dir, "__cores__")
            if not isdir(libcores_dir):
                continue
            for item in os.listdir(libcores_dir):
                libcore_dir = join(libcores_dir, item)
                if not isdir(libcore_dir):
                    continue
                storages[libcore_dir] = "%s-core-%s" % (opts["package"], item)

        return [dict(name=name, path=path) for path, name in storages.items()]

    def on_installed(self):
        pass

    def on_uninstalled(self):
        pass

    def install_python_packages(self):
        if not self.python_packages:
            return None
        click.echo(
            "Installing Python packages: %s"
            % ", ".join(list(self.python_packages.keys())),
        )
        args = [proc.get_pythonexe_path(), "-m", "pip", "install", "--upgrade"]
        for name, requirements in self.python_packages.items():
            if any(c in requirements for c in ("<", ">", "=")):
                args.append("%s%s" % (name, requirements))
            else:
                args.append("%s==%s" % (name, requirements))
        try:
            return subprocess.call(args) == 0
        except Exception as e:  # pylint: disable=broad-except
            click.secho(
                "Could not install Python packages -> %s" % e, fg="red", err=True
            )

    def uninstall_python_packages(self):
        if not self.python_packages:
            return
        click.echo("Uninstalling Python packages")
        args = [proc.get_pythonexe_path(), "-m", "pip", "uninstall", "--yes"]
        args.extend(list(self.python_packages.keys()))
        try:
            subprocess.call(args) == 0
        except Exception as e:  # pylint: disable=broad-except
            click.secho(
                "Could not install Python packages -> %s" % e, fg="red", err=True
            )


class PlatformBoardConfig(object):
    def __init__(self, manifest_path):
        self._id = basename(manifest_path)[:-5]
        assert isfile(manifest_path)
        self.manifest_path = manifest_path
        try:
            self._manifest = fs.load_json(manifest_path)
        except ValueError:
            raise exception.InvalidBoardManifest(manifest_path)
        if not set(["name", "url", "vendor"]) <= set(self._manifest):
            raise exception.PlatformioException(
                "Please specify name, url and vendor fields for " + manifest_path
            )

    def get(self, path, default=None):
        try:
            value = self._manifest
            for k in path.split("."):
                value = value[k]
            # pylint: disable=undefined-variable
            if PY2 and isinstance(value, unicode):
                # cast to plain string from unicode for PY2, resolves issue in
                # dev/platform when BoardConfig.get() is used in pair with
                # os.path.join(file_encoding, unicode_encoding)
                try:
                    value = value.encode("utf-8")
                except UnicodeEncodeError:
                    pass
            return value
        except KeyError:
            if default is not None:
                return default
        raise KeyError("Invalid board option '%s'" % path)

    def update(self, path, value):
        newdict = None
        for key in path.split(".")[::-1]:
            if newdict is None:
                newdict = {key: value}
            else:
                newdict = {key: newdict}
        util.merge_dicts(self._manifest, newdict)

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
            "name": self._manifest["name"],
            "platform": self._manifest.get("platform"),
            "mcu": self._manifest.get("build", {}).get("mcu", "").upper(),
            "fcpu": int(
                "".join(
                    [
                        c
                        for c in str(self._manifest.get("build", {}).get("f_cpu", "0L"))
                        if c.isdigit()
                    ]
                )
            ),
            "ram": self._manifest.get("upload", {}).get("maximum_ram_size", 0),
            "rom": self._manifest.get("upload", {}).get("maximum_size", 0),
            "connectivity": self._manifest.get("connectivity"),
            "frameworks": self._manifest.get("frameworks"),
            "debug": self.get_debug_data(),
            "vendor": self._manifest["vendor"],
            "url": self._manifest["url"],
        }

    def get_debug_data(self):
        if not self._manifest.get("debug", {}).get("tools"):
            return None
        tools = {}
        for name, options in self._manifest["debug"]["tools"].items():
            tools[name] = {}
            for key, value in options.items():
                if key in ("default", "onboard"):
                    tools[name][key] = value
        return {"tools": tools}

    def get_debug_tool_name(self, custom=None):
        debug_tools = self._manifest.get("debug", {}).get("tools")
        tool_name = custom
        if tool_name == "custom":
            return tool_name
        if not debug_tools:
            telemetry.send_event("Debug", "Request", self.id)
            raise DebugSupportError(self._manifest["name"])
        if tool_name:
            if tool_name in debug_tools:
                return tool_name
            raise DebugInvalidOptionsError(
                "Unknown debug tool `%s`. Please use one of `%s` or `custom`"
                % (tool_name, ", ".join(sorted(list(debug_tools))))
            )

        # automatically select best tool
        data = {"default": [], "onboard": [], "external": []}
        for key, value in debug_tools.items():
            if value.get("default"):
                data["default"].append(key)
            elif value.get("onboard"):
                data["onboard"].append(key)
            data["external"].append(key)

        for key, value in data.items():
            if not value:
                continue
            return sorted(value)[0]

        assert any(item for item in data)
