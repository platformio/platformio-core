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

# pylint: disable=no-member, no-self-use, unused-argument

from __future__ import absolute_import

import os
import sys
from os.path import basename, commonprefix, isdir, isfile, join, realpath, sep
from platform import system

import SCons.Scanner
from SCons.Script import ARGUMENTS

from platformio import util
from platformio.builder.tools import platformio as piotool
from platformio.managers.lib import LibraryManager


class LibBuilderFactory(object):

    @staticmethod
    def new(env, path):
        clsname = "UnknownLibBuilder"
        if isfile(join(path, "library.json")):
            clsname = "PlatformIOLibBuilder"
        else:
            env_frameworks = [
                f.lower().strip()
                for f in env.get("PIOFRAMEWORK", "").split(",")
            ]
            used_frameworks = LibBuilderFactory.get_used_frameworks(env, path)
            common_frameworks = set(env_frameworks) & set(used_frameworks)
            if common_frameworks:
                clsname = "%sLibBuilder" % list(common_frameworks)[0].title()
            elif used_frameworks:
                clsname = "%sLibBuilder" % used_frameworks[0].title()

        obj = getattr(sys.modules[__name__], clsname)(env, path)
        assert isinstance(obj, LibBuilderBase)
        return obj

    @staticmethod
    def get_used_frameworks(env, path):
        if any([isfile(join(path, fname))
                for fname in ("library.properties", "keywords.txt")]):
            return ["arduino"]

        if isfile(join(path, "module.json")):
            return ["mbed"]

        # check source files
        for root, _, files in os.walk(path, followlinks=True):
            for fname in files:
                if not env.IsFileWithExt(fname, ("c", "cpp", "h", "hpp")):
                    continue
                with open(join(root, fname)) as f:
                    content = f.read()
                    if "Arduino.h" in content:
                        return ["arduino"]
                    elif "mbed.h" in content:
                        return ["mbed"]
        return []

# pylint: disable=too-many-instance-attributes, too-many-public-methods


class LibBuilderBase(object):

    INC_SCANNER = SCons.Scanner.C.CScanner()
    INC_DIRS_CACHE = None

    def __init__(self, env, path, manifest=None):
        self.env = env.Clone()
        self.envorigin = env.Clone()
        self.path = realpath(env.subst(path))
        self._manifest = manifest if manifest else self.load_manifest()
        self._is_dependent = False
        self._depbuilders = list()
        self._scanned_paths = list()
        self._built_node = None

        # process extra options and append to build environment
        self.process_extra_options()

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.path)

    def __contains__(self, path):
        p1 = self.path
        p2 = path
        if system() == "Windows":
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
    def dependencies(self):
        return LibraryManager.normalize_dependencies(
            self._manifest.get("dependencies", []))

    @property
    def src_filter(self):
        return piotool.SRC_FILTER_DEFAULT + [
            "-<example%s>" % os.sep, "-<examples%s>" % os.sep, "-<test%s>" %
            os.sep, "-<tests%s>" % os.sep
        ]

    @property
    def src_dir(self):
        return (join(self.path, "src")
                if isdir(join(self.path, "src")) else self.path)

    @property
    def build_dir(self):
        return join("$BUILD_DIR", "lib", basename(self.path))

    def get_inc_dirs(self):
        return [self.src_dir]

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
        return True

    @property
    def lib_ldf_mode(self):
        return int(self.env.get("LIB_LDF_MODE", 1))

    @property
    def depbuilders(self):
        return self._depbuilders

    @property
    def dependent(self):
        return self._is_dependent

    def is_platform_compatible(self, platform):
        return True

    def is_framework_compatible(self, framework):
        return True

    def load_manifest(self):
        return {}

    def get_src_files(self):
        return [
            join(self.src_dir, item)
            for item in self.env.MatchSourceFiles(self.src_dir,
                                                  self.src_filter)
        ]

    def process_extra_options(self):
        with util.cd(self.path):
            self.env.ProcessUnFlags(self.build_unflags)
            self.env.ProcessFlags(self.build_flags)
            if self.extra_script:
                self.env.SConscript(
                    realpath(self.extra_script),
                    exports={"env": self.env,
                             "pio_lib_builder": self})

    def _process_dependencies(self, lib_builders):
        if not self.dependencies:
            return
        for item in self.dependencies:
            found = False
            for lb in lib_builders:
                if item['name'] != lb.name:
                    continue
                elif "frameworks" in item and \
                     not any([lb.is_framework_compatible(f)
                              for f in item["frameworks"]]):
                    continue
                elif "platforms" in item and \
                     not any([lb.is_platform_compatible(p)
                              for p in item["platforms"]]):
                    continue
                found = True
                self.depend_recursive(lb, lib_builders)
                break

            if not found:
                sys.stderr.write(
                    "Error: Could not find `%s` dependency for `%s` "
                    "library\n" % (item['name'], self.name))
                self.env.Exit(1)

    def _validate_search_paths(self, search_paths=None):
        if not search_paths:
            search_paths = []
        assert isinstance(search_paths, list)

        _search_paths = []
        for path in search_paths:
            if path not in self._scanned_paths:
                _search_paths.append(path)
                self._scanned_paths.append(path)

        return _search_paths

    def _get_found_includes(self, lib_builders, search_paths=None):
        # all include directories
        if not LibBuilderBase.INC_DIRS_CACHE:
            inc_dirs = []
            used_inc_dirs = []
            for lb in lib_builders:
                items = [self.env.Dir(d) for d in lb.get_inc_dirs()]
                if lb.dependent:
                    used_inc_dirs.extend(items)
                else:
                    inc_dirs.extend(items)
            LibBuilderBase.INC_DIRS_CACHE = used_inc_dirs + inc_dirs

        # append self include directories
        inc_dirs = [self.env.Dir(d) for d in self.get_inc_dirs()]
        inc_dirs.extend(LibBuilderBase.INC_DIRS_CACHE)

        result = []
        for path in self._validate_search_paths(search_paths):
            for inc in self.env.File(path).get_found_includes(
                    self.env, LibBuilderBase.INC_SCANNER, tuple(inc_dirs)):
                if inc not in result:
                    result.append(inc)
        return result

    def depend_recursive(self, lb, lib_builders, search_paths=None):
        # assert isinstance(lb, LibBuilderBase)
        if self != lb:
            if self in lb.depbuilders:
                sys.stderr.write("Warning! Circular dependencies detected "
                                 "between `%s` and `%s`\n" %
                                 (self.path, lb.path))
            elif lb not in self._depbuilders:
                self._depbuilders.append(lb)
                LibBuilderBase.INC_DIRS_CACHE = None
        lb.search_deps_recursive(lib_builders, search_paths)

    def search_deps_recursive(self, lib_builders, search_paths=None):
        if not self._is_dependent:
            self._is_dependent = True
            self._process_dependencies(lib_builders)

            if self.lib_ldf_mode == 2:
                search_paths = self.get_src_files()

        # when LDF is disabled
        if self.lib_ldf_mode == 0:
            return

        lib_inc_map = {}
        for inc in self._get_found_includes(lib_builders, search_paths):
            for lb in lib_builders:
                if inc.get_abspath() in lb:
                    if lb not in lib_inc_map:
                        lib_inc_map[lb] = []
                    lib_inc_map[lb].append(inc.get_abspath())
                    break

        for lb, lb_search_paths in lib_inc_map.items():
            self.depend_recursive(lb, lib_builders, lb_search_paths)

    def build(self):
        libs = []
        for lb in self.depbuilders:
            libs.extend(lb.build())
            # copy shared information to self env
            for key in ("CPPPATH", "LIBPATH", "LIBS", "LINKFLAGS"):
                self.env.AppendUnique(**{key: lb.env.get(key)})

        if not self._built_node:
            self.env.AppendUnique(CPPPATH=self.get_inc_dirs())
            if self.lib_archive:
                self._built_node = self.env.BuildLibrary(
                    self.build_dir, self.src_dir, self.src_filter)
            else:
                self._built_node = self.env.BuildSources(
                    self.build_dir, self.src_dir, self.src_filter)
            libs.append(self._built_node)
        return libs


