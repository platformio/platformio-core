PlatformIO
==========

.. image:: https://travis-ci.org/ivankravets/platformio.svg?branch=develop
    :target: https://travis-ci.org/ivankravets/platformio
    :alt: Build Status
.. image:: https://gemnasium.com/ivankravets/platformio.png
    :target: https://gemnasium.com/ivankravets/platformio
    :alt: Dependency Status
.. image:: https://pypip.in/version/platformio/badge.png
    :target: https://pypi.python.org/pypi/platformio/
    :alt: Latest Version
.. image:: https://pypip.in/download/platformio/badge.png
    :target: https://pypi.python.org/pypi/platformio/
    :alt: Downloads
.. image:: https://pypip.in/license/platformio/badge.png
    :target: https://pypi.python.org/pypi/platformio/
    :alt:  License

`Website + Library Search <http://platformio.ikravets.com>`_ |
`Documentation <http://docs.platformio.ikravets.com>`_ |
`Project Examples <https://github.com/ivankravets/platformio/tree/develop/examples>`_ |
`Blog <http://www.ikravets.com/category/computer-life/platformio>`_ |
`Twitter <https://twitter.com/PlatformIOTool>`_

.. image:: https://raw.githubusercontent.com/ivankravets/platformio/develop/docs/_static/platformio-logo.png
    :target: http://platformio.ikravets.com

`PlatformIO <http://platformio.ikravets.com>`_ is a cross-platform code builder
and the missing library manager.

* `Get Started <http://platformio.ikravets.com/#!/get-started>`_
* `Web 2.0 Library Search <http://platformio.ikravets.com/#!/lib>`_
* `Development Platforms <http://platformio.ikravets.com/#!/platforms>`_
* `Embedded Boards <http://platformio.ikravets.com/#!/boards>`_
* `Library Manager <http://docs.platformio.ikravets.com/en/latest/librarymanager/index.html>`_
* `User Guide <http://docs.platformio.ikravets.com/en/latest/userguide/index.html>`_
* `IDE Integration <http://docs.platformio.ikravets.com/en/latest/ide.html>`_
* `Release History <http://docs.platformio.ikravets.com/en/latest/history.html>`_

You have no need to install any *IDE* or compile any tool chains. *PlatformIO*
has pre-built different development platforms including: compiler, debugger,
uploader (for embedded boards) and many other useful tools.

**PlatformIO** allows developer to compile the same code with different
platforms using only one command
`platformio run <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_run.html>`_.
This happens due to
`Project Configuration File <http://docs.platformio.ikravets.com/en/latest/projectconf.html>`_
where you can setup different environments with specific
options: platform type, firmware uploading settings, pre-built framework
and many more.

.. image:: examples/platformio-examples.png
    :target: https://raw.githubusercontent.com/ivankravets/platformio/develop/examples/platformio-examples.png
    :alt:  Examples
    :width: 730px

**PlatformIO** is well suited for **embedded development**. It can:

* Automatically analyse dependency
* Reliably detect build changes
* Build framework or library source code to static library
* Upload firmware to your device
* Lookup for external libraries which are installed via
  `Library Manager <http://docs.platformio.ikravets.com/en/latest/librarymanager/index.html>`_

It has support for many popular embedded platforms like these:

* ``atmelavr`` `Atmel AVR <http://platformio.ikravets.com/#!/platforms/atmelavr>`_
  (including Arduino-based boards)
* ``timsp430`` `TI MSP430 <http://platformio.ikravets.com/#!/platforms/timsp430>`_
  (including MSP430 LaunchPads)
* ``titiva`` `TI TIVA C <http://platformio.ikravets.com/#!/platforms/titiva>`_
  (including TIVA C Series LaunchPads)


Licence
-------

Copyright (C) 2014 Ivan Kravets

Licenced under the MIT Licence.

