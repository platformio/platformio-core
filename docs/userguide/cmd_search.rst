.. _cmd_search:

platformio search
=================

.. contents::

Usage
-----

.. code-block:: bash

    # Print all available development platforms
    platformio search all

    # Filter platforms by "Query"
    platformio search QUERY


Description
-----------

Search for development :ref:`Platforms <platforms>`


Examples
--------

1. Search for TI development platforms

.. code-block:: bash

    $ platformio search ti
    timsp430 - An embedded platform for TI MSP430 microcontrollers (with Energia Framework)
    titiva   - An embedded platform for TI TIVA C ARM microcontrollers (with Energia Framework)

2. Search for development platforms which support "Arduino Framework"

.. code-block:: bash

    $ platformio search arduino
    atmelavr - An embedded platform for Atmel AVR microcontrollers (with Arduino Framework)
