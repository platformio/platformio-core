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

# pylint: disable=no-member, no-self-use, unused-argument
# pylint: disable=too-many-instance-attributes, too-many-public-methods

from __future__ import absolute_import

import hashlib
import os
import sys
from glob import glob
from os.path import (basename, commonprefix, dirname, isdir, isfile, join,
                     realpath, sep)

import SCons.Scanner
from SCons.Script import ARGUMENTS, COMMAND_LINE_TARGETS, DefaultEnvironment

from platformio import exception, util
from platformio.builder.tools import platformio as piotool
from platformio.managers.lib import LibraryManager
from platformio.managers.package import PackageManager


class LibBuilderFactory(object):

    @staticmethod
    def new(env, path, verbose=False):
        clsname = "UnknownLibBuilder"
        if isfile(join(path, "library.json")):
            clsname = "PlatformIOLibBuilder"
        else:
            used_frameworks = LibBuilderFactory.get_used_frameworks(env, path)
            common_frameworks = (
                set(env.get("PIOFRAMEWORK", [])) & set(used_frameworks))
            if common_frameworks:
                clsname = "%sLibBuilder" % list(common_frameworks)[0].title()
            elif used_frameworks:
                clsname = "%sLibBuilder" % used_frameworks[0].title()

        obj = getattr(sys.modules[__name__], clsname)(
            env, path, verbose=verbose)
        assert isinstance(obj, LibBuilderBase)
        return obj

    @staticmethod
    def get_used_frameworks(env, path):
        if any(
                isfile(join(path, fname))
                for fname in ("library.properties", "keywords.txt")):
            return ["arduino"]

        if isfile(join(path, "module.json")):
            return ["mbed"]

        # check source files
        for root, _, files in os.walk(path, followlinks=True):
            for fname in files:
                if not env.IsFileWithExt(
                        fname, piotool.SRC_BUILD_EXT + piotool.SRC_HEADER_EXT):
                    continue
                with open(join(root, fname)) as f:
                    content = f.read()
                    if "Arduino.h" in content:
                        return ["arduino"]
                    elif "mbed.h" in content:
                        return ["mbed"]
        return []


