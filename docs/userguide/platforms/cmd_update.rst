..  Copyright 2014-present Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _cmd_platform_update:

platformio platform update
==========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platform update


Description
-----------

Check or update installed :ref:`platforms`

Options
-------

.. program:: platformio platform update

.. option::
    --only-packages

Update only platform related packages. Do not update development platform
build scripts, board configs and etc.

Examples
--------

.. code-block:: bash

    $ platformio platform update
    Platform atmelavr @ 0.0.0
    --------
    Updating platform atmelavr @ latest:
    Versions: Current=0.0.0, Latest=0.0.0    [Up-to-date]
    Updating package framework-arduinoavr @ ~1.10608.0:
    Versions: Current=1.10608.0, Latest=1.10608.0    [Up-to-date]
    Updating package toolchain-atmelavr @ ~1.40801.0:
    Versions: Current=1.40801.0, Latest=1.40801.0    [Up-to-date]
    Updating package framework-simba @ ~1.500.0:
    Versions: Current=1.500.0, Latest=1.500.0    [Up-to-date]
    Updating package tool-scons @ >=2.3.0,<2.6.0:
    Versions: Current=2.5.0, Latest=2.5.0    [Up-to-date]

    Platform atmelsam @ 0.0.0
    --------
    Updating platform atmelsam @ latest:
    Versions: Current=0.0.0, Latest=0.0.0    [Up-to-date]
    Updating package toolchain-gccarmnoneeabi @ >=1.40803.0,<1.40805.0:
    Versions: Current=1.40804.0, Latest=1.40804.0    [Up-to-date]
    Updating package framework-arduinosam @ ~1.10607.0:
    Versions: Current=1.10607.0, Latest=1.10607.0    [Up-to-date]
    Updating package framework-simba @ ~1.500.0:
    Versions: Current=1.500.0, Latest=1.500.0    [Up-to-date]
    Updating package framework-mbed @ ~1.117.0:
    Versions: Current=1.117.0, Latest=1.117.0    [Up-to-date]
    Updating package tool-scons @ >=2.3.0,<2.6.0:
    Versions: Current=2.5.0, Latest=2.5.0    [Up-to-date]
    Updating package tool-bossac @ ~1.10500.0:
    Versions: Current=1.10500.0, Latest=1.10500.0    [Up-to-date]

    Platform espressif @ 0.0.0
    --------
    Updating platform espressif @ latest:
    Versions: Current=0.0.0, Latest=0.0.0    [Up-to-date]
    Updating package tool-scons @ >=2.3.0,<2.6.0:
    Versions: Current=2.5.0, Latest=2.5.0    [Up-to-date]
    Updating package toolchain-xtensa @ ~1.40802.0:
    Versions: Current=1.40802.0, Latest=1.40802.0    [Up-to-date]
    Updating package framework-simba @ ~1.500.0:
    Versions: Current=1.500.0, Latest=1.500.0    [Up-to-date]
    Updating package tool-esptool @ ~1.408.0:
    Versions: Current=1.408.0, Latest=1.408.0    [Up-to-date]
    Updating package tool-mkspiffs @ ~1.102.0:
    Versions: Current=1.102.0, Latest=1.102.0    [Up-to-date]
    Updating package framework-arduinoespressif @ ~1.20200.0:
    Versions: Current=1.20200.0, Latest=1.20200.0    [Up-to-date]
    Updating package sdk-esp8266 @ ~1.10502.0:
    Versions: Current=1.10502.0, Latest=1.10502.0    [Up-to-date]

    ...
