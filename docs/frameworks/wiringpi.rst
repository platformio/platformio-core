..  Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _framework_wiringpi:

Framework ``wiringpi``
======================
WiringPi is a GPIO access library written in C for the BCM2835 used in the Raspberry Pi. It's designed to be familiar to people who have used the Arduino "wiring" system.

For more detailed information please visit `vendor site <http://wiringpi.com>`_.

.. contents::

Platforms
---------
.. list-table::
    :header-rows:  1

    * - Name
      - Description

    * - :ref:`platform_linux_arm`
      - Linux ARM is a Unix-like and mostly POSIX-compliant computer operating system (OS) assembled under the model of free and open-source software development and distribution. Using host OS (Mac OS X, Linux ARM) you can build native application for Linux ARM platform.

Boards
------

.. note::
    * You can list pre-configured boards by :ref:`cmd_boards` command or
      `PlatformIO Boards Explorer <http://platformio.org/#!/boards>`_
    * For more detailed ``board`` information please scroll tables below by horizontal.

Raspberry Pi
~~~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller
      - Frequency
      - Flash
      - RAM

    * - ``raspberrypi_1b``
      - `Raspberry Pi 1 Model B <https://www.raspberrypi.org>`_
      - BCM2835
      - 700 MHz
      - 524288 Kb
      - 524288 Kb

    * - ``raspberrypi_2b``
      - `Raspberry Pi 2 Model B <https://www.raspberrypi.org>`_
      - BCM2836
      - 900 MHz
      - 1048576 Kb
      - 1048576 Kb

    * - ``raspberrypi_zero``
      - `Raspberry Pi Zero <https://www.raspberrypi.org>`_
      - BCM2835
      - 1000 MHz
      - 524288 Kb
      - 524288 Kb

.. include:: wiringpi_extra.rst
