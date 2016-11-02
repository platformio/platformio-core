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

.. _cmd_remote_run:

platformio remote run
=====================

**Over-The-Air (OTA) Firmware Updates**

.. contents::

Usage
-----

.. code-block:: bash

    platformio remote run [OPTIONS]

    # process environments using specified PIO Remote Agent
    platformio remote --agent NAME run [OPTIONS]


Description
-----------

Process remotely environments which are defined in :ref:`projectconf` file.
By default, :ref:`pio_remote` builds project on the local machine and deploy
final firmware Over-The-Air (OTA) to remote device.

If you need to build project on remote machine, please use
:option:`platformio remote run --build-remotely` option. In this case,
:ref:`pio_remote` will automatically deploy your project to remote machine,
install required toolchains, frameworks, SDKs, etc and build/upload firmware.


Options
-------

.. program:: platformio remote run

.. option::
    -e, --environment

Process specified environments.

You can also specify which environments should be processed by default using
:ref:`projectconf_pio_env_default` option from :ref:`projectconf`.


.. option::
    -t, --target

Process specified targets.

Built-in targets:

* ``clean`` delete compiled object files, libraries and firmware/program binaries
* ``upload`` firmware "auto-uploading" for embedded platforms
* ``program`` firmware "auto-uploading" for embedded platforms using external
  programmer (available only for :ref:`platform_atmelavr`)
* ``buildfs`` :ref:`platform_espressif_uploadfs`
* ``uploadfs`` :ref:`platform_espressif_uploadfs`
* ``envdump`` dump current build environment
* ``size`` print the size of the sections in a firmware/program

.. option::
    --upload-port

Custom upload port of embedded board. To print all available ports use
:ref:`cmd_remote_device` command.

If upload port is not specified, PlatformIO will try to detect it automatically.

.. option::
    -d, --project-dir

Specify the path to project directory. By default, ``--project-dir`` is equal
to current working directory (``CWD``).

.. option::
    -v, --verbose

Shows detailed information when processing environments.

This option can be set globally using :ref:`setting_force_verbose` setting
or by environment variable :envvar:`PLATFORMIO_SETTING_FORCE_VERBOSE`.

.. option::
    --disable-auto-clean

Disable auto-clean of :ref:`projectconf_pio_envs_dir` when :ref:`projectconf`
or :ref:`projectconf_pio_src_dir` (project structure) have been modified.

.. option::
    -r, --build-remotely

By default, :ref:`pio_remote` builds project on the local machine and deploy
final firmware Over-The-Air (OTA) to remote device.

If you need to build project on remote machine, please use
:option:`platformio remote run --build-remotely` option. In this case,
:ref:`pio_remote` will automatically deploy your project to remote machine,
install required toolchains, frameworks, SDKs, etc and build/upload firmware.

Example
-------

.. code::

    > platformio remote run --environment uno --target upload

    PlatformIO Plus (https://pioplus.com)
    Building project locally
    [Wed Oct 26 16:35:09 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    --------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 25 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/uno/src/main.o
    Archiving .pioenvs/uno/libFrameworkArduinoVariant.a
    Indexing .pioenvs/uno/libFrameworkArduinoVariant.a
    Compiling .pioenvs/uno/FrameworkArduino/CDC.o
    Compiling .pioenvs/uno/FrameworkArduino/HardwareSerial.o
    Compiling .pioenvs/uno/FrameworkArduino/HardwareSerial0.o
    Compiling .pioenvs/uno/FrameworkArduino/HardwareSerial1.o
    Compiling .pioenvs/uno/FrameworkArduino/HardwareSerial2.o
    Compiling .pioenvs/uno/FrameworkArduino/HardwareSerial3.o
    Compiling .pioenvs/uno/FrameworkArduino/IPAddress.o
    Compiling .pioenvs/uno/FrameworkArduino/PluggableUSB.o
    Compiling .pioenvs/uno/FrameworkArduino/Print.o
    Compiling .pioenvs/uno/FrameworkArduino/Stream.o
    Compiling .pioenvs/uno/FrameworkArduino/Tone.o
    Compiling .pioenvs/uno/FrameworkArduino/USBCore.o
    Compiling .pioenvs/uno/FrameworkArduino/WInterrupts.o
    Compiling .pioenvs/uno/FrameworkArduino/WMath.o
    Compiling .pioenvs/uno/FrameworkArduino/WString.o
    Compiling .pioenvs/uno/FrameworkArduino/_wiring_pulse.o
    Compiling .pioenvs/uno/FrameworkArduino/abi.o
    Compiling .pioenvs/uno/FrameworkArduino/hooks.o
    Compiling .pioenvs/uno/FrameworkArduino/main.o
    Compiling .pioenvs/uno/FrameworkArduino/new.o
    Compiling .pioenvs/uno/FrameworkArduino/wiring.o
    Compiling .pioenvs/uno/FrameworkArduino/wiring_analog.o
    Compiling .pioenvs/uno/FrameworkArduino/wiring_digital.o
    Compiling .pioenvs/uno/FrameworkArduino/wiring_pulse.o
    Compiling .pioenvs/uno/FrameworkArduino/wiring_shift.o
    Archiving .pioenvs/uno/libFrameworkArduino.a
    Indexing .pioenvs/uno/libFrameworkArduino.a
    Linking .pioenvs/uno/firmware.elf
    Checking program size
    Building .pioenvs/uno/firmware.hex
    text       data     bss     dec     hex filename
    2574         48     168    2790     ae6 .pioenvs/uno/firmware.elf
    ========================= [SUCCESS] Took 10.01 seconds =======================
    ================================== [SUMMARY] =================================
    Environment nodemcuv2   [SKIP]
    Environment uno_pic32   [SKIP]
    Environment teensy31    [SKIP]
    Environment uno         [SUCCESS]
    ========================= [SUCCESS] Took 10.01 seconds ========================
    Uploading firmware remotely
    [Wed Oct 26 19:35:20 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    ----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Looking for upload port...
    Auto-detected: /dev/cu.usbmodemFA1431
    Uploading .pioenvs/uno/firmware.hex
    avrdude: AVR device initialized and ready to accept instructions
    Reading | ################################################## | 100% 0.00s
    avrdude: Device signature = 0x1e950f
    avrdude: reading input file ".pioenvs/uno/firmware.hex"
    avrdude: writing flash (2622 bytes):
    Writing | ################################################## | 100% 0.43s
    avrdude: 2622 bytes of flash written
    avrdude: verifying flash memory against .pioenvs/uno/firmware.hex:
    avrdude: load data flash data from input file .pioenvs/uno/firmware.hex:
    avrdude: input file .pioenvs/uno/firmware.hex contains 2622 bytes
    avrdude: reading on-chip flash data:
    Reading | ################################################## | 100% 0.34s
    avrdude: verifying ...
    avrdude: 2622 bytes of flash verified
    avrdude done.  Thank you.
    ========================= [SUCCESS] Took 3.04 seconds =======================
    ========================= [SUMMARY] =========================================
    Environment nodemcuv2   [SKIP]
    Environment uno_pic32   [SKIP]
    Environment teensy31    [SKIP]
    Environment uno         [SUCCESS]
    ========================= [SUCCESS] Took 3.04 seconds ========================
