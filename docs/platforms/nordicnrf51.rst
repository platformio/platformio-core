.. _platform_nordicnrf51:

Platform ``nordicnrf51``
========================

`The Nordic nRF51 Series <https://www.nordicsemi.com/eng/Products/nRF51-Series-SoC>`_ is a family of highly flexible, multi-protocol, system-on-chip (SoC) devices for ultra-low power wireless applications. nRF51 Series devices support a range of protocol stacks including Bluetooth Smart (previously called Bluetooth low energy), ANT and proprietary 2.4GHz protocols such as Gazell.

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
      - See below in :ref:`nordicnrf51_frameworks`

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).


.. _nordicnrf51_frameworks:

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
    * - ``nrf51_mkit``
      - `Nordic nRF51822-mKIT <http://developer.mbed.org/platforms/Nordic-nRF51822/>`_
      - nrf51822 ``cortex-m0``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 16 Kb
    * - ``nrf51_dongle``
      - `Nordic nRF51-Dongle <https://developer.mbed.org/platforms/Nordic-nRF51-Dongle/>`_
      - nrf51822/nrf51422 ``cortex-m0``
      - 32 MHz ``32000000L``
      - 256 Kb
      - 16 Kb
    * - ``nrf51_dk``
      - `Nordic nRF51-DK <https://developer.mbed.org/platforms/Nordic-nRF51-DK/>`_
      - nrf51822/nrf51422 ``cortex-m0``
      - 32 MHz ``32000000L``
      - 256 Kb
      - 16 Kb
    * - ``redBearLab``
      - `RedBearLab nRF51822 <https://developer.mbed.org/platforms/RedBearLab-nRF51822/>`_
      - nrf51822 ``cortex-m0``
      - 16 MHz ``16000000L``
      - 256 Kb
      - 16 Kb
    * - ``redBearLabBLENano``
      - `RedBearLab BLE Nano <https://developer.mbed.org/platforms/RedBearLab-BLE-Nano/>`_
      - nrf51822 ``cortex-m0``
      - 16 MHz ``16000000L``
      - 256 Kb
      - 16 Kb
    * - ``wallBotBLE``
      - `JKSoft Wallbot BLE <https://developer.mbed.org/platforms/JKSoft-Wallbot-BLE/>`_
      - nrf51822 ``cortex-m0``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 16 Kb
    * - ``hrm1017``
      - `Switch Science mbed HRM1017 <https://developer.mbed.org/platforms/mbed-HRM1017/>`_
      - nrf51822 ``cortex-m0``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 16 Kb


More detailed information you can find here
`nRF51 platforms with support MBED framework <http://developer.mbed.org/platforms/?tvend=11>`_.