class UnknownLibBuilder(LibBuilderBase):
    pass


class ProjectAsLibBuilder(LibBuilderBase):

    @property
    def lib_ldf_mode(self):
        return 2  # parse all project files

    @property
    def src_filter(self):
        return self.env.get("SRC_FILTER", LibBuilderBase.src_filter.fget(self))

    def process_extra_options(self):
        # skip for project, options are already processed
        pass

    def search_deps_recursive(self, lib_builders, search_paths=None):
        for lib_name in self.env.get("LIB_FORCE", []):
            for lb in lib_builders:
                if lb.name == lib_name:
                    if lb not in self.depbuilders:
                        self.depend_recursive(lb, lib_builders)
                    break
        return LibBuilderBase.search_deps_recursive(self, lib_builders,
                                                    search_paths)

    def build(self):
        # dummy mark that project is built
        self._built_node = "dummy"
        return [l for l in LibBuilderBase.build(self) if l != "dummy"]


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

    def get_inc_dirs(self):
        inc_dirs = LibBuilderBase.get_inc_dirs(self)
        if isdir(join(self.path, "src")):
            return inc_dirs
        if isdir(join(self.path, "utility")):
            inc_dirs.append(join(self.path, "utility"))
        return inc_dirs

    @property
    def src_filter(self):
        if isdir(join(self.path, "src")):
            return LibBuilderBase.src_filter.fget(self)
        src_filter = []
        is_utility = isdir(join(self.path, "utility"))
        for ext in piotool.SRC_BUILD_EXT + piotool.SRC_HEADER_EXT:
            src_filter.append("+<*.%s>" % ext)
            if is_utility:
                src_filter.append("+<utility%s*.%s>" % (sep, ext))
        return src_filter

    def is_framework_compatible(self, framework):
        return framework.lower() in ("arduino", "energia")


