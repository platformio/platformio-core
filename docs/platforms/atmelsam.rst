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

.. _platform_atmelsam:

Platform ``atmelsam``
=====================
Atmel | SMART offers Flash- based ARM products based on the ARM Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB to 2MB of Flash including a rich peripheral and feature mix.

For more detailed information please visit `vendor site <http://www.atmel.com/products/microcontrollers/arm/default.aspx>`_.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``framework-mbed``
      - `mbed Framework <http://mbed.org>`_

    * - ``toolchain-gccarmnoneeabi``
      - `gcc-arm-embedded <https://launchpad.net/gcc-arm-embedded>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``framework-arduinosam``
      - `Arduino Wiring-based Framework (SAM Core, 1.6) <http://arduino.cc/en/Reference/HomePage>`_

    * - ``ldscripts``
      - `Linker Scripts <https://sourceware.org/binutils/docs/ld/Scripts.html>`_

    * - ``framework-simba``
      - `Simba Framework <https://github.com/eerimoq/simba>`_

    * - ``tool-openocd``
      - `OpenOCD <http://openocd.org>`_

    * - ``tool-avrdude``
      - `AVRDUDE <http://www.nongnu.org/avrdude/>`_

    * - ``tool-bossac``
      - `BOSSA CLI <https://sourceforge.net/projects/b-o-s-s-a/>`_

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).


    **Windows Users:** Please check that you have correctly installed USB
    driver from board manufacturer



Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description

    * - :ref:`framework_arduino`
      - Arduino Wiring-based Framework allows writing cross-platform software to control devices attached to a wide range of Arduino boards to create all kinds of creative coding, interactive objects, spaces or physical experiences.

    * - :ref:`framework_mbed`
      - The mbed framework The mbed SDK has been designed to provide enough hardware abstraction to be intuitive and concise, yet powerful enough to build complex projects. It is built on the low-level ARM CMSIS APIs, allowing you to code down to the metal if needed. In addition to RTOS, USB and Networking libraries, a cookbook of hundreds of reusable peripheral and module libraries have been built on top of the SDK by the mbed Developer Community.

    * - :ref:`framework_simba`
      - Simba is an RTOS and build framework. It aims to make embedded programming easy and portable.

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

Adafruit
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``adafruit_feather_m0_usb``
      - `Adafruit Feather M0 <https://www.adafruit.com/product/2772>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

Arduino
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``due``
      - `Arduino Due (Programming Port) <http://www.arduino.org/products/boards/4-arduino-boards/arduino-due>`_
      - SAM3X8E
      - 84 MHz
      - 512 Kb
      - 32 Kb

    * - ``dueUSB``
      - `Arduino Due (USB Native Port) <http://www.arduino.org/products/boards/4-arduino-boards/arduino-due>`_
      - SAM3X8E
      - 84 MHz
      - 512 Kb
      - 32 Kb

    * - ``mkr1000USB``
      - `Arduino MKR1000 <https://www.arduino.cc/en/Main/ArduinoMKR1000>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``mzeroUSB``
      - `Arduino M0 <http://www.arduino.org/products/boards/arduino-m0>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``mzeropro``
      - `Arduino M0 Pro (Programming Port) <http://www.arduino.org/products/boards/arduino-m0-pro>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``mzeroproUSB``
      - `Arduino M0 Pro (Native USB Port) <http://www.arduino.org/products/boards/arduino-m0-pro>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``tian``
      - `Arduino Tian <http://www.arduino.org/products/boards/arduino-tian>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``zero``
      - `Arduino Zero (Programming Port) <https://www.arduino.cc/en/Main/ArduinoBoardZero>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``zeroUSB``
      - `Arduino Zero (USB Native Port) <https://www.arduino.cc/en/Main/ArduinoBoardZero>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

Atmel
~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``samd21_xpro``
      - `Atmel SAMD21-XPRO <https://developer.mbed.org/platforms/SAMD21-XPRO/>`_
      - ATSAMD21J18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``saml21_xpro_b``
      - `Atmel SAML21-XPRO-B <https://developer.mbed.org/platforms/SAML21-XPRO/>`_
      - ATSAML21J18B
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``samr21_xpro``
      - `Atmel ATSAMR21-XPRO <https://developer.mbed.org/platforms/SAMR21-XPRO/>`_
      - ATSAMR21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

Digistump
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``digix``
      - `Digistump DigiX <http://digistump.com/products/50>`_
      - AT91SAM3X8E
      - 84 MHz
      - 512 Kb
      - 28 Kb

SainSmart
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``sainSmartDue``
      - `SainSmart Due (Programming Port) <http://www.sainsmart.com/arduino/control-boards/sainsmart-due-atmel-sam3x8e-arm-cortex-m3-board-black.html>`_
      - AT91SAM3X8E
      - 84 MHz
      - 512 Kb
      - 32 Kb

    * - ``sainSmartDueUSB``
      - `SainSmart Due (USB Native Port) <http://www.sainsmart.com/arduino/control-boards/sainsmart-due-atmel-sam3x8e-arm-cortex-m3-board-black.html>`_
      - AT91SAM3X8E
      - 84 MHz
      - 512 Kb
      - 32 Kb

SparkFun
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``sparkfun_samd21_dev_usb``
      - `SparkFun SAMD21 Dev Breakout <https://www.sparkfun.com/products/13672>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``sparkfun_samd21_mini_usb``
      - `SparkFun SAMD21 Mini Breakout <https://www.sparkfun.com/products/13664>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb
