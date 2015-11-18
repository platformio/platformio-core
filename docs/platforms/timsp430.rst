..  Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _platform_timsp430:

Platform ``timsp430``
=====================
MSP430 microcontrollers (MCUs) from Texas Instruments (TI) are 16-bit, RISC-based, mixed-signal processors designed for ultra-low power. These MCUs offer the lowest power consumption and the perfect mix of integrated peripherals for thousands of applications.

For more detailed information please visit `vendor site <http://www.ti.com/lsds/ti/microcontrollers_16-bit_32-bit/msp/overview.page>`_.

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

    * - ``framework-arduinomsp430``
      - `Arduino Wiring-based Framework (MSP430 Core) <http://arduino.cc/en/Reference/HomePage>`_

.. warning::
    **Linux Users:** Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).

    **Windows Users:** Please check that you have correctly installed USB driver
    from board manufacturer



Frameworks
----------
.. list-table::
    :header-rows:  1

    * - Name
      - Description

    * - :ref:`framework_arduino`
      - Arduino Framework allows writing cross-platform software to control devices attached to a wide range of Arduino boards to create all kinds of creative coding, interactive objects, spaces or physical experiences.

    * - :ref:`framework_energia`
      - Energia framework enables pretty much anyone to start easily creating microcontroller-based projects and applications. Its easy-to-use libraries and functions provide developers of all experience levels to start blinking LEDs, buzzing buzzers and sensing sensors more quickly than ever before.

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

PanStamp
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``panStampNRG``
      - `PanStamp NRG 1.1 <http://www.panstamp.com/product/197/>`_
      - CC430F5137
      - 12 MHz
      - 32 Kb
      - 4 Kb

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
      - `TI LaunchPad w/ msp430f5529 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529
      - 16 MHz
      - 128 Kb
      - 1 Kb

    * - ``lpmsp430f5529_25``
      - `TI LaunchPad w/ msp430f5529 (25MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430f5529lp.html>`_
      - MSP430F5529
      - 25 MHz
      - 128 Kb
      - 1 Kb

    * - ``lpmsp430fr5739``
      - `TI FraunchPad w/ msp430fr5739 <http://www.ti.com/tool/msp-exp430fr5739>`_
      - MSP430FR5739
      - 16 MHz
      - 16 Kb
      - 1 Kb

    * - ``lpmsp430fr5969``
      - `TI LaunchPad w/ msp430fr5969 <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430fr5969.html>`_
      - MSP430FR5969
      - 8 MHz
      - 64 Kb
      - 1 Kb

    * - ``lpmsp430g2231``
      - `TI LaunchPad w/ msp430g2231 (1 MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2231
      - 1 MHz
      - 2 Kb
      - 0.125 Kb

    * - ``lpmsp430g2452``
      - `TI LaunchPad w/ msp430g2452 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2452
      - 16 MHz
      - 8 Kb
      - 0.25 Kb

    * - ``lpmsp430g2553``
      - `TI LaunchPad w/ msp430g2553 (16MHz) <http://www.ti.com/ww/en/launchpad/launchpads-msp430-msp-exp430g2.html>`_
      - MSP430G2553
      - 16 MHz
      - 16 Kb
      - 0.5 Kb
