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

.. _embedded_boards:

Embedded Boards
===============

Rapid Embedded Development, Continuous and IDE integration in a few
steps with PlatformIO thanks to built-in project generator for the most
popular embedded boards and IDE.

* You can list pre-configured boards using :ref:`cmd_boards` command or
  `PlatformIO Boards Explorer <http://platformio.org/boards>`_
* For more detailed ``board`` information please scroll tables below by
  horizontal.

.. contents::

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

96Boards
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``b96b_f446ve``
      - `96Boards B96B-F446VE <https://developer.mbed.org/platforms/ST-B96B-F446VE/>`_
      - STM32F446VET6
      - 168 MHz
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

Armstrap
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``armstrap_eagle1024``
      - `Armstrap Eagle 1024 <http://docs.armstrap.org/en/latest/hardware-overview.html>`_
      - STM32F417VGT6
      - 168 MHz
      - 1024 Kb
      - 192 Kb

    * - ``armstrap_eagle2048``
      - `Armstrap Eagle 2048 <http://docs.armstrap.org/en/latest/hardware-overview.html>`_
      - STM32F427VIT6
      - 168 MHz
      - 2048 Kb
      - 256 Kb

    * - ``armstrap_eagle512``
      - `Armstrap Eagle 512 <http://docs.armstrap.org/en/latest/hardware-overview.html>`_
      - STM32F407VET6
      - 168 MHz
      - 512 Kb
      - 192 Kb

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

BBC
~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``bbcmicrobit``
      - `BBC micro:bit <https://developer.mbed.org/platforms/Microbit/>`_
      - NRF51822
      - 16 MHz
      - 256 Kb
      - 16 Kb

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

    * - ``icezum``
      - `BQ IceZUM Alhambra FPGA <https://github.com/bqlabs/icezum/wiki>`_
      - ICE40HX1K
      - 12 MHz
      - 32 Kb
      - 32 Kb

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

CQ Publishing
~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lpc11u35_501``
      - `CQ Publishing TG-LPC11U35-501 <https://developer.mbed.org/platforms/TG-LPC11U35-501/>`_
      - LPC11U35
      - 48 MHz
      - 64 Kb
      - 10 Kb

Delta
~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``dfcm_nnn40``
      - `Delta DFCM-NNN40 <https://developer.mbed.org/platforms/Delta-DFCM-NNN40/>`_
      - NRF51822
      - 32 MHz
      - 256 Kb
      - 32 Kb

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

Embedded Artists
~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lpc11u35``
      - `Embedded Artists LPC11U35 QuickStart Board <https://developer.mbed.org/platforms/EA-LPC11U35/>`_
      - LPC11U35
      - 48 MHz
      - 64 Kb
      - 10 Kb

    * - ``lpc4088``
      - `Embedded Artists LPC4088 QuickStart Board <https://developer.mbed.org/platforms/EA-LPC4088/>`_
      - LPC4088
      - 120 MHz
      - 512 Kb
      - 96 Kb

    * - ``lpc4088_dm``
      - `Embedded Artists LPC4088 Display Module <https://developer.mbed.org/platforms/EA-LPC4088-Display-Module/>`_
      - LPC4088
      - 120 MHz
      - 512 Kb
      - 96 Kb

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

