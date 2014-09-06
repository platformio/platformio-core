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

Search for library over ``name``, ``description`` and ``keywords`` fields from
the :ref:`library_config` file in the boolean mode.

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

.. option::
    -a, --author

Filter libraries by specified author

.. option::
    -k, --keyword

Filter libraries by specified keyword

Examples
--------

1. Search for "1-Wire" library

.. code-block:: bash

    $ platformio lib search 1-wire
    Found N libraries:
    Arduino-OneWire       Control devices (from Dallas Semiconductor) that use the One Wire protocol
    ...

2. Search for Arduino-based "I2C" libraries. The ``+`` sign is here like ``AND``
   operator.

.. code-block:: bash

    $ platformio lib search "+i2c +arduino"
    Found N libraries:
    i2cdevlib-Arduino-i2cdev The I2C Device Library (i2cdevlib) is a collection of uniform and well-documented classes to provide simple and intuitive interfaces to I2C devices.
    i2cdevlib-Arduino-AK8975 AK8975 is 3-axis electronic compass IC with high sensitive Hall sensor technology
    ...

3. Search for libraries by "web" and "http" keywords. The ``""`` here is for
   "empty" query argument.

.. code-block:: bash

    $ platformio lib search "" --keyword web --keyword http
    Found N libraries:
    Arduino-Webduino      An extensible web server library (for use with the Arduino Ethernet Shield)
    Arduino-aJson         An Arduino library to enable JSON processing with Arduino
    ...

4. Search for libraries from "Adafruit Industries" author.

.. code-block:: bash

    $ platformio lib search "" --author "Adafruit Industries"
    Found N libraries:
    Adafruit-Arduino-ST7735 A library for the Adafruit 1.8" SPI display
    Adafruit-Arduino-GFX  A core graphics library for all our displays, providing a common set of graphics primitives (points, lines, circles, etc.)
    ...

5. Search for libraries that are compatible with Dallas temperature sensors
   like DS18B20, DS18S20 and etc.

.. code-block:: bash

    $ platformio lib search "DS*"
    Found N libraries:
    Arduino-OneWire       Control devices (from Dallas Semiconductor) that use the One Wire protocol
    ...

6. Search for Arduino-based *X10* or *XBee* libraries. The search query that is
   described below can be interpreted like ``arduino x10 OR arduino xbee``.

.. code-block:: bash

    $ platformio lib search "+arduino +(x10 xbee)"
    Found 2 libraries:
    Arduino-X10           Sending X10 signals over AC power lines
    Arduino-XBee          Arduino library for communicating with XBees in API mode
