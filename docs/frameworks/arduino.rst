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

.. _framework_arduino:

Framework ``arduino``
=====================
Arduino Wiring-based Framework allows writing cross-platform software to control devices attached to a wide range of Arduino boards to create all kinds of creative coding, interactive objects, spaces or physical experiences.

For more detailed information please visit `vendor site <http://arduino.cc/en/Reference/HomePage>`_.

.. contents::

Platforms
---------
.. list-table::
    :header-rows:  1

    * - Name
      - Description

    * - :ref:`platform_atmelavr`
      - Atmel AVR 8- and 32-bit MCUs deliver a unique combination of performance, power efficiency and design flexibility. Optimized to speed time to market-and easily adapt to new ones-they are based on the industrys most code-efficient architecture for C and assembly programming.

    * - :ref:`platform_atmelsam`
      - Atmel | SMART offers Flash- based ARM products based on the ARM Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB to 2MB of Flash including a rich peripheral and feature mix.

    * - :ref:`platform_espressif8266`
      - Espressif Systems is a privately held fabless semiconductor company. They provide wireless communications and Wi-Fi chips which are widely used in mobile devices and the Internet of Things applications.

    * - :ref:`platform_intel_arc32`
      - ARC embedded processors are a family of 32-bit CPUs that are widely used in SoC devices for storage, home, mobile, automotive, and Internet of Things applications.

    * - :ref:`platform_microchippic32`
      - Microchip's 32-bit portfolio with the MIPS microAptiv or M4K core offer high performance microcontrollers, and all the tools needed to develop your embedded projects. PIC32 MCUs gives your application the processing power, memory and peripherals your design needs!

    * - :ref:`platform_nordicnrf51`
      - The Nordic nRF51 Series is a family of highly flexible, multi-protocol, system-on-chip (SoC) devices for ultra-low power wireless applications. nRF51 Series devices support a range of protocol stacks including Bluetooth Smart (previously called Bluetooth low energy), ANT and proprietary 2.4GHz protocols such as Gazell.

    * - :ref:`platform_teensy`
      - Teensy is a complete USB-based microcontroller development system, in a very small footprint, capable of implementing many types of projects. All programming is done via the USB port. No special programmer is needed, only a standard USB cable and a PC or Macintosh with a USB port.

    * - :ref:`platform_timsp430`
      - MSP430 microcontrollers (MCUs) from Texas Instruments (TI) are 16-bit, RISC-based, mixed-signal processors designed for ultra-low power. These MCUs offer the lowest power consumption and the perfect mix of integrated peripherals for thousands of applications.

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.

4DSystems
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``picadillo_35t``
      - `4DSystems PICadillo 35T <http://www.4dsystems.com.au/product/Picadillo_35T/>`_
      - 32MX795F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

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

    * - ``huzzah``
      - `Adafruit HUZZAH ESP8266 <https://www.adafruit.com/products/2471>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

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
      - 12 MHz
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

    * - ``tian``
      - `Arduino Tian <http://www.arduino.org/products/boards/arduino-tian>`_
      - SAMD21G18A
      - 48 MHz
      - 256 Kb
      - 32 Kb

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

