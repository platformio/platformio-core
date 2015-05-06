.. _cmd_run:

platformio run
==============

.. contents::

Usage
-----

.. code-block:: bash

    platformio run [OPTIONS]


Description
-----------

Process environments which are defined in :ref:`projectconf` file


Options
-------

.. option::
    -e, --environment

Process specified environments


.. option::
    -t, --target

Process specified targets

.. option::
    --upload-port

Upload port of embedded board. To print all available ports use
:ref:`cmd_serialports` command

.. option::
    --build-dir

Specify the path to project directory. By default, ``--build-dir`` is equal to
current working directory (``CWD``).

Examples
--------

1. Process `Wiring Blink Example <https://github.com/platformio/platformio/tree/develop/examples/wiring-blink>`_

.. code-block::   bash

    $ platformio run
    Processing arduino_pro5v environment:
    scons: `.pioenvs/arduino_pro5v/firmware.elf' is up to date.
    scons: `.pioenvs/arduino_pro5v/firmware.hex' is up to date.

    Processing launchpad_msp430g2 environment:
    scons: `.pioenvs/launchpad_msp430g2/firmware.elf' is up to date.
    scons: `.pioenvs/launchpad_msp430g2/firmware.hex' is up to date.

    Processing launchpad_lm4f120 environment:
    scons: `.pioenvs/launchpad_lm4f120/firmware.elf' is up to date.
    scons: `.pioenvs/launchpad_lm4f120/firmware.hex' is up to   date


2. Process specific environment

.. code-block:: bash

    $ platformio run -e arduino_pro5v -e launchpad_lm4f120
    Processing arduino_pro5v environment:
    scons: `.pioenvs/arduino_pro5v/firmware.elf' is up to date.
    scons: `.pioenvs/arduino_pro5v/firmware.hex' is up to date.

    Processing launchpad_lm4f120 environment:
    scons: `.pioenvs/launchpad_lm4f120/firmware.elf' is up to date.
    scons: `.pioenvs/launchpad_lm4f120/firmware.hex' is up to date.


3. Process specific target

.. code-block:: bash

    $ platformio run -t clean
    Processing arduino_pro5v environment:
    Removed .pioenvs/arduino_pro5v/src/main.o
    ...
    Removed .pioenvs/arduino_pro5v/firmware.hex

    Processing launchpad_msp430g2 environment:
    Removed .pioenvs/launchpad_msp430g2/src/main.o
    ...
    Removed .pioenvs/launchpad_msp430g2/firmware.hex

    Processing launchpad_lm4f120 environment:
    Removed .pioenvs/launchpad_lm4f120/src/main.o
    ...
    Removed .pioenvs/launchpad_lm4f120/firmware.hex


4. Mix environments and targets

.. code-block:: bash

    $ platformio run -e launchpad_msp430g2 -t upload
    Processing launchpad_msp430g2 environment:
    /Users/ikravets/.platformio/timsp430/tools/mspdebug/mspdebug rf2500 --force-reset "prog .pioenvs/launchpad_msp430g2/firmware.hex"
    MSPDebug version 0.20 - debugging tool for MSP430 MCUs
    Copyright (C) 2009-2012 Daniel Beer <dlbeer@gmail.com>
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    Trying to open interface 1 on 009
    Initializing FET...
    FET protocol version is 30394216
    Configured for Spy-Bi-Wire
    Sending reset...
    Set Vcc: 3000 mV
    Device ID: 0x2553
      Code start address: 0xc000
      Code size         : 16384 byte = 16 kb
      RAM  start address: 0x200
      RAM  end   address: 0x3ff
      RAM  size         : 512 byte = 0 kb
    Device: MSP430G2553/G2403
    Code memory starts at 0xc000
    Number of breakpoints: 2
    Chip ID data: 25 53
    Erasing...
    Programming...
    Writing  646 bytes at c000...
    Writing   32 bytes at ffe0...
    Done, 678 bytes total