class MbedLibBuilder(LibBuilderBase):

    def load_manifest(self):
        if not isfile(join(self.path, "module.json")):
            return {}
        return util.load_json(join(self.path, "module.json"))

    @property
    def src_dir(self):
        if isdir(join(self.path, "source")):
            return join(self.path, "source")
        return LibBuilderBase.src_dir.fget(self)

    def get_inc_dirs(self):
        inc_dirs = LibBuilderBase.get_inc_dirs(self)
        if self.path not in inc_dirs:
            inc_dirs.append(self.path)
        for p in self._manifest.get("extraIncludes", []):
            inc_dirs.append(join(self.path, p))
        return inc_dirs

    def is_framework_compatible(self, framework):
        return framework.lower() == "mbed"


class PlatformIOLibBuilder(LibBuilderBase):

    def load_manifest(self):
        assert isfile(join(self.path, "library.json"))
        manifest = util.load_json(join(self.path, "library.json"))
        assert "name" in manifest
        return manifest

    def _is_arduino_manifest(self):
        return isfile(join(self.path, "library.properties"))

    @property
    def src_filter(self):
        if "srcFilter" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("srcFilter")
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
            return int(self._manifest.get("build").get("libLDFMode"))
        return LibBuilderBase.lib_ldf_mode.fget(self)

    def is_platform_compatible(self, platform):
        items = self._manifest.get("platforms")
        if not items:
            return LibBuilderBase.is_platform_compatible(self, platform)
        return self._item_in_list(platform, items)

    def is_framework_compatible(self, framework):
        items = self._manifest.get("frameworks")
        if not items:
            return LibBuilderBase.is_framework_compatible(self, framework)
        return self._item_in_list(framework, items)

    def _item_in_list(self, item, ilist):
        if ilist == "*":
            return True
        if not isinstance(ilist, list):
            ilist = [i.strip() for i in ilist.split(",")]
        return item.lower() in [i.lower() for i in ilist]

    def get_inc_dirs(self):
        inc_dirs = LibBuilderBase.get_inc_dirs(self)

        #  backwards compatibility with PlatformIO 2.0
        if ("build" not in self._manifest and self._is_arduino_manifest() and
                not isdir(join(self.path, "src")) and
                isdir(join(self.path, "utility"))):
            inc_dirs.append(join(self.path, "utility"))

        for path in self.env['CPPPATH']:
            if path not in self.envorigin['CPPPATH']:
                inc_dirs.append(self.env.subst(path))
        return inc_dirs


def GetLibBuilders(env):
    items = []
    env_frameworks = [
        f.lower().strip() for f in env.get("PIOFRAMEWORK", "").split(",")
    ]
    compat_mode = int(env.get("LIB_COMPAT_MODE", 1))
    verbose = (int(ARGUMENTS.get("PIOVERBOSE", 0)) and
               not env.GetOption('clean'))

    def _check_lib_builder(lb):
        if lb.name in env.get("LIB_IGNORE", []):
            if verbose:
                sys.stderr.write("Ignored library %s\n" % lb.path)
            return
        if compat_mode > 1 and not lb.is_platform_compatible(env[
                'PIOPLATFORM']):
            if verbose:
                sys.stderr.write("Platform incompatible library %s\n" %
                                 lb.path)
            return False
        if compat_mode > 0 and not any([lb.is_framework_compatible(f)
                                        for f in env_frameworks]):
            if verbose:
                sys.stderr.write("Framework incompatible library %s\n" %
                                 lb.path)
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
                lb = LibBuilderFactory.new(env, join(libs_dir, item))
            except ValueError:
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
            "http://docs.platformio.org/en/latest/librarymanager/ldf.html#"
            "ldf-compat-mode\n")

    return items


def BuildDependentLibraries(env, src_dir):

    def correct_found_libs(lib_builders):
        # build full dependency graph
        found_lbs = [lb for lb in lib_builders if lb.dependent]
        for lb in lib_builders:
            lb.search_deps_recursive(lib_builders, lb.get_src_files())
        for lb in lib_builders:
            for deplb in lb.depbuilders[:]:
                if deplb not in found_lbs:
                    lb.depbuilders.remove(deplb)

    def print_deps_tree(root, level=0):
        margin = "|   " * (level)
        for lb in root.depbuilders:
            title = "<%s>" % lb.name
            if lb.version:
                title += " v%s" % lb.version
            if int(ARGUMENTS.get("PIOVERBOSE", 0)):
                title += " (%s)" % lb.path
            print "%s|-- %s" % (margin, title)
            if lb.depbuilders:
                print_deps_tree(lb, level + 1)

    lib_builders = env.GetLibBuilders()

    print "Collected %d compatible libraries" % len(lib_builders)
    print "Looking for dependencies..."

    project = ProjectAsLibBuilder(env, src_dir)
    project.env = env
    project.search_deps_recursive(lib_builders)

    if int(env.get("LIB_LDF_MODE", 1)) == 1 and project.depbuilders:
        correct_found_libs(lib_builders)

    if project.depbuilders:
        print "Library Dependency Graph"
        print_deps_tree(project)
    else:
        print "Project does not have dependencies"

    return project.build()


def exists(_):
    return True


def generate(env):
    env.AddMethod(GetLibBuilders)
    env.AddMethod(BuildDependentLibraries)
    return env
