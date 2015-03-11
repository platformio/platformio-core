.. _platform_titiva:

Platform ``titiva``
===================

Texas Instruments TM4C12x MCUs offer the industrys most popular
ARM Cortex-M4 core with scalable memory and package options, unparalleled
connectivity peripherals, advanced application functions, industry-leading
analog integration, and extensive software solutions.

http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/c2000_performance/control_automation/tm4c12x/overview.page

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``ldscripts``
      - `Linker Scripts <https://sourceware.org/binutils/docs/ld/Scripts.html>`_

    * - ``toolchain-gccarmnoneeabi``
      - `gcc-arm-embedded <https://launchpad.net/gcc-arm-embedded>`_, `GDB <http://www.gnu.org/software/gdb/>`_

    * - ``tool-lm4flash``
      - `Flash Programmer <http://www.ti.com/tool/lmflashprogrammer>`_

    * - ``framework-opencm3``
      - `libOpenCM3 Framework <http://www.libopencm3.org/>`_

    * - ``framework-energiativa``
      - `Energia Wiring-based Framework (LM4F Core) <http://energia.nu/reference/>`_

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

    * - ``lplm4f120h5qr``
      - `LaunchPad (Stellaris) w/ lm4f120 (80MHz) <http://www.ti.com/tool/ek-lm4f120xl>`_
      - LPLM4F120H5QR
      - 80 MHz
      - 256 Kb
      - 32 Kb
      

    * - ``lptm4c1230c3pm``
      - `LaunchPad (Tiva C) w/ tm4c123 (80MHz) <http://www.ti.com/ww/en/launchpad/launchpads-connected-ek-tm4c123gxl.html>`_
      - LPTM4C1230C3PM
      - 80 MHz
      - 256 Kb
      - 32 Kb
      

    * - ``lptm4c1294ncpdt``
      - `LaunchPad (Tiva C) w/ tm4c129 (120MHz) <http://www.ti.com/ww/en/launchpad/launchpads-connected-ek-tm4c1294xl.html>`_
      - LPTM4C1294NCPDT
      - 120 MHz
      - 1024 Kb
      - 256 Kb
      