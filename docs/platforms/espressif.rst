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

.. _platform_espressif:

Platform ``espressif``
======================
Espressif Systems is a privately held fabless semiconductor company. They provide wireless communications and Wi-Fi chips which are widely used in mobile devices and the Internet of Things applications.

For more detailed information please visit `vendor site <https://espressif.com/>`_.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``ldscripts``
      - `Linker Scripts <https://sourceware.org/binutils/docs/ld/Scripts.html>`_

    * - ``sdk-esp8266``
      - `ESP8266 SDK <http://bbs.espressif.com>`_

    * - ``tool-esptool``
      - `esptool-ck <https://github.com/igrr/esptool-ck>`_

    * - ``framework-arduinoespressif``
      - `Arduino Wiring-based Framework (ESP8266 Core) <https://github.com/esp8266/Arduino>`_

    * - ``toolchain-xtensa``
      - `xtensa-gcc <https://github.com/jcmvbkbc/gcc-xtensa>`_, `GDB <http://www.gnu.org/software/gdb/>`_

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
      - Arduino Framework allows writing cross-platform software to control devices attached to a wide range of Arduino boards to create all kinds of creative coding, interactive objects, spaces or physical experiences.

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

Espressif
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``d1``
      - `WeMos D1 <http://www.wemos.cc/wiki/doku.php?id=en:d1>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``d1_mini``
      - `WeMos D1 mini <http://www.wemos.cc/wiki/doku.php?id=en:d1_mini>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``esp01``
      - `Espressif Generic ESP8266 ESP-01 <https://nurdspace.nl/ESP8266>`_
      - ESP8266
      - 80 MHz
      - 512 Kb
      - 80 Kb

    * - ``esp12e``
      - `Espressif ESP8266 ESP-12E <https://nurdspace.nl/ESP8266>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``esp210``
      - `SweetPea ESP-210 <http://wiki.sweetpeas.se/index.php?title=ESP-210>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``espino``
      - `ESPino <http://www.espino.io>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``huzzah``
      - `Adafruit HUZZAH ESP8266 <https://www.adafruit.com/products/2471>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``modwifi``
      - `Olimex MOD-WIFI-ESP8266(-DEV) <https://www.olimex.com/Products/IoT/MOD-WIFI-ESP8266-DEV/open-source-hardware>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``nodemcu``
      - `NodeMCU 0.9 & 1.0 <http://www.nodemcu.com/>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``thing``
      - `SparkFun ESP8266 Thing <https://www.sparkfun.com/products/13231>`_
      - ESP8266
      - 80 MHz
      - 512 Kb
      - 80 Kb
