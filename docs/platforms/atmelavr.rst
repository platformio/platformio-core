..  Copyright 2014-present Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _platform_atmelavr:

Platform ``atmelavr``
=====================
Atmel AVR 8- and 32-bit MCUs deliver a unique combination of performance, power efficiency and design flexibility. Optimized to speed time to market-and easily adapt to new ones-they are based on the industrys most code-efficient architecture for C and assembly programming.

For more detailed information please visit `vendor site <http://www.atmel.com/products/microcontrollers/avr/default.aspx>`_.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``toolchain-atmelavr``
      - `avr-gcc <https://gcc.gnu.org/wiki/avr-gcc>`_, `GDB <http://www.gnu.org/software/gdb/>`_, `AVaRICE <http://avarice.sourceforge.net/>`_, `SimulAVR <http://www.nongnu.org/simulavr/>`_

    * - ``tool-avrdude``
      - `AVRDUDE <http://www.nongnu.org/avrdude/>`_

    * - ``framework-simba``
      - `Simba Framework <https://github.com/eerimoq/simba>`_

    * - ``framework-arduinoavr``
      - `Arduino Wiring-based Framework (AVR Core, 1.6) <http://arduino.cc/en/Reference/HomePage>`_

    * - ``tool-micronucleus``
      - `Micronucleus <https://github.com/micronucleus/micronucleus>`_

Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description

    * - :ref:`framework_arduino`
      - Arduino Wiring-based Framework allows writing cross-platform software to control devices attached to a wide range of Arduino boards to create all kinds of creative coding, interactive objects, spaces or physical experiences.

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

    * - ``bluefruitmicro``
      - `Adafruit Bluefruit Micro <https://www.adafruit.com/products/2661>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``feather32u4``
      - `Adafruit Feather <https://learn.adafruit.com/adafruit-feather-32u4-bluefruit-le/>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``flora8``
      - `Adafruit Flora <http://www.adafruit.com/product/659>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``gemma``
      - `Adafruit Gemma <http://www.adafruit.com/products/1222>`_
      - ATTINY85
      - 8 MHz
      - 8 Kb
      - 0.5 Kb

    * - ``metro``
      - `Adafruit Metro <https://www.adafruit.com/products/2466>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``protrinket3``
      - `Adafruit Pro Trinket 3V/12MHz (USB) <http://www.adafruit.com/products/2010>`_
      - ATMEGA328P
      - 12 MHz
      - 32 Kb
      - 2 Kb

    * - ``protrinket3ftdi``
      - `Adafruit Pro Trinket 3V/12MHz (FTDI) <http://www.adafruit.com/products/2010>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``protrinket5``
      - `Adafruit Pro Trinket 5V/16MHz (USB) <http://www.adafruit.com/products/2000>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``protrinket5ftdi``
      - `Adafruit Pro Trinket 5V/16MHz (USB) <http://www.adafruit.com/products/2000>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``trinket3``
      - `Adafruit Trinket 3V/8MHz <http://www.adafruit.com/products/1500>`_
      - ATTINY85
      - 8 MHz
      - 8 Kb
      - 0.5 Kb

    * - ``trinket5``
      - `Adafruit Trinket 5V/16MHz <http://www.adafruit.com/products/1501>`_
      - ATTINY85
      - 16 MHz
      - 8 Kb
      - 0.5 Kb

