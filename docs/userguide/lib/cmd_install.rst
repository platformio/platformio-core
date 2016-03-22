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
`PlatformIO Library Registry ID <http://platformio.org/lib>`_.

Options
-------

.. program:: platformio lib install

.. option::
    -v, --version

Install specified version of library


Examples
--------

1. Install the latest version of library

.. code-block:: bash

    # IRremote: http://platformio.org/lib/show/4/IRremote
    $ platformio lib install 4
    # Installing library [ 4 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #4 'IRremote' has been successfully installed!


2. Install specified version of library

.. code-block:: bash

    # XBee: http://platformio.org/lib/show/6/XBee
    $ platformio lib install 6 --version=0.5
    # Installing library [ 6 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #6 'XBee' has been successfully installed!


3. Install library with dependencies

.. code-block:: bash

    # Adafruit-ST7735: http://platformio.org/lib/show/12/Adafruit-ST7735
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
