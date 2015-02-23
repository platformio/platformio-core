.. _platform_atmelsam:

Platform ``atmelsam``
=====================

`Atmel® | SMART <http://www.atmel.com/products/microcontrollers/arm/default.aspx>`_ 
offers Flash- based ARM® products based on the ARM Cortex-®M0+, Cortex-M3 and 
Cortex-M4 architectures, ranging from 8KB to 2MB of Flash including a rich 
peripheral and feature mix.

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
    * - ``tool-bossac``
      - uploader
      - `Bossac <https://sourceforge.net/projects/b-o-s-s-a/>`_
    * - ``framework-arduino``
      -
      - See below in :ref:`atmelsam_frameworks`


.. note::
    You can install ``atmelsam`` platform with these packages
    via :ref:`cmd_install` command.


.. _atmelsam_frameworks:

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
    * - ``due``
      - `Arduino Due <http://arduino.cc/en/Main/arduinoBoardDue>`_
      - at91sam3x8e ``cortex-m3``
      - 84 MHz ``84000000L``
      - 512 Kb
      - 32 Kb
    * - ``digix``
      - `Digistump DigiX <http://digistump.com/products/50>`_
      - at91sam3x8e ``cortex-m3``
      - 84 MHz ``84000000L``
      - 512 kb
      - 32 Kb

More detailed information you can find here
`Atmel SMART ARM-based MCUs <http://www.atmel.com/products/microcontrollers/arm/default.aspx>`_.
