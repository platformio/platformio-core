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

You have **no need** to install any *IDE* or compile any tool chains. *PlatformIO*
has pre-built different development platforms including: compiler, debugger,
uploader (for embedded boards) and many other useful tools.

Use whenever. *Run everywhere.*
-------------------------------
*PlatformIO* is written in pure *Python* and **doesn't depend** on any
additional libraries/tools from an operation system. It allows you to use
*PlatformIO* beginning from *PC (Mac, Linux, Win)* and ending with credit-card
sized computers (like *Raspberry Pi*).

Embedded Development. *Easier Than Ever.*
-----------------------------------------
*PlatformIO* is well suited for embedded development and has pre-configured
settings for most popular `Embedded Boards <http://platformio.ikravets.com/#!/boards>`_.

* Colourful `command-line output <https://raw.githubusercontent.com/ivankravets/platformio/develop/examples/platformio-examples.png>`_
* Built-in `Serial Port Monitor <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_
* Configurable `build -flags/-options <http://docs.platformio.ikravets.com/en/latest/projectconf.html#build-flags>`_
* Automatic **firmware uploading**
* Integration with `development environments (IDE) <http://docs.platformio.ikravets.com/en/latest/ide.html>`_
* Ready for **cloud compilers**
* Pre-built tool chains, frameworks for the popular `Hardware Platforms <http://platformio.ikravets.com/#!/platforms>`_

.. image:: https://raw.githubusercontent.com/ivankravets/platformio-web/develop/app/images/platformio-embedded-development.png
    :target: http://platformio.ikravets.com
    :alt:  PlatformIO Embedded Development Process

The Missing Library Manager. *It's here!*
-----------------------------------------
*PlatformIO Library Manager* is the missing library manager for development
platforms which allows you to organize and have up-to-date external libraries.

* Friendly `Command-Line Interface <http://docs.platformio.ikravets.com/en/latest/librarymanager/index.html>`_
* Modern `Web 2.0 Library Search <http://platformio.ikravets.com/#!/lib>`_
* Open Source `Library Registry API <https://github.com/ivankravets/platformio-api>`_
* Library Crawler based on `library.json <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html>`_
  specification
* Library **dependency management**
* Automatic library updating

.. image:: https://raw.githubusercontent.com/ivankravets/platformio-web/develop/app/images/platformio-library-manager.png
    :target: http://platformio.ikravets.com
    :alt:  PlatformIO Library Manager Architecture

Smart Code Builder. *Fast and Reliable.*
----------------------------------------
*PlatformIO Code Builder* is built-on a next-generation software construction
tool named `SCons <http://www.scons.org/>`_. Think of *SCons* as an improved,
cross-platform substitute for the classic *Make* utility.

* Reliable, automatic *dependency analysis*
* Reliable detection of *build changes*
* Improved support for *parallel builds*
* Ability to share *built files in a cache*
* Lookup for external libraries which are installed via `Library Manager <http://docs.platformio.ikravets.com/en/latest/librarymanager/index.html>`_

.. image:: https://raw.githubusercontent.com/ivankravets/platformio-web/develop/app/images/platformio-scons-builder.png
    :target: http://platformio.ikravets.com
    :alt:  PlatformIO Code Builder Architecture

Single source code. *Multiple platforms.*
-----------------------------------------
*PlatformIO* allows developer to compile the same code with different
development platforms using the *Only One Command*
`platformio run <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_run.html>`_.
This happens due to
`Project Configuration File (platformio.ini) <http://docs.platformio.ikravets.com/en/latest/projectconf.html>`_
where you can setup different environments with specific options (platform
type, firmware uploading settings, pre-built framework, build flags and many
more).

It has support for many popular embedded platforms like these:

* ``atmelavr`` `Atmel AVR <http://platformio.ikravets.com/#!/platforms/atmelavr>`_
  (including *Arduino*-based boards, *Microduino, Raspduino, Teensy*)
* ``timsp430`` `TI MSP430 <http://platformio.ikravets.com/#!/platforms/timsp430>`_
  (including *MSP430* LaunchPads)
* ``titiva`` `TI TIVA C <http://platformio.ikravets.com/#!/platforms/titiva>`_
  (including *TIVA C* Series LaunchPads)


Licence
-------

Copyright (C) 2014 Ivan Kravets

Licenced under the MIT Licence.
