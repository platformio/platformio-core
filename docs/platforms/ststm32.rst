.. _platform_ststm32:

Platform ``ststm32``
====================

`The STM32 family of 32-bit Flash MCUs <http://www.st.com/web/en/catalog/mmc/FM141/SC1169?sc=stm32>`_ based on the ARM® Cortex®-M processor is designed to offer new degrees of freedom to MCU users. It offers a 32-bit product range that combines very high performance, real-time capabilities, digital signal processing, and low-power, low-voltage operation, while maintaining full integration and ease of development.

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
      - `STLink <https://github.com/texane/stlink>`_
    * - ``framework-cmsis``
      -
      - See below in :ref:`ststm32_frameworks`
    * - ``framework-spl``
      -
      - See below in :ref:`ststm32_frameworks`
    * - ``framework-opencm3``
      -
      - See below in :ref:`ststm32_frameworks`
    * - ``framework-mbed``
      -
      - See below in :ref:`ststm32_frameworks`

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).


.. _ststm32_frameworks:

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
      - Standard Peripheral Library for ST STM32 MCUs
      - `Documentation <http://www.st.com/web/catalog/tools/FM147/CL1794/SC961/SS1743/PF257890>`__
    * - ``opencm3``
      - libOpenCM3 Framework
      - `Documentation <http://www.libopencm3.org>`__
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
    * - ``disco_l152rb``
      - `STM32LDISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF258515>`_
      - STM32L152rbt6 ``cortex-m3``
      - 32 MHz ``32000000L``
      - 128 Kb
      - 16 Kb
    * - ``disco_f303vc``
      - `STM32F3DISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF254044>`_
      - STM32F303vct6 ``cortex-m4``
      - 72 MHz ``72000000L``
      - 256 Kb
      - 48 Kb
    * - ``disco_f407vg``
      - `STM32F4DISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF252419>`_
      - STM32F407vgt6 ``cortex-m4``
      - 168 Mhz ``168000000L``
      - 1 Mb
      - 192 Kb
    * - ``disco_f100rb``
      - `STM32VLDISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF250863>`_
      - STM32F100rbt6 ``cortex-m3``
      - 24 Mhz ``24000000L``
      - 128 Kb
      - 8 Kb
    * - ``disco_f051r8``
      - `STM32F0DISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF253215>`_
      - STM32F051r8t6 ``cortex-m0``
      - 48 Mhz ``48000000L``
      - 64 Kb
      - 8 Kb
    * - ``disco_f334c8``
      - `32F3348DISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF260318>`_
      - STM32F334c8t6 ``cortex-m4``
      - 72 Mhz ``72000000L``
      - 64 Kb
      - 16 Kb
    * - ``disco_f401vc``
      - `32F401CDISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF259098>`_
      - STM32F401vct6 ``cortex-m4``
      - 84 Mhz ``84000000L``
      - 256 Kb
      - 64 Kb
    * - ``disco_f429zi``
      - `32F429IDISCOVERY
        <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF259090>`_
      - STM32F429zit6 ``cortex-m4``
      - 180 Mhz ``180000000L``
      - 2 Mb
      - 256 Kb
    * - ``nucleo_f030r8``
      - `ST Nucleo F030R8
        <https://developer.mbed.org/platforms/ST-Nucleo-F030R8/>`_
      - STM32F030r8t6 ``cortex-m0``
      - 48 Mhz ``48000000L``
      - 64 Kb
      - 8 Kb
    * - ``nucleo_f070rb``
      - `ST Nucleo F070RB
        <https://developer.mbed.org/platforms/ST-Nucleo-F070RB/>`_
      - STM32F070rbt6 ``cortex-m0``
      - 48 Mhz ``48000000L``
      - 128 Kb
      - 16 Kb
    * - ``nucleo_f072rb``
      - `ST Nucleo F072RB
        <https://developer.mbed.org/platforms/ST-Nucleo-F072RB/>`_
      - STM32F072rbt6 ``cortex-m0``
      - 48 Mhz ``48000000L``
      - 128 Kb
      - 16 Kb
    * - ``nucleo_f091rc``
      - `ST Nucleo F091RC
        <https://developer.mbed.org/platforms/ST-Nucleo-F091RC/>`_
      - STM32F091rct6 ``cortex-m0``
      - 48 Mhz ``48000000L``
      - 256 Kb
      - 32 Kb
    * - ``nucleo_f103rb``
      - `ST Nucleo F103RB
        <https://developer.mbed.org/platforms/ST-Nucleo-F103RB/>`_
      - STM32F103rbt6 ``cortex-m3``
      - 72 Mhz ``72000000L``
      - 128 Kb
      - 20 Kb
    * - ``nucleo_f302r8``
      - `ST Nucleo F302R8
        <https://developer.mbed.org/platforms/ST-Nucleo-F302R8/>`_
      - STM32F302r8t6 ``cortex-m4``
      - 72 Mhz ``72000000L``
      - 64 Kb
      - 16 Kb
    * - ``nucleo_f334r8``
      - `ST Nucleo F334R8
        <https://developer.mbed.org/platforms/ST-Nucleo-F334R8/>`_
      - STM32F334r8t6 ``cortex-m4``
      - 72 Mhz ``72000000L``
      - 64 Kb
      - 16 Kb
    * - ``nucleo_f401re``
      - `ST Nucleo F401RE
        <https://developer.mbed.org/platforms/ST-Nucleo-F401RE/>`_
      - STM32F401ret6 ``cortex-m4``
      - 84 Mhz ``84000000L``
      - 512 Kb
      - 96 Kb
    * - ``nucleo_f411re``
      - `ST Nucleo F411RE
        <https://developer.mbed.org/platforms/ST-Nucleo-F411RE/>`_
      - STM32F411ret6 ``cortex-m4``
      - 100 Mhz ``100000000L``
      - 512 Kb
      - 128 Kb
    * - ``nucleo_l053r8``
      - `ST Nucleo L053R8
        <https://developer.mbed.org/platforms/ST-Nucleo-L053R8/>`_
      - STM32L053r8t6 ``cortex-m0``
      - 48 Mhz ``48000000L``
      - 64 Kb
      - 8 Kb
    * - ``nucleo_l152re``
      - `ST Nucleo L152RE
        <https://developer.mbed.org/platforms/ST-Nucleo-L152RE/>`_
      - STM32L152ret6 ``cortex-m3``
      - 32 Mhz ``32000000L``
      - 512 Kb
      - 80 Kb

More detailed information you can find here
`STM32 Discovery kits <http://www.st.com/web/en/catalog/tools/FM116/SC959/SS1532/LN1848?icmp=ln1848_pron_pr-stm32f446_dec2014&sc=stm32discovery-pr>`_ and here 
`ST Nucleo boards with MBED support <https://developer.mbed.org/platforms/?tvend=10>`_.