class LibBuilderBase(object):

    IS_WINDOWS = "windows" in util.get_systype()

    LDF_MODES = ["off", "chain", "deep", "chain+", "deep+"]
    LDF_MODE_DEFAULT = "chain"

    COMPAT_MODES = ["off", "soft", "strict"]
    COMPAT_MODE_DEFAULT = "soft"

    CLASSIC_SCANNER = SCons.Scanner.C.CScanner()
    CCONDITIONAL_SCANNER = SCons.Scanner.C.CConditionalScanner()
    # Max depth of nested includes:
    # -1 = unlimited
    # 0 - disabled nesting
    # >0 - number of allowed nested includes
    CCONDITIONAL_SCANNER_DEPTH = 99
    PARSE_SRC_BY_H_NAME = True

    _INCLUDE_DIRS_CACHE = None

    def __init__(self, env, path, manifest=None, verbose=False):
        self.env = env.Clone()
        self.envorigin = env.Clone()
        self.path = realpath(env.subst(path))
        self.verbose = verbose

        self._manifest = manifest if manifest else self.load_manifest()
        self._is_dependent = False
        self._is_built = False
        self._depbuilders = list()
        self._circular_deps = list()
        self._processed_files = list()

        # reset source filter, could be overridden with extra script
        self.env['SRC_FILTER'] = ""

        # process extra options and append to build environment
        self.process_extra_options()

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.path)

    def __contains__(self, path):
        p1 = self.path
        p2 = path
        if self.IS_WINDOWS:
            p1 = p1.lower()
            p2 = p2.lower()
        return commonprefix((p1 + sep, p2)) == p1 + sep

    @property
    def name(self):
        return self._manifest.get("name", basename(self.path))

    @property
    def version(self):
        return self._manifest.get("version")

    @property
    def vcs_info(self):
        items = glob(join(self.path, ".*", PackageManager.SRC_MANIFEST_NAME))
        if not items:
            return None
        return util.load_json(items[0])

    @property
    def dependencies(self):
        return LibraryManager.normalize_dependencies(
            self._manifest.get("dependencies", []))

    @property
    def src_filter(self):
        return piotool.SRC_FILTER_DEFAULT + [
            "-<example%s>" % os.sep,
            "-<examples%s>" % os.sep,
            "-<test%s>" % os.sep,
            "-<tests%s>" % os.sep
        ]

    @property
    def include_dir(self):
        if not all(isdir(join(self.path, d)) for d in ("include", "src")):
            return None
        return join(self.path, "include")

    @property
    def src_dir(self):
        return (join(self.path, "src")
                if isdir(join(self.path, "src")) else self.path)

    def get_include_dirs(self):
        items = [self.src_dir]
        include_dir = self.include_dir
        if include_dir and include_dir not in items:
            items.append(include_dir)
        return items

    @property
    def build_dir(self):
        return join("$BUILD_DIR",
                    "lib%s" % hashlib.sha1(self.path).hexdigest()[:3],
                    basename(self.path))

    @property
    def build_flags(self):
        return None

    @property
    def build_unflags(self):
        return None

    @property
    def extra_script(self):
        return None

    @property
    def lib_archive(self):
        return self.env.get("LIB_ARCHIVE", "") != "false"

    @property
    def lib_ldf_mode(self):
        return self.validate_ldf_mode(
            self.env.get("LIB_LDF_MODE", self.LDF_MODE_DEFAULT))

    @property
    def lib_compat_mode(self):
        return self.validate_compat_mode(
            self.env.get("LIB_COMPAT_MODE", self.COMPAT_MODE_DEFAULT))

    @property
    def depbuilders(self):
        return self._depbuilders

    @property
    def dependent(self):
        return self._is_dependent

    @property
    def is_built(self):
        return self._is_built

    @staticmethod
    def validate_ldf_mode(mode):
        if isinstance(mode, basestring):
            mode = mode.strip().lower()
        if mode in LibBuilderBase.LDF_MODES:
            return mode
        try:
            return LibBuilderBase.LDF_MODES[int(mode)]
        except (IndexError, ValueError):
            pass
        return LibBuilderBase.LDF_MODE_DEFAULT

    @staticmethod
    def validate_compat_mode(mode):
        if isinstance(mode, basestring):
            mode = mode.strip().lower()
        if mode in LibBuilderBase.COMPAT_MODES:
            return mode
        try:
            return LibBuilderBase.COMPAT_MODES[int(mode)]
        except (IndexError, ValueError):
            pass
        return LibBuilderBase.COMPAT_MODE_DEFAULT

    def is_platforms_compatible(self, platforms):
        return True

    def is_frameworks_compatible(self, frameworks):
        return True

    def load_manifest(self):
        return {}

    def process_extra_options(self):
        with util.cd(self.path):
            self.env.ProcessUnFlags(self.build_unflags)
            self.env.ProcessFlags(self.build_flags)
            if self.extra_script:
                self.env.SConscriptChdir(1)
                self.env.SConscript(
                    realpath(self.extra_script),
                    exports={
                        "env": self.env,
                        "pio_lib_builder": self
                    })

    def process_dependencies(self):
        if not self.dependencies:
            return
        for item in self.dependencies:
            skip = False
            for key in ("platforms", "frameworks"):
                env_key = "PIO" + key.upper()[:-1]
                if env_key not in self.env:
                    continue
                if (key in item and
                        not util.items_in_list(self.env[env_key], item[key])):
                    if self.verbose:
                        sys.stderr.write("Skip %s incompatible dependency %s\n"
                                         % (key[:-1], item))
                    skip = True
            if skip:
                continue

            found = False
            for lb in self.env.GetLibBuilders():
                if item['name'] != lb.name:
                    continue
                elif "frameworks" in item and \
                     not lb.is_frameworks_compatible(item["frameworks"]):
                    continue
                elif "platforms" in item and \
                     not lb.is_platforms_compatible(item["platforms"]):
                    continue
                found = True
                self.depend_recursive(lb)
                break

            if not found:
                sys.stderr.write(
                    "Error: Could not find `%s` dependency for `%s` "
                    "library\n" % (item['name'], self.name))
                self.env.Exit(1)

    def get_search_files(self):
        items = [
            join(self.src_dir, item) for item in self.env.MatchSourceFiles(
                self.src_dir, self.src_filter)
        ]
        include_dir = self.include_dir
        if include_dir:
            items.extend([
                join(include_dir, item)
                for item in self.env.MatchSourceFiles(include_dir)
            ])
        return items

    def _validate_search_files(self, search_files=None):
        if not search_files:
            search_files = []
        assert isinstance(search_files, list)

        _search_files = []
        for path in search_files:
            if path not in self._processed_files:
                _search_files.append(path)
                self._processed_files.append(path)

        return _search_files

    def _get_found_includes(self, search_files=None):
        # all include directories
        if not LibBuilderBase._INCLUDE_DIRS_CACHE:
            LibBuilderBase._INCLUDE_DIRS_CACHE = []
            for lb in self.env.GetLibBuilders():
                LibBuilderBase._INCLUDE_DIRS_CACHE.extend(
                    [self.env.Dir(d) for d in lb.get_include_dirs()])

        # append self include directories
        include_dirs = [self.env.Dir(d) for d in self.get_include_dirs()]
        include_dirs.extend(LibBuilderBase._INCLUDE_DIRS_CACHE)

        result = []
        for path in self._validate_search_files(search_files):
            try:
                assert "+" in self.lib_ldf_mode
                candidates = LibBuilderBase.CCONDITIONAL_SCANNER(
                    self.env.File(path),
                    self.env,
                    tuple(include_dirs),
                    depth=self.CCONDITIONAL_SCANNER_DEPTH)
            except Exception as e:  # pylint: disable=broad-except
                if self.verbose and "+" in self.lib_ldf_mode:
                    sys.stderr.write(
                        "Warning! Classic Pre Processor is used for `%s`, "
                        "advanced has failed with `%s`\n" % (path, e))
                candidates = LibBuilderBase.CLASSIC_SCANNER(
                    self.env.File(path), self.env, tuple(include_dirs))

            # print(path, map(lambda n: n.get_abspath(), candidates))
            for item in candidates:
                if item not in result:
                    result.append(item)
                if not self.PARSE_SRC_BY_H_NAME:
                    continue
                _h_path = item.get_abspath()
                if not self.env.IsFileWithExt(_h_path, piotool.SRC_HEADER_EXT):
                    continue
                _f_part = _h_path[:_h_path.rindex(".")]
                for ext in piotool.SRC_C_EXT:
                    if not isfile("%s.%s" % (_f_part, ext)):
                        continue
                    _c_path = self.env.File("%s.%s" % (_f_part, ext))
                    if _c_path not in result:
                        result.append(_c_path)

        return result

    def depend_recursive(self, lb, search_files=None):

        def _already_depends(_lb):
            if self in _lb.depbuilders:
                return True
            for __lb in _lb.depbuilders:
                if _already_depends(__lb):
                    return True
            return False

        # assert isinstance(lb, LibBuilderBase)
        if self != lb:
            if _already_depends(lb):
                if self.verbose:
                    sys.stderr.write(
                        "Warning! Circular dependencies detected "
                        "between `%s` and `%s`\n" % (self.path, lb.path))
                self._circular_deps.append(lb)
            elif lb not in self._depbuilders:
                self._depbuilders.append(lb)
                LibBuilderBase._INCLUDE_DIRS_CACHE = None
        lb.search_deps_recursive(search_files)

    def search_deps_recursive(self, search_files=None):
        if not self._is_dependent:
            self._is_dependent = True
            self.process_dependencies()

            if self.lib_ldf_mode.startswith("deep"):
                search_files = self.get_search_files()

        # when LDF is disabled
        if self.lib_ldf_mode == "off":
            return

        lib_inc_map = {}
        for inc in self._get_found_includes(search_files):
            for lb in self.env.GetLibBuilders():
                if inc.get_abspath() in lb:
                    if lb not in lib_inc_map:
                        lib_inc_map[lb] = []
                    lib_inc_map[lb].append(inc.get_abspath())
                    break

        for lb, lb_search_files in lib_inc_map.items():
            self.depend_recursive(lb, lb_search_files)

    def build(self):
        libs = []
        for lb in self._depbuilders:
            libs.extend(lb.build())
            # copy shared information to self env
            for key in ("CPPPATH", "LIBPATH", "LIBS", "LINKFLAGS"):
                self.env.PrependUnique(**{key: lb.env.get(key)})

        for lb in self._circular_deps:
            self.env.PrependUnique(CPPPATH=lb.get_include_dirs())

        if self._is_built:
            return libs
        self._is_built = True

        self.env.PrependUnique(CPPPATH=self.get_include_dirs())

        if self.lib_ldf_mode == "off":
            for lb in self.env.GetLibBuilders():
                if self == lb or not lb.is_built:
                    continue
                for key in ("CPPPATH", "LIBPATH", "LIBS", "LINKFLAGS"):
                    self.env.PrependUnique(**{key: lb.env.get(key)})

        if self.lib_archive:
            libs.append(
                self.env.BuildLibrary(self.build_dir, self.src_dir,
                                      self.src_filter))
        else:
            self.env.BuildSources(self.build_dir, self.src_dir,
                                  self.src_filter)
        return libs


