PlatformIO
==========

.. image:: https://travis-ci.org/platformio/platformio.svg?branch=develop
    :target: https://travis-ci.org/platformio/platformio
    :alt: Travis.CI Build Status
.. image:: https://ci.appveyor.com/api/projects/status/dku0h2rutfj0ctls/branch/develop?svg=true
    :target: https://ci.appveyor.com/project/ivankravets/platformio
    :alt: AppVeyor.CI Build Status
.. image:: https://api.shippable.com/projects/555b0ceeedd7f2c052f3c2d0/badge?branchName=develop
    :target: https://app.shippable.com/projects/555b0ceeedd7f2c052f3c2d0
    :alt: Shippable Build Status
.. image:: https://circleci.com/gh/platformio/platformio/tree/develop.svg?style=svg
    :target: https://circleci.com/gh/platformio/platformio/tree/develop
    :alt: Circle.CI Build Status
.. image:: https://gemnasium.com/platformio/platformio.png
    :target: https://gemnasium.com/platformio/platformio
    :alt: Dependency Status
.. image:: https://img.shields.io/pypi/v/platformio.svg
    :target: https://pypi.python.org/pypi/platformio/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/dm/platformio.svg
    :target: https://pypi.python.org/pypi/platformio/
    :alt: Downloads
.. image:: https://img.shields.io/pypi/l/platformio.svg
    :target: https://pypi.python.org/pypi/platformio/
    :alt:  License
.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/platformio/platformio
   :target: https://gitter.im/platformio/platformio
.. image:: https://www.openhub.net/p/platformio/widgets/project_thin_badge.gif
   :target: https://www.openhub.net/p/platformio

`Website + Library Search <http://platformio.org>`_ |
`Documentation <http://docs.platformio.org>`_ |
`Project Examples <https://github.com/platformio/platformio/tree/develop/examples>`_ |
`Blog <http://www.ikravets.com/category/computer-life/platformio>`_ |
`Reddit <http://www.reddit.com/r/platformio/>`_ |
`Twitter <https://twitter.com/PlatformIO_Org>`_

*Atmel AVR & SAM, Espressif, Freescale Kinetis, Nordic nRF51, NXP LPC,
Silicon Labs EFM32, ST STM32, TI MSP430 & Tiva, Teensy, Arduino, mbed,
libOpenCM3, etc.*

.. image:: https://raw.githubusercontent.com/platformio/platformio/develop/docs/_static/platformio-logo.png
    :target: http://platformio.org

`PlatformIO <http://platformio.org>`_ is a cross-platform code builder
and the missing library manager.

* `Get Started <http://platformio.org/#!/get-started>`_
* `Web 2.0 Library Search <http://platformio.org/#!/lib>`_
* `Development Platforms <http://platformio.org/#!/platforms>`_
* `Frameworks <http://platformio.org/#!/frameworks>`_
* `Embedded Boards Explorer <http://platformio.org/#!/boards>`_
* `Library Manager <http://docs.platformio.org/en/latest/librarymanager/index.html>`_
* `User Guide <http://docs.platformio.org/en/latest/userguide/index.html>`_
* `Continuous Integration <http://docs.platformio.org/en/latest/ci/index.html>`_
* `IDE Integration <http://docs.platformio.org/en/latest/ide.html>`_
* `Articles about us <http://docs.platformio.org/en/latest/articles.html>`_
* `FAQ <http://docs.platformio.org/en/latest/faq.html>`_
* `Release History <http://docs.platformio.org/en/latest/history.html>`_

You have **no need** to install any *IDE* or compile any tool chains. *PlatformIO*
has pre-built different development platforms and pre-configured settings for
the most popular embedded boards. For further details, please
refer to `What is PlatformIO? <http://docs.platformio.org/en/latest/faq.html#what-is-platformio>`_

Use whenever. *Run everywhere.*
-------------------------------
*PlatformIO* is written in pure *Python* and **doesn't depend** on any
additional libraries/tools from an operation system. It allows you to use
*PlatformIO* beginning from *PC (Mac, Linux, Win)* and ending with credit-card
sized computers (`Raspberry Pi <http://www.raspberrypi.org>`_,
`BeagleBone <http://beagleboard.org>`_,
`CubieBoard <http://cubieboard.org>`_).

