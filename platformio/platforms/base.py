# Copyright (C) Ivan Kravets <me@ikravets.com>
# See LICENSE for details.

import os
import re
import sys
from glob import glob
from imp import load_source
from os.path import isdir, isfile, join

import click

from platformio import exception, util
from platformio.app import get_state_item, set_state_item
from platformio.pkgmanager import PackageManager

PLATFORM_PACKAGES = {

    "framework-arduinoavr": [
        ("Arduino Wiring-based Framework (AVR Core, 1.6)",
         "http://arduino.cc/en/Reference/HomePage")
    ],
    "framework-arduinosam": [
        ("Arduino Wiring-based Framework (SAM Core, 1.6)",
         "http://arduino.cc/en/Reference/HomePage")
    ],
    "framework-arduinoteensy": [
        ("Arduino Wiring-based Framework",
         "http://arduino.cc/en/Reference/HomePage")
    ],
    "framework-arduinomsp430": [
        ("Arduino Wiring-based Framework (MSP430 Core)",
         "http://arduino.cc/en/Reference/HomePage")
    ],
    "framework-arduinoespressif": [
        ("Arduino Wiring-based Framework (ESP8266 Core)",
         "https://github.com/esp8266/Arduino")
    ],
    "framework-energiamsp430": [
        ("Energia Wiring-based Framework (MSP430 Core)",
         "http://energia.nu/reference/")
    ],
    "framework-energiativa": [
        ("Energia Wiring-based Framework (LM4F Core)",
         "http://energia.nu/reference/")
    ],
    "framework-cmsis": [
        ("Vendor-independent hardware abstraction layer for the Cortex-M "
         "processor series",
         "http://www.arm.com/products/processors/"
         "cortex-m/cortex-microcontroller-software-interface-standard.php")
    ],
    "framework-spl": [
        ("Standard Peripheral Library for STM32 MCUs",
         "http://www.st.com"
         "/web/catalog/tools/FM147/CL1794/SC961/SS1743/PF257890")
    ],
    "framework-libopencm3": [
        ("libOpenCM3 Framework", "http://www.libopencm3.org/")
    ],
    "framework-mbed": [
        ("mbed Framework", "http://mbed.org")
    ],
    "sdk-esp8266": [
        ("ESP8266 SDK", "http://bbs.espressif.com")
    ],
    "ldscripts": [
        ("Linker Scripts",
         "https://sourceware.org/binutils/docs/ld/Scripts.html")
    ],
    "toolchain-atmelavr": [
        ("avr-gcc", "https://gcc.gnu.org/wiki/avr-gcc"),
        ("GDB", "http://www.gnu.org/software/gdb/"),
        ("AVaRICE", "http://avarice.sourceforge.net/"),
        ("SimulAVR", "http://www.nongnu.org/simulavr/")
    ],
    "toolchain-gccarmnoneeabi": [
        ("gcc-arm-embedded", "https://launchpad.net/gcc-arm-embedded"),
        ("GDB", "http://www.gnu.org/software/gdb/")
    ],
    "toolchain-gccarmlinuxgnueabi": [
        ("GCC for Linux ARM GNU EABI", "https://gcc.gnu.org"),
        ("GDB", "http://www.gnu.org/software/gdb/")
    ],
    "toolchain-gccmingw32": [
        ("MinGW", "http://www.mingw.org")
    ],
    "toolchain-gcclinux32": [
        ("GCC for Linux i686", "https://gcc.gnu.org")
    ],
    "toolchain-gcclinux64": [
        ("GCC for Linux x86_64", "https://gcc.gnu.org")
    ],
    "toolchain-xtensa": [
        ("xtensa-gcc", "https://github.com/jcmvbkbc/gcc-xtensa"),
        ("GDB", "http://www.gnu.org/software/gdb/")
    ],
    "toolchain-timsp430": [
        ("msp-gcc", "http://sourceforge.net/projects/mspgcc/"),
        ("GDB", "http://www.gnu.org/software/gdb/")
    ],
    "tool-avrdude": [
        ("AVRDUDE", "http://www.nongnu.org/avrdude/")
    ],
    "tool-micronucleus": [
        ("Micronucleus", "https://github.com/micronucleus/micronucleus")
    ],
    "tool-bossac": [
        ("BOSSA CLI", "https://sourceforge.net/projects/b-o-s-s-a/")
    ],
    "tool-stlink": [
        ("ST-Link", "https://github.com/texane/stlink")
    ],
    "tool-teensy": [
        ("Teensy Loader", "https://www.pjrc.com/teensy/loader.html")
    ],
    "tool-lm4flash": [
        ("Flash Programmer", "http://www.ti.com/tool/lmflashprogrammer")
    ],
    "tool-mspdebug": [
        ("MSPDebug", "http://mspdebug.sourceforge.net/")
    ],
    "tool-esptool": [
        ("esptool-ck", "https://github.com/igrr/esptool-ck")
    ]
}