Digilent
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``cerebot32mx4``
      - `Digilent Cerebot 32MX4 <http://store.digilentinc.com/cerebot-32mx4-limited-time-see-chipkit-pro-mx4/>`_
      - 32MX460F512L
      - 80 MHz
      - 512 Kb
      - 32 Kb

    * - ``cerebot32mx7``
      - `Digilent Cerebot 32MX7 <http://www.microchip.com/Developmenttools/ProductDetails.aspx?PartNO=TDGL004>`_
      - 32MX795F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

    * - ``chipkit_cmod``
      - `Digilent chipKIT Cmod <http://store.digilentinc.com/chipkit-cmod-breadboardable-mz-microcontroller-board/>`_
      - 32MX150F128D
      - 40 MHz
      - 128 Kb
      - 32 Kb

    * - ``chipkit_dp32``
      - `Digilent chipKIT DP32 <http://store.digilentinc.com/chipkit-dp32-dip-package-prototyping-microcontroller-board/>`_
      - 32MX250F128B
      - 40 MHz
      - 128 Kb
      - 32 Kb

    * - ``chipkit_mx3``
      - `Digilent chipKIT MX3 <http://store.digilentinc.com/chipkit-mx3-microcontroller-board-with-pmod-headers/>`_
      - 32MX320F128H
      - 80 MHz
      - 128 Kb
      - 16 Kb

    * - ``chipkit_pro_mx4``
      - `Digilent chipKIT Pro MX4 <http://store.digilentinc.com/chipkit-pro-mx4-embedded-systems-trainer-board/>`_
      - 32MX460F512L
      - 80 MHz
      - 512 Kb
      - 32 Kb

    * - ``chipkit_pro_mx7``
      - `Digilent chipKIT Pro MX7 <http://store.digilentinc.com/chipkit-pro-mx7-advanced-peripherals-embedded-systems-trainer-board/>`_
      - 32MX795F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

    * - ``chipkit_uc32``
      - `Digilent chipKIT uC32 <http://store.digilentinc.com/chipkit-uc32-basic-microcontroller-board-with-uno-r3-headers/>`_
      - 32MX340F512H
      - 80 MHz
      - 512 Kb
      - 32 Kb

    * - ``chipkit_wf32``
      - `Digilent chipKIT WF32 <http://store.digilentinc.com/chipkit-wf32-wifi-enabled-microntroller-board-with-uno-r3-headers/>`_
      - 32MX695F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

    * - ``chipkit_wifire``
      - `Digilent chipKIT WiFire <http://store.digilentinc.com/chipkit-wi-fire-wifi-enabled-mz-microcontroller-board/>`_
      - 32MZ2048ECG100
      - 200 MHz
      - 2048 Kb
      - 512 Kb

    * - ``mega_pic32``
      - `Digilent chipKIT MAX32 <http://store.digilentinc.com/chipkit-max32-microcontroller-board-with-mega-r3-headers/>`_
      - 32MX795F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

    * - ``openscope``
      - `Digilent OpenScope <http://store.digilentinc.com/>`_
      - 32MZ2048EFG124
      - 200 MHz
      - 2048 Kb
      - 512 Kb

    * - ``uno_pic32``
      - `Digilent chipKIT UNO32 <http://store.digilentinc.com/chipkit-uno32-basic-microcontroller-board-retired-see-chipkit-uc32/>`_
      - 32MX320F128H
      - 80 MHz
      - 128 Kb
      - 16 Kb

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

    * - ``digix``
      - `Digistump DigiX <http://digistump.com/products/50>`_
      - AT91SAM3X8E
      - 84 MHz
      - 512 Kb
      - 28 Kb

Doit
~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``espduino``
      - `ESPDuino (ESP-13 Module) <https://www.tindie.com/products/doit/espduinowifi-uno-r3/>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

ESPert
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``espresso_lite_v1``
      - `ESPresso Lite 1.0 <http://www.espert.co>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

    * - ``espresso_lite_v2``
      - `ESPresso Lite 2.0 <http://www.espert.co>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

ESPino
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``espino``
      - `ESPino <http://www.espino.io>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

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

    * - ``esp01``
      - `Espressif Generic ESP8266 ESP-01 512k <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 512 Kb
      - 80 Kb

    * - ``esp01_1m``
      - `Espressif Generic ESP8266 ESP-01 1M <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``esp07``
      - `Espressif Generic ESP8266 ESP-07 <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family#esp-07>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

    * - ``esp12e``
      - `Espressif ESP8266 ESP-12E <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

    * - ``esp8285``
      - `Generic ESP8285 Module <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 448 Kb
      - 80 Kb

    * - ``esp_wroom_02``
      - `ESP-WROOM-02 <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 50 Kb

    * - ``phoenix_v1``
      - `Phoenix 1.0 <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``phoenix_v2``
      - `Phoenix 2.0 <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

    * - ``wifinfo``
      - `WifInfo <http://www.esp8266.com/wiki/doku.php?id=esp8266-module-family>`_
      - ESP8266
      - 80 MHz
      - 448 Kb
      - 80 Kb

Fubarino
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``fubarino_mini``
      - `Fubarino Mini <http://fubarino.org/mini/>`_
      - 32MX250F128D
      - 48 MHz
      - 128 Kb
      - 32 Kb

    * - ``fubarino_sd``
      - `Fubarino SD (1.5) <http://fubarino.org/sd/index.html>`_
      - 32MX795F512H
      - 80 MHz
      - 512 Kb
      - 128 Kb

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

Intel
~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``genuino101``
      - `Arduino/Genuino 101 <https://www.arduino.cc/en/Main/ArduinoBoard101>`_
      - ARCV2EM
      - 32 MHz
      - 192 Kb
      - 80 Kb

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

NodeMCU
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``nodemcu``
      - `NodeMCU 0.9 (ESP-12 Module) <http://www.nodemcu.com/>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

    * - ``nodemcuv2``
      - `NodeMCU 1.0 (ESP-12E Module) <http://www.nodemcu.com/>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

Olimex
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``modwifi``
      - `Olimex MOD-WIFI-ESP8266(-DEV) <https://www.olimex.com/Products/IoT/MOD-WIFI-ESP8266-DEV/open-source-hardware>`_
      - ESP8266
      - 80 MHz
      - 2048 Kb
      - 80 Kb

    * - ``pinguino32``
      - `Olimex PIC32-PINGUINO <https://www.olimex.com/Products/Duino/PIC32/PIC32-PINGUINO/open-source-hardware>`_
      - 32MX440F256H
      - 80 MHz
      - 256 Kb
      - 32 Kb