Freescale
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``IBMEthernetKit``
      - `Ethernet IoT Starter Kit <http://developer.mbed.org/platforms/IBMEthernetKit/>`_
      - MK64FN1M0VLL12
      - 120 MHz
      - 1024 Kb
      - 256 Kb

    * - ``frdm_k20d50m``
      - `Freescale Kinetis FRDM-K20D50M <https://developer.mbed.org/platforms/FRDM-K20D50M/>`_
      - MK20DX128VLH5
      - 48 MHz
      - 128 Kb
      - 16 Kb

    * - ``frdm_k22f``
      - `Freescale Kinetis FRDM-K22F <https://developer.mbed.org/platforms/FRDM-K22F/>`_
      - MK22FN512VLH12
      - 120 MHz
      - 512 Kb
      - 128 Kb

    * - ``frdm_k64f``
      - `Freescale Kinetis FRDM-K64F <https://developer.mbed.org/platforms/FRDM-K64F/>`_
      - MK64FN1M0VLL12
      - 120 MHz
      - 1024 Kb
      - 256 Kb

    * - ``frdm_kl05z``
      - `Freescale Kinetis FRDM-KL05Z <https://developer.mbed.org/platforms/FRDM-KL05Z/>`_
      - MKL05Z32VFM4
      - 48 MHz
      - 32 Kb
      - 4 Kb

    * - ``frdm_kl25z``
      - `Freescale Kinetis FRDM-KL25Z <https://developer.mbed.org/platforms/KL25Z/>`_
      - MKL25Z128VLK4
      - 48 MHz
      - 128 Kb
      - 16 Kb

    * - ``frdm_kl46z``
      - `Freescale Kinetis FRDM-KL46Z <https://developer.mbed.org/platforms/FRDM-KL46Z/>`_
      - MKL46Z256VLL4
      - 48 MHz
      - 256 Kb
      - 32 Kb

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

Generic
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``bluepill_f103c8``
      - `BluePill F103C8 <http://www.st.com/content/st_com/en/products/microcontrollers/stm32-32-bit-arm-cortex-mcus/stm32f1-series/stm32f103/stm32f103c8.html>`_
      - STM32F103C8T6
      - 72 MHz
      - 64 Kb
      - 20 Kb

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

JKSoft
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``wallBotBLE``
      - `JKSoft Wallbot BLE <https://developer.mbed.org/platforms/JKSoft-Wallbot-BLE/>`_
      - NRF51822
      - 16 MHz
      - 128 Kb
      - 16 Kb

Lattice
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``icestick``
      - `Lattice iCEstick FPGA Evaluation Kit <http://www.latticesemi.com/icestick>`_
      - ICE40HX1K
      - 12 MHz
      - 32 Kb
      - 32 Kb

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

MultiTech
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``mts_mdot_f411re``
      - `MultiTech mDot F411 <https://developer.mbed.org/platforms/MTS-mDot-F411/>`_
      - STM32F411RET6
      - 100 MHz
      - 512 Kb
      - 128 Kb

NGX Technologies
~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``blueboard_lpc11u24``
      - `NGX Technologies BlueBoard-LPC11U24 <https://developer.mbed.org/platforms/BlueBoard-LPC11U24/>`_
      - LPC11U24
      - 48 MHz
      - 32 Kb
      - 8 Kb

NXP
~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lpc11u24``
      - `NXP mbed LPC11U24 <https://developer.mbed.org/platforms/mbed-LPC11U24/>`_
      - LPC11U24
      - 48 MHz
      - 32 Kb
      - 8 Kb

    * - ``lpc1549``
      - `NXP LPCXpresso1549 <https://developer.mbed.org/platforms/LPCXpresso1549/>`_
      - LPC1549
      - 72 MHz
      - 256 Kb
      - 36 Kb

    * - ``lpc1768``
      - `NXP mbed LPC1768 <http://developer.mbed.org/platforms/mbed-LPC1768/>`_
      - LPC1768
      - 96 MHz
      - 512 Kb
      - 64 Kb

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

Nordic
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``nrf51_dk``
      - `Nordic nRF51-DK <https://developer.mbed.org/platforms/Nordic-nRF51-DK/>`_
      - NRF51822
      - 32 MHz
      - 256 Kb
      - 32 Kb

    * - ``nrf51_dongle``
      - `Nordic nRF51-Dongle <https://developer.mbed.org/platforms/Nordic-nRF51-Dongle/>`_
      - NRF51822
      - 32 MHz
      - 256 Kb
      - 32 Kb

    * - ``nrf51_mkit``
      - `Nordic nRF51822-mKIT <http://developer.mbed.org/platforms/Nordic-nRF51822/>`_
      - NRF51822
      - 16 MHz
      - 128 Kb
      - 16 Kb

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

