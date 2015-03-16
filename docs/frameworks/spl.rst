.. _framework_spl:

Framework ``spl``
=================
The ST Standard Peripheral Library provides a set of functions for handling the peripherals on the STM32 Cortex-M3 family. The idea is to save the user (the new user, in particular) having to deal directly with the registers.

For more detailed information please visit `vendor site <http://www.st.com/web/en/catalog/tools/FM147/CL1794/SC961/SS1743?sc=stm32embeddedsoftware>`_.

.. contents::

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Web 2.0 <http://platformio.org/#!/boards>`_ site
    * For more detailed ``board`` information please scroll tables below by horizontal.

ST
~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``disco_f303vc``
      - `STM32F3DISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF254044>`_
      - STM32F303VCT6
      - 72 MHz
      - 256 Kb
      - 48 Kb

    * - ``disco_f407vg``
      - `STM32F4DISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF252419>`_
      - STM32F407VGT6
      - 168 MHz
      - 1024 Kb
      - 128 Kb

    * - ``disco_l152rb``
      - `STM32LDISCOVERY <http://www.st.com/web/catalog/tools/FM116/SC959/SS1532/LN1848/PF258515>`_
      - STM32L152RBT6
      - 32 MHz
      - 128 Kb
      - 16 Kb
