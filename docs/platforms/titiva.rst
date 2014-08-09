.. _platform_titiva:

Platform ``titiva``
===================

`Texas Instruments TM4C12x MCUs <http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/c2000_performance/control_automation/tm4c12x/overview.page>`_
offer the industry’s most popular ARM®
Cortex®-M4 core with scalable memory and package options, unparalleled
connectivity peripherals, advanced application functions, industry-leading
analog integration, and extensive software solutions.

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
      - `gcc-arm-embedded <https://launchpad.net/gcc-arm-embedded/>`_,
        `GDB <http://www.gnu.org/software/gdb/>`_
    * - ``tool-lm4flash``
      - uploader
      - `Flash Programmer <http://www.ti.com/tool/lmflashprogrammer>`_
    * - ``framework-energiativa``
      -
      - See below in :ref:`titiva_frameworks`

.. note::
    You can install ``titiva`` platform with these packages
    via :ref:`cmd_install` command.


.. _titiva_frameworks:

Frameworks
----------

.. list-table::
    :header-rows:  1

    * - Type ``framework``
      - Name
      - Reference
    * - ``energia``
      - Energia Wiring-based Framework (LM4F Core)
      - `Documentation <http://energia.nu/reference/>`_


Boards
------

.. note::
   For more detailed ``board`` information please scroll table below by
   horizontal.

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller ``board_mcu``
      - Frequency ``board_f_cpu``
      - Flash
      - RAM
    * - ``lplm4f120h5qr``
      - `Stellaris LM4F120 LaunchPad <http://www.ti.com/tool/ek-lm4f120xl>`_
      - LM4F120H5QR ``cortex-m4``
      - 80 MHz ``80000000L``
      - 256 Kb
      - 32 Kb
    * - ``lptm4c1230c3pm``
      - `Tiva C Series TM4C123G LaunchPad
        <http://www.ti.com/ww/en/launchpad/launchpads-connected-ek-tm4c123gxl.html>`_
      - TM4C123GH6PM ``cortex-m4``
      - 80 MHz ``80000000L``
      - 256 Kb
      - 32 Kb
    * - ``lptm4c1294ncpdt``
      - `Tiva C Series TM4C1294 Connected LaunchPad
        <http://www.ti.com/ww/en/launchpad/launchpads-connected-ek-tm4c1294xl.html>`_
      - TM4C1294NCPDT ``cortex-m4``
      - 120 Mhz ``120000000L``
      - 1 Mb
      - 256 Kb

More detailed information you can find here
`TIVA C Series LaunchPads <http://www.ti.com/ww/en/launchpad/launchpads-connected.html>`_.