Arduboy
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``arduboy``
      - `Arduboy <https://www.arduboy.com>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``arduboy_devkit``
      - `Arduboy DevKit <https://www.arduboy.com>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

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

    * - ``LilyPadUSB``
      - `Arduino LilyPad USB <http://arduino.cc/en/Main/ArduinoBoardLilyPadUSB>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``atmegangatmega168``
      - `Arduino NG or older ATmega168 <http://arduino.cc/en/main/boards>`_
      - ATMEGA168
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``atmegangatmega8``
      - `Arduino NG or older ATmega8 <http://arduino.cc/en/main/boards>`_
      - ATMEGA8
      - 16 MHz
      - 8 Kb
      - 1 Kb

    * - ``btatmega168``
      - `Arduino BT ATmega168 <http://arduino.cc/en/main/boards>`_
      - ATMEGA168
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``btatmega328``
      - `Arduino BT ATmega328 <http://arduino.cc/en/main/boards>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``chiwawa``
      - `Arduino Industrial 101 <http://www.arduino.org/products/boards/4-arduino-boards/arduino-industrial-101>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``diecimilaatmega168``
      - `Arduino Duemilanove or Diecimila ATmega168 <http://arduino.cc/en/Main/ArduinoBoardDiecimila>`_
      - ATMEGA168
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``diecimilaatmega328``
      - `Arduino Duemilanove or Diecimila ATmega328 <http://arduino.cc/en/Main/ArduinoBoardDiecimila>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``esplora``
      - `Arduino Esplora <http://www.arduino.org/products/boards/4-arduino-boards/arduino-esplora>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``ethernet``
      - `Arduino Ethernet <http://www.arduino.org/products/boards/4-arduino-boards/arduino-ethernet>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``fio``
      - `Arduino Fio <http://arduino.cc/en/Main/ArduinoBoardFio>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

    * - ``leonardo``
      - `Arduino Leonardo <http://www.arduino.org/products/boards/4-arduino-boards/arduino-leonardo>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``leonardoeth``
      - `Arduino Leonardo ETH <http://www.arduino.org/products/boards/4-arduino-boards/arduino-leonardo-eth>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``lilypadatmega168``
      - `Arduino LilyPad ATmega168 <http://arduino.cc/en/Main/ArduinoBoardLilyPad>`_
      - ATMEGA168
      - 8 MHz
      - 16 Kb
      - 1 Kb

    * - ``lilypadatmega328``
      - `Arduino LilyPad ATmega328 <http://arduino.cc/en/Main/ArduinoBoardLilyPad>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

    * - ``megaADK``
      - `Arduino Mega ADK <http://www.arduino.org/products/boards/4-arduino-boards/arduino-mega-adk>`_
      - ATMEGA2560
      - 16 MHz
      - 256 Kb
      - 8 Kb

    * - ``megaatmega1280``
      - `Arduino Mega or Mega 2560 ATmega1280 <http://www.arduino.org/products/boards/4-arduino-boards/arduino-mega-2560>`_
      - ATMEGA1280
      - 16 MHz
      - 128 Kb
      - 8 Kb

    * - ``megaatmega2560``
      - `Arduino Mega or Mega 2560 ATmega2560 (Mega 2560) <http://www.arduino.org/products/boards/4-arduino-boards/arduino-mega-2560>`_
      - ATMEGA2560
      - 16 MHz
      - 256 Kb
      - 8 Kb

    * - ``micro``
      - `Arduino Micro <http://www.arduino.org/products/boards/4-arduino-boards/arduino-micro>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``miniatmega168``
      - `Arduino Mini ATmega168 <http://arduino.cc/en/Main/ArduinoBoardMini>`_
      - ATMEGA168
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``miniatmega328``
      - `Arduino Mini ATmega328 <http://arduino.cc/en/Main/ArduinoBoardMini>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``nanoatmega168``
      - `Arduino Nano ATmega168 <http://www.arduino.org/products/boards/4-arduino-boards/arduino-nano>`_
      - ATMEGA168
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``nanoatmega328``
      - `Arduino Nano ATmega328 <http://www.arduino.org/products/boards/4-arduino-boards/arduino-nano>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``pro16MHzatmega168``
      - `Arduino Pro or Pro Mini ATmega168 (5V, 16 MHz) <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATMEGA168
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``pro16MHzatmega328``
      - `Arduino Pro or Pro Mini ATmega328 (5V, 16 MHz) <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``pro8MHzatmega168``
      - `Arduino Pro or Pro Mini ATmega168 (3.3V, 8 MHz) <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATMEGA168
      - 8 MHz
      - 16 Kb
      - 1 Kb

    * - ``pro8MHzatmega328``
      - `Arduino Pro or Pro Mini ATmega328 (3.3V, 8 MHz) <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

    * - ``robotControl``
      - `Arduino Robot Control <http://www.arduino.org/products/boards/4-arduino-boards/arduino-robot>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``robotMotor``
      - `Arduino Robot Motor <http://www.arduino.org/products/boards/4-arduino-boards/arduino-robot>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``uno``
      - `Arduino Uno <http://www.arduino.org/products/boards/4-arduino-boards/arduino-uno>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``yun``
      - `Arduino Yun <http://www.arduino.org/products/boards/4-arduino-boards/arduino-yun>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``yunmini``
      - `Arduino Yun Mini <http://www.arduino.org/products/boards/4-arduino-boards/arduino-yun-mini>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

