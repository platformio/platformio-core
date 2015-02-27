# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import atexit
import platform
import re
from os import getenv, listdir, remove, sep, walk
from os.path import basename, dirname, isdir, isfile, join, normpath
from time import sleep

from SCons.Script import Exit, SConscript, SConscriptChdir
from SCons.Util import case_sensitive_suffixes
from serial import Serial

from platformio.util import get_serialports


def ProcessGeneral(env):
    # fix ASM handling under non-casitive OS
    if not case_sensitive_suffixes('.s', '.S'):
        env.Replace(
            AS="$CC",
            ASCOM="$ASPPCOM"
        )

    if "extra_flags" in env.get("BOARD_OPTIONS", {}).get("build", {}):
        env.MergeFlags(env.subst("${BOARD_OPTIONS['build']['extra_flags']}"))

    if "BUILD_FLAGS" in env:
        env.MergeFlags(env['BUILD_FLAGS'])

    corelibs = []
    if "FRAMEWORK" in env:
        if env['FRAMEWORK'] in ("arduino", "energia"):
            env.ConvertInoToCpp()
        for f in env['FRAMEWORK'].split(","):
            SConscriptChdir(0)
            corelibs += SConscript(
                env.subst(join("$PIOBUILDER_DIR", "scripts", "frameworks",
                               "%s.py" % f.strip().lower()))
            )
    return corelibs


def BuildFirmware(env, corelibs):
    firmenv = env.Clone()
    vdirs = firmenv.VariantDirRecursive(
        join("$BUILD_DIR", "src"), "$PROJECTSRC_DIR")

    # build dependent libs
    deplibs = firmenv.BuildDependentLibraries("$PROJECTSRC_DIR")

    # append specified LD_SCRIPT
    if "LDSCRIPT_PATH" in firmenv:
        firmenv.Append(
            LINKFLAGS=["-T", "$LDSCRIPT_PATH"]
        )

    # enable "cyclic reference" for linker
    firmenv.Prepend(
        _LIBFLAGS="-Wl,--start-group "
    )
    firmenv.Append(
        _LIBFLAGS=" -Wl,--end-group"
    )

    firmenv.MergeFlags(getenv("PIOSRCBUILD_FLAGS", "$SRCBUILD_FLAGS"))

    return firmenv.Program(
        join("$BUILD_DIR", "firmware"),
        [firmenv.GlobCXXFiles(vdir) for vdir in vdirs],
        LIBS=corelibs + deplibs,
        LIBPATH="$BUILD_DIR",
        PROGSUFFIX=".elf"
    )


def GlobCXXFiles(env, path):
    files = []
    for suff in ["*.c", "*.cpp", "*.S"]:
        _list = env.Glob(join(path, suff))
        if _list:
            files += _list
    return files


def VariantDirRecursive(env, variant_dir, src_dir, duplicate=True,
                        ignore_pattern=None):
    if not ignore_pattern:
        ignore_pattern = (".git", ".svn")
    variants = []
    src_dir = env.subst(src_dir)
    for root, _, _ in walk(src_dir):
        _src_dir = root
        _var_dir = variant_dir + root.replace(src_dir, "")
        if any([s in _var_dir.lower() for s in ignore_pattern]):
            continue
        env.VariantDir(_var_dir, _src_dir, duplicate)
        variants.append(_var_dir)
    return variants


def BuildLibrary(env, variant_dir, library_dir, ignore_files=None):
    lib = env.Clone()
    vdirs = lib.VariantDirRecursive(
        variant_dir, library_dir, ignore_pattern=(".git", ".svn", "examples"))
    srcfiles = []
    for vdir in vdirs:
        for item in lib.GlobCXXFiles(vdir):
            if not ignore_files or item.name not in ignore_files:
                srcfiles.append(item)
    return lib.Library(
        lib.subst(variant_dir),
        srcfiles
    )


