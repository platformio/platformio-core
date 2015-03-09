.. _platform_nxplpc:

Platform ``nxplpc``
===================

`The NXP LPC <http://www.nxp.com/products/microcontrollers/>`_ is a family of 32-bit microcontroller integrated circuits by NXP Semiconductors. The LPC chips are grouped into related series that are based around the same 32-bit ARM processor core, such as the Cortex-M4F, Cortex-M3, Cortex-M0+, or Cortex-M0. Internally, each microcontroller consists of the processor core, static RAM memory, flash memory, debugging interface, and various peripherals.

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
    * - ``framework-mbed``
      -
      - See below in :ref:`nxplpc_frameworks`

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).


.. _nxplpc_frameworks:

Frameworks
----------

.. list-table::
    :header-rows:  1

    * - Type ``framework``
      - Name
      - Reference
    * - ``mbed``
      - MBED Framework
      - `Documentation <http://mbed.org>`__


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
    * - ``lpc1549``
      - `LPCXpresso1549 <https://developer.mbed.org/platforms/LPCXpresso1549/>`_
      - LPC1549 ``cortex-m3``
      - 72 MHz ``72000000L``
      - 256 Kb
      - 36 Kb
    * - ``lpc1768``
      - `mbed LPC1768 <http://developer.mbed.org/platforms/mbed-LPC1768/>`_
      - LPC1768 ``cortex-m3``
      - 96 MHz ``96000000L``
      - 512 Kb
      - 32 Kb
    * - ``seeeduinoArchPro``
      - `Seeeduino-Arch-Pro <https://developer.mbed.org/platforms/Seeeduino-Arch-Pro/>`_
      - LPC1768 ``cortex-m3``
      - 96 MHz ``96000000L``
      - 512 Kb
      - 32 Kb
    * - ``ubloxc027``
      - `U-blox C027 <https://developer.mbed.org/platforms/u-blox-C027/>`_
      - LPC1768 ``cortex-m3``
      - 96 MHz ``96000000L``
      - 512 Kb
      - 32 Kb
    * - ``lpc1114fn28``
      - `mbed LPC1114FN28 <https://developer.mbed.org/platforms/LPC1114FN28/>`_
      - LPC1114FN28 ``cortex-m0``
      - 48 MHz ``48000000L``
      - 32 Kb
      - 4 Kb
    * - ``lpc11u24``
      - `mbed LPC11U24 <https://developer.mbed.org/platforms/mbed-LPC11U24/>`_
      - LPC11U24 ``cortex-m0``
      - 48 MHz ``48000000L``
      - 32 Kb
      - 8 Kb
    * - ``dipcortexm0``
      - `DipCortex M0 <https://developer.mbed.org/platforms/DipCortex-M0/>`_
      - LPC11U24 ``cortex-m0``
      - 50 MHz ``50000000L``
      - 32 Kb
      - 8 Kb
    * - ``blueboard_lpc11u24``
      - `BlueBoard-LPC11U24 <https://developer.mbed.org/platforms/BlueBoard-LPC11U24/>`_
      - LPC11U24 ``cortex-m0``
      - 48 MHz ``48000000L``
      - 32 Kb
      - 8 Kb
    * - ``mbuino``
      - `Outrageous Circuits mBuino <https://developer.mbed.org/platforms/Outrageous-Circuits-mBuino/>`_
      - LPC11U24 ``cortex-m0``
      - 50 MHz ``50000000L``
      - 32 Kb
      - 8 Kb
    * - ``lpc11u35``
      - `EA LPC11U35 QuickStart Board <https://developer.mbed.org/platforms/EA-LPC11U35/>`_
      - LPC11U35 ``cortex-m0``
      - 48 MHz ``48000000L``
      - 64 Kb
      - 10 Kb
    * - ``lpc11u35_501``
      - `TG-LPC11U35-501 QuickStart Board <https://developer.mbed.org/platforms/TG-LPC11U35-501/>`_
      - LPC11U35 ``cortex-m0``
      - 48 MHz ``48000000L``
      - 64 Kb
      - 10 Kb
    * - ``lpc4088``
      - `EA LPC4088 QuickStart Board <https://developer.mbed.org/platforms/EA-LPC4088/>`_
      - LPC4088 ``cortex-m4``
      - 120 MHz ``120000000L``
      - 512 Kb
      - 96 Kb
    * - ``lpc4088_dm``
      - `EA LPC4088 Display Module <https://developer.mbed.org/platforms/EA-LPC4088-Display-Module/>`_
      - LPC4088 ``cortex-m4``
      - 120 MHz ``120000000L``
      - 512 Kb
      - 96 Kb


More detailed information you can find here
`NXP platforms with support MBED framework <http://developer.mbed.org/platforms/?tvend=3>`_.