Outrageous Circuits
~~~~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``mbuino``
      - `Outrageous Circuits mBuino <https://developer.mbed.org/platforms/Outrageous-Circuits-mBuino/>`_
      - LPC11U24
      - 48 MHz
      - 32 Kb
      - 8 Kb

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

Raspberry Pi
~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``raspberrypi_1b``
      - `Raspberry Pi 1 Model B <https://www.raspberrypi.org>`_
      - BCM2835
      - 700 MHz
      - 524288 Kb
      - 524288 Kb

    * - ``raspberrypi_2b``
      - `Raspberry Pi 2 Model B <https://www.raspberrypi.org>`_
      - BCM2836
      - 900 MHz
      - 1048576 Kb
      - 1048576 Kb

    * - ``raspberrypi_zero``
      - `Raspberry Pi Zero <https://www.raspberrypi.org>`_
      - BCM2835
      - 1000 MHz
      - 524288 Kb
      - 524288 Kb

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

    * - ``redBearLab``
      - `RedBearLab nRF51822 <https://developer.mbed.org/platforms/RedBearLab-nRF51822/>`_
      - NRF51822
      - 16 MHz
      - 256 Kb
      - 16 Kb

    * - ``redBearLabBLENano``
      - `RedBearLab BLE Nano <https://developer.mbed.org/platforms/RedBearLab-BLE-Nano/>`_
      - NRF51822
      - 16 MHz
      - 256 Kb
      - 16 Kb

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

