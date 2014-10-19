PlatformIO: A cross-platform code builder and library manager for Arduino, MSP430, ARM
======================================================================================

`Website + Library Search <http://platformio.ikravets.com>`_ |
`Project Examples <https://github.com/ivankravets/platformio/tree/develop/examples>`_ |
`Source Code <https://github.com/ivankravets/platformio>`_ |
`Bugs/Questions <https://github.com/ivankravets/platformio/issues>`_ |
`Blog <http://www.ikravets.com/category/computer-life/platformio>`_ |
`Twitter <https://twitter.com/smartanthill>`_

You have no need to install any *IDE* or compile any tool chains. *PlatformIO*
has pre-built different development platforms including: compiler, debugger,
uploader (for embedded) and many other useful tools.

**PlatformIO** allows developer to compile the same code with different
platforms using only one command :ref:`cmd_run`. This happens due to
:ref:`projectconf` where you can setup different environments with specific
options: platform type, firmware uploading settings, pre-built framework
and many more.

Each platform consists of packages which are located in own repository.
Due to :ref:`cmd_update` command you will have up-to-date development
instruments.

**PlatformIO** is well suited for **embedded development**. It can:

* Automatically analyse dependency
* Reliably detect build changes
* Build framework or library source code to static library
* Build *ELF* (executable and linkable firmware)
* Convert *ELF* to *HEX* or *BIN* file
* Extract *EEPROM* data
* Upload firmware to your device


Contents
--------

.. toctree::
    :maxdepth: 2

    quickstart
    installation
    projectconf
    platforms/index
    librarymanager/index
    userguide/index
    ide
    history
