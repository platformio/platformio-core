.. _platform_teensy:

Platform ``teensy``
===================

`Teensy <https://www.pjrc.com/teensy/>`_ is a complete USB-based microcontroller development system, in a very small footprint, capable of implementing many types of projects. All programming is done via the USB port. No special programmer is needed, only a standard "Mini-B" USB cable and a PC or Macintosh with a USB port.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Alias
      - Contents
    * - ``toolchain-gccarmnoneeabi``
      - toolchain
      - `gcc-arm-embedded <https://launchpad.net/gcc-arm-embedded>`_,
        `GDB <http://www.gnu.org/software/gdb/>`_
    * - ``toolchain-atmelavr``
      - toolchain
      - `avr-gcc <https://gcc.gnu.org/wiki/avr-gcc>`_,
        `GDB <http://www.gnu.org/software/gdb/>`_,
        `AVaRICE <http://avarice.sourceforge.net>`_,
        `SimulAVR <http://www.nongnu.org/simulavr/>`_
    * - ``tool-teensy``
      - uploader
      - `Teensy Loader <https://www.pjrc.com/teensy/loader.html>`_
    * - ``framework-arduinoteensy``
      -
      - See below in :ref:`teensy_frameworks`


.. note::
    You can install ``teensy`` platform with these packages
    via :ref:`cmd_install` command.


.. _teensy_frameworks:

Frameworks
----------

.. list-table::
    :header-rows:  1

    * - Type ``framework``
      - Name
      - Reference
    * - ``arduino``
      - Arduino Wiring-based Framework
      - `Documentation <http://arduino.cc/en/Reference/HomePage>`_


Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller ``board_mcu``
      - Frequency ``board_f_cpu``
      - Flash
      - RAM
    * - ``teensy20``
      - `Teensy 2.0 <https://www.pjrc.com/store/teensy.html>`_
      - ATmega32u4 ``atmega32u4``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2.5 Kb
    * - ``teensy20pp``
      - `Teensy++ 2.0 <https://www.pjrc.com/store/teensypp.html>`_
      - AT90USB1289 ``at90usb1286``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 8 Kb
    * - ``teensy30``
      - `Teensy 3.0 <https://www.pjrc.com/store/teensy3.html>`_
      - MK20DX128 ``cortex-m4``
      - 48 Mhz ``48000000L``
      - 128 kb
      - 16 Kb
    * - ``teensy31``
      - `Teensy 3.1 <https://www.pjrc.com/store/teensy31.html>`_
      - MK20DX256 ``cortex-m4``
      - 72 Mhz ``72000000L``
      - 256 kb
      - 64 Kb

More detailed information you can find here
`Teensy USB Development Boards <https://www.pjrc.com/teensy/>`_.