ST
~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``disco_f051r8``
      - `ST STM32F0DISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF253215>`_
      - STM32F051R8T6
      - 48 MHz
      - 64 Kb
      - 8 Kb

    * - ``disco_f100rb``
      - `ST STM32VLDISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF250863>`_
      - STM32F100RBT6
      - 24 MHz
      - 128 Kb
      - 8 Kb

    * - ``disco_f303vc``
      - `ST STM32F3DISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF254044>`_
      - STM32F303VCT6
      - 72 MHz
      - 256 Kb
      - 48 Kb

    * - ``disco_f334c8``
      - `ST 32F3348DISCOVERY <http://www.st.com/web/en/catalog/tools/PF260318>`_
      - STM32F334C8T6
      - 72 MHz
      - 64 Kb
      - 12 Kb

    * - ``disco_f401vc``
      - `ST 32F401CDISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF259098>`_
      - STM32F401VCT6
      - 84 MHz
      - 256 Kb
      - 64 Kb

    * - ``disco_f407vg``
      - `ST STM32F4DISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF252419>`_
      - STM32F407VGT6
      - 168 MHz
      - 1024 Kb
      - 128 Kb

    * - ``disco_f429zi``
      - `ST 32F429IDISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF259090>`_
      - STM32F429ZIT6
      - 180 MHz
      - 2048 Kb
      - 256 Kb

    * - ``disco_f469ni``
      - `ST 32F469IDISCOVERY <http://www.st.com/web/catalog/tools/FM116/CL1620/SC959/SS1532/LN1848/PF262395>`_
      - STM32F469NIH6
      - 180 MHz
      - 1024 Kb
      - 384 Kb

    * - ``disco_l053c8``
      - `ST 32L0538DISCOVERY <http://www.st.com/web/en/catalog/tools/PF260319>`_
      - STM32L053C8T6
      - 32 MHz
      - 64 Kb
      - 8 Kb

    * - ``disco_l152rb``
      - `ST STM32LDISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF258515>`_
      - STM32L152RBT6
      - 32 MHz
      - 128 Kb
      - 16 Kb

    * - ``disco_l476vg``
      - `ST 32L476GDISCOVERY <http://www.st.com/web/catalog/tools/FM116/CL1620/SC959/SS1532/LN1848/PF261635>`_
      - STM32L476VGT6
      - 80 MHz
      - 1024 Kb
      - 128 Kb

    * - ``nucleo_f030r8``
      - `ST Nucleo F030R8 <https://developer.mbed.org/platforms/ST-Nucleo-F030R8/>`_
      - STM32F030R8T6
      - 48 MHz
      - 64 Kb
      - 8 Kb

    * - ``nucleo_f031k6``
      - `ST Nucleo F031K6 <https://developer.mbed.org/platforms/ST-Nucleo-F031K6/>`_
      - STM32F031K6T6
      - 48 MHz
      - 32 Kb
      - 4 Kb

    * - ``nucleo_f042k6``
      - `ST Nucleo F042K6 <https://developer.mbed.org/platforms/ST-Nucleo-F042K6/>`_
      - STM32F042K6T6
      - 48 MHz
      - 32 Kb
      - 6 Kb

    * - ``nucleo_f070rb``
      - `ST Nucleo F070RB <https://developer.mbed.org/platforms/ST-Nucleo-F070RB/>`_
      - STM32F070RBT6
      - 48 MHz
      - 128 Kb
      - 16 Kb

    * - ``nucleo_f072rb``
      - `ST Nucleo F072RB <https://developer.mbed.org/platforms/ST-Nucleo-F072RB/>`_
      - STM32F072RBT6
      - 48 MHz
      - 128 Kb
      - 16 Kb

    * - ``nucleo_f091rc``
      - `ST Nucleo F091RC <https://developer.mbed.org/platforms/ST-Nucleo-F091RC/>`_
      - STM32F091RCT6
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``nucleo_f103rb``
      - `ST Nucleo F103RB <https://developer.mbed.org/platforms/ST-Nucleo-F103RB/>`_
      - STM32F103RBT6
      - 72 MHz
      - 128 Kb
      - 20 Kb

    * - ``nucleo_f302r8``
      - `ST Nucleo F302R8 <https://developer.mbed.org/platforms/ST-Nucleo-F302R8/>`_
      - STM32F302R8T6
      - 72 MHz
      - 64 Kb
      - 16 Kb

    * - ``nucleo_f303k8``
      - `ST Nucleo F303K8 <https://developer.mbed.org/platforms/ST-Nucleo-F303K8/>`_
      - STM32F303K8T6
      - 72 MHz
      - 64 Kb
      - 16 Kb

    * - ``nucleo_f303re``
      - `ST Nucleo F303RE <http://developer.mbed.org/platforms/ST-Nucleo-F303RE/>`_
      - STM32F303RET6
      - 72 MHz
      - 512 Kb
      - 64 Kb

    * - ``nucleo_f334r8``
      - `ST Nucleo F334R8 <https://developer.mbed.org/platforms/ST-Nucleo-F334R8/>`_
      - STM32F334R8T6
      - 72 MHz
      - 64 Kb
      - 16 Kb

    * - ``nucleo_f401re``
      - `ST Nucleo F401RE <https://developer.mbed.org/platforms/ST-Nucleo-F401RE/>`_
      - STM32F401RET6
      - 84 MHz
      - 512 Kb
      - 96 Kb

    * - ``nucleo_f410rb``
      - `ST Nucleo F410RB <https://developer.mbed.org/platforms/ST-Nucleo-F410RB/>`_
      - STM32F410RBT6
      - 100 MHz
      - 128 Kb
      - 32 Kb

    * - ``nucleo_f411re``
      - `ST Nucleo F411RE <https://developer.mbed.org/platforms/ST-Nucleo-F411RE/>`_
      - STM32F411RET6
      - 100 MHz
      - 512 Kb
      - 128 Kb

    * - ``nucleo_f446re``
      - `ST Nucleo F446RE <https://developer.mbed.org/platforms/ST-Nucleo-F446RE/>`_
      - STM32F446RET6
      - 180 MHz
      - 512 Kb
      - 128 Kb

    * - ``nucleo_l031k6``
      - `ST Nucleo L031K6 <https://developer.mbed.org/platforms/ST-Nucleo-L031K6/>`_
      - STM32L031K6T6
      - 32 MHz
      - 32 Kb
      - 8 Kb

    * - ``nucleo_l053r8``
      - `ST Nucleo L053R8 <https://developer.mbed.org/platforms/ST-Nucleo-L053R8/>`_
      - STM32L053R8T6
      - 48 MHz
      - 64 Kb
      - 8 Kb

    * - ``nucleo_l073rz``
      - `ST Nucleo L073RZ <https://developer.mbed.org/platforms/ST-Nucleo-L073RZ/>`_
      - STM32L073RZ
      - 32 MHz
      - 192 Kb
      - 20 Kb

    * - ``nucleo_l152re``
      - `ST Nucleo L152RE <https://developer.mbed.org/platforms/ST-Nucleo-L152RE/>`_
      - STM32L152RET6
      - 32 MHz
      - 512 Kb
      - 80 Kb

    * - ``nucleo_l476rg``
      - `ST Nucleo L476RG <https://developer.mbed.org/platforms/ST-Nucleo-L476RG/>`_
      - STM32L476RGT6
      - 80 MHz
      - 1024 Kb
      - 128 Kb

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

    * - ``seeedArchMax``
      - `SeeedStudio Arch Max <https://developer.mbed.org/platforms/Seeed-Arch-Max/>`_
      - STM32F407VET6
      - 168 MHz
      - 512 Kb
      - 192 Kb

    * - ``seeedTinyBLE``
      - `SeeedStudio Seeed Tiny BLE <http://developer.mbed.org/platforms/Seeed-Tiny-BLE/>`_
      - NRF51822
      - 16 MHz
      - 256 Kb
      - 16 Kb

    * - ``seeeduinoArchPro``
      - `SeeedStudio Seeeduino-Arch-Pro <https://developer.mbed.org/platforms/Seeeduino-Arch-Pro/>`_
      - LPC1768
      - 96 MHz
      - 512 Kb
      - 64 Kb

