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

.. _cmd_lib_list:

platformio lib list
===================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib list [OPTIONS]


Description
-----------

List installed libraries

Options
~~~~~~~

.. program:: platformio lib list

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format

Examples
--------

.. code-block:: bash

    $ platformio lib list
    #
    # [ ID  ] Name             Compatibility         "Authors": Description
    # -------------------------------------------------------------------------------------
    # [ 23  ] Adafruit-L3GD20-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the L3GD20 Gyroscope
    # [ 12  ] Adafruit-ST7735  arduino, atmelavr     "Adafruit Industries": A library for the Adafruit 1.8" SPI display
    # [ 31  ] Adafruit-Unified-Sensor arduino, atmelavr     "Adafruit Industries": Adafruit Unified Sensor Driver
    # [ 26  ] Adafruit-LSM303DLHC-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for Adafruit's LSM303 Breakout (Accelerometer + Magnetometer)
    # [  6  ] XBee             arduino, atmelavr     "Andrew Rapp": Arduino library for communicating with XBees in API mode
    # [ 13  ] Adafruit-GFX     arduino, atmelavr     "Adafruit Industries": A core graphics library for all our displays, providing a common set of graphics primitives (points, lines, circles, etc.)
    # [  4  ] IRremote         arduino, atmelavr     "Ken Shirriff": Send and receive infrared signals with multiple protocols
    # [ 14  ] Adafruit-9DOF-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the Adafruit 9DOF Breakout (L3GD20 / LSM303)
    # ...
