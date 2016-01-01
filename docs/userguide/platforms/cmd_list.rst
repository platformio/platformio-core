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

.. _cmd_platforms_list:

platformio platforms list
=========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platforms list [OPTIONS]


Description
-----------

List installed :ref:`Platforms <platforms>`

Options
~~~~~~~

.. program:: platformio platforms list

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format

Examples
--------

.. code-block:: bash

    $ platformio platforms list
    atmelavr    with packages: toolchain-atmelavr, tool-avrdude, framework-arduinoavr, tool-micronucleus
    atmelsam    with packages: framework-arduinosam, ldscripts, toolchain-gccarmnoneeabi, tool-bossac
    freescalekinetis with packages: framework-mbed, toolchain-gccarmnoneeabi
    nordicnrf51 with packages: framework-mbed, toolchain-gccarmnoneeabi
    nxplpc      with packages: framework-mbed, toolchain-gccarmnoneeabi
    ststm32     with packages: framework-libopencm3, toolchain-gccarmnoneeabi, tool-stlink, framework-spl, framework-cmsis, framework-mbed, ldscripts
    teensy      with packages: toolchain-atmelavr, ldscripts, framework-arduinoteensy, toolchain-gccarmnoneeabi, tool-teensy
    timsp430    with packages: toolchain-timsp430, tool-mspdebug, framework-energiamsp430, framework-arduinomsp430
    titiva      with packages: ldscripts, framework-libopencm3, toolchain-gccarmnoneeabi, tool-lm4flash, framework-energiativa