Silicon Labs
~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``efm32gg_stk3700``
      - `Silicon Labs EFM32GG-STK3700 (Giant Gecko) <https://developer.mbed.org/platforms/EFM32-Giant-Gecko/>`_
      - EFM32GG990F1024
      - 48 MHz
      - 1024 Kb
      - 128 Kb

    * - ``efm32hg_stk3400``
      - `Silicon Labs SLSTK3400A USB-enabled (Happy Gecko) <https://developer.mbed.org/platforms/EFM32-Happy-Gecko/>`_
      - EFM32HG322F64
      - 24 MHz
      - 64 Kb
      - 8 Kb

    * - ``efm32lg_stk3600``
      - `Silicon Labs EFM32LG-STK3600 (Leopard Gecko) <https://developer.mbed.org/platforms/EFM32-Leopard-Gecko/>`_
      - EFM32LG990F256
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``efm32pg_stk3401``
      - `Silicon Labs SLSTK3401A (Pearl Gecko) <https://developer.mbed.org/platforms/EFM32-Pearl-Gecko/>`_
      - EFM32PG1B200F256
      - 40 MHz
      - 256 Kb
      - 32 Kb

    * - ``efm32wg_stk3800``
      - `Silicon Labs EFM32WG-STK3800 (Wonder Gecko) <https://developer.mbed.org/platforms/EFM32-Wonder-Gecko/>`_
      - EFM32WG990F256
      - 48 MHz
      - 256 Kb
      - 32 Kb

    * - ``efm32zg_stk3200``
      - `Silicon Labs EFM32ZG-STK3200 (Zero Gecko) <https://developer.mbed.org/platforms/EFM32-Zero-Gecko/>`_
      - EFM2ZG222F32
      - 24 MHz
      - 32 Kb
      - 4 Kb

