.. _platform_timsp430:

Platform ``timsp430``
=====================

MSP430 microcontrollers (MCUs) from Texas Instruments (TI)
are 16-bit, RISC-based, mixed-signal processors designed for ultra-low
power. These MCUs offer the lowest power consumption and the perfect
mix of integrated peripherals for thousands of applications.

http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/msp/overview.page

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``toolchain-timsp430``
      - `msp-gcc <http://sourceforge.net/projects/mspgcc/>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``tool-mspdebug``
      - `MSPDebug <http://mspdebug.sourceforge.net/>`_

    * - ``framework-energiamsp430``
      - `Energia Wiring-based Framework (MSP430 Core) <http://energia.nu/reference/>`_

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).



Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

TI
~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``lpmsp430f5529``
      - `LaunchPad w/ msp430f5529 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529
      - 16 MHz
      - 128 Kb
      - 1 Kb

    * - ``lpmsp430f5529_25``
      - `LaunchPad w/ msp430f5529 (25MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529
      - 25 MHz
      - 128 Kb
      - 1 Kb

    * - ``lpmsp430fr5739``
      - `FraunchPad w/ msp430fr5739 <http://www.ti.com/tool/msp-exp430fr5739>`_
      - MSP430FR5739
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``lpmsp430fr5969``
      - `LaunchPad w/ msp430fr5969 <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430fr5969.html>`_
      - MSP430FR5969
      - 8 MHz
      - 64 Kb
      - 1 Kb

    * - ``lpmsp430g2231``
      - `LaunchPad w/ msp430g2231 (1 MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2231
      - 1 MHz
      - 2 Kb
      - 0.125 Kb

    * - ``lpmsp430g2452``
      - `LaunchPad w/ msp430g2452 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2452
      - 16 MHz
      - 8 Kb
      - 0.25 Kb

    * - ``lpmsp430g2553``
      - `LaunchPad w/ msp430g2553 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2553
      - 16 MHz
      - 16 Kb
      - 0.5 Kb
