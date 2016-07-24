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

# pylint: disable=no-member, no-self-use, unused-argument

from __future__ import absolute_import

import os
import sys
from os.path import basename, commonprefix, isdir, isfile, join, realpath

import SCons.Scanner

from platformio import util
from platformio.builder.tools import platformio as piotool


class LibBuilderFactory(object):

    @staticmethod
    def new(env, path):
        clsname = "UnknownLibBuilder"
        if isfile(join(path, "library.json")):
            clsname = "PlatformIOLibBuilder"
        else:
            env_frameworks = [
                f.lower().strip()
                for f in env.get("PIOFRAMEWORK", "").split(",")]
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


class LibBuilderBase(object):

    def __init__(self, env, path):
        self.env = env
        self.path = path
        self._is_built = False
        self._manifest = self.load_manifest()

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.path)

    def __contains__(self, path):
        return commonprefix((self.path, path)) == self.path

    @property
    def name(self):
        return self._manifest.get("name", basename(self.path))

    @property
    def version(self):
        return self._manifest.get("version")

    @property
    def src_filter(self):
        return piotool.SRC_FILTER_DEFAULT + [
            "-<example%s>" % os.sep, "-<examples%s>" % os.sep,
            "-<test%s>" % os.sep, "-<tests%s>" % os.sep
        ]

    @property
    def src_dir(self):
        return (join(self.path, "src") if isdir(join(self.path, "src"))
                else self.path)

    @property
    def build_dir(self):
        return join("$BUILD_DIR", "lib", self.name)

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
    def is_built(self):
        return self._is_built

    def is_platform_compatible(self, platform):
        return True

    def is_framework_compatible(self, framework):
        return True

    def load_manifest(self):
        return {}

    def get_path_dirs(self, use_build_dir=False):
        return [self.build_dir if use_build_dir else self.src_dir]

    def append_to_cpppath(self):
        self.env.AppendUnique(
            CPPPATH=self.get_path_dirs(use_build_dir=True)
        )

    def build(self):
        if self.version:
            print "Depends on <%s> v%s" % (self.name, self.version)
        else:
            print "Depends on <%s>" % self.name
        assert self._is_built is False
        self._is_built = True
        self.append_to_cpppath()

        env = self.env.Clone()
        with util.cd(self.path):
            env.ProcessUnFlags(self.build_unflags)
            env.ProcessFlags(self.build_flags)
            if self.extra_script:
                env.SConscript(realpath(self.extra_script), exports="env")

        # copy some data to global env
        for key in ("CPPPATH", "LIBPATH", "LIBS", "LINKFLAGS"):
            self.env.AppendUnique(**{key: env.get(key)})

        return env.BuildLibrary(self.build_dir, self.src_dir, self.src_filter)


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

    def get_path_dirs(self, use_build_dir=False):
        path_dirs = LibBuilderBase.get_path_dirs(self, use_build_dir)
        if not isdir(join(self.src_dir, "utility")):
            return path_dirs
        path_dirs.append(
            join(self.build_dir if use_build_dir else self.src_dir, "utility"))
        return path_dirs

    @property
    def src_filter(self):
        if isdir(join(self.path, "src")):
            return LibBuilderBase.src_filter.fget(self)
        return ["+<*.%s>" % ext
                for ext in piotool.SRC_BUILD_EXT + piotool.SRC_HEADER_EXT]

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

    def get_path_dirs(self, use_build_dir=False):
        path_dirs = LibBuilderBase.get_path_dirs(self, use_build_dir)
        for p in self._manifest.get("extraIncludes", []):
            if p.startswith("source/"):
                p = p[7:]
            path_dirs.append(
                join(self.build_dir if use_build_dir else self.src_dir, p))
        return path_dirs

    def is_framework_compatible(self, framework):
        return framework.lower() == "mbed"


