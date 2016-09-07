..  Copyright 2014-present PlatformIO <contact@platformio.org>
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

Custom Development Platform
===========================

*PlatformIO* was developed like a tool that may build the same source code
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
    :ref:`platforms`, you don't need to create (or duplicate) own
    development platforms! Please use :ref:`projectconf_build_flags` option.

**Step-by-Step Manual**

1. Choose :ref:`platform_creating_packages` for platform
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

    * - ``framework-arduinoespressif8266``
      - `Arduino Wiring-based Framework (ESP8266 Core) <https://github.com/esp8266/Arduino>`_

    * - ``framework-arduinointel``
      - `Arduino Wiring-based Framework (Intel ARC Core) <https://github.com/01org/corelibs-arduino101>`_

    * - ``framework-arduinomicrochippic32``
      - `Arduino Wiring-based Framework (PIC32 Core) <https://github.com/chipKIT32/chipKIT-core>`_

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

    * - ``framework-simba``
      - `Simba Framework <https://github.com/eerimoq/simba>`_

    * - ``framework-spl``
      - `Standard Peripheral Library for STM32 MCUs <http://www.st.com/web/catalog/tools/FM147/CL1794/SC961/SS1743/PF257890>`_

    * - ``framework-wiringpi``
      - `GPIO Interface library for the Raspberry Pi <http://wiringpi.com>`_

    * - ``ldscripts``
      - `Linker Scripts <https://sourceware.org/binutils/docs/ld/Scripts.html>`_

    * - ``sdk-esp8266``
      - `ESP8266 SDK <http://bbs.espressif.com>`_

    * - ``tool-arduino101load``
      - `Genuino101 uploader <https://github.com/01org/intel-arduino-tools>`_

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

    * - ``tool-mkspiffs``
      - `Tool to build and unpack SPIFFS images <https://github.com/igrr/mkspiffs>`_

    * - ``tool-mspdebug``
      - `MSPDebug <http://mspdebug.sourceforge.net/>`_

    * - ``tool-openocd``
      - `OpenOCD <http://openocd.org>`_

    * - ``tool-pic32prog``
      - `pic32prog <https://github.com/sergev/pic32prog>`_

    * - ``tool-rfdloader``
      - `rfdloader <https://github.com/RFduino/RFduino>`_

    * - ``tool-scons``
      - `SCons software construction tool <http://www.scons.org>`_

    * - ``tool-sreccat``
      - `Merging tool <https://github.com/marcows/SRecord>`_

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

    * - ``toolchain-icestorm``
      - `GCC for FPGA IceStorm <http://www.clifford.at/icestorm/>`_

    * - ``toolchain-intelarc32``
      - `GCC for Intel ARC <https://github.com/foss-for-synopsys-dwc-arc-processors/toolchain>`_

    * - ``toolchain-microchippic32``
      - `GCC for Microchip PIC32 <https://github.com/chipKIT32/chipKIT-cxx>`_

    * - ``toolchain-timsp430``
      - `msp-gcc <http://sourceforge.net/projects/mspgcc/>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``toolchain-xtensa``
      - `xtensa-gcc <https://github.com/jcmvbkbc/gcc-xtensa>`_, `GDB <http://www.gnu.org/software/gdb/>`_

.. _platform_creating_manifest_file:

Manifest File ``platform.json``
-------------------------------

.. code-block:: json

    {
      "name": "myplatform",
      "title": "My Platform",
      "description": "My custom development platform",
      "url": "http://example.com",
      "homepage": "http://platformio.org/platforms/myplatform",
      "license": "Apache-2.0",
      "engines": {
        "platformio": "~3.0.0",
        "scons": ">=2.3.0,<2.6.0"
      },
      "repository": {
        "type": "git",
        "url": "https://github.com/platformio/platform-myplatform.git"
      },
      "version": "0.0.0",
      "packageRepositories": [
        "https://dl.bintray.com/platformio/dl-packages/manifest.json",
        "https://sourceforge.net/projects/platformio-storage/files/packages/manifest.json/download",
        "http://dl.platformio.org/packages/manifest.json",
        {
          "framework-%FRAMEWORK_NAME_1%": [
            {
              "url": "http://dl.example.com/packages/framework-%FRAMEWORK_NAME_1%-1.10607.0.tar.gz",
              "sha1": "adce2cd30a830d71cb6572575bf08461b7b73c07",
              "version": "1.10607.0",
              "system": "*"
            }
          ]
        }
      ],
      "frameworks": {
        "%FRAMEWORK_NAME_1%": {
          "package": "framework-%FRAMEWORK_NAME_1%",
          "script": "builder/frameworks/%FRAMEWORK_NAME_1%.py"
        },
        "%FRAMEWORK_NAME_N%": {
          "package": "framework-%FRAMEWORK_NAME_N%",
          "script": "builder/frameworks/%FRAMEWORK_NAME_N%.py"
        }
      },
      "packages": {
        "toolchain-gccarmnoneeabi": {
          "type": "toolchain",
          "version": ">=1.40803.0,<1.40805.0"
        },
        "framework-%FRAMEWORK_NAME_1%": {
          "type": "framework",
          "optional": true,
          "version": "~1.10607.0"
        },
        "framework-%FRAMEWORK_NAME_N%": {
          "type": "framework",
          "optional": true,
          "version": "~1.117.0"
        }
      }
    }

.. _platform_creating_build_script:

Build Script ``main.py``
------------------------

Platform's build script is based on a next-generation build tool named
`SCons <http://www.scons.org>`_. PlatformIO has own built-in firmware builder
``env.BuildProgram`` with the deep libraries search. Please look into a
base template of ``main.py``.

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


.. _platform_creating_installation:

Installation
------------

1. Create ``platforms`` directory in :ref:`projectconf_pio_home_dir` if it
   doesn't exist.
2. Create ``myplatform`` directory in ``platforms``
3. Copy ``platform.json`` and ``builder/main.py`` files to ``myplatform`` directory.
4. Search available platforms via :ref:`cmd_platform_search` command. You
   should see ``myplatform`` platform.
5. Install ``myplatform`` platform via :ref:`cmd_platform_install` command.

Now, you can use ``myplatform`` for the :ref:`projectconf_env_platform`
option in :ref:`projectconf`.

Examples
--------

Please take a look at the source code of
`PlatformIO Development Platforms <https://github.com/platformio?query=platform->`_.
