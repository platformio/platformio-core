.. _cmd_lib_install:

platformio lib install
======================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib install [OPTIONS] [LIBRARY_ID]


Description
-----------

Install new library  by specified
`PlatformIO Library Registry ID <http://platformio.org/#!/lib>`_.

Options
-------

.. option::
    -v, --version

Install specified version of library


Examples
--------

1. Install the latest version of library

.. code-block:: bash

    # IRremote: http://platformio.org/#!/lib/show/4/IRremote
    $ platformio lib install 4
    # Installing library [ 4 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #4 'IRremote' has been successfully installed!


2. Install specified version of library

.. code-block:: bash

    # XBee: http://platformio.org/#!/lib/show/6/XBee
    $ platformio lib install 6 --version=0.5
    # Installing library [ 6 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #6 'XBee' has been successfully installed!


3. Install library with dependencies

.. code-block:: bash

    # Adafruit-ST7735: http://platformio.org/#!/lib/show/12/Adafruit-ST7735
    $ platformio lib install 12
    # Installing library [ 12 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #12 'Adafruit-ST7735' has been successfully installed!
    # Installing dependencies:
    # Installing library [ 13 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #13 'Adafruit-GFX' has been successfully installed!