class PlatformIOLibBuilder(LibBuilderBase):

    def load_manifest(self):
        assert isfile(join(self.path, "library.json"))
        manifest = util.load_json(join(self.path, "library.json"))
        assert "name" in manifest
        return manifest

    @property
    def src_filter(self):
        if "srcFilter" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("srcFilter")
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
        if "extra_script" in self._manifest.get("build", {}):
            return self._manifest.get("build").get("extra_script")
        return LibBuilderBase.extra_script.fget(self)

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


def find_deps(env, scanner, path_dirs, src_dir, src_filter):
    result = []
    for item in env.MatchSourceFiles(src_dir, src_filter):
        result.extend(env.File(join(src_dir, item)).get_implicit_deps(
            env, scanner, path_dirs))
    return result


def find_and_build_deps(env, lib_builders, scanner,
                        src_dir, src_filter):
    path_dirs = tuple()
    built_path_dirs = tuple()
    for lb in lib_builders:
        items = [env.Dir(d) for d in lb.get_path_dirs()]
        if lb.is_built:
            built_path_dirs += tuple(items)
        else:
            path_dirs += tuple(items)
    path_dirs = built_path_dirs + path_dirs

    target_lbs = []
    deps = find_deps(env, scanner, path_dirs, src_dir, src_filter)
    for d in deps:
        for lb in lib_builders:
            if d.get_abspath() in lb:
                if lb not in target_lbs and not lb.is_built:
                    target_lbs.append(lb)
                break

    libs = []
    # append PATH directories to global CPPPATH before build starts
    for lb in target_lbs:
        lb.append_to_cpppath()
    # start builder
    for lb in target_lbs:
        libs.append(lb.build())

    if env.get("LIB_DEEP_SEARCH", "").lower() == "true":
        for lb in target_lbs:
            libs.extend(find_and_build_deps(
                env, lib_builders, scanner, lb.src_dir, lb.src_filter))

    return libs


def GetLibBuilders(env):
    items = []
    env_frameworks = [
        f.lower().strip() for f in env.get("PIOFRAMEWORK", "").split(",")
    ]
    compat_level = int(env.get("LIB_COMPAT_LEVEL", 1))

    for libs_dir in env['LIBSOURCE_DIRS']:
        libs_dir = env.subst(libs_dir)
        if not isdir(libs_dir):
            continue
        for item in sorted(os.listdir(libs_dir)):
            if item == "__cores__" or not isdir(join(libs_dir, item)):
                continue
            lb = LibBuilderFactory.new(env, join(libs_dir, item))
            if lb.name in env.get("LIB_IGNORE", []):
                if not env.GetOption("silent"):
                    print "Ignored library " + lb.path
                continue
            if compat_level > 1 and not lb.is_platform_compatible(env[
                    'PIOPLATFORM']):
                if not env.GetOption("silent"):
                    sys.stderr.write("Platform incompatible library %s\n" %
                                     lb.path)
                continue
            if compat_level > 0 and not any([lb.is_framework_compatible(f)
                                             for f in env_frameworks]):
                if not env.GetOption("silent"):
                    sys.stderr.write("Framework incompatible library %s\n" %
                                     lb.path)
                continue
            items.append(lb)
    return items


def BuildDependentLibraries(env, src_dir):
    libs = []
    scanner = SCons.Scanner.C.CScanner()
    lib_builders = env.GetLibBuilders()

    print "Collecting %d compatible libraries" % len(lib_builders)
    print "Looking for dependencies..."

    built_lib_names = []
    for lib_name in env.get("LIB_FORCE", []):
        for lb in lib_builders:
            if lb.name != lib_name or lb.name in built_lib_names:
                continue
            built_lib_names.append(lb.name)
            libs.extend(find_and_build_deps(
                env, lib_builders, scanner, lb.src_dir, lb.src_filter))
            if not lb.is_built:
                libs.append(lb.build())

    # process project source code
    libs.extend(find_and_build_deps(
        env, lib_builders, scanner, src_dir, env.get("SRC_FILTER")))

    return libs


def exists(_):
    return True


def generate(env):
    env.AddMethod(GetLibBuilders)
    env.AddMethod(BuildDependentLibraries)
    return env
