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

.. _cmd_lib_list:

platformio lib list
===================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib [STORAGE_OPTIONS] list [OPTIONS]

    # list project dependent libraries
    # (run it from a project root where is located "platformio.ini")
    platformio lib list [OPTIONS]

    # list libraries from global storage
    platformio lib --global list [OPTIONS]
    platformio lib -g list [OPTIONS]

    # list libraries from custom storage
    platformio lib --storage-dir /path/to/dir list [OPTIONS]
    platformio lib -d /path/to/dir list [OPTIONS]

Description
-----------

List installed libraries

Storage Options
---------------

See base options for :ref:`userguide_lib`.

Options
~~~~~~~

.. program:: platformio lib list

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format

Examples
--------

.. code::

    > platformio lib list

    pio lib -g list
     Library Storage: /storage/dir/...
    [ ID  ] Name             Compatibility         "Authors": Description
    -----------------------------------------------------------------------------------------------------------
    [  4  ] IRremote         arduino, atmelavr     "Rafi Khan, Ken Shirriff": Send and receive infrared signals with multiple protocols | @2.2.1
    [ 64  ] Json             arduino, atmelavr, atmelsam, timsp430, titiva, teensy, freescalekinetis, ststm32, nordicnrf51, nxplpc, espressif8266, siliconlabsefm32, linux_arm, native, intel_arc32 "Benoit Blanchon": An elegant and efficient JSON library for embedded systems | @5.4.0
    [ VCS ] TextLCD          -                     "Unknown": hg+https://developer.mbed.org/users/simon/code/TextLCD/ | @308d188a2d3a
