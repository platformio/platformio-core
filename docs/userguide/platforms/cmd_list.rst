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

.. _cmd_platform_list:

platformio platform list
========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platform list [OPTIONS]


Description
-----------

List installed :ref:`platforms`

Options
~~~~~~~

.. program:: platformio platform list

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format

Examples
--------

.. code-block:: bash

    $ platformio platform list
    atmelavr ~ Atmel AVR
    ====================
    Atmel AVR 8- and 32-bit MCUs deliver a unique combination of performance, power efficiency and design flexibility. Optimized to speed time to market-and easily adapt to new ones-they are based on the industrys most code-efficient architecture for C and assembly programming.

    Home: http://platformio.org/platforms/atmelavr
    Packages: toolchain-atmelavr, framework-simba
    Version: 0.0.0

    atmelsam ~ Atmel SAM
    ====================
    Atmel | SMART offers Flash- based ARM products based on the ARM Cortex-M0+, Cortex-M3 and Cortex-M4 architectures, ranging from 8KB to 2MB of Flash including a rich peripheral and feature mix.

    Home: http://platformio.org/platforms/atmelsam
    Packages: framework-arduinosam, framework-mbed, framework-simba, toolchain-gccarmnoneeabi, tool-bossac
    Version: 0.0.0

    espressif ~ Espressif
    =====================
    Espressif Systems is a privately held fabless semiconductor company. They provide wireless communications and Wi-Fi chips which are widely used in mobile devices and the Internet of Things applications.

    Home: http://platformio.org/platforms/espressif
    Packages: framework-simba, tool-esptool, framework-arduinoespressif, sdk-esp8266, toolchain-xtensa
    Version: 0.0.0
    ...