BQ
~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``zumbt328``
      - `BQ ZUM BT-328 <http://www.bq.com/gb/products/zum.html>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

BitWizard
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``raspduino``
      - `BitWizard Raspduino <http://www.bitwizard.nl/wiki/index.php/Raspduino>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

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

    * - ``digispark-pro``
      - `Digistump Digispark Pro (Default 16 MHz) <http://digistump.com/products/109>`_
      - ATTINY167
      - 16 MHz
      - 16 Kb
      - 0.5 Kb

    * - ``digispark-pro32``
      - `Digistump Digispark Pro (16 MHz) (32 byte buffer) <http://digistump.com/products/109>`_
      - ATTINY167
      - 16 MHz
      - 16 Kb
      - 0.5 Kb

    * - ``digispark-pro64``
      - `Digistump Digispark Pro (16 MHz) (64 byte buffer) <http://digistump.com/products/109>`_
      - ATTINY167
      - 16 MHz
      - 16 Kb
      - 0.5 Kb

    * - ``digispark-tiny``
      - `Digistump Digispark (Default - 16 MHz) <http://digistump.com/products/1>`_
      - ATTINY85
      - 16 MHz
      - 8 Kb
      - 0.5 Kb

Engduino
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``engduinov1``
      - `Engduino 1 <http://www.engduino.org>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``engduinov2``
      - `Engduino 2 <http://www.engduino.org>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``engduinov3``
      - `Engduino 3 <http://www.engduino.org>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

Generic ATTiny
~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``attiny13``
      - `Generic ATTiny13 <http://www.atmel.com/devices/ATTINY13.aspx>`_
      - ATTINY13
      - 9 MHz
      - 1 Kb
      - 0.0625 Kb

    * - ``attiny24``
      - `Generic ATTiny24 <http://www.atmel.com/devices/ATTINY24.aspx>`_
      - ATTINY24
      - 8 MHz
      - 2 Kb
      - 0.125 Kb

    * - ``attiny25``
      - `Generic ATTiny25 <http://www.atmel.com/devices/ATTINY25.aspx>`_
      - ATTINY25
      - 8 MHz
      - 2 Kb
      - 0.125 Kb

    * - ``attiny44``
      - `Generic ATTiny44 <http://www.atmel.com/devices/ATTINY44.aspx>`_
      - ATTINY44
      - 8 MHz
      - 4 Kb
      - 0.25 Kb

    * - ``attiny45``
      - `Generic ATTiny45 <http://www.atmel.com/devices/ATTINY45.aspx>`_
      - ATTINY45
      - 8 MHz
      - 4 Kb
      - 0.25 Kb

    * - ``attiny84``
      - `Generic ATTiny84 <http://www.atmel.com/devices/ATTINY84.aspx>`_
      - ATTINY84
      - 8 MHz
      - 8 Kb
      - 0.5 Kb

    * - ``attiny85``
      - `Generic ATTiny85 <http://www.atmel.com/devices/ATTINY85.aspx>`_
      - ATTINY85
      - 8 MHz
      - 8 Kb
      - 0.5 Kb

LightUp
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lightup``
      - `LightUp <https://www.lightup.io/>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

Linino
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``one``
      - `Linino One <http://www.linino.org/portfolio/linino-one/>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

