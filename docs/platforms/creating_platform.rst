..  Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _platform_creating:

Custom Platform
===============

*PlatformIO* was developed like a tool which would build the same source code
for the different development platforms via single command :ref:`cmd_run`
without any dependent software or requirements.

For this purpose *PlatformIO* uses own pre-configured platforms data:
build scripts, toolchains, the settings for the most popular embedded
boards and etc. These data are pre-built and packaged to the different
``packages``. It allows *PlatformIO* to have multiple development platforms
which can use the same packages(toolchains, frameworks), but have
different/own build scripts, uploader and etc.

.. note::
    If you want to change some build flags for the existing
    :ref:`Platforms <platforms>`, you don't need to create (or duplicate) own
    development platforms! Please use :ref:`projectconf_build_flags` option.

**Step-by-Step Manual**

1. Chose :ref:`platform_creating_packages` for platform
2. Create :ref:`platform_creating_manifest_file`
3. Create :ref:`platform_creating_build_script`
4. Finish with the :ref:`platform_creating_installation`.

.. contents::

.. _platform_creating_packages:

Packages
--------

*PlatformIO* has pre-built packages for the most popular operation systems:
*Mac OS*, *Linux (+ARM)* and *Windows*.

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``framework-arduinoavr``
      - `Arduino Wiring-based Framework (AVR Core, 1.6) <http://arduino.cc/en/Reference/HomePage>`_

    * - ``framework-arduinoespressif``
      - `Arduino Wiring-based Framework (ESP8266 Core) <https://github.com/esp8266/Arduino>`_

    * - ``framework-arduinomsp430``
      - `Arduino Wiring-based Framework (MSP430 Core) <http://arduino.cc/en/Reference/HomePage>`_

    * - ``framework-arduinonordicnrf51``
      - `Arduino Wiring-based Framework (RFduino Core) <https://github.com/RFduino/RFduino>`_

    * - ``framework-arduinosam``
      - `Arduino Wiring-based Framework (SAM Core, 1.6) <http://arduino.cc/en/Reference/HomePage>`_

    * - ``framework-arduinoteensy``
      - `Arduino Wiring-based Framework <http://arduino.cc/en/Reference/HomePage>`_

    * - ``framework-cmsis``
      - `Vendor-independent hardware abstraction layer for the Cortex-M processor series <http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php>`_

    * - ``framework-energiamsp430``
      - `Energia Wiring-based Framework (MSP430 Core) <http://energia.nu/reference/>`_

    * - ``framework-energiativa``
      - `Energia Wiring-based Framework (LM4F Core) <http://energia.nu/reference/>`_

    * - ``framework-libopencm3``
      - `libOpenCM3 Framework <http://www.libopencm3.org/>`_

    * - ``framework-mbed``
      - `mbed Framework <http://mbed.org>`_

    * - ``framework-spl``
      - `Standard Peripheral Library for STM32 MCUs <http://www.st.com/web/catalog/tools/FM147/CL1794/SC961/SS1743/PF257890>`_

    * - ``framework-wiringpi``
      - `GPIO Interface library for the Raspberry Pi <http://wiringpi.com>`_

    * - ``ldscripts``
      - `Linker Scripts <https://sourceware.org/binutils/docs/ld/Scripts.html>`_

    * - ``sdk-esp8266``
      - `ESP8266 SDK <http://bbs.espressif.com>`_

    * - ``tool-avrdude``
      - `AVRDUDE <http://www.nongnu.org/avrdude/>`_

    * - ``tool-bossac``
      - `BOSSA CLI <https://sourceforge.net/projects/b-o-s-s-a/>`_

    * - ``tool-esptool``
      - `esptool-ck <https://github.com/igrr/esptool-ck>`_

    * - ``tool-lm4flash``
      - `Flash Programmer <http://www.ti.com/tool/lmflashprogrammer>`_

    * - ``tool-micronucleus``
      - `Micronucleus <https://github.com/micronucleus/micronucleus>`_

    * - ``tool-mspdebug``
      - `MSPDebug <http://mspdebug.sourceforge.net/>`_

    * - ``tool-rfdloader``
      - `rfdloader <https://github.com/RFduino/RFduino>`_

    * - ``tool-scons``
      - `SCons software construction tool <http://www.scons.org>`_

    * - ``tool-stlink``
      - `ST-Link <https://github.com/texane/stlink>`_

    * - ``tool-teensy``
      - `Teensy Loader <https://www.pjrc.com/teensy/loader.html>`_

    * - ``toolchain-atmelavr``
      - `avr-gcc <https://gcc.gnu.org/wiki/avr-gcc>`_, `GDB <http://www.gnu.org/software/gdb/>`_, `AVaRICE <http://avarice.sourceforge.net/>`_, `SimulAVR <http://www.nongnu.org/simulavr/>`_

    * - ``toolchain-gccarmlinuxgnueabi``
      - `GCC for Linux ARM GNU EABI <https://gcc.gnu.org>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``toolchain-gccarmnoneeabi``
      - `gcc-arm-embedded <https://launchpad.net/gcc-arm-embedded>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``toolchain-gcclinux32``
      - `GCC for Linux i686 <https://gcc.gnu.org>`_

    * - ``toolchain-gcclinux64``
      - `GCC for Linux x86_64 <https://gcc.gnu.org>`_

    * - ``toolchain-gccmingw32``
      - `MinGW <http://www.mingw.org>`_

    * - ``toolchain-timsp430``
      - `msp-gcc <http://sourceforge.net/projects/mspgcc/>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``toolchain-xtensa``
      - `xtensa-gcc <https://github.com/jcmvbkbc/gcc-xtensa>`_, `GDB <http://www.gnu.org/software/gdb/>`_

