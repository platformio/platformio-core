..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _platform_lattice_ice40:

Platform ``lattice_ice40``
==========================
The iCE40 family of ultra-low power, non-volatile FPGAs has five devices with densities ranging from 384 to 7680 Look-Up Tables (LUTs). In addition to LUT-based,low-cost programmable logic, these devices feature Embedded Block RAM (EBR), Non-volatile Configuration Memory (NVCM) and Phase Locked Loops (PLLs). These features allow the devices to be used in low-cost, high-volume consumer and system applications.

For more detailed information please visit `vendor site <http://www.latticesemi.com/Products/FPGAandCPLD/iCE40.aspx>`_.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Contents

    * - ``toolchain-icestorm``
      - `Tools for analyzing and creating bitstream files for FPGA IceStorm <http://www.clifford.at/icestorm/>`_

    * - ``toolchain-iverilog``
      - `Verilog simulation and synthesis tool <http://iverilog.icarus.com>`_

.. warning::
    **Linux Users**:

    * Ubuntu/Debian users may need to add own "username" to the "dialout"
      group if they are not "root", doing this issuing a
      ``sudo usermod -a -G dialout yourusername``.
    * Install "udev" rules file `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_
      (an instruction is located in the file).
    * Raspberry Pi users, please read this article
      `Enable serial port on Raspberry Pi <https://hallard.me/enable-serial-port-on-raspberry-pi/>`__.


    **Windows Users:** Please check that you have correctly installed USB
    driver from board manufacturer



Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/boards>`_
    * For more detailed ``board`` information please scroll tables below by
      horizontal.

FPGAwars
~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``icezum``
      - `IceZUM Alhambra FPGA <https://github.com/FPGAwars/icezum/wiki>`_
      - ICE40-HX1K-TQ144
      - 12 MHz
      - 32 Kb
      - 32 Kb

Lattice
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``icestick``
      - `Lattice iCEstick FPGA Evaluation Kit <http://www.latticesemi.com/icestick>`_
      - ICE40-HX1K-TQ144
      - 12 MHz
      - 32 Kb
      - 32 Kb