Solder Splash Labs
~~~~~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``dipcortexm0``
      - `Solder Splash Labs DipCortex M0 <https://developer.mbed.org/platforms/DipCortex-M0/>`_
      - LPC11U24
      - 50 MHz
      - 32 Kb
      - 8 Kb

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

Switch Science
~~~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``hrm1017``
      - `Switch Science mbed HRM1017 <https://developer.mbed.org/platforms/mbed-HRM1017/>`_
      - NRF51822
      - 16 MHz
      - 256 Kb
      - 16 Kb

    * - ``lpc1114fn28``
      - `Switch Science mbed LPC1114FN28 <https://developer.mbed.org/platforms/LPC1114FN28/>`_
      - LPC1114FN28
      - 48 MHz
      - 32 Kb
      - 4 Kb

TI
~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lplm4f120h5qr``
      - `TI LaunchPad (Stellaris) w/ lm4f120 (80MHz) <http://www.ti.com/tool/ek-lm4f120xl>`_
      - LPLM4F120H5QR
      - 80 MHz
      - 256 Kb
      - 32 Kb

    * - ``lpmsp430f5529``
      - `TI LaunchPad w/ msp430f5529 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529
      - 16 MHz
      - 128 Kb
      - 1 Kb

    * - ``lpmsp430f5529_25``
      - `TI LaunchPad w/ msp430f5529 (25MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529
      - 25 MHz
      - 128 Kb
      - 1 Kb

    * - ``lpmsp430fr4133``
      - `TI LaunchPad w/ msp430fr4133 <http://www.ti.com/tool/msp-exp430fr4133>`_
      - MSP430FR4133
      - 16 MHz
      - 16 Kb
      - 2 Kb

    * - ``lpmsp430fr5739``
      - `TI FraunchPad w/ msp430fr5739 <http://www.ti.com/tool/msp-exp430fr5739>`_
      - MSP430FR5739
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``lpmsp430fr5969``
      - `TI LaunchPad w/ msp430fr5969 <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430fr5969.html>`_
      - MSP430FR5969
      - 8 MHz
      - 64 Kb
      - 1 Kb

    * - ``lpmsp430fr6989``
      - `TI LaunchPad w/ msp430fr6989 <http://www.ti.com/tool/msp-exp430fr6989>`_
      - MSP430FR6989
      - 16 MHz
      - 128 Kb
      - 2 Kb

    * - ``lpmsp430g2231``
      - `TI LaunchPad w/ msp430g2231 (1 MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2231
      - 1 MHz
      - 2 Kb
      - 0.125 Kb

    * - ``lpmsp430g2452``
      - `TI LaunchPad w/ msp430g2452 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2452
      - 16 MHz
      - 8 Kb
      - 0.25 Kb

    * - ``lpmsp430g2553``
      - `TI LaunchPad w/ msp430g2553 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2553
      - 16 MHz
      - 16 Kb
      - 0.5 Kb

    * - ``lptm4c1230c3pm``
      - `TI LaunchPad (Tiva C) w/ tm4c123 (80MHz) <http://www.ti.com/ww/en/launchpad/launchpads-connected-ek-tm4c123gxl.html>`_
      - LPTM4C1230C3PM
      - 80 MHz
      - 256 Kb
      - 32 Kb

    * - ``lptm4c1294ncpdt``
      - `TI LaunchPad (Tiva C) w/ tm4c129 (120MHz) <http://www.ti.com/ww/en/launchpad/launchpads-connected-ek-tm4c1294xl.html>`_
      - LPTM4C1294NCPDT
      - 120 MHz
      - 1024 Kb
      - 256 Kb

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

u-blox
~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``ubloxc027``
      - `u-blox C027 <https://developer.mbed.org/platforms/u-blox-C027/>`_
      - LPC1768
      - 96 MHz
      - 512 Kb
      - 64 Kb

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