.. _platform_creating_manifest_file:

Manifest File
-------------

A platform manifest file is a `Python <https://www.python.org>`_ script with the
next requirements:

1. The file should have ``.py`` extension
2. The **name of the file** is the **platform name** (lowercase)
3. The source code of this file should contain a ``class`` which describes your
   own platform. The name of the ``class`` should start with your
   **platform name** (the first letter should be capitalized) + ``Platform``
   ending. This ``class`` should be derived from *PlatformIO* ``BasePlatform``
   class.

.. warning::
    If you are new to *Python* language, please read:

    * `Style Guide for Python Code <https://www.python.org/dev/peps/pep-0008>`_.
    * A hash sign (#) that is not inside a string literal begins a comment.
      All characters after the # and up to the physical line end are part
      of the comment and the *Python* interpreter ignores them.

Example of the **test** platform (``test.py``):

.. code-block:: python

    import os

    from platformio.platforms.base import BasePlatform

    class TestPlatform(BasePlatform):
        # This is a description of your platform.
        # Platformio uses it for the `platformio search / list` commands
        """
            My Test platform - test.py
        """

        PACKAGES = {

            "toolchain-foo": {

                # alias is used for quick access to package.
                # For example,
                # `> platformio install test --without-package=toolchain`
                "alias": "toolchain",

                # Flag which allows PlatformIO to install this package by
                # default via `> platformio install test` command
                "default": True
            },

            "tool-bar": {
                "alias": "uploader",
                "default": True
            },

            "framework-baz": {
                "default": True
            }
        }

        def get_build_script(self):
            """ Returns a path to build script """

            # You can return static path
            #return "/path/to/test-builder.py"

            # or detect dynamically if `test-builder.py` is located in the same
            # folder with `test.py`
            return os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "test-builder.py"
            )

.. _platform_creating_build_script:

Build Script
------------

Platform's build script is based on a next-generation build tool named
`SCons <http://www.scons.org>`_. PlatformIO has own built-in firmware builder
``env.BuildProgram`` with the nested libraries search. Please look into a
base template of ``test-builder.py``.

.. code-block:: python

    """
        Build script for test.py
        test-builder.py
    """

    from os.path import join
    from SCons.Script import AlwaysBuild, Builder, Default, DefaultEnvironment

    env = DefaultEnvironment()

    # A full list with the available variables
    # http://www.scons.org/doc/production/HTML/scons-user.html#app-variables
    env.Replace(
        AR="ar",
        AS="gcc",
        CC="gcc",
        CXX="g++",
        OBJCOPY="objcopy",
        RANLIB="ranlib",

        ARFLAGS=["..."],

        ASFLAGS=["flag1", "flag2", "flagN"],
        CCFLAGS=["flag1", "flag2", "flagN"],
        CXXFLAGS=["flag1", "flag2", "flagN"],
        LINKFLAGS=["flag1", "flag2", "flagN"],

        CPPDEFINES=["DEFINE_1", "DEFINE=2", "DEFINE_N"],

        LIBS=["additional", "libs", "here"],

        UPLOADER=join("$PIOPACKAGES_DIR", "tool-bar", "uploader"),
        UPLOADCMD="$UPLOADER $SOURCES"
    )

    env.Append(
        BUILDERS=dict(
            ElfToBin=Builder(
                action=" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET"]),
                suffix=".bin"
            )
        )
    )

    # The source code of "platformio-build-tool" is here
    # https://github.com/platformio/platformio/blob/develop/platformio/builder/tools/platformio.py

    #
    # Target: Build executable and linkable firmware
    #
    target_elf = env.BuildProgram()

    #
    # Target: Build the .bin file
    #
    target_bin = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

    #
    # Target: Upload firmware
    #
    upload = env.Alias(["upload"], target_bin, "$UPLOADCMD")
    AlwaysBuild(upload)

    #
    # Target: Define targets
    #
    Default(target_bin)


