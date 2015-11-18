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

.. _cmd_platforms_show:

platformio platforms show
=========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platforms show PLATFORM


Description
-----------

Show details about the installed :ref:`Platforms <platforms>`


Examples
--------

.. code-block:: bash

    $ platformio platforms show atmelavr
    atmelavr    - An embedded platform for Atmel AVR microcontrollers (with Arduino Framework)
    ----------
    Package: toolchain-atmelavr
    Alias: toolchain
    Version: 1
    Installed: 2014-12-13 23:58:48
    ----------
    Package: tool-avrdude
    Version: 2
    Installed: 2015-02-13 22:23:17
    ----------
    Package: framework-arduinoavr
    Version: 12
    Installed: 2015-02-23 20:57:40
    ----------
    Package: tool-micronucleus
    Version: 1
    Installed: 2015-02-23 21:20:14
