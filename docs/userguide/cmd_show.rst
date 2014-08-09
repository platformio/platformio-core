.. _cmd_show:

platformio show
===============

.. contents::

Usage
-----

.. code-block:: bash

    platformio show PLATFORM


Description
-----------

Show details about the installed :ref:`Platforms <platforms>`


Examples
--------

.. code-block:: bash

    $ platformio show atmelavr
    atmelavr    - An embedded platform for Atmel AVR microcontrollers (with Arduino Framework)
    ----------
    Package: toolchain-atmelavr
    Alias: toolchain
    Location: /Users/ikravets/.platformio/atmelavr/tools/toolchain
    Version: 1
    ----------
    Package: tool-avrdude
    Alias: uploader
    Location: /Users/ikravets/.platformio/atmelavr/tools/avrdude
    Version: 1
    ----------
    Package: framework-arduinoavr
    Location: /Users/ikravets/.platformio/atmelavr/frameworks/arduino
    Version: 1
