.. _cmd_lib_install:

platformio lib install
======================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib install [OPTIONS] [NAMES]


Description
-----------

Install new library

Options
-------

.. option::
    -v, --version

Install specified version of library


Examples
--------

1. Install the latest version of library

.. code-block:: bash

    $ platformio lib install Arduino-IRremote
    Installing Arduino-IRremote library:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The library 'Arduino-IRremote' has been successfully installed!


2. Install specified version of library

.. code-block:: bash

    $ platformio lib install Arduino-XBee --version=0.5
    Installing Arduino-XBee library:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The library 'Arduino-XBee' has been successfully installed!


3. Install library with dependencies

.. code-block:: bash

    $ platformio lib install Adafruit-Arduino-ST7735
    Installing Adafruit-Arduino-ST7735 library:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The library 'Adafruit-Arduino-ST7735' has been successfully installed!
    Installing dependencies:
    Installing Adafruit-Arduino-GFX library:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The library 'Adafruit-Arduino-GFX' has been successfully installed!
