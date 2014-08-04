..

PlatformIO: A cross-platform code builder and library manager
=============================================================

You have no need to install any *IDE* or compile any toolchains. *PlatformIO*
has pre-built different development platforms including: compiler, debugger,
flasher (for embedded) and many other useful tools.

**PlatformIO** allows developer to compile the same code with different
platforms using only one command ``platformio run``. This happens due to
``platformio.ini`` project's file (see
`default template <https://github.com/ivankravets/platformio/blob/develop/platformio/projectconftpl.ini>`_)
where you can setup different environments with specific settings: platform,
firmware uploading options, pre-built framework and many more.

Each platform consists of packages which are located in own repository.
Due to ``platformio update`` command you will have up-to-date development
instruments.


**PlatformIO** is well suited for **embedded development**. It can:

* Automatically analyse dependency
* Reliably detect build changes
* Build framework or library source code to static library
* Build *ELF* (executable and linkable firmware)
* Convert *ELF* to *HEX* or *BIN* file
* Extract *EEPROM* data
* Upload firmware to your device

It has support for many popular embedded platforms like these:

* ``atmelavr`` `Atmel AVR <http://en.wikipedia.org/wiki/Atmel_AVR>`_
  (including `Arduino <http://www.arduino.cc>`_ based boards)
* ``timsp430`` `TI MSP430 <http://www.ti.com/lsds/ti/microcontroller/16-bit_msp430/overview.page>`_
  (including `MSP430 LaunchPads <http://www.ti.com/ww/en/launchpad/launchpads-msp430.html>`_)
* ``titiva`` `TI TIVA C <http://www.ti.com/lsds/ti/microcontroller/tiva_arm_cortex/c_series/overview.page>`_
  (including `TIVA C Series LaunchPads <http://www.ti.com/ww/en/launchpad/launchpads-connected.html>`_)

.. toctree::
   :maxdepth: 2



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