def BuildDependentLibraries(env, src_dir):  # pylint: disable=R0914

    INCLUDES_RE = re.compile(r"^\s*#include\s+(\<|\")([^\>\"\']+)(?:\>|\")",
                             re.M)
    LIBSOURCE_DIRS = [env.subst(d) for d in env.get("LIBSOURCE_DIRS", [])]

    # start internal prototypes

    class IncludeFinder(object):

        def __init__(self, base_dir, name, is_system=False):
            self.base_dir = base_dir
            self.name = name
            self.is_system = is_system

            self._inc_path = None
            self._lib_dir = None
            self._lib_name = None

        def getIncPath(self):
            return self._inc_path

        def getLibDir(self):
            return self._lib_dir

        def getLibName(self):
            return self._lib_name

        def run(self):
            if not self.is_system and self._find_in_local():
                return True
            return self._find_in_system()

        def _find_in_local(self):
            if isfile(join(self.base_dir, self.name)):
                self._inc_path = join(self.base_dir, self.name)
                return True
            else:
                return False

        def _find_in_system(self):
            for lsd_dir in LIBSOURCE_DIRS:
                if not isdir(lsd_dir):
                    continue

                for ld in listdir(lsd_dir):
                    inc_path = normpath(join(lsd_dir, ld, self.name))
                    lib_dir = inc_path[:inc_path.index(sep, len(lsd_dir) + 1)]
                    lib_name = basename(lib_dir)

                    # ignore user's specified libs
                    if "IGNORE_LIBS" in env and lib_name in env['IGNORE_LIBS']:
                        continue

                    if not isfile(inc_path):
                        # if source code is in "src" dir
                        lib_dir = join(lsd_dir, lib_name, "src")
                        inc_path = join(lib_dir, self.name)

                    if isfile(inc_path):
                        self._lib_dir = lib_dir
                        self._lib_name = lib_name
                        self._inc_path = inc_path
                        return True
            return False

    def _get_dep_libs(src_dir):
        state = {
            "paths": set(),
            "libs": set(),
            "ordered": set()
        }
        state = _process_src_dir(state, env.subst(src_dir))

        result = []
        for item in sorted(state['ordered'], key=lambda s: s[0]):
            result.append((item[1], item[2]))
        return result

    def _process_src_dir(state, src_dir):
        for root, _, _ in walk(src_dir):
            for node in (env.GlobCXXFiles(root) +
                         env.Glob(join(root, "*.h"))):
                state = _parse_includes(state, node)
        return state

    def _parse_includes(state, node):
        if node.path in state['paths']:
            return state
        else:
            state['paths'].add(node.path)

        skip_includes = ("arduino.h", "energia.h")
        matches = INCLUDES_RE.findall(node.get_text_contents())
        for (inc_type, inc_name) in matches:
            base_dir = dirname(node.path)
            if inc_name.lower() in skip_includes:
                continue
            if join(base_dir, inc_name) in state['paths']:
                continue
            else:
                state['paths'].add(join(base_dir, inc_name))

            finder = IncludeFinder(base_dir, inc_name, inc_type == "<")
            if finder.run():
                _parse_includes(state, env.File(finder.getIncPath()))

                _lib_dir = finder.getLibDir()
                if _lib_dir and _lib_dir not in state['libs']:
                    state['ordered'].add((
                        len(state['ordered']) + 1, finder.getLibName(),
                        _lib_dir))
                    state['libs'].add(_lib_dir)
                    state = _process_src_dir(state, _lib_dir)
        return state

    # end internal prototypes

    deplibs = _get_dep_libs(src_dir)
    env.Prepend(
        CPPPATH=[join("$BUILD_DIR", l) for (l, _) in deplibs]
    )

    # add automatically "utility" dir from the lib (Arduino issue)
    env.Prepend(
        CPPPATH=[
            join("$BUILD_DIR", l, "utility") for (l, ld) in deplibs
            if isdir(join(ld, "utility"))
        ]
    )

    libs = []
    for (libname, inc_dir) in deplibs:
        lib = env.BuildLibrary(
            join("$BUILD_DIR", libname), inc_dir)
        env.Clean(libname, lib)
        libs.append(lib)
    return libs


