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

.. _cmd_platform_show:

platformio platform show
========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platform show PLATFORM


Description
-----------

Show details about the installed :ref:`platforms`


Examples
--------

.. code::

    > platformio platform show atmelavr

    atmelavr ~ Atmel AVR
    ====================
    Atmel AVR 8- and 32-bit MCUs deliver a unique combination of performance, power efficiency and design flexibility. Optimized to speed time to market-and easily adapt to new ones-they are based on the industrys most code-efficient architecture for C and assembly programming.

    Version: 1.2.1
    Home: http://platformio.org/platforms/atmelavr
    License: Apache-2.0
    Frameworks: simba, arduino

    Package toolchain-atmelavr
    --------------------------
    Type: toolchain
    Requirements: ~1.40902.0
    Installed: Yes
    Description: avr-gcc
    Url: http://www.atmel.com/products/microcontrollers/avr/32-bitavruc3.aspx?tab=tools
    Version: 1.40902.0 (4.9.2)

    Package framework-arduinoavr
    ----------------------------
    Type: framework
    Requirements: ~1.10612.1
    Installed: Yes
    Url: https://www.arduino.cc/en/Main/Software
    Version: 1.10612.1 (1.6.12)
    Description: Arduino Wiring-based Framework (AVR Core, 1.6)

    Package framework-simba
    -----------------------
    Type: framework
    Requirements: >=7.0.0
    Installed: Yes
    Url: https://github.com/eerimoq/simba
    Version: 11.0.0
    Description: Simba Embedded Programming Platform

    Package tool-avrdude
    --------------------
    Type: uploader
    Requirements: ~1.60300.0
    Installed: Yes
    Description: AVRDUDE
    Url: http://www.nongnu.org/avrdude/
    Version: 1.60300.0 (6.3.0)

    Package tool-micronucleus
    -------------------------
    Type: uploader
    Requirements: ~1.200.0
    Installed: No (optional)
