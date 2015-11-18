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

.. _cmd_lib_update:

platformio lib update
=====================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib update [LIBRARY_ID]


Description
-----------

Check or update installed libraries


Examples
--------

1. Update all installed libraries

.. code-block:: bash

    $ platformio lib update
    # Updating  [ 23 ] Adafruit-L3GD20-Unified library:
    # Versions: Current=63de2eb9ea, Latest=63de2eb9ea 	 [Up-to-date]
    # Updating  [ 12 ] Adafruit-ST7735 library:
    # Versions: Current=e880eb1687, Latest=e880eb1687 	 [Up-to-date]
    # Updating  [ 31 ] Adafruit-Unified-Sensor library:
    # Versions: Current=88ae805bce, Latest=88ae805bce 	 [Up-to-date]
    # Updating  [ 26 ] Adafruit-LSM303DLHC-Unified library:
    # Versions: Current=59767208a8, Latest=59767208a8 	 [Up-to-date]
    # Updating  [ 13 ] Adafruit-GFX library:
    # Versions: Current=a9e5bc4707, Latest=a9e5bc4707 	 [Up-to-date]
    # Updating  [ 1 ] OneWire library:
    # Versions: Current=2.2, Latest=2.2 	             [Up-to-date]
    # Updating  [ 4 ] IRremote library:
    # Versions: Current=f2dafe5030, Latest=f2dafe5030 	 [Up-to-date]
    # Updating  [ 14 ] Adafruit-9DOF-Unified library:
    # Versions: Current=b2f07242ac, Latest=b2f07242ac 	 [Up-to-date]

2. Update specified libraries

.. code-block:: bash

    $ platformio lib update 1 59
    # Updating  [ 1 ] OneWire library:
    # Versions: Current=2.2, Latest=2.2 	             [Up-to-date]
    # Updating [ 59 ] USB-Host-Shield-20 library:
    # Versions: Current=fcab83dcb3, Latest=c61f9ce1c2 	 [Out-of-date]
    # The library #59 'USB-Host-Shield-20' has been successfully uninstalled!
    # Installing library [ 59 ]:
    # Downloading  [####################################]  100%
    # Unpacking  [####################################]  100%
    # The library #59 'USB-Host-Shield-20' has been successfully installed!