Please look into the examples with built-in scripts for the popular
platforms:

* `baseavr.py <https://github.com/platformio/platformio/blob/develop/platformio/builder/scripts/baseavr.py>`_
* `basearm.py <https://github.com/platformio/platformio/blob/develop/platformio/builder/scripts/basearm.py>`_
* `atmelavr.py <https://github.com/platformio/platformio/blob/develop/platformio/builder/scripts/atmelavr.py>`_
* `timsp430.py <https://github.com/platformio/platformio/blob/develop/platformio/builder/scripts/timsp430.py>`_
* `ststm32.py <https://github.com/platformio/platformio/blob/develop/platformio/builder/scripts/ststm32.py>`_

.. _platform_creating_installation:

Installation
------------

1. Create ``platforms`` directory in :ref:`projectconf_pio_home_dir` if it
   doesn't exist.
2. Copy ``test.py`` and ``test-builder.py`` files to ``platforms`` directory.
3. Search available platforms via :ref:`cmd_platforms_search` command. You should see
   ``test`` platform.
4. Install ``test`` platform via :ref:`cmd_platforms_install` command.

Now, you can use ``test`` for the :ref:`projectconf_env_platform` option in
:ref:`projectconf`.

Example
-------

Let's use the real example which was requested by our user in `issue 175 <https://github.com/platformio/platformio/issues/175>`_. Need to add support for uploading firmware using GDB to
:ref:`platform_ststm32`.

First of all, need to create new folder ``platforms`` in :ref:`projectconf_pio_home_dir`
and copy there two files:

1. Platform manifest file ``ststm32gdb.py`` with the next content:

.. code-block:: python

    import os

    from platformio.platforms.ststm32 import Ststm32Platform


    class Ststm32gdbPlatform(Ststm32Platform):

        """
        ST STM32 using GDB as uploader

        http://www.st.com/web/en/catalog/mmc/FM141/SC1169?sc=stm32
        """

        def get_build_script(self):

            return os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "ststm32gdb-builder.py"
            )

2. Build script file ``ststm32gdb-builder.py`` with the next content:

.. code-block:: python

    """
        Builder for ST STM32 Series ARM microcontrollers with GDB upload.
    """

    from os.path import join

    from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                              DefaultEnvironment, SConscript)


    env = DefaultEnvironment()

    SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

    env.Replace(
        UPLOADER=join(
            "$PIOPACKAGES_DIR", "toolchain-gccarmnoneeabi",
            "bin", "arm-none-eabi-gdb"
        ),
        UPLOADERFLAGS=[
            join("$BUILD_DIR", "firmware.elf"),
            "-batch",
            "-x", join("$PROJECT_DIR", "upload.gdb")
        ],

        UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
    )

    env.Append(
        CPPDEFINES=[
            "${BOARD_OPTIONS['build']['variant'].upper()}"
        ],

        LINKFLAGS=[
            "-nostartfiles",
            "-nostdlib"
        ]
    )

    #
    # Target: Build executable and linkable firmware
    #

    target_elf = env.BuildProgram()

    #
    # Target: Build the .bin file
    #

    if "uploadlazy" in COMMAND_LINE_TARGETS:
        target_firm = join("$BUILD_DIR", "firmware.bin")
    else:
        target_firm = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

    #
    # Target: Print binary size
    #

    target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
    AlwaysBuild(target_size)

    #
    # Target: Upload by default .bin file
    #

    upload = env.Alias(
        ["upload", "uploadlazy"], target_firm, "$UPLOADCMD")
    AlwaysBuild(upload)

    #
    # Target: Define targets
    #

    Default([target_firm, target_size])

Now, we should see ``ststm32gdb`` platform using :ref:`cmd_platforms_search` command output
and can install it via :ref:`platformio platforms install ststm32gdb <cmd_platforms_install>` command.