Embedded Development. *Easier Than Ever.*
-----------------------------------------
*PlatformIO* is well suited for embedded development and has pre-configured
settings for most popular `Embedded Boards <http://platformio.org/#!/boards>`_.

* Colourful `command-line output <https://raw.githubusercontent.com/platformio/platformio/develop/examples/platformio-examples.png>`_
* Built-in `Serial Port Monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_
* Configurable `build -flags/-options <http://docs.platformio.org/en/latest/projectconf.html#build-flags>`_
* Automatic **firmware uploading**
* Integration with `development environments (IDE) <http://docs.platformio.org/en/latest/ide.html>`_
* Ready for **Cloud Compiling** and `Continuous Integration <http://docs.platformio.org/en/latest/ci/index.html>`_
* Pre-built tool chains, frameworks for the popular `Hardware Platforms <http://platformio.org/#!/platforms>`_

.. image:: https://raw.githubusercontent.com/platformio/platformio-web/develop/app/images/platformio-embedded-development.png
    :target: http://platformio.org
    :alt:  PlatformIO Embedded Development Process

The Missing Library Manager. *It's here!*
-----------------------------------------
*PlatformIO Library Manager* is the missing library manager for development
platforms which allows you to organize and have up-to-date external libraries.

* Friendly `Command-Line Interface <http://docs.platformio.org/en/latest/librarymanager/index.html>`_
* Modern `Web 2.0 Library Search <http://platformio.org/#!/lib>`_
* Open Source `Library Registry API <https://github.com/platformio/platformio-api>`_
* Library Crawler based on `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`_
  specification
* Library **dependency management**
* Automatic library updating

.. image:: https://raw.githubusercontent.com/platformio/platformio-web/develop/app/images/platformio-library-manager.png
    :target: http://platformio.org
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
* Lookup for external libraries which are installed via `Library Manager <http://docs.platformio.org/en/latest/librarymanager/index.html>`_

.. image:: https://raw.githubusercontent.com/platformio/platformio-web/develop/app/images/platformio-scons-builder.png
    :target: http://platformio.org
    :alt:  PlatformIO Code Builder Architecture

Single source code. *Multiple platforms.*
-----------------------------------------
*PlatformIO* allows developer to compile the same code with different
development platforms using the *Only One Command*
`platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`_.
This happens due to
`Project Configuration File (platformio.ini) <http://docs.platformio.org/en/latest/projectconf.html>`_
where you can setup different environments with specific options (platform
type, firmware uploading settings, pre-built framework, build flags and many
more).

It has support for the most popular embedded platforms:

* `Atmel AVR <http://platformio.org/#!/platforms/atmelavr>`_
* `Atmel SAM <http://platformio.org/#!/platforms/atmelsam>`_
* `Espressif <http://platformio.org/#!/platforms/espressif>`_
* `Freescale Kinetis <http://platformio.org/#!/platforms/freescalekinetis>`_
* `Nordic nRF51 <http://platformio.org/#!/platforms/nordicnrf51>`_
* `NXP LPC <http://platformio.org/#!/platforms/nxplpc>`_
* `ST STM32 <http://platformio.org/#!/platforms/ststm32>`_
* `Silicon Labs EFM32 <http://platformio.org/#!/platforms/siliconlabsefm32>`_
* `Teensy <http://platformio.org/#!/platforms/teensy>`_
* `TI MSP430 <http://platformio.org/#!/platforms/timsp430>`_
* `TI TIVA C <http://platformio.org/#!/platforms/titiva>`_

Frameworks:

* `Arduino <http://platformio.org/#!/frameworks/arduino>`_
* `CMSIS <http://platformio.org/#!/frameworks/cmsis>`_
* `libOpenCM3 <http://platformio.org/#!/frameworks/libopencm3>`_
* `Energia <http://platformio.org/#!/frameworks/energia>`_
* `SPL <http://platformio.org/#!/frameworks/spl>`_
* `mbed <http://platformio.org/#!/frameworks/mbed>`_


Licence
-------

Copyright (C) 2014-2015 Ivan Kravets

Licenced under the MIT Licence.
