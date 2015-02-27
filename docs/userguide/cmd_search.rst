.. _cmd_search:

platformio search
=================

.. contents::

Usage
-----

.. code-block:: bash

    platformio search QUERY [OPTIONS]


Description
-----------

Search for development :ref:`Platforms <platforms>`

Options
~~~~~~~

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format


Examples
--------

1. Print all available development platforms

.. code-block:: bash

    $ platformio search
    atmelavr    - An embedded platform for Atmel AVR microcontrollers (with Arduino Framework)
    atmelsam    - An embedded platform for Atmel SAM microcontrollers (with Arduino Framework)
    stm32       - An embedded platform for STMicroelectronics ARM microcontrollers
    teensy      - An embedded platform for Teensy boards (with Arduino Framework)
    timsp430    - An embedded platform for TI MSP430 microcontrollers (with Energia Framework)
    titiva      - An embedded platform for TI TIVA C ARM microcontrollers (with Energia and OpenCM3 Frameworks)
    ...

2. Search for TI development platforms

.. code-block:: bash

    $ platformio search ti
    timsp430 - An embedded platform for TI MSP430 microcontrollers (with Energia Framework)
    titiva   - An embedded platform for TI TIVA C ARM microcontrollers (with Energia Framework)

3. Search for development platforms which support "Arduino Framework"

.. code-block:: bash

    $ platformio search arduino
    atmelavr    - An embedded platform for Atmel AVR microcontrollers (with Arduino Framework)
    atmelsam    - An embedded platform for Atmel SAM microcontrollers (with Arduino Framework)
    teensy      - An embedded platform for Teensy boards (with Arduino Framework)
