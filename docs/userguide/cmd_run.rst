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

.. _cmd_run:

platformio run
==============

.. contents::

Usage
-----

.. code-block:: bash

    platformio run [OPTIONS]


Description
-----------

Process environments which are defined in :ref:`projectconf` file


Options
-------

.. program:: platformio run

.. option::
    -e, --environment

Process specified environments.

You can also specify which environments should be processed by default using
:ref:`projectconf_pio_env_default`.


.. option::
    -t, --target

Process specified targets.

Pre-built targets:

* ``clean`` delete compiled object files, libraries and firmware/program binaries
* ``upload`` firmware "auto-uploading" for embedded platforms
* ``program`` firmware "auto-uploading" for embedded platforms using external
  programmer (available only for :ref:`platform_atmelavr`)
* ``uploadlazy`` upload existing firmware without project rebuilding
* ``uploadfs`` :ref:`platform_espressif_uploadfs`
* ``envdump`` dump current build environment
* ``size`` print the size of the sections in a firmware/program

.. option::
    --upload-port

Upload port of embedded board. To print all available ports use
:ref:`cmd_device` command.

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

Examples
--------

1. Process `Wiring Blink Example <https://github.com/platformio/platformio-examples/tree/develop/wiring-blink>`_

.. code::

    > platformio run

    [Wed Sep  7 15:48:58 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    -----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 36 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/uno/src/main.o
    Archiving .pioenvs/uno/libFrameworkArduinoVariant.a
    Indexing .pioenvs/uno/libFrameworkArduinoVariant.a
    Compiling .pioenvs/uno/FrameworkArduino/CDC.o
    ...
    Compiling .pioenvs/uno/FrameworkArduino/wiring_shift.o
    Archiving .pioenvs/uno/libFrameworkArduino.a
    Indexing .pioenvs/uno/libFrameworkArduino.a
    Linking .pioenvs/uno/firmware.elf
    Building .pioenvs/uno/firmware.hex
    Calculating size .pioenvs/uno/firmware.elf
    AVR Memory Usage
    ----------------
    Device: atmega328p

    Program:    1034 bytes (3.2% Full)
    (.text + .data + .bootloader)

    Data:          9 bytes (0.4% Full)
    (.data + .bss + .noinit)


    =========================== [SUCCESS] Took 2.47 seconds ===========================

    [Wed Sep  7 15:49:01 2016] Processing nodemcu (platform: espressif8266, board: nodemcu, framework: arduino)
    -----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 34 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/nodemcu/src/main.o
    Archiving .pioenvs/nodemcu/libFrameworkArduinoVariant.a
    Indexing .pioenvs/nodemcu/libFrameworkArduinoVariant.a
    Compiling .pioenvs/nodemcu/FrameworkArduino/Esp.o
    Compiling .pioenvs/nodemcu/FrameworkArduino/FS.o
    Compiling .pioenvs/nodemcu/FrameworkArduino/HardwareSerial.o
    ...
    Archiving .pioenvs/nodemcu/libFrameworkArduino.a
    Indexing .pioenvs/nodemcu/libFrameworkArduino.a
    Linking .pioenvs/nodemcu/firmware.elf
    Calculating size .pioenvs/nodemcu/firmware.elf
    text       data     bss     dec     hex filename
    221240      888   29400  251528   3d688 .pioenvs/nodemcu/firmware.elf
    Building .pioenvs/nodemcu/firmware.bin
    =========================== [SUCCESS] Took 6.43 seconds ===========================

    [Wed Sep  7 15:49:07 2016] Processing teensy31 (platform: teensy, board: teensy31, framework: arduino)
    -----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 96 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/teensy31/src/main.o
    Compiling .pioenvs/teensy31/FrameworkArduino/AudioStream.o
    Compiling .pioenvs/teensy31/FrameworkArduino/DMAChannel.o
    ...
    Compiling .pioenvs/teensy31/FrameworkArduino/yield.o
    Archiving .pioenvs/teensy31/libFrameworkArduino.a
    Indexing .pioenvs/teensy31/libFrameworkArduino.a
    Linking .pioenvs/teensy31/firmware.elf
    Calculating size .pioenvs/teensy31/firmware.elf
    text       data     bss     dec     hex filename
    11288       168    2288   13744    35b0 .pioenvs/teensy31/firmware.elf
    Building .pioenvs/teensy31/firmware.hex
    =========================== [SUCCESS] Took 5.36 seconds ===========================

    [Wed Sep  7 15:49:12 2016] Processing lpmsp430g2553 (platform: timsp430, build_flags: -D LED_BUILTIN=RED_LED, board: lpmsp430g2553, framework: energia)
    -----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 29 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/lpmsp430g2553/src/main.o
    Compiling .pioenvs/lpmsp430g2553/FrameworkEnergia/HardwareSerial.o
    Compiling .pioenvs/lpmsp430g2553/FrameworkEnergia/IPAddress.o
    ...
    Compiling .pioenvs/lpmsp430g2553/FrameworkEnergia/wiring_digital.o
    Compiling .pioenvs/lpmsp430g2553/FrameworkEnergia/wiring_pulse.o
    Compiling .pioenvs/lpmsp430g2553/FrameworkEnergia/wiring_shift.o
    Archiving .pioenvs/lpmsp430g2553/libFrameworkEnergia.a
    Indexing .pioenvs/lpmsp430g2553/libFrameworkEnergia.a
    Linking .pioenvs/lpmsp430g2553/firmware.elf
    Calculating size .pioenvs/lpmsp430g2553/firmware.elf
    text       data     bss     dec     hex filename
    820           0      20     840     348 .pioenvs/lpmsp430g2553/firmware.elf
    Building .pioenvs/lpmsp430g2553/firmware.hex
    =========================== [SUCCESS] Took 2.34 seconds ===========================

2. Process specific environment

.. code::

    > platformio run -e nodemcu -e teensy31

    [Wed Sep  7 15:49:01 2016] Processing nodemcu (platform: espressif8266, board: nodemcu, framework: arduino)
    -----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 34 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/nodemcu/src/main.o
    Archiving .pioenvs/nodemcu/libFrameworkArduinoVariant.a
    Indexing .pioenvs/nodemcu/libFrameworkArduinoVariant.a
    Compiling .pioenvs/nodemcu/FrameworkArduino/Esp.o
    Compiling .pioenvs/nodemcu/FrameworkArduino/FS.o
    Compiling .pioenvs/nodemcu/FrameworkArduino/HardwareSerial.o
    ...
    Archiving .pioenvs/nodemcu/libFrameworkArduino.a
    Indexing .pioenvs/nodemcu/libFrameworkArduino.a
    Linking .pioenvs/nodemcu/firmware.elf
    Calculating size .pioenvs/nodemcu/firmware.elf
    text       data     bss     dec     hex filename
    221240      888   29400  251528   3d688 .pioenvs/nodemcu/firmware.elf
    Building .pioenvs/nodemcu/firmware.bin
    =========================== [SUCCESS] Took 6.43 seconds ===========================

    [Wed Sep  7 15:49:07 2016] Processing teensy31 (platform: teensy, board: teensy31, framework: arduino)
    -----------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 96 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/teensy31/src/main.o
    Compiling .pioenvs/teensy31/FrameworkArduino/AudioStream.o
    Compiling .pioenvs/teensy31/FrameworkArduino/DMAChannel.o
    ...
    Compiling .pioenvs/teensy31/FrameworkArduino/yield.o
    Archiving .pioenvs/teensy31/libFrameworkArduino.a
    Indexing .pioenvs/teensy31/libFrameworkArduino.a
    Linking .pioenvs/teensy31/firmware.elf
    Calculating size .pioenvs/teensy31/firmware.elf
    text       data     bss     dec     hex filename
    11288       168    2288   13744    35b0 .pioenvs/teensy31/firmware.elf
    Building .pioenvs/teensy31/firmware.hex
    =========================== [SUCCESS] Took 5.36 seconds ===========================


3. Process specific target (clean project)

.. code:: bash

    > platformio run -t clean
    [Wed Sep  7 15:53:26 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    -----------------------------------------------------------------------------------------------------
    Removed .pioenvs/uno/firmware.elf
    Removed .pioenvs/uno/firmware.hex
    Removed .pioenvs/uno/libFrameworkArduino.a
    Removed .pioenvs/uno/libFrameworkArduinoVariant.a
    Removed .pioenvs/uno/FrameworkArduino/_wiring_pulse.o
    Removed .pioenvs/uno/FrameworkArduino/abi.o
    Removed .pioenvs/uno/FrameworkArduino/CDC.o
    Removed .pioenvs/uno/FrameworkArduino/HardwareSerial.o
    Removed .pioenvs/uno/FrameworkArduino/HardwareSerial0.o
    Removed .pioenvs/uno/FrameworkArduino/HardwareSerial1.o
    Removed .pioenvs/uno/FrameworkArduino/HardwareSerial2.o
    Removed .pioenvs/uno/FrameworkArduino/HardwareSerial3.o
    Removed .pioenvs/uno/FrameworkArduino/hooks.o
    Removed .pioenvs/uno/FrameworkArduino/IPAddress.o
    Removed .pioenvs/uno/FrameworkArduino/main.o
    Removed .pioenvs/uno/FrameworkArduino/new.o
    Removed .pioenvs/uno/FrameworkArduino/PluggableUSB.o
    Removed .pioenvs/uno/FrameworkArduino/Print.o
    Removed .pioenvs/uno/FrameworkArduino/Stream.o
    Removed .pioenvs/uno/FrameworkArduino/Tone.o
    Removed .pioenvs/uno/FrameworkArduino/USBCore.o
    Removed .pioenvs/uno/FrameworkArduino/WInterrupts.o
    Removed .pioenvs/uno/FrameworkArduino/wiring.o
    Removed .pioenvs/uno/FrameworkArduino/wiring_analog.o
    Removed .pioenvs/uno/FrameworkArduino/wiring_digital.o
    Removed .pioenvs/uno/FrameworkArduino/wiring_pulse.o
    Removed .pioenvs/uno/FrameworkArduino/wiring_shift.o
    Removed .pioenvs/uno/FrameworkArduino/WMath.o
    Removed .pioenvs/uno/FrameworkArduino/WString.o
    Removed .pioenvs/uno/src/main.o
    Done cleaning
    ======================= [SUCCESS] Took 0.49 seconds =======================

    [Wed Sep  7 15:53:27 2016] Processing nodemcu (platform: espressif8266, board: nodemcu, framework: arduino)
    -----------------------------------------------------------------------------------------------------
    Removed .pioenvs/nodemcu/firmware.bin
    Removed .pioenvs/nodemcu/firmware.elf
    Removed .pioenvs/nodemcu/libFrameworkArduino.a
    Removed .pioenvs/nodemcu/libFrameworkArduinoVariant.a
    ...
    Removed .pioenvs/nodemcu/FrameworkArduino/spiffs/spiffs_nucleus.o
    Removed .pioenvs/nodemcu/FrameworkArduino/umm_malloc/umm_malloc.o
    Removed .pioenvs/nodemcu/src/main.o
    Done cleaning
    ======================= [SUCCESS] Took 0.50 seconds =======================

    [Wed Sep  7 15:53:27 2016] Processing teensy31 (platform: teensy, board: teensy31, framework: arduino)
    -----------------------------------------------------------------------------------------------------
    Removed .pioenvs/teensy31/firmware.elf
    Removed .pioenvs/teensy31/firmware.hex
    Removed .pioenvs/teensy31/libFrameworkArduino.a
    Removed .pioenvs/teensy31/FrameworkArduino/analog.o
    Removed .pioenvs/teensy31/FrameworkArduino/AudioStream.o
    ...
    Removed .pioenvs/teensy31/FrameworkArduino/WString.o
    Removed .pioenvs/teensy31/FrameworkArduino/yield.o
    Removed .pioenvs/teensy31/src/main.o
    Done cleaning
    ======================= [SUCCESS] Took 0.50 seconds =======================

    [Wed Sep  7 15:53:28 2016] Processing lpmsp430g2553 (platform: timsp430, build_flags: -D LED_BUILTIN=RED_LED, board: lpmsp430g2553, framework: energia)
    -----------------------------------------------------------------------------------------------------
    Removed .pioenvs/lpmsp430g2553/firmware.elf
    Removed .pioenvs/lpmsp430g2553/firmware.hex
    Removed .pioenvs/lpmsp430g2553/libFrameworkEnergia.a
    Removed .pioenvs/lpmsp430g2553/FrameworkEnergia/atof.o
    ...
    Removed .pioenvs/lpmsp430g2553/FrameworkEnergia/avr/dtostrf.o
    Removed .pioenvs/lpmsp430g2553/src/main.o
    Done cleaning
    ======================= [SUCCESS] Took 0.49 seconds =======================


4. Mix environments and targets

.. code::

    > platformio run -e uno -t upload

    [Wed Sep  7 15:55:11 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    --------------------------------------------------------------------------------------------------
    Verbose mode can be enabled via `-v, --verbose` option
    Collected 36 compatible libraries
    Looking for dependencies...
    Project does not have dependencies
    Compiling .pioenvs/uno/src/main.o
    Archiving .pioenvs/uno/libFrameworkArduinoVariant.a
    Indexing .pioenvs/uno/libFrameworkArduinoVariant.a
    Compiling .pioenvs/uno/FrameworkArduino/CDC.o
    ...
    Compiling .pioenvs/uno/FrameworkArduino/wiring_shift.o
    Archiving .pioenvs/uno/libFrameworkArduino.a
    Indexing .pioenvs/uno/libFrameworkArduino.a
    Linking .pioenvs/uno/firmware.elf
    Checking program size .pioenvs/uno/firmware.elf
    text       data     bss     dec     hex filename
    1034          0       9    1043     413 .pioenvs/uno/firmware.elf
    Building .pioenvs/uno/firmware.hex
    Looking for upload port...
    Auto-detected: /dev/cu.usbmodemFA141
    Uploading .pioenvs/uno/firmware.hex

    avrdude: AVR device initialized and ready to accept instructions

    Reading | ################################################## | 100% 0.01s

    avrdude: Device signature = 0x1e950f
    avrdude: reading input file ".pioenvs/uno/firmware.hex"
    avrdude: writing flash (1034 bytes):

    Writing | ################################################## | 100% 0.18s

    avrdude: 1034 bytes of flash written
    avrdude: verifying flash memory against .pioenvs/uno/firmware.hex:
    avrdude: load data flash data from input file .pioenvs/uno/firmware.hex:
    avrdude: input file .pioenvs/uno/firmware.hex contains 1034 bytes
    avrdude: reading on-chip flash data:

    Reading | ################################################## | 100% 0.15s

    avrdude: verifying ...
    avrdude: 1034 bytes of flash verified

    avrdude: safemode: Fuses OK (H:00, E:00, L:00)

    avrdude done.  Thank you.

    ======================== [SUCCESS] Took 4.14 seconds ========================