def get_packages():
    return PLATFORM_PACKAGES


class PlatformFactory(object):

    @staticmethod
    def get_clsname(type_):
        return "%s%sPlatform" % (type_.upper()[0], type_.lower()[1:])

    @staticmethod
    def load_module(type_, path):
        module = None
        try:
            module = load_source(
                "platformio.platforms.%s" % type_, path)
        except ImportError:
            raise exception.UnknownPlatform(type_)
        return module

    @classmethod
    @util.memoized
    def _lookup_platforms(cls):
        platforms = {}
        for d in (util.get_home_dir(), util.get_source_dir()):
            pdir = join(d, "platforms")
            if not isdir(pdir):
                continue
            for p in sorted(os.listdir(pdir)):
                if (p in ("__init__.py", "base.py") or not
                        p.endswith(".py")):
                    continue
                type_ = p[:-3]
                path = join(pdir, p)
                try:
                    isplatform = hasattr(
                        cls.load_module(type_, path),
                        cls.get_clsname(type_)
                    )
                    if isplatform:
                        platforms[type_] = path
                except exception.UnknownPlatform:
                    pass
        return platforms

    @classmethod
    def get_platforms(cls, installed=False):
        platforms = cls._lookup_platforms()

        if not installed:
            return platforms

        installed_platforms = {}
        for type_ in get_state_item("installed_platforms", []):
            if type_ in platforms:
                installed_platforms[type_] = platforms[type_]
        return installed_platforms

    @classmethod
    def newPlatform(cls, type_):
        platforms = cls.get_platforms()
        if type_ not in platforms:
            raise exception.UnknownPlatform(type_)

        _instance = getattr(
            cls.load_module(type_, platforms[type_]),
            cls.get_clsname(type_)
        )()
        assert isinstance(_instance, BasePlatform)
        return _instance