def ConvertInoToCpp(env):

    def delete_tmpcpp(files):
        for f in files:
            remove(f)

    tmpcpp = []
    items = (env.Glob(join("$PROJECTSRC_DIR", "*.ino")) +
             env.Glob(join("$PROJECTSRC_DIR", "*.pde")))
    for item in items:
        cppfile = item.get_path()[:-3] + "cpp"
        if isfile(cppfile):
            continue
        ino_contents = item.get_text_contents()

        re_includes = re.compile(r"^(#include\s+(?:\<|\")[^\r\n]+)",
                                 re.M | re.I)
        includes = re_includes.findall(ino_contents)
        prototypes = re.findall(
            r"""^(
            (?:\s*[a-z_\d]+){1,2}       # return type
            \s+[a-z_\d]+\s*             # name of prototype
            \([a-z_,\.\*\&\[\]\s\d]*\)  # args
            )\s*\{                      # must end with {
            """,
            ino_contents,
            re.X | re.M | re.I
        )
        # print includes, prototypes

        # disable previous includes
        ino_contents = re_includes.sub(r"//\1", ino_contents)

        # create new temporary C++ valid file
        with open(cppfile, "w") as f:
            f.write("#include <Arduino.h>\n")
            if includes:
                f.write("%s\n" % "\n".join(includes))
            if prototypes:
                f.write("%s;\n" % ";\n".join(prototypes))
            f.write("#line 1 \"%s\"\n" % basename(item.path))
            f.write(ino_contents)
        tmpcpp.append(cppfile)

    if tmpcpp:
        atexit.register(delete_tmpcpp, tmpcpp)


def FlushSerialBuffer(env, port):
    s = Serial(env.subst(port))
    s.flushInput()
    s.setDTR(False)
    s.setRTS(False)
    sleep(0.1)
    s.setDTR(True)
    s.setRTS(True)
    s.close()


def TouchSerialPort(env, port, baudrate):
    s = Serial(port=env.subst(port), baudrate=baudrate)
    s.close()
    if platform.system() != "Darwin":
        sleep(0.3)


def WaitForNewSerialPort(_, before):
    new_port = None
    elapsed = 0
    while elapsed < 10:
        now = [i['port'] for i in get_serialports()]
        diff = list(set(now) - set(before))
        if diff:
            new_port = diff[0]
            break

        before = now
        sleep(0.25)
        elapsed += 0.25

    if not new_port:
        Exit("Error: Couldn't find a board on the selected port. "
             "Check that you have the correct port selected. "
             "If it is correct, try pressing the board's reset "
             "button after initiating the upload.")

    return new_port


def AutodetectUploadPort(env):
    if "UPLOAD_PORT" not in env:
        for item in get_serialports():
            if "VID:PID" in item['hwid']:
                print "Auto-detected UPLOAD_PORT: %s" % item['port']
                env.Replace(UPLOAD_PORT=item['port'])
                break

    if "UPLOAD_PORT" not in env:
        Exit("Error: Please specify `upload_port` for environment or use "
             "global `--upload-port` option.\n")


def exists(_):
    return True


def generate(env):
    env.AddMethod(ProcessGeneral)
    env.AddMethod(BuildFirmware)
    env.AddMethod(GlobCXXFiles)
    env.AddMethod(VariantDirRecursive)
    env.AddMethod(BuildLibrary)
    env.AddMethod(BuildDependentLibraries)
    env.AddMethod(ConvertInoToCpp)
    env.AddMethod(FlushSerialBuffer)
    env.AddMethod(TouchSerialPort)
    env.AddMethod(WaitForNewSerialPort)
    env.AddMethod(AutodetectUploadPort)
    return env
