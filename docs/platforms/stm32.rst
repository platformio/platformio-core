.. _platform_stm32:

Platform ``stm32``
==================

`The STM32 family of 32-bit Flash microcontrollers <http://www.st.com/web/en/catalog/mmc/FM141/SC1169?sc=stm32>`_ based on the ARM® Cortex®-M processor is designed to offer new degrees of freedom to MCU users. It offers a 32-bit product range that combines very high performance, real-time capabilities, digital signal processing, and low-power, low-voltage operation, while maintaining full integration and ease of development.

The unparalleled and large range of STM32 devices, based on an industry-standard core and accompanied by a vast choice of tools and software, makes this family of products the ideal choice, both for small projects and for entire platform decisions.

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
    * - ``tool-stlink``
      - uploader
      - `Flash Programmer <https://github.com/texane/stlink>`_
    * - ``framework-cmsis``
      -
      - See below in :ref:`stm32_frameworks`
    * - ``framework-spl``
      -
      - See below in :ref:`stm32_frameworks`
    * - ``framework-opencm3``
      -
      - See below in :ref:`stm32_frameworks`

.. note::
    You can install ``stm32`` platform with these packages
    via :ref:`cmd_install` command.


.. _stm32_frameworks:

Frameworks
----------

.. list-table::
    :header-rows:  1

    * - Type ``framework``
      - Name
      - Reference
    * - ``cmsis``
      - Vendor-independent hardware abstraction layer for the Cortex-M processor series
      - `Documentation <http://www.arm.com/products/processors/cortex-m/cortex-microcontroller-software-interface-standard.php>`__
    * - ``spl``
      - Standard Peripheral Library for STM32 MCUs
      - `Documentation <http://www.st.com/web/catalog/tools/FM147/CL1794/SC961/SS1743/PF257890>`__
    * - ``opencm3``
      - libOpenCM3 Framework
      - `Documentation <http://www.libopencm3.org>`__


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
    * - ``stm32ldiscovery``
      - `Discovery kit for STM32L151/152 line <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/PF250990?sc=internet/evalboard/product/250990.jsp>`_
      - stm32l152rbt6 ``cortex-m3``
      - 32 MHz ``32000000L``
      - 128 Kb
      - 16 Kb
    * - ``stm32f3discovery``
      - `Discovery kit for STM32F303xx microcontrollers
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/PF254044>`_
      - stm32f303vct6 ``cortex-m4``
      - 72 MHz ``72000000L``
      - 256 Kb
      - 48 Kb
    * - ``stm32f4discovery``
      - `Discovery kit for STM32F407/417 lines
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/PF252419>`_
      - stm32f407vgt6 ``cortex-m4``
      - 168 Mhz ``168000000L``
      - 1 Mb
      - 192 Kb

More detailed information you can find here
`STM32 Discovery kits <http://www.st.com/web/en/catalog/tools/FM116/SC959/SS1532/LN1848?icmp=ln1848_pron_pr-stm32f446_dec2014&sc=stm32discovery-pr>`_.
