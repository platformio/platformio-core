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

.. _cmd_lib_register:

platformio lib register
=======================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib register [MANIFEST_URL]


Description
-----------

Register new library in `PlatformIO Library Registry <http://platformio.org/lib>`_.

PlatformIO Library Registry supports the next library manifests:

* PlatformIO :ref:`library_config`
* Arduino `library.properties <https://github.com/arduino/Arduino/wiki/Arduino-IDE-1.5:-Library-specification>`_
* ARM mbed yotta `module.json <http://yottadocs.mbed.com/reference/module.html>`_.

Examples
--------

.. code::

    platformio lib register https://raw.githubusercontent.com/bblanchon/ArduinoJson/master/library.json
    platformio lib register https://raw.githubusercontent.com/adafruit/DHT-sensor-library/master/library.properties
    platformio lib register https://raw.githubusercontent.com/ARMmbed/ble/master/module.json
