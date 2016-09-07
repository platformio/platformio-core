..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _cmd_lib_search:

platformio lib search
=====================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib search [OPTIONS] [QUERY]


Description
-----------

Search for library in `PlatformIO Library Registry <http://platformio.org/lib>`_
by :ref:`library_config` fields in the boolean mode.

The boolean search capability supports the following operators:

.. list-table::
    :header-rows:  1

    * - Operator
      - Description
    * - ``+``
      - A leading or trailing plus sign indicates that this word must be present
        in library fields (see above) that is returned.
    * - ``-``
      - A leading or trailing minus sign indicates that this word must not be
        present in any of the libraries that are returned.
    * - ``(no operator)``
      - By default (when neither ``+`` nor ``-`` is specified), the
        word is optional, but the libraries that contain it are rated higher.
    * - ``> <``
      - These two operators are used to change a word's contribution to the
        relevance value that is assigned to a library. The ``>`` operator
        increases the contribution and the ``<`` operator decreases it.
    * - ``( )``
      - Parentheses group words into subexpressions. Parenthesized groups can
        be nested.
    * - ``~``
      - A leading tilde acts as a negation operator, causing the word's
        contribution to the library's relevance to be negative. This is useful for
        marking "noise" words. A library containing such a word is rated lower than
        others, but is not excluded altogether, as it would be with the ``-`` operator.
    * - ``*``
      - The asterisk serves as the truncation (or wildcard) operator. Unlike the
        other operators, it is appended to the word to be affected. Words match if
        they begin with the word preceding the ``*`` operator.
    * - ``"``
      - A phrase that is enclosed within double quote (``"``) characters matches
        only libraries that contain the phrase literally, as it was typed.

For more detail information please go to
`MySQL Boolean Full-Text Searches <http://dev.mysql.com/doc/refman/5.6/en/fulltext-boolean.html>`_.

Options
-------

.. program:: platformio lib search

.. option::
    -n, --name

Filter libraries by specified name (strict search)

.. option::
    -a, --author

Filter libraries by specified author

.. option::
    -k, --keyword

Filter libraries by specified keyword

.. option::
    -f, --framework

Filter libraries by specified framework

.. option::
    -p, --platform

Filter libraries by specified keyword

.. option::
    -i, --header

Filter libraries by header file (include)

For example, ``platformio lib search --header "OneWire.h"``

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format

.. option::
   --page

Manually paginate through search results. This option is useful in pair with
``--json-output``.

Examples
--------

1. List all libraries

.. code::

    > platformio lib search

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [ 14  ] Adafruit-9DOF-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the Adafruit 9DOF Breakout (L3GD20 / LSM303)
    [ 13  ] Adafruit-GFX     arduino, atmelavr     "Adafruit Industries": A core graphics library for all our displays, providing a common set of graphics primitives (points, lines, circles, etc.)
    [ 23  ] Adafruit-L3GD20-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the L3GD20 Gyroscope
    [ 26  ] Adafruit-LSM303DLHC-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for Adafruit's LSM303 Breakout (Accelerometer + Magnetometer)
    [ 12  ] Adafruit-ST7735  arduino, atmelavr     "Adafruit Industries": A library for the Adafruit 1.8" SPI display
    [ 31  ] Adafruit-Unified-Sensor arduino, atmelavr     "Adafruit Industries": Adafruit Unified Sensor Driver
    [  4  ] IRremote         arduino, atmelavr     "Ken Shirriff": Send and receive infrared signals with multiple protocols
    [  1  ] OneWire          arduino, atmelavr     "Paul Stoffregen": Control devices (from Dallas Semiconductor) that use the One Wire protocol (DS18S20, DS18B20, DS2408 and etc)
    [  6  ] XBee             arduino, atmelavr     "Andrew Rapp": Arduino library for communicating with XBees in API mode
    [ 15  ] Adafruit-ADXL345-Unified arduino, atmelavr     "Adafruit Industries": Unified driver for the ADXL345 Accelerometer
    Show next libraries? [y/N]:
    ...

2. Search for `1-Wire libraries <http://platformio.org/lib/search?query=%25221-wire%2522>`_

.. code::

    > platformio lib search "1-wire"

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [  1  ] OneWire          arduino, atmelavr     "Paul Stoffregen": Control devices (from Dallas Semiconductor) that use the One Wire protocol (DS18S20, DS18B20, DS2408 and etc)
    ...

3. Search for `Arduino-based "I2C" libraries <http://platformio.org/lib/search?query=framework%253Aarduino%2520i2c>`_

.. code::

    > platformio lib search "i2c" --framework="arduino"

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [ 11  ] I2Cdevlib-Core   arduino, atmelavr     "Jeff Rowberg": The I2C Device Library (I2Cdevlib) is a collection of uniform and well-documented classes to provide simple and intuitive interfaces to I2C devices.
    [ 24  ] Adafruit-L3GD20  arduino, atmelavr     "Adafruit Industries": Driver for Adafruit's L3GD20 I2C Gyroscope Breakout
    [ 10  ] I2Cdevlib-AK8975 arduino, atmelavr     "Jeff Rowberg": AK8975 is 3-axis electronic compass IC with high sensitive Hall sensor technology
    [ 14  ] Adafruit-9DOF-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the Adafruit 9DOF Breakout (L3GD20 / LSM303)
    ...

4. Search for `libraries by "web" and "http" keywords <http://platformio.org/lib/search?query=keyword%253A%2522web%2522%2520keyword%253A%2522http%2522>`_.

.. code::

    > platformio lib search --keyword="web" --keyword="http"

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [  5  ] Webduino         arduino, atmelavr     "Ben Combee": An extensible web server library (for use with the Arduino WizNet Ethernet Shield)
    [ 17  ] Adafruit-CC3000  arduino, atmelavr     "Adafruit Industries": Library code for Adafruit's CC3000 Wi-Fi/WiFi breakouts
    ...

5. Search for `libraries by "Adafruit Industries" author <http://platformio.org/lib/search?query=author%253A%2522Adafruit%20Industries%2522>`_

.. code::

    > platformio lib search --author="Adafruit Industries"

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [ 14  ] Adafruit-9DOF-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the Adafruit 9DOF Breakout (L3GD20 / LSM303)
    [ 13  ] Adafruit-GFX     arduino, atmelavr     "Adafruit Industries": A core graphics library for all our displays, providing a common set of graphics primitives (points, lines, circles, etc.)
    [ 23  ] Adafruit-L3GD20-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the L3GD20 Gyroscope
    [ 26  ] Adafruit-LSM303DLHC-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for Adafruit's LSM303 Breakout (Accelerometer + Magnetometer)
    ...

6. Search for `libraries which are compatible with Dallas temperature sensors <http://platformio.org/lib/search?query=DS*>`_
   like DS18B20, DS18S20 and etc.

.. code::

    > platformio lib search "DS*"

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [  1  ] OneWire          arduino, atmelavr     "Paul Stoffregen": Control devices (from Dallas Semiconductor) that use the One Wire protocol (DS18S20, DS18B20, DS2408 and etc)
    ...

7. Search for `Energia-based *nRF24* or *HttpClient* libraries <http://platformio.org/lib/search?query=framework%253Aenergia%2520%252B(nRF24%2520HttpClient)>`_.
   The search query that is described below can be interpreted like
   ``energia nRF24 OR energia HttpClient``

.. code::

    > platformio lib search "+(nRF24 HttpClient)" --framework="energia"

    Found 2 libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [ 46  ] HttpClient       energia, timsp430, titiva "Zack Lalanne": HttpClient is a library to make it easier to interact with web servers
    [ 43  ] nRF24            energia, timsp430     "Eric": The nRF24L01 is a low-cost 2.4GHz ISM transceiver module. It supports a number of channel frequencies in the 2.4GHz band and a range of data rates.


8. Search for the `all sensor libraries excluding temperature <http://platformio.org/lib/search?query=sensor%2520-temperature>`_.

.. code::

    > platformio lib search "sensor -temperature"

    Found N libraries:

    [ ID  ] Name             Compatibility         "Authors": Description
    -------------------------------------------------------------------------------------
    [ 31  ] Adafruit-Unified-Sensor arduino, atmelavr     "Adafruit Industries": Adafruit Unified Sensor Driver
    [ 10  ] I2Cdevlib-AK8975 arduino, atmelavr     "Jeff Rowberg": AK8975 is 3-axis electronic compass IC with high sensitive Hall sensor technology
    [ 14  ] Adafruit-9DOF-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the Adafruit 9DOF Breakout (L3GD20 / LSM303)
    [ 23  ] Adafruit-L3GD20-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for the L3GD20 Gyroscope
    [ 26  ] Adafruit-LSM303DLHC-Unified arduino, atmelavr     "Adafruit Industries": Unified sensor driver for Adafruit's LSM303 Breakout (Accelerometer + Magnetometer)
    [ 33  ] Adafruit-TMP006  arduino, atmelavr     "Adafruit Industries": A library for the Adafruit TMP006 Infrared Thermopile Sensor
    [ 34  ] Adafruit-TSL2561-Unified arduino, atmelavr     "Adafruit Industries": Unified light sensor driver for Adafruit's TSL2561 breakouts
    [ 97  ] I2Cdevlib-BMA150 arduino, atmelavr     "Jeff Rowberg": The BMA150 is a triaxial, low-g acceleration sensor IC with digital output for consumer market applications
    [ 106 ] I2Cdevlib-MPR121 arduino, atmelavr     "Jeff Rowberg": The MPR121 is a 12-bit proximity capacitive touch sensor
    [ 111 ] I2Cdevlib-AK8975 energia, timsp430     "Jeff Rowberg": AK8975 is 3-axis electronic compass IC with high sensitive Hall sensor technology
    Show next libraries? [y/N]:
