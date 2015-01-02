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
    timsp430    with packages: toolchain-timsp430, tool-mspdebug, framework-energiamsp430
    atmelavr    with packages: toolchain-atmelavr, tool-avrdude, framework-arduinoavr
    titiva      with packages: toolchain-gccarmnoneeabi, tool-lm4flash, framework-energiativa
