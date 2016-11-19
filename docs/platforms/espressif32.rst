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

.. _platform_espressif32:

Platform ``espressif32``
========================
Espressif Systems is a privately held fabless semiconductor company. They provide wireless communications and Wi-Fi chips which are widely used in mobile devices and the Internet of Things applications.

For more detailed information please visit `vendor site <https://espressif.com/>`_.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``framework-arduinoespressif32``
      - `Arduino Wiring-based Framework (ESP32 Core) <https://github.com/espressif/arduino-esp32>`_

    * - ``framework-espidf``
      - `Espressif IoT Development Framework <https://github.com/espressif/esp-idf>`_

    * - ``tool-esptoolpy``
      - `Espressif ROM Bootloader utility <https://github.com/espressif/esptool>`_

    * - ``toolchain-xtensa32``
      - `xtensa32-gcc <https://github.com/espressif/esp-idf>`_, `GDB <http://www.gnu.org/software/gdb/>`_

.. warning::
    **Linux Users**:

    * Ubuntu/Debian users may need to add own "username" to the "dialout"
      group if they are not "root", doing this issuing a
      ``sudo usermod -a -G dialout yourusername``.
    * Install "udev" rules file `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_
      (an instruction is located in the file).
    * Raspberry Pi users, please read this article
      `Enable serial port on Raspberry Pi <https://hallard.me/enable-serial-port-on-raspberry-pi/>`__.


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

    * - :ref:`framework_espidf`
      - Espressif IoT Development Framework. Official development framework for ESP32.

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

April Brother
~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``espea32``
      - `April Brother ESPea32 <https://blog.aprbrother.com/product/espea>`_
      - ESP32
      - 160 MHz
      - 1024 Kb
      - 288 Kb

Electronic SweetPeas
~~~~~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``esp320``
      - `Electronic SweetPeas ESP320 <http://www.sweetpeas.se/controller-modules/10-esp210.html>`_
      - ESP32
      - 160 MHz
      - 1024 Kb
      - 288 Kb

Espressif
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``esp32dev``
      - `Espressif ESP32 Dev Module <https://en.wikipedia.org/wiki/ESP32>`_
      - ESP32
      - 160 MHz
      - 1024 Kb
      - 112 Kb

MakerAsia
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``nano32``
      - `MakerAsia Nano32 <http://iot-bits.com/nano32-esp32-development-board>`_
      - ESP32
      - 160 MHz
      - 1024 Kb
      - 288 Kb

Noduino
~~~~~~~

.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``quantum``
      - `Noduino Quantum <http://wiki.jackslab.org/Noduino>`_
      - ESP32
      - 160 MHz
      - 1024 Kb
      - 288 Kb

WEMOS
~~~~~

.. list-table::
    :header-rows:  1

    * - ID
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lolin32``
      - `WEMOS LoLin32 <https://wemos.cc>`_
      - ESP32
      - 160 MHz
      - 1024 Kb
      - 288 Kb