class UnknownLibBuilder(LibBuilderBase):
    pass


class ArduinoLibBuilder(LibBuilderBase):

    def load_manifest(self):
        manifest = {}
        if not isfile(join(self.path, "library.properties")):
            return manifest
        with open(join(self.path, "library.properties")) as fp:
            for line in fp.readlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                manifest[key.strip()] = value.strip()
        return manifest

    def get_include_dirs(self):
        include_dirs = LibBuilderBase.get_include_dirs(self)
        if isdir(join(self.path, "src")):
            return include_dirs
        if isdir(join(self.path, "utility")):
            include_dirs.append(join(self.path, "utility"))
        return include_dirs

    @property
    def src_filter(self):
        src_dir = join(self.path, "src")
        if isdir(src_dir):
            src_filter = LibBuilderBase.src_filter.fget(self)
            for root, _, files in os.walk(src_dir, followlinks=True):
                found = False
                for fname in files:
                    if fname.lower().endswith("asm"):
                        found = True
                        break
                if not found:
                    continue
                rel_path = root.replace(src_dir, "")
                if rel_path.startswith(sep):
                    rel_path = rel_path[1:] + sep
                src_filter.append("-<%s*.[aA][sS][mM]>" % rel_path)
            return src_filter

        src_filter = []
        is_utility = isdir(join(self.path, "utility"))
        for ext in piotool.SRC_BUILD_EXT + piotool.SRC_HEADER_EXT:
            # arduino ide ignores files with .asm or .ASM extensions
            if ext.lower() == "asm":
                continue
            src_filter.append("+<*.%s>" % ext)
            if is_utility:
                src_filter.append("+<utility%s*.%s>" % (sep, ext))
        return src_filter

    def is_frameworks_compatible(self, frameworks):
        return util.items_in_list(frameworks, ["arduino", "energia"])

    def is_platforms_compatible(self, platforms):
        platforms_map = {
            "avr": "atmelavr",
            "sam": "atmelsam",
            "samd": "atmelsam",
            "esp8266": "espressif8266",
            "esp32": "espressif32",
            "arc32": "intel_arc32",
            "stm32": "ststm32"
        }
        items = []
        for arch in self._manifest.get("architectures", "").split(","):
            arch = arch.strip()
            if arch == "*":
                items = "*"
                break
            if arch in platforms_map:
                items.append(platforms_map[arch])
        if not items:
            return LibBuilderBase.is_platforms_compatible(self, platforms)
        return util.items_in_list(platforms, items)


