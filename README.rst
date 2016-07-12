PlatformIO
==========

.. image:: https://travis-ci.org/platformio/platformio.svg?branch=develop
    :target: https://travis-ci.org/platformio/platformio
    :alt: Travis.CI Build Status
.. image:: https://ci.appveyor.com/api/projects/status/dku0h2rutfj0ctls/branch/develop?svg=true
    :target: https://ci.appveyor.com/project/ivankravets/platformio
    :alt: AppVeyor.CI Build Status
.. image:: https://requires.io/github/platformio/platformio/requirements.svg?branch=develop
    :target: https://requires.io/github/platformio/platformio/requirements/?branch=develop
    :alt: Requirements Status
.. image:: https://img.shields.io/pypi/v/platformio.svg
    :target: https://pypi.python.org/pypi/platformio/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/l/platformio.svg
    :target: https://pypi.python.org/pypi/platformio/
    :alt:  License
.. image:: https://img.shields.io/community/PlatformIO.png
   :alt: Community Forums
   :target: https://community.platformio.org
.. image:: https://img.shields.io/donate/PlatformIO.png?color=yellow
   :alt: Donate for PlatformIO.Org
   :target: http://platformio.org/donate


`Home <http://platformio.org>`_ |
`IDE <http://platformio.org/platformio-ide>`_ |
`Project Examples <https://github.com/platformio/platformio-examples/tree/develop>`_ |
`Docs <http://docs.platformio.org>`_ |
`Twitter <https://twitter.com/PlatformIO_Org>`_ |
`Facebook <https://www.facebook.com/platformio>`_ |
`Hackaday <https://hackaday.io/project/7980-platformio>`_ |
`Bintray <https://bintray.com/platformio>`_ |
`Community <https://community.platformio.org>`_ |
`Donate <http://platformio.org/donate>`_ |
`Contact Us <http://platformio.org/contact>`_

.. image:: https://raw.githubusercontent.com/platformio/platformio/develop/docs/_static/platformio-logo.png
    :target: http://platformio.org

`PlatformIO <http://platformio.org>`_ is an open source ecosystem for IoT
development. Cross-platform build system and library manager. Continuous and
IDE integration. Arduino and MBED compatible. Ready for Cloud compiling.

* **PlatformIO IDE** - The next-generation integrated development environment for IoT.
  C/C++ Intelligent Code Completion and Smart Code Linter for the super-fast coding.
  Multi-projects workflow with Multiple Panes. Themes Support with dark and light colors.
  Built-in Terminal with PlatformIO CLI tool and support for the powerful Serial Port Monitor.
  All advanced instruments without leaving your favourite development environment.
* **Development Platforms** - Embedded and Desktop development platforms with
  pre-built toolchains, debuggers, uploaders and frameworks which work under
  popular host OS: Mac, Windows, Linux (+ARM)
* **Embedded Boards** - Rapid Embedded Programming, IDE and Continuous
  Integration in a few steps with PlatformIO thanks to built-in project
  generator for the most popular embedded boards and IDE
* **Library Manager** - Hundreds Popular Libraries are organized into single
  Web 2.0 platform: list by categories, keywords, authors, compatible
  platforms and frameworks; learn via examples; be up-to-date with the latest
  version.

*Atmel AVR & SAM, Espressif, Freescale Kinetis, Intel ARC32, Lattice iCE40,
Microchip PIC32, Nordic nRF51, NXP LPC, Silicon Labs EFM32, ST STM32,
TI MSP430 & Tiva, Teensy, Arduino, mbed, libOpenCM3, etc.*

.. image:: https://raw.githubusercontent.com/platformio/platformio/develop/docs/_static/platformio-demo-wiring.gif
    :target: http://platformio.org

* `PlatformIO IDE <http://platformio.org/platformio-ide>`_
* `Get Started <http://platformio.org/get-started>`_
* `Web 2.0 Library Search <http://platformio.org/lib>`_
* `Development Platforms <http://platformio.org/platforms>`_
* `Frameworks <http://platformio.org/frameworks>`_
* `Embedded Boards Explorer <http://platformio.org/boards>`_
* `Library Manager <http://docs.platformio.org/en/latest/librarymanager/index.html>`_
* `User Guide <http://docs.platformio.org/en/latest/userguide/index.html>`_
* `Continuous Integration <http://docs.platformio.org/en/latest/ci/index.html>`_
* `IDE Integration <http://docs.platformio.org/en/latest/ide.html>`_
* `Articles about us <http://docs.platformio.org/en/latest/articles.html>`_
* `FAQ <http://docs.platformio.org/en/latest/faq.html>`_
* `Release Notes <http://docs.platformio.org/en/latest/history.html>`_

Use whenever. *Run everywhere.*
-------------------------------
*PlatformIO* is written in pure *Python* and **doesn't depend** on any
additional libraries/tools from an operating system. It allows you to use
*PlatformIO* beginning from *PC (Mac, Linux, Win)* and ending with credit-card
sized computers (`Raspberry Pi <http://www.raspberrypi.org>`_,
`BeagleBone <http://beagleboard.org>`_,
`CubieBoard <http://cubieboard.org>`_).

