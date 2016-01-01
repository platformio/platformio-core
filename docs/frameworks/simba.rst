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

.. _framework_simba:

Framework ``simba``
===================
Simba is an RTOS and build framework. It aims to make embedded programming easy and portable.

For more detailed information please visit `vendor site <http://simba-os.readthedocs.org>`_.

.. contents::

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.

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
      - AT91SAM3X8E
      - 84 MHz
      - 512 Kb
      - 32 Kb

    * - ``megaatmega2560``
      - `Arduino Mega or Mega 2560 ATmega2560 (Mega 2560) <http://arduino.cc/en/Main/arduinoBoardMega2560>`_
      - ATMEGA2560
      - 16 MHz
      - 256 Kb
      - 8 Kb

    * - ``nanoatmega328``
      - `Arduino Nano ATmega328 <http://arduino.cc/en/Main/ArduinoBoardNano>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``uno``
      - `Arduino Uno <http://arduino.cc/en/Main/ArduinoBoardUno>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

.. include:: simba_extra.rst