class MbedLibBuilder(LibBuilderBase):

    def load_manifest(self):
        if not isfile(join(self.path, "module.json")):
            return {}
        return util.load_json(join(self.path, "module.json"))

    @property
    def include_dir(self):
        if isdir(join(self.path, "include")):
            return join(self.path, "include")
        return None

    @property
    def src_dir(self):
        if isdir(join(self.path, "source")):
            return join(self.path, "source")
        return LibBuilderBase.src_dir.fget(self)

    def get_include_dirs(self):
        include_dirs = LibBuilderBase.get_include_dirs(self)
        if self.path not in include_dirs:
            include_dirs.append(self.path)

        # library with module.json
        for p in self._manifest.get("extraIncludes", []):
            include_dirs.append(join(self.path, p))

        # old mbed library without manifest, add to CPPPATH all folders
        if not self._manifest:
            for root, _, __ in os.walk(self.path):
                part = root.replace(self.path, "").lower()
                if any(s in part for s in ("%s." % sep, "test", "example")):
                    continue
                if root not in include_dirs:
                    include_dirs.append(root)

        return include_dirs

    def is_frameworks_compatible(self, frameworks):
        return util.items_in_list(frameworks, ["mbed"])


class PlatformIOLibBuilder(LibBuilderBase):

    def load_manifest(self):
        assert isfile(join(self.path, "library.json"))
        manifest = util.load_json(join(self.path, "library.json"))
        assert "name" in manifest

        # replace "espressif" old name dev/platform with ESP8266
        if "platforms" in manifest:
            manifest['platforms'] = [
                "espressif8266" if p == "espressif" else p
                for p in util.items_to_list(manifest['platforms'])
            ]

        return manifest

    def _is_arduino_manifest(self):
        return isfile(join(self.path, "library.properties"))

    @property
    def src_filter(self):
        if "srcFilter" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("srcFilter")
        elif self.env['SRC_FILTER']:
            return self.env['SRC_FILTER']
        elif self._is_arduino_manifest():
            return ArduinoLibBuilder.src_filter.fget(self)
        return LibBuilderBase.src_filter.fget(self)

    @property
    def build_flags(self):
        if "flags" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("flags")
        return LibBuilderBase.build_flags.fget(self)

    @property
    def build_unflags(self):
        if "unflags" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("unflags")
        return LibBuilderBase.build_unflags.fget(self)

    @property
    def extra_script(self):
        if "extraScript" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("extraScript")
        return LibBuilderBase.extra_script.fget(self)

    @property
    def lib_archive(self):
        if "libArchive" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("libArchive")
        return LibBuilderBase.lib_archive.fget(self)

    @property
    def lib_ldf_mode(self):
        if "libLDFMode" in self._manifest.get("build", {}):
            return self.validate_ldf_mode(
                self._manifest.get("build").get("libLDFMode"))
        return LibBuilderBase.lib_ldf_mode.fget(self)

    @property
    def lib_compat_mode(self):
        if "libCompatMode" in self._manifest.get("build", {}):
            return self.validate_compat_mode(
                self._manifest.get("build").get("libCompatMode"))
        return LibBuilderBase.lib_compat_mode.fget(self)

    def is_platforms_compatible(self, platforms):
        items = self._manifest.get("platforms")
        if not items:
            return LibBuilderBase.is_platforms_compatible(self, platforms)
        return util.items_in_list(platforms, items)

    def is_frameworks_compatible(self, frameworks):
        items = self._manifest.get("frameworks")
        if not items:
            return LibBuilderBase.is_frameworks_compatible(self, frameworks)
        return util.items_in_list(frameworks, items)

    def get_include_dirs(self):
        include_dirs = LibBuilderBase.get_include_dirs(self)

        # backwards compatibility with PlatformIO 2.0
        if ("build" not in self._manifest and self._is_arduino_manifest()
                and not isdir(join(self.path, "src"))
                and isdir(join(self.path, "utility"))):
            include_dirs.append(join(self.path, "utility"))

        for path in self.env.get("CPPPATH", []):
            if path not in self.envorigin.get("CPPPATH", []):
                include_dirs.append(self.env.subst(path))
        return include_dirs


