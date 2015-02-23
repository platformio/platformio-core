.. _cmd_list:

platformio list
===============

.. contents::

Usage
-----

.. code-block:: bash

    platformio list [OPTIONS]


Description
-----------

List installed :ref:`Platforms <platforms>`

Options
~~~~~~~

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format

Examples
--------

.. code-block:: bash

    $ platformio list
    atmelavr    with packages: toolchain-atmelavr, tool-avrdude, framework-arduinoavr, tool-micronucleus
    atmelsam    with packages: framework-arduinosam, ldscripts, toolchain-gccarmnoneeabi, tool-bossac
    stm32       with packages: toolchain-gccarmnoneeabi, tool-stlink, framework-spl, framework-cmsis, framework-opencm3, ldscripts
    teensy      with packages: toolchain-atmelavr, ldscripts, framework-arduinoteensy, toolchain-gccarmnoneeabi, tool-teensy
    timsp430    with packages: toolchain-timsp430, tool-mspdebug, framework-energiamsp430
    titiva      with packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa
