.. _platform_timsp430:

Platform ``timsp430``
=====================

`MSP430 microcontrollers (MCUs) from Texas Instruments (TI) <http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/msp/overview.page>`_
are 16-bit, RISC-based, mixed-signal processors designed for ultra-low power.
These MCUs offer the lowest power consumption and the perfect mix of integrated
peripherals for thousands of applications.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Alias
      - Contents
    * - ``toolchain-timsp430``
      - toolchain
      - `msp-gcc <http://sourceforge.net/projects/mspgcc/>`_,
        `GDB <http://www.gnu.org/software/gdb/>`_
    * - ``tool-mspdebug``
      - uploader
      - `MSPDebug <http://mspdebug.sourceforge.net>`_
    * - ``framework-energiamsp430``
      -
      - See below in :ref:`timsp430_frameworks`


.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).


.. _timsp430_frameworks:

Frameworks
----------

.. list-table::
    :header-rows:  1

    * - Type ``framework``
      - Name
      - Reference
    * - ``energia``
      - Energia Wiring-based Framework (MSP430 Core)
      - `Documentation <http://energia.nu/reference/>`_


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
    * - ``lpmsp430g2231``
      - `MSP430G2231 LaunchPad <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2231 ``msp430g2231``
      - 16 MHz ``16000000L``
      - 2 Kb
      - 128 B
    * - ``lpmsp430g2452``
      - `MSP430G2452 LaunchPad <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2452 ``msp430g2452``
      - 16 MHz ``16000000L``
      - 8 Kb
      - 256 B
    * - ``lpmsp430g2553``
      - `MSP430G2553 LaunchPad <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2553 ``msp430g2553``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 512 B
    * - ``lpmsp430f5529``
      - `MSP430F5529 LaunchPad (16 Mhz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529 ``msp430f5529``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 8 KB
    * - ``lpmsp430f5529_25``
      - `MSP430F5529 LaunchPad (25 Mhz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529 ``msp430f5529``
      - 25 MHz ``25000000L``
      - 128 Kb
      - 8 KB
    * - ``lpmsp430fr5739``
      - `MSP430FR5739 Experimenter Board <http://www.ti.com/tool/msp-exp430fr5739>`_
      - MSP430FR5739 ``msp430fr5739``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 1 KB
    * - ``lpmsp430fr5969``
      - `MSP430FR5969 LaunchPad <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430fr5969.html>`_
      - MSP430FR5969 ``msp430fr5969``
      - 16 MHz ``16000000L``
      - 64 Kb
      - 2 KB


More detailed information you can find here
`MSP430 LaunchPads <http://www.ti.com/ww/en/launchpad/launchpads-msp430.html>`_.