class ProjectAsLibBuilder(LibBuilderBase):

    def __init__(self, env, *args, **kwargs):
        # backup original value, will be reset in base.__init__
        project_src_filter = env.get("SRC_FILTER")
        super(ProjectAsLibBuilder, self).__init__(env, *args, **kwargs)
        self.env['SRC_FILTER'] = project_src_filter

    @property
    def include_dir(self):
        include_dir = self.env.subst("$PROJECTINCLUDE_DIR")
        return include_dir if isdir(include_dir) else None

    @property
    def src_dir(self):
        return self.env.subst("$PROJECTSRC_DIR")

    def get_include_dirs(self):
        include_dirs = LibBuilderBase.get_include_dirs(self)
        project_include_dir = self.env.subst("$PROJECTINCLUDE_DIR")
        if isdir(project_include_dir):
            include_dirs.append(project_include_dir)
        return include_dirs

    def get_search_files(self):
        # project files
        items = LibBuilderBase.get_search_files(self)
        # test files
        if "__test" in COMMAND_LINE_TARGETS:
            items.extend([
                join("$PROJECTTEST_DIR",
                     item) for item in self.env.MatchSourceFiles(
                         "$PROJECTTEST_DIR", "$PIOTEST_SRC_FILTER")
            ])
        return items

    @property
    def lib_ldf_mode(self):
        mode = LibBuilderBase.lib_ldf_mode.fget(self)
        if not mode.startswith("chain"):
            return mode
        # parse all project files
        return "deep+" if "+" in mode else "deep"

    @property
    def src_filter(self):
        return (self.env.get("SRC_FILTER")
                or LibBuilderBase.src_filter.fget(self))

    def process_extra_options(self):
        # skip for project, options are already processed
        pass

    def process_dependencies(self):  # pylint: disable=too-many-branches
        uris = self.env.get("LIB_DEPS", [])
        if not uris:
            return
        storage_dirs = []
        for lb in self.env.GetLibBuilders():
            if dirname(lb.path) not in storage_dirs:
                storage_dirs.append(dirname(lb.path))

        for uri in uris:
            found = False
            for storage_dir in storage_dirs:
                if found:
                    break
                lm = LibraryManager(storage_dir)
                pkg_dir = lm.get_package_dir(*lm.parse_pkg_uri(uri))
                if not pkg_dir:
                    continue
                for lb in self.env.GetLibBuilders():
                    if lb.path != pkg_dir:
                        continue
                    if lb not in self.depbuilders:
                        self.depend_recursive(lb)
                    found = True
                    break

            if not found:
                for lb in self.env.GetLibBuilders():
                    if lb.name != uri:
                        continue
                    if lb not in self.depbuilders:
                        self.depend_recursive(lb)
                    break

    def build(self):
        self._is_built = True  # do not build Project now
        self.env.PrependUnique(CPPPATH=self.get_include_dirs())
        return LibBuilderBase.build(self)


