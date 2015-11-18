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

PlatformIO is an open-source cross-platform code builder and the missing library manager
========================================================================================

**Ready for embedded development, IDE and Continuous integration, Arduino and
MBED compatible**

*Atmel AVR & SAM, Espressif, Freescale Kinetis, Nordic nRF51, NXP LPC,
Silicon Labs EFM32, ST STM32, TI MSP430 & Tiva, Teensy, Arduino, mbed,
libOpenCM3, etc.*

.. image:: _static/platformio-logo.png
    :target: http://platformio.org

* `Website <http://platformio.org>`_
* `Web 2.0 Library Search <http://platformio.org/#!/lib>`_ |
  `Embedded Boards Explorer <http://platformio.org/#!/boards>`_
* `Project Examples <https://github.com/platformio/platformio/tree/develop/examples>`_
* `Source Code <https://github.com/platformio/platformio>`_ |
  `Issues <https://github.com/platformio/platformio/issues>`_
* `Blog <http://www.ikravets.com/category/computer-life/platformio>`_ |
  `Twitter <https://twitter.com/PlatformIO_Org>`_ |
  `Hackaday <https://hackaday.io/project/7980-platformio>`_ |
  `Facebook <https://www.facebook.com/platformio>`_ |
  `Reddit <http://www.reddit.com/r/platformio/>`_

You have **no need** to install any *IDE* or compile any tool chains. *PlatformIO*
has pre-built different development platforms and pre-configured settings for
the most popular embedded boards. For further details, please
refer to :ref:`faq_what_is_platformio`

Embedded Development. *Easier Than Ever.*
-----------------------------------------

* Colourful command-line output
* :ref:`IDE Integration <ide>` with *Arduino, Eclipse, Energia, Qt Creator,
  Sublime Text, Vim, Visual Studio*
* :ref:`ci` with *AppVeyor, Circle CI, Drone, Shippable, Travis CI*
* Built-in :ref:`Serial Port Monitor <cmd_serialports_monitor>` and
  configurable build :ref:`-flags/-options <projectconf_build_flags>`
* Pre-built tool chains, :ref:`frameworks` for the
  :ref:`Development Platforms <platforms>`

Smart Code Builder. *Fast and Reliable.*
----------------------------------------

* Reliable, automatic dependency analysis and detection of build changes
* Improved support for parallel builds
* Ability to share built files in a cache
* Lookup for external libraries which are installed via :ref:`librarymanager`

The Missing Library Manager. *It's here!*
-----------------------------------------

* Friendly Command-Line Interface
* Modern `Web 2.0 Library Search <http://platformio.org/#!/lib>`_
* Library dependency management
* Automatic library updating
* It runs on Windows, Mac OS X, and Linux (+ARM).


Contents
--------

.. toctree::
    :caption: Getting Started
    :maxdepth: 2

    demo
    installation
    quickstart
    userguide/index

.. toctree::
    :caption: Configuration
    :maxdepth: 2

    projectconf
    envvars

.. toctree::
    :caption: Instruments
    :maxdepth: 2

    Platforms & Boards <platforms/index>
    frameworks/index

.. toctree::
    :caption: Integration
    :maxdepth: 2

    librarymanager/index
    ci/index
    ide

.. toctree::
    :caption: Miscellaneous
    :maxdepth: 2

    articles
    FAQ <faq>
    history
