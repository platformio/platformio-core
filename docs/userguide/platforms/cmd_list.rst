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
