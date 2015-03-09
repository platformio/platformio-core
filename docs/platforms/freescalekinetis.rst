.. _platform_freescalekinetis:

Platform ``freescalekinetis``
=============================

`Freescale Kinetis Microcontrollers <http://www.freescale.com/webapp/sps/site/homepage.jsp?code=KINETIS>`_ is family of multiple hardware- and software-compatible ARM® Cortex®-M0+, Cortex-M4 and Cortex-M7-based MCU series. Kinetis MCUs offer exceptional low-power performance, scalability and feature integration.

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
      - See below in :ref:`freescalekinetis_frameworks`

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/ivankravets/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).


.. _freescalekinetis_frameworks:

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
    * - ``frdm_kl05z``
      - `Freescale Kinetis FRDM-KL05Z <https://developer.mbed.org/platforms/FRDM-KL05Z/>`_
      - MKL05Z32VFM4 ``cortex-m0plus``
      - 48 MHz ``48000000L``
      - 32 Kb
      - 4 Kb
    * - ``frdm_kl25z``
      - `Freescale Kinetis FRDM-KL25Z <https://developer.mbed.org/platforms/KL25Z/>`_
      - MKL25Z128VLK4 ``cortex-m0plus``
      - 48 MHz ``48000000L``
      - 128 Kb
      - 16 Kb
    * - ``frdm_kl46z``
      - `Freescale Kinetis FRDM-KL46Z <https://developer.mbed.org/platforms/FRDM-KL46Z/>`_
      - MKL46Z256Vll4 ``cortex-m0plus``
      - 48 MHz ``48000000L``
      - 256 Kb
      - 32 Kb
    * - ``frdm_k22f``
      - `Freescale Kinetis FRDM-K22F <https://developer.mbed.org/platforms/FRDM-K22F/>`_
      - MK22FN512VLH12 ``cortex-m4``
      - 120 MHz ``120000000L``
      - 512 Kb
      - 128 Kb
    * - ``frdm_k64f``
      - `Freescale Kinetis FRDM-K64F <https://developer.mbed.org/platforms/FRDM-K64F/>`_
      - MK64fN1M0VLL12 ``cortex-m4``
      - 120 MHz ``120000000L``
      - 1 Mb
      - 256 Kb
    * - ``frdm_k20d50m``
      - `Freescale Kinetis FRDM-K20D50M <https://developer.mbed.org/platforms/FRDM-K20D50M/>`_
      - MK20DX128VLH5 ``cortex-m4``
      - 48 MHz ``48000000L``
      - 128 Kb
      - 16 Kb


More detailed information you can find here
`Freescale Kinetis platforms with support MBED framework <https://developer.mbed.org/platforms/?tvend=4>`_.