def GetLibBuilders(env):  # pylint: disable=too-many-branches

    if "__PIO_LIB_BUILDERS" in DefaultEnvironment():
        return sorted(
            DefaultEnvironment()['__PIO_LIB_BUILDERS'],
            key=lambda lb: 0 if lb.dependent else 1)

    items = []
    verbose = int(ARGUMENTS.get("PIOVERBOSE",
                                0)) and not env.GetOption('clean')

    def _check_lib_builder(lb):
        compat_mode = lb.lib_compat_mode
        if lb.name in env.get("LIB_IGNORE", []):
            if verbose:
                sys.stderr.write("Ignored library %s\n" % lb.path)
            return None
        if compat_mode == "strict" and not lb.is_platforms_compatible(
                env['PIOPLATFORM']):
            if verbose:
                sys.stderr.write(
                    "Platform incompatible library %s\n" % lb.path)
            return False
        if compat_mode == "soft" and "PIOFRAMEWORK" in env and \
           not lb.is_frameworks_compatible(env.get("PIOFRAMEWORK", [])):
            if verbose:
                sys.stderr.write(
                    "Framework incompatible library %s\n" % lb.path)
            return False
        return True

    found_incompat = False
    for libs_dir in env['LIBSOURCE_DIRS']:
        libs_dir = env.subst(libs_dir)
        if not isdir(libs_dir):
            continue
        for item in sorted(os.listdir(libs_dir)):
            if item == "__cores__" or not isdir(join(libs_dir, item)):
                continue
            try:
                lb = LibBuilderFactory.new(
                    env, join(libs_dir, item), verbose=verbose)
            except exception.InvalidJSONFile:
                if verbose:
                    sys.stderr.write("Skip library with broken manifest: %s\n"
                                     % join(libs_dir, item))
                continue
            if _check_lib_builder(lb):
                items.append(lb)
            else:
                found_incompat = True

    for lb in env.get("EXTRA_LIB_BUILDERS", []):
        if _check_lib_builder(lb):
            items.append(lb)
        else:
            found_incompat = True

    if verbose and found_incompat:
        sys.stderr.write(
            "More details about \"Library Compatibility Mode\": "
            "https://docs.platformio.org/page/librarymanager/ldf.html#"
            "ldf-compat-mode\n")

    DefaultEnvironment()['__PIO_LIB_BUILDERS'] = items
    return items


