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

.. code-block::   bash

    $ platformio run
    [Sun Jul 17 00:09:16 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    -----------------------------------------------------------------------------------------------
    Looking for dependencies...
    Collecting 32 compatible libraries
    Processing src/main.cpp
    Processing .pioenvs/uno/libFrameworkArduinoVariant.a
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/CDC.cpp
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/HardwareSerial.cpp
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/HardwareSerial0.cpp
    ...
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/wiring_analog.c
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/wiring_digital.c
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/wiring_pulse.c
    Processing .platformio/packages/framework-arduinoavr/cores/arduino/wiring_shift.c
    Processing .pioenvs/uno/libFrameworkArduino.a
    Processing .pioenvs/uno/firmware.elf
    Processing .pioenvs/uno/firmware.hex
    Processing size
    AVR Memory Usage
    ----------------
    Device: atmega328p

    Program:    1034 bytes (3.2% Full)
    (.text + .data + .bootloader)

    Data:          9 bytes (0.4% Full)
    (.data + .bss + .noinit)



2. Process specific environment

.. code-block:: bash

    $ platformio run -e arduino_pro5v -e launchpad_lm4f120
    [Sun Jul 17 00:10:14 2016] Processing nodemcu (platform: espressif, board: nodemcu, framework: arduino)
    --------------------------------------------------------------------------------------------------------
    Looking for dependencies...
    Collecting 29 compatible libraries
    Processing src/main.cpp
    Processing .pioenvs/nodemcu/libFrameworkArduinoVariant.a
    Processing .platformio/packages/framework-arduinoespressif/cores/esp8266/Esp.cpp
    ...
    Processing .platformio/packages/framework-arduinoespressif/cores/esp8266/pgmspace.cpp
    Processing .platformio/packages/framework-arduinoespressif/cores/esp8266/setjmp.S
    Processing .pioenvs/nodemcu/libFrameworkArduino.a
    Processing .platformio/packages/framework-arduinoespressif/tools/sdk/lib/libmesh.a
    ...
    Processing .platformio/packages/framework-arduinoespressif/tools/sdk/lib/libaxtls.a
    Processing .platformio/packages/framework-arduinoespressif/tools/sdk/lib/libstdc++.a
    Processing .pioenvs/nodemcu/firmware.elf
    Processing .platformio/packages/tool-esptool/esptool
    Processing .pioenvs/nodemcu/firmware.bin
    Processing size
    text       data     bss     dec     hex filename
    221456      884   29496  251836   3d7bc .pioenvs/nodemcu/firmware.elf


3. Process specific target

.. code-block:: bash

    $ platformio run -t clean
    [Sun Jul 17 00:19:36 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    Looking for dependencies...
    Collecting 32 compatible libraries
    Removed .pioenvs/uno/FrameworkArduino/CDC.o
    Removed .pioenvs/uno/FrameworkArduino/HardwareSerial.o
    ...
    Removed .pioenvs/uno/libFrameworkArduinoVariant.a
    Removed .pioenvs/uno/src/main.o
    Removed .pioenvs/uno/libFrameworkArduino.a
    Removed .pioenvs/uno/firmware.elf
    Removed .pioenvs/uno/firmware.hex


4. Mix environments and targets

.. code-block:: bash

    $ platformio run -e teensy31 -t upload
    [Sun Jul 17 00:27:14 2016] Processing teensy31 (platform: teensy, board: teensy31, framework: arduino)
    -------------------------------------------------------------------------------------------------------
    Looking for dependencies...
    Collecting 25 compatible libraries
    Processing src/main.cpp
    Processing .platformio/packages/framework-arduinoteensy/cores/teensy3/AudioStream.cpp
    Processing .platformio/packages/framework-arduinoteensy/cores/teensy3/DMAChannel.cpp
    Processing .platformio/packages/framework-arduinoteensy/cores/teensy3/HardwareSerial1.cpp
    ...
    Processing .platformio/packages/framework-arduinoteensy/cores/teensy3/yield.cpp
    Processing .platformio/packages/tool-teensy/teensy_loader_cli
    Processing .pioenvs/teensy31/libFrameworkArduino.a
    Processing .pioenvs/teensy31/firmware.elf
    Check program size...
    text       data     bss     dec     hex filename
    11080       168    2288   13536    34e0 .pioenvs/teensy31/firmware.elf
    Processing .pioenvs/teensy31/firmware.hex
    Processing upload
    Teensy Loader, Command Line, Version 2.0
    Read ".pioenvs/teensy31/firmware.hex": 11248 bytes, 4.3% usage
    Soft reboot is not implemented for OSX
    Waiting for Teensy device...
    (hint: press the reset button)
    Found HalfKay Bootloader
    Read ".pioenvs/teensy31/firmware.hex": 11248 bytes, 4.3% usage
    Programming...........
    Booting
