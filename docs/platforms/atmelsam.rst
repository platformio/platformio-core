..  Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
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

    * - ``toolchain-gccarmnoneeabi``
      - `gcc-arm-embedded <https://launchpad.net/gcc-arm-embedded>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``framework-arduinosam``
      - `Arduino Wiring-based Framework (SAM Core, 1.6) <http://arduino.cc/en/Reference/HomePage>`_

    * - ``tool-openocd``
      - `OpenOCD <http://openocd.org>`_

    * - ``framework-mbed``
      - `mbed Framework <http://mbed.org>`_

    * - ``ldscripts``
      - `Linker Scripts <https://sourceware.org/binutils/docs/ld/Scripts.html>`_

    * - ``tool-bossac``
      - `BOSSA CLI <https://sourceforge.net/projects/b-o-s-s-a/>`_

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).

    **Windows Users:** Please check that you have correctly installed USB driver
    from board manufacturer



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

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

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
      - `Arduino Due (Programming Port) <http://arduino.cc/en/Main/arduinoBoardDue>`_
      - SAM3X8E
      - 84 MHz
      - 512 Kb
      - 32 Kb

    * - ``dueUSB``
      - `Arduino Due (USB Native Port) <http://arduino.cc/en/Main/arduinoBoardDue>`_
      - SAM3X8E
      - 84 MHz
      - 512 Kb
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