OpenBCI
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``openbci``
      - `OpenBCI 32bit <http://shop.openbci.com/>`_
      - 32MX250F128B
      - 40 MHz
      - 128 Kb
      - 32 Kb

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

PONTECH
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``quick240_usb``
      - `PONTECH quicK240 <http://quick240.com/quicki/>`_
      - 32MX795F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

    * - ``usbono_pic32``
      - `PONTECH UAV100 <http://www.pontech.com/productdisplay/uav100>`_
      - 32MX440F512H
      - 80 MHz
      - 512 Kb
      - 32 Kb

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

    * - ``panStampNRG``
      - `PanStamp NRG 1.1 <http://www.panstamp.com/product/197/>`_
      - CC430F5137
      - 12 MHz
      - 32 Kb
      - 4 Kb

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

RFduino
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``rfduino``
      - `RFduino <http://www.rfduino.com/product/rfd22102-rfduino-dip/index.html>`_
      - NRF51822
      - 16 MHz
      - 128 Kb
      - 8 Kb

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

SeeedStudio
~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``cui32stem``
      - `SeeedStudio CUI32stem <http://www.seeedstudio.com/wiki/CUI32Stem>`_
      - 32MX795F512H
      - 80 MHz
      - 512 Kb
      - 128 Kb

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

    * - ``sparkfunBlynk``
      - `SparkFun Blynk Board <https://www.sparkfun.com/products/13794>`_
      - ESP8266
      - 80 MHz
      - 1024 Kb
      - 80 Kb

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

    * - ``thing``
      - `SparkFun ESP8266 Thing <https://www.sparkfun.com/products/13231>`_
      - ESP8266
      - 80 MHz
      - 512 Kb
      - 80 Kb

    * - ``thingdev``
      - `SparkFun ESP8266 Thing Dev <https://www.sparkfun.com/products/13231>`_
      - ESP8266
      - 80 MHz
      - 512 Kb
      - 80 Kb

    * - ``uview``
      - `SparkFun MicroView <https://www.sparkfun.com/products/12923>`_
      - ATMEGA328P
      - 16 MHz
      - 32 Kb
      - 2 Kb

SweetPea
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``esp210``
      - `SweetPea ESP-210 <http://wiki.sweetpeas.se/index.php?title=ESP-210>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

Teensy
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``teensy20``
      - `Teensy 2.0 <https://www.pjrc.com/store/teensy.html>`_
      - ATMEGA32U4
      - 16 MHz
      - 32 Kb
      - 2.5 Kb

    * - ``teensy20pp``
      - `Teensy++ 2.0 <https://www.pjrc.com/store/teensypp.html>`_
      - AT90USB1286
      - 16 MHz
      - 128 Kb
      - 8 Kb

    * - ``teensy30``
      - `Teensy 3.0 <https://www.pjrc.com/store/teensy3.html>`_
      - MK20DX128
      - 48 MHz
      - 128 Kb
      - 16 Kb

    * - ``teensy31``
      - `Teensy 3.1 / 3.2 <https://www.pjrc.com/store/teensy31.html>`_
      - MK20DX256
      - 72 MHz
      - 256 Kb
      - 64 Kb

    * - ``teensylc``
      - `Teensy LC <http://www.pjrc.com/teensy/teensyLC.html>`_
      - MKL26Z64
      - 48 MHz
      - 64 Kb
      - 8 Kb

ThaiEasyElec
~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``espinotee``
      - `ThaiEasyElec ESPino <http://www.thaieasyelec.com/products/wireless-modules/wifi-modules/espino-wifi-development-board-detail.html>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

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

UBW32
~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``ubw32_mx460``
      - `UBW32 MX460 <http://www.schmalzhaus.com/UBW32/>`_
      - 32MX460F512L
      - 80 MHz
      - 512 Kb
      - 32 Kb

    * - ``ubw32_mx795``
      - `UBW32 MX795 <http://www.schmalzhaus.com/UBW32/>`_
      - 32MX795F512L
      - 80 MHz
      - 512 Kb
      - 128 Kb

WeMos
~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``d1``
      - `WeMos D1(Retired) <http://www.wemos.cc/wiki/doku.php?id=en:d1>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

    * - ``d1_mini``
      - `WeMos D1 R2 & mini <http://www.wemos.cc/wiki/doku.php?id=en:d1_mini>`_
      - ESP8266
      - 80 MHz
      - 4096 Kb
      - 80 Kb

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

chipKIT
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lenny``
      - `chipKIT Lenny <http://chipkit.net/tag/lenny/>`_
      - 32MX270F256D
      - 40 MHz
      - 128 Kb
      - 32 Kb

element14
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``chipkit_pi``
      - `Element14 chipKIT Pi <http://www.element14.com/community/community/knode/dev_platforms_kits/element14_dev_kits/microchip-chipkit/chipkit_pi>`_
      - 32MX250F128B
      - 40 MHz
      - 128 Kb
      - 32 Kb

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
