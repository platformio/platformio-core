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

    platformio platform update [OPTIONS] [PLATFORM...]

    # update specific platform version using Semantic Versioning
    platformio platform update PLATFORM@X.Y.Z


Description
-----------

Check or update installed :ref:`platforms`

Options
-------

.. program:: platformio platform update

.. option::
    -p, --only-packages

Update only platform related packages. Do not update development platform
build scripts, board configs and etc.

.. option::
    -c, --only-check

Do not update, only check for new version

Examples
--------

.. code::

    > platformio platform update

    Platform atmelavr
    --------
    Updating atmelavr @ 0.0.0:  [Up-to-date]
    Updating framework-arduinoavr @ 1.10608.1:  [Up-to-date]
    Updating tool-avrdude @ 1.60001.1:  [Up-to-date]
    Updating toolchain-atmelavr @ 1.40801.0:    [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]

    Platform espressif
    --------
    Updating espressif @ 0.0.0:     [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]
    Updating toolchain-xtensa @ 1.40802.0:  [Up-to-date]
    Updating tool-esptool @ 1.409.0:    [Up-to-date]
    Updating tool-mkspiffs @ 1.102.0:   [Up-to-date]
    Updating framework-arduinoespressif @ 1.20300.0:    [Up-to-date]
    Updating sdk-esp8266 @ 1.10502.0:   [Up-to-date]

    Platform teensy
    --------
    Updating teensy @ 0.0.0:    [Up-to-date]
    Updating framework-arduinoteensy @ 1.128.0:     [Up-to-date]
    Updating tool-teensy @ 1.1.0:   [Up-to-date]
    Updating framework-mbed @ 1.121.0:  [Up-to-date]
    Updating tool-scons @ 2.4.1:    [Up-to-date]
    Updating toolchain-atmelavr @ 1.40801.0:    [Up-to-date]
    Updating toolchain-gccarmnoneeabi @ 1.40804.0:  [Up-to-date]

    ...