LowPowerLab
~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``moteino``
      - `LowPowerLab Moteino <https://lowpowerlab.com/shop/moteino-r4>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``moteinomega``
      - `LowPowerLab MoteinoMEGA <http://lowpowerlab.com/blog/2014/08/09/moteinomega-available-now/>`_
      - ATMEGA1284P
      - 16 MHz
      - 128 Kb
      - 16 Kb

Mcudude
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``mightycore1284``
      - `MightyCore ATmega1284 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA1284P
      - 16 MHz
      - 128 Kb
      - 16 Kb

    * - ``mightycore16``
      - `MightyCore ATmega16 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA16
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``mightycore164``
      - `MightyCore ATmega164 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA164P
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``mightycore32``
      - `MightyCore ATmega32 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA32
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``mightycore324``
      - `MightyCore ATmega324 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA324P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``mightycore644``
      - `MightyCore ATmega644 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA644P
      - 16 MHz
      - 64 Kb
      - 4 Kb

    * - ``mightycore8535``
      - `MightyCore ATmega8535 <https://www.tindie.com/products/MCUdude/dip-40-arduino-compatible-development-board>`_
      - ATMEGA16
      - 16 MHz
      - 8 Kb
      - 0.5 Kb

Microduino
~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``1284p16m``
      - `Microduino Core+ (ATmega1284P@16M,5V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - ATMEGA1284P
      - 16 MHz
      - 128 Kb
      - 16 Kb

    * - ``1284p8m``
      - `Microduino Core+ (ATmega1284P@8M,3.3V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - ATMEGA1284P
      - 8 MHz
      - 128 Kb
      - 16 Kb

    * - ``168pa16m``
      - `Microduino Core (Atmega168PA@16M,5V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATMEGA168P
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``168pa8m``
      - `Microduino Core (Atmega168PA@8M,3.3V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATMEGA168P
      - 8 MHz
      - 16 Kb
      - 1 Kb

    * - ``328p16m``
      - `Microduino Core (Atmega328P@16M,5V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``328p8m``
      - `Microduino Core (Atmega328P@8M,3.3V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

    * - ``32u416m``
      - `Microduino Core USB (ATmega32U4@16M,5V) <https://www.microduino.cc/wiki/index.php?title=Microduino-CoreUSB>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``644pa16m``
      - `Microduino Core+ (Atmega644PA@16M,5V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - ATMEGA644P
      - 16 MHz
      - 64 Kb
      - 4 Kb

    * - ``644pa8m``
      - `Microduino Core+ (Atmega644PA@8M,3.3V) <https://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - ATMEGA644P
      - 8 MHz
      - 64 Kb
      - 4 Kb

OpenEnergyMonitor
~~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``emonpi``
      - `OpenEnergyMonitor emonPi <https://github.com/openenergymonitor/emonpi>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

PanStamp
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``panStampAVR``
      - `PanStamp AVR <http://www.panstamp.com/product/panstamp-avr/>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

Pinoccio
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``pinoccio``
      - `Pinoccio Scout <https://www.crowdsupply.com/pinoccio/mesh-sensor-network>`_
      - ATMEGA256RFR2
      - 16 MHz
      - 256 Kb
      - 32 Kb

Punch Through
~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lightblue-bean``
      - `LightBlue Bean <https://punchthrough.com/bean>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

Quirkbot
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``quirkbot``
      - `Quirkbot <http://quirkbot.com>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

RedBearLab
~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``blend``
      - `RedBearLab Blend <http://redbearlab.com/blend/>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``blendmicro16``
      - `RedBearLab Blend Micro 3.3V/16MHz (overclock) <http://redbearlab.com/blendmicro/>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``blendmicro8``
      - `RedBearLab Blend Micro 3.3V/8MHz <http://redbearlab.com/blendmicro/>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

RepRap
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``reprap_rambo``
      - `RepRap RAMBo <http://reprap.org/wiki/Rambo>`_
      - ATMEGA2560
      - 16 MHz
      - 256 Kb
      - 8 Kb

Sanguino
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``sanguino_atmega1284_8m``
      - `Sanguino ATmega1284p (8MHz) <https://code.google.com/p/sanguino/>`_
      - ATMEGA1284P
      - 8 MHz
      - 128 Kb
      - 16 Kb

    * - ``sanguino_atmega1284p``
      - `Sanguino ATmega1284p (16MHz) <https://code.google.com/p/sanguino/>`_
      - ATMEGA1284P
      - 16 MHz
      - 128 Kb
      - 16 Kb

    * - ``sanguino_atmega644``
      - `Sanguino ATmega644 or ATmega644A (16 MHz) <https://code.google.com/p/sanguino/>`_
      - ATMEGA644
      - 16 MHz
      - 64 Kb
      - 4 Kb

    * - ``sanguino_atmega644_8m``
      - `Sanguino ATmega644 or ATmega644A (8 MHz) <https://code.google.com/p/sanguino/>`_
      - ATMEGA644
      - 8 MHz
      - 64 Kb
      - 4 Kb

    * - ``sanguino_atmega644p``
      - `Sanguino ATmega644P or ATmega644PA (16 MHz) <https://code.google.com/p/sanguino/>`_
      - ATMEGA644P
      - 16 MHz
      - 64 Kb
      - 4 Kb

    * - ``sanguino_atmega644p_8m``
      - `Sanguino ATmega644P or ATmega644PA (8 MHz) <https://code.google.com/p/sanguino/>`_
      - ATMEGA644P
      - 8 MHz
      - 64 Kb
      - 4 Kb

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

    * - ``sparkfun_digitalsandbox``
      - `SparkFun Digital Sandbox <https://www.sparkfun.com/products/12651>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``sparkfun_fiov3``
      - `SparkFun Fio V3 3.3V/8MHz <https://www.sparkfun.com/products/11520>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``sparkfun_makeymakey``
      - `SparkFun Makey Makey <https://www.sparkfun.com/products/11511>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``sparkfun_megamini``
      - `SparkFun Mega Pro Mini 3.3V <https://www.sparkfun.com/products/10743>`_
      - ATMEGA2560
      - 8 MHz
      - 256 Kb
      - 8 Kb

    * - ``sparkfun_megapro16MHz``
      - `SparkFun Mega Pro 5V/16MHz <https://www.sparkfun.com/products/11007>`_
      - ATMEGA2560
      - 16 MHz
      - 256 Kb
      - 8 Kb

    * - ``sparkfun_megapro8MHz``
      - `SparkFun Mega Pro 3.3V/8MHz <https://www.sparkfun.com/products/10744>`_
      - ATMEGA2560
      - 8 MHz
      - 256 Kb
      - 8 Kb

    * - ``sparkfun_promicro16``
      - `SparkFun Pro Micro 5V/16MHz <https://www.sparkfun.com/products/12640>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``sparkfun_promicro8``
      - `SparkFun Pro Micro 3.3V/8MHz <https://www.sparkfun.com/products/12587>`_
      - ATMEGA32U4
      - 8 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``sparkfun_redboard``
      - `SparkFun RedBoard <https://www.sparkfun.com/products/12757>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

    * - ``uview``
      - `SparkFun MicroView <https://www.sparkfun.com/products/12923>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

TinyCircuits
~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``tinyduino``
      - `TinyCircuits TinyDuino Processor Board <https://tiny-circuits.com/tinyduino-processor-board.html>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

    * - ``tinylily``
      - `TinyCircuits TinyLily Mini Processor <https://tiny-circuits.com/tiny-lily-mini-processor.html>`_
      - ATMEGA328P
      - 8 MHz
      - 32 Kb
      - 2 Kb

Wicked Device
~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``wildfirev2``
      - `Wicked Device WildFire V2 <http://shop.wickeddevice.com/resources/wildfire/>`_
      - ATMEGA1284P
      - 16 MHz
      - 128 Kb
      - 16 Kb

    * - ``wildfirev3``
      - `Wicked Device WildFire V3 <http://shop.wickeddevice.com/resources/wildfire/>`_
      - ATMEGA1284P
      - 16 MHz
      - 128 Kb
      - 16 Kb

ubIQio
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``ardhat``
      - `ubIQio Ardhat <http://ardhat.com>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

.. include:: atmelavr_extra.rst