class BasePlatform(object):

    PACKAGES = {}
    LINE_ERROR_RE = re.compile(r"(\s+error|error[:\s]+)", re.I)

    def __init__(self):
        self._found_error = False
        self._last_echo_line = None

        # 1 = errors
        # 2 = 1 + warnings
        # 3 = 2 + others
        self._verbose_level = 3

    def get_type(self):
        return self.__class__.__name__[:-8].lower()

    def get_name(self):
        return self.get_type().title()

    def get_build_script(self):
        builtin = join(util.get_source_dir(), "builder", "scripts", "%s.py" %
                       self.get_type())
        if isfile(builtin):
            return builtin
        raise NotImplementedError()

    def get_description(self):
        if self.__doc__:
            doclines = [l.strip() for l in self.__doc__.splitlines() if
                        l.strip()]
            return " ".join(doclines[:-1]).strip()
        else:
            raise NotImplementedError()

    def get_vendor_url(self):
        if self.__doc__ and "http" in self.__doc__:
            return self.__doc__[self.__doc__.index("http"):].strip()
        else:
            raise NotImplementedError()

    def is_embedded(self):
        for name, opts in self.get_packages().items():
            if name == "framework-mbed" or opts.get("alias") == "uploader":
                return True
        return False

    def get_packages(self):
        return self.PACKAGES

    def get_pkg_alias(self, pkgname):
        return self.PACKAGES[pkgname].get("alias", None)

    def pkg_aliases_to_names(self, aliases):
        names = []
        for alias in aliases:
            name = alias
            # lookup by package aliases
            for _name, _opts in self.get_packages().items():
                if _opts.get("alias", None) == alias:
                    name = _name
                    break
            names.append(name)
        return names

    def get_default_packages(self):
        return [k for k, v in self.get_packages().items()
                if v.get("default", False)]

    def get_installed_packages(self):
        pm = PackageManager()
        return [n for n in self.get_packages().keys() if pm.is_installed(n)]

    def install(self, with_packages, without_packages, skip_default_packages):
        with_packages = set(self.pkg_aliases_to_names(with_packages))
        without_packages = set(self.pkg_aliases_to_names(without_packages))

        upkgs = with_packages | without_packages
        ppkgs = set(self.get_packages().keys())
        if not upkgs.issubset(ppkgs):
            raise exception.UnknownPackage(", ".join(upkgs - ppkgs))

        requirements = []
        for name, opts in self.get_packages().items():
            if name in without_packages:
                continue
            elif (name in with_packages or (not skip_default_packages and
                                            opts['default'])):
                requirements.append(name)

        pm = PackageManager()
        for name in requirements:
            pm.install(name)

        # register installed platform
        data = get_state_item("installed_platforms", [])
        if self.get_type() not in data:
            data.append(self.get_type())
            set_state_item("installed_platforms", data)

        return len(requirements)

    def uninstall(self):
        platform = self.get_type()
        installed_platforms = PlatformFactory.get_platforms(
            installed=True).keys()

        if platform not in installed_platforms:
            raise exception.PlatformNotInstalledYet(platform)

        deppkgs = set()
        for item in installed_platforms:
            if item == platform:
                continue
            p = PlatformFactory.newPlatform(item)
            deppkgs = deppkgs.union(set(p.get_packages().keys()))

        pm = PackageManager()
        for name in self.get_packages().keys():
            if not pm.is_installed(name) or name in deppkgs:
                continue
            pm.uninstall(name)

        # unregister installed platform
        installed_platforms.remove(platform)
        set_state_item("installed_platforms", installed_platforms)

        return True

    def update(self):
        pm = PackageManager()
        for name in self.get_installed_packages():
            pm.update(name)

    def is_outdated(self):
        pm = PackageManager()
        obsolated = pm.get_outdated()
        return not set(self.get_packages().keys()).isdisjoint(set(obsolated))

    def run(self, variables, targets, verbose):
        assert isinstance(variables, list)
        assert isinstance(targets, list)

        self._verbose_level = int(verbose)

        installed_platforms = PlatformFactory.get_platforms(
            installed=True).keys()
        installed_packages = PackageManager.get_installed()

        if self.get_type() not in installed_platforms:
            raise exception.PlatformNotInstalledYet(self.get_type())

        if "clean" in targets:
            targets.remove("clean")
            targets.append("-c")

        if not any([v.startswith("BUILD_SCRIPT=") for v in variables]):
            variables.append("BUILD_SCRIPT=%s" % self.get_build_script())

        for v in variables:
            if not v.startswith("BUILD_SCRIPT="):
                continue
            _, path = v.split("=", 2)
            if not isfile(path):
                raise exception.BuildScriptNotFound(path)

        # append aliases of the installed packages
        for name, options in self.get_packages().items():
            if "alias" not in options or name not in installed_packages:
                continue
            variables.append(
                "PIOPACKAGE_%s=%s" % (options['alias'].upper(), name))

        self._found_error = False
        try:
            # test that SCons is installed correctly
            assert self.test_scons()

            result = util.exec_command(
                [
                    "scons",
                    "-Q",
                    "-f", join(util.get_source_dir(), "builder", "main.py")
                ] + variables + targets,
                stdout=util.AsyncPipe(self.on_run_out),
                stderr=util.AsyncPipe(self.on_run_err)
            )
        except (OSError, AssertionError):
            raise exception.SConsNotInstalled()

        assert "returncode" in result
        # if self._found_error:
        #     result['returncode'] = 1

        if self._last_echo_line == ".":
            click.echo("")

        return result

    @staticmethod
    def test_scons():
        try:
            r = util.exec_command(["scons", "--version"])
            if "ImportError: No module named SCons.Script" in r['err']:
                _PYTHONPATH = []
                for p in sys.path:
                    if not p.endswith("-packages"):
                        continue
                    for item in glob(join(p, "scons*")):
                        if isdir(join(item, "SCons")) and item not in sys.path:
                            _PYTHONPATH.append(item)
                            sys.path.insert(0, item)
                if _PYTHONPATH:
                    _PYTHONPATH = str(os.pathsep).join(_PYTHONPATH)
                    if os.getenv("PYTHONPATH"):
                        os.environ['PYTHONPATH'] += os.pathsep + _PYTHONPATH
                    else:
                        os.environ['PYTHONPATH'] = _PYTHONPATH
                    r = util.exec_command(["scons", "--version"])
            assert r['returncode'] == 0
            return True
        except (OSError, AssertionError):
            for p in sys.path:
                try:
                    r = util.exec_command([join(p, "scons"), "--version"])
                    assert r['returncode'] == 0
                    os.environ['PATH'] += os.pathsep + p
                    return True
                except (OSError, AssertionError):
                    pass
        return False

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
