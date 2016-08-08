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

.. _cmd_update:

platformio update
=================

.. contents::

Usage
-----

.. code-block:: bash

    platformio update [OPTIONS]


Description
-----------

Check or update installed :ref:`platforms` and global
:ref:`Libraries <librarymanager>`. This command is combination of 2 sub-commands:

* :ref:`cmd_platform_update`
* :ref:`cmd_lib_update`

Options
-------

.. program:: platformio update

.. option::
    -c, --only-check

Do not update, only check for new version


Examples
--------

.. code::

    > platformio update

    Platform Manager
    ================
    Platform timsp430
    --------
    Updating timsp430 @ 0.0.0:  [Up-to-date]
    Updating toolchain-timsp430 @ 1.40603.0:    [Up-to-date]
    Updating framework-energiamsp430 @ 1.17.0:  [Up-to-date]
    Updating framework-arduinomsp430 @ 1.10601.0:   [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform freescalekinetis
    --------
    Updating freescalekinetis @ 0.0.0:  [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform ststm32
    --------
    Updating ststm32 @ 0.0.0:   [Up-to-date]
    Updating framework-libopencm3 @ 1.1.0:  [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating tool-stlink @ 1.10200.0:   [Up-to-date]
    Updating framework-spl @ 1.10201.0:     [Up-to-date]
    Updating framework-cmsis @ 1.40300.0:   [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform lattice_ice40
    --------
    Updating lattice_ice40 @ 0.0.0:     [Up-to-date]
    Updating toolchain-icestorm @ 1.7.0:    [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform atmelavr
    --------
    Updating atmelavr @ 0.0.0:  [Up-to-date]
    Updating framework-arduinoavr @ 1.10608.1:  [Up-to-date]
    Updating tool-avrdude @ 1.60001.1:  [Up-to-date]
    Updating toolchain-atmelavr @ 1.40801.0:    [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform espressif
    --------
    Updating espressif @ 0.0.0:     [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]
    Updating toolchain-xtensa @ 1.40802.0:  [Up-to-date]
    Updating tool-esptool @ 1.409.0:    [Up-to-date]
    Updating tool-mkspiffs @ 1.102.0:   [Up-to-date]
    Updating framework-arduinoespressif @ 1.20300.0:    [Up-to-date]
    Updating sdk-esp8266 @ 1.10502.0:   [Up-to-date]

    Platform linux_x86_64
    --------
    Updating linux_x86_64 @ 0.0.0:  [Up-to-date]
    Updating toolchain-gcclinux64 @ 1.40801.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform windows_x86
    --------
    Updating windows_x86 @ 0.0.0:   [Up-to-date]
    Updating toolchain-gccmingw32 @ 1.40800.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform teensy
    --------
    Updating teensy @ 0.0.0:    [Up-to-date]
    Updating framework-arduinoteensy @ 1.128.0:     [Up-to-date]
    Updating tool-teensy @ 1.1.0:   [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]
    Updating toolchain-atmelavr @ 1.40801.0:    [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]

    Platform nordicnrf51
    --------
    Updating nordicnrf51 @ 0.0.0:   [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating framework-arduinonordicnrf51 @ 1.20302.0:  [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform titiva
    --------
    Updating titiva @ 0.0.0:    [Up-to-date]
    Updating framework-libopencm3 @ 1.1.0:  [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating framework-energiativa @ 1.17.0:    [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform atmelsam
    --------
    Updating atmelsam @ 0.0.0:  [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating tool-openocd @ 1.900.0:    [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]
    Updating tool-avrdude @ 1.60001.1:  [Up-to-date]
    Updating tool-bossac @ 1.10601.0:   [Up-to-date]

    Platform siliconlabsefm32
    --------
    Updating siliconlabsefm32 @ 0.0.0:  [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform microchippic32
    --------
    Updating microchippic32 @ 0.0.0:    [Up-to-date]
    Updating framework-arduinomicrochippic32 @ 1.10201.0:   [Up-to-date]
    Updating toolchain-microchippic32 @ 1.40803.0:  [Up-to-date]
    Updating tool-pic32prog @ 1.200200.0:   [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform linux_i686
    --------
    Updating linux_i686 @ 0.0.0:    [Up-to-date]
    Updating toolchain-gcclinux32 @ 1.40801.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform intel_arc32
    --------
    Updating intel_arc32 @ 0.0.0:   [Up-to-date]
    Updating framework-arduinointel @ 1.10006.0:    [Up-to-date]
    Updating tool-arduino101load @ 1.124.0:     [Up-to-date]
    Updating toolchain-intelarc32 @ 1.40805.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform nxplpc
    --------
    Updating nxplpc @ 0.0.0:    [Up-to-date]
    Updating framework-mbed @ 1.121.1:  [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform linux_arm
    --------
    Updating linux_arm @ 0.0.0:     [Up-to-date]
    Updating toolchain-gccarmlinuxgnueabi @ 1.40802.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform native
    --------
    Updating native @ 0.0.0:    [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]


    Library Manager
    ===============
    Updating Adafruit-GFX @ 334e815bc1:     [Up-to-date]
    Updating Adafruit-ST7735 @ d53d4bf03a:  [Up-to-date]
    Updating Adafruit-DHT @ 09344416d2:     [Up-to-date]
    Updating Adafruit-Unified-Sensor @ f2af6f4efc:  [Up-to-date]
    Updating ESP8266_SSD1306 @ 3.2.3:   [Up-to-date]
    Updating EngduinoMagnetometer @ 3.1.0:  [Up-to-date]
    Updating IRremote @ 2.2.1:  [Up-to-date]
    Updating Json @ 5.6.4:  [Up-to-date]
    Updating MODSERIAL @ d8422efe47:    [Up-to-date]
    Updating PJON @ 1fb26fd:    [Checking]
    git version 2.7.4 (Apple Git-66)
    Already up-to-date.
    Updating Servo @ 36b69a7ced07:  [Checking]
    Mercurial Distributed SCM (version 3.8.4)
    (see https://mercurial-scm.org for more information)

    Copyright (C) 2005-2016 Matt Mackall and others
    This is free software; see the source for copying conditions. There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    pulling from https://developer.mbed.org/users/simon/code/Servo/
    searching for changes
    no changes found
    Updating TextLCD @ 308d188a2d3a:    [Checking]
    Mercurial Distributed SCM (version 3.8.4)
    (see https://mercurial-scm.org for more information)

    Copyright (C) 2005-2016 Matt Mackall and others
    This is free software; see the source for copying conditions. There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    pulling from https://developer.mbed.org/users/simon/code/TextLCD/
    searching for changes
    no changes found