def ConfigureProjectLibBuilder(env):

    def correct_found_libs(lib_builders):
        # build full dependency graph
        found_lbs = [lb for lb in lib_builders if lb.dependent]
        for lb in lib_builders:
            if lb in found_lbs:
                lb.search_deps_recursive(lb.get_search_files())
        for lb in lib_builders:
            for deplb in lb.depbuilders[:]:
                if deplb not in found_lbs:
                    lb.depbuilders.remove(deplb)

    def print_deps_tree(root, level=0):
        margin = "|   " * (level)
        for lb in root.depbuilders:
            title = "<%s>" % lb.name
            vcs_info = lb.vcs_info
            if lb.version:
                title += " %s" % lb.version
            if vcs_info and vcs_info.get("version"):
                title += " #%s" % vcs_info.get("version")
            sys.stdout.write("%s|-- %s" % (margin, title))
            if int(ARGUMENTS.get("PIOVERBOSE", 0)):
                if vcs_info:
                    sys.stdout.write(" [%s]" % vcs_info.get("url"))
                sys.stdout.write(" (")
                sys.stdout.write(lb.path)
                sys.stdout.write(")")
            sys.stdout.write("\n")
            if lb.depbuilders:
                print_deps_tree(lb, level + 1)

    project = ProjectAsLibBuilder(env, "$PROJECT_DIR")
    ldf_mode = LibBuilderBase.lib_ldf_mode.fget(project)

    print("Library Dependency Finder -> http://bit.ly/configure-pio-ldf")
    print("LDF MODES: FINDER(%s) COMPATIBILITY(%s)" %
          (ldf_mode, project.lib_compat_mode))

    lib_builders = env.GetLibBuilders()
    print("Collected %d compatible libraries" % len(lib_builders))

    print("Scanning dependencies...")
    project.search_deps_recursive()

    if ldf_mode.startswith("chain") and project.depbuilders:
        correct_found_libs(lib_builders)

    if project.depbuilders:
        print("Dependency Graph")
        print_deps_tree(project)
    else:
        print("No dependencies")

    return project


def exists(_):
    return True


def generate(env):
    env.AddMethod(GetLibBuilders)
    env.AddMethod(ConfigureProjectLibBuilder)
    return env