Embedded Development. *Easier Than Ever.*
-----------------------------------------
*PlatformIO* is well suited for embedded development and has pre-configured
settings for most popular `Embedded Boards <http://platformio.org/boards>`_.

* Colourful `command-line output <https://raw.githubusercontent.com/platformio/platformio/develop/examples/platformio-examples.png>`_
* `IDE Integration <http://docs.platformio.org/en/latest/ide.html>`_ with
  *Arduino, Atom, Eclipse, Emacs, Energia, Qt Creator, Sublime Text, Vim, Visual Studio*
* Cloud compiling and `Continuous Integration <http://docs.platformio.org/en/latest/ci/index.html>`_
  with *AppVeyor, Circle CI, Drone, Shippable, Travis CI*
* Built-in `Serial Port Monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ and configurable
  `build -flags/-options <http://docs.platformio.org/en/latest/projectconf.html#build-flags>`_
* Automatic **firmware uploading**
* Pre-built tool chains, frameworks for the popular `Hardware Platforms <http://platformio.org/platforms>`_

.. image:: https://raw.githubusercontent.com/platformio/platformio-web/develop/app/images/platformio-embedded-development.png
    :target: http://platformio.org
    :alt:  PlatformIO Embedded Development Process

The Missing Library Manager. *It's here!*
-----------------------------------------
*PlatformIO Library Manager* is the missing library manager for development
platforms which allows you to organize and have up-to-date external libraries.

* Friendly `Command-Line Interface <http://docs.platformio.org/en/latest/librarymanager/index.html>`_
* Modern `Web 2.0 Library Search <http://platformio.org/lib>`_
* Open Source `Library Registry API <https://github.com/platformio/platformio-api>`_
* Library Crawler based on `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`_
  specification
* Library **dependency management**
* Automatic library updating

.. image:: https://raw.githubusercontent.com/platformio/platformio-web/develop/app/images/platformio-library-manager.png
    :target: http://platformio.org
    :alt:  PlatformIO Library Manager Architecture

Smart Build System. *Fast and Reliable.*
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
    :alt:  PlatformIO Build System Architecture

Single source code. *Multiple platforms.*
-----------------------------------------
*PlatformIO* allows the developer to compile the same code with different
development platforms using only *One Command*
`platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`_.
This happens due to
`Project Configuration File (platformio.ini) <http://docs.platformio.org/en/latest/projectconf.html>`_
where you can setup different environments with specific options (platform
type, firmware uploading settings, pre-built framework, build flags and many
more).

It has support for the most popular embedded platforms:

* `Atmel AVR <http://platformio.org/platforms/atmelavr>`_
* `Atmel SAM <http://platformio.org/platforms/atmelsam>`_
* `Espressif <http://platformio.org/platforms/espressif>`_
* `Freescale Kinetis <http://platformio.org/platforms/freescalekinetis>`_
* `Intel ARC32 <http://platformio.org/platforms/intel_arc32>`_
* `Lattice iCE40 <http://platformio.org/platforms/lattice_ice40>`_
* `Microchip PIC32 <http://platformio.org/platforms/microchippic32>`_
* `Nordic nRF51 <http://platformio.org/platforms/nordicnrf51>`_
* `NXP LPC <http://platformio.org/platforms/nxplpc>`_
* `ST STM32 <http://platformio.org/platforms/ststm32>`_
* `Silicon Labs EFM32 <http://platformio.org/platforms/siliconlabsefm32>`_
* `Teensy <http://platformio.org/platforms/teensy>`_
* `TI MSP430 <http://platformio.org/platforms/timsp430>`_
* `TI TIVA C <http://platformio.org/platforms/titiva>`_

Frameworks:

* `Arduino <http://platformio.org/frameworks/arduino>`_
* `CMSIS <http://platformio.org/frameworks/cmsis>`_
* `Energia <http://platformio.org/frameworks/energia>`_
* `libOpenCM3 <http://platformio.org/frameworks/libopencm3>`_
* `mbed <http://platformio.org/frameworks/mbed>`_
* `Simba <http://platformio.org/frameworks/simba>`_
* `SPL <http://platformio.org/frameworks/spl>`_
* `WiringPi <http://platformio.org/frameworks/wiringpi>`_

For further details, please refer to `What is PlatformIO? <http://docs.platformio.org/en/latest/faq.html#what-is-platformio>`_

Contributing
------------

See `contributing guidelines <https://github.com/platformio/platformio/blob/develop/CONTRIBUTING.md>`_.

License
-------

Copyright 2014-2016 Ivan Kravets <me@ikravets.com>

The PlatformIO is licensed under the permissive Apache 2.0 license,
so you can use it in both commercial and personal projects with confidence.
