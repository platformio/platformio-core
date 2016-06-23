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

from __future__ import absolute_import

import os
from os.path import basename, commonprefix, isdir, isfile, join
from sys import modules

import SCons.Scanner

from platformio import util


class LibBuilderFactory(object):

    @staticmethod
    def new(env, path):
        clsname = "UnknownLibBuilder"
        if isfile(join(path, "library.json")):
            clsname = "PlatformIOLibBuilder"
        else:
            env_frameworks = [
                f.lower().strip() for f in env.get("FRAMEWORK", "").split(",")]
            used_frameworks = LibBuilderFactory.get_used_frameworks(env, path)
            common_frameworks = set(env_frameworks) & set(used_frameworks)
            if common_frameworks:
                clsname = "%sLibBuilder" % list(common_frameworks)[0].title()
            elif used_frameworks:
                clsname = "%sLibBuilder" % used_frameworks[0].title()

        obj = getattr(modules[__name__], clsname)(env, path)
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

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.path)

    def __contains__(self, path):
        return commonprefix((self.path, path)) == self.path

    @property
    def name(self):
        return basename(self.path)

    @property
    def src_filter(self):
        return " ".join([
            "+<*>", "-<.git%s>" % os.sep, "-<svn%s>" % os.sep,
            "-<example%s>" % os.sep, "-<examples%s>" % os.sep,
            "-<test%s>" % os.sep, "-<tests%s>" % os.sep
        ])

    @property
    def src_dir(self):
        return (join(self.path, "src") if isdir(join(self.path, "src"))
                else self.path)

    @property
    def build_dir(self):
        return join("$BUILD_DIR", "lib", self.name)

    @property
    def is_built(self):
        return self._is_built

    def get_path_dirs(self, use_build_dir=False):
        return [self.build_dir if use_build_dir else self.src_dir]

    def build(self):
        print "Depends on <%s>" % self.name
        assert self._is_built is False
        self._is_built = True
        return self.env.BuildLibrary(self.build_dir, self.src_dir)


class UnknownLibBuilder(LibBuilderBase):
    pass


class ArduinoLibBuilder(LibBuilderBase):

    def get_path_dirs(self, use_build_dir=False):
        path_dirs = LibBuilderBase.get_path_dirs(self, use_build_dir)
        if not isdir(join(self.src_dir, "utility")):
            return path_dirs
        path_dirs.append(join(self.build_dir if use_build_dir
                              else self.src_dir, "utility"))
        return path_dirs


class MbedLibBuilder(LibBuilderBase):

    def __init__(self, env, path):
        self.module_json = {}
        if isfile(join(path, "module.json")):
            self.module_json = util.load_json(join(path, "module.json"))

        LibBuilderBase.__init__(self, env, path)

    @property
    def src_dir(self):
        if isdir(join(self.path, "source")):
            return join(self.path, "source")
        return super(LibBuilderBase, self).src_dir  # pylint: disable=no-member

    def get_path_dirs(self, use_build_dir=False):
        path_dirs = LibBuilderBase.get_path_dirs(self, use_build_dir)
        for p in self.module_json.get("extraIncludes", []):
            if p.startswith("source/"):
                p = p[7:]
            path_dirs.append(
                join(self.build_dir if use_build_dir else self.src_dir, p))
        return path_dirs


class PlatformIOLibBuilder(LibBuilderBase):

    def __init__(self, env, path):
        self.library_json = {}
        if isfile(join(path, "library.json")):
            self.library_json = util.load_json(join(path, "library.json"))

        LibBuilderBase.__init__(self, env, path)


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
    # add build dirs to global CPPPATH
    for lb in target_lbs:
        env.Append(
            CPPPATH=lb.get_path_dirs(use_build_dir=True)
        )
    # start builder
    for lb in target_lbs:
        libs.append(lb.build())

    if env.get("LIB_DFCYCLIC", "").lower() == "true":
        for lb in target_lbs:
            libs.extend(find_and_build_deps(
                env, lib_builders, scanner, lb.src_dir, lb.src_filter))

    return libs


def BuildDependentLibraries(env, src_dir):
    lib_builders = []
    libs_dirs = [env.subst(d) for d in env.get("LIBSOURCE_DIRS", [])
                 if isdir(env.subst(d))]
    for libs_dir in libs_dirs:
        if not isdir(libs_dir):
            continue
        for item in sorted(os.listdir(libs_dir)):
            if isdir(join(libs_dir, item)):
                lib_builders.append(
                    LibBuilderFactory.new(env, join(libs_dir, item)))

    print "Looking for dependencies..."
    print "Collecting %d libraries" % len(lib_builders)

    return find_and_build_deps(
        env, lib_builders, SCons.Scanner.C.CScanner(),
        src_dir, env.get("SRC_FILTER"))


def exists(_):
    return True


def generate(env):
    env.AddMethod(BuildDependentLibraries)
    return env
