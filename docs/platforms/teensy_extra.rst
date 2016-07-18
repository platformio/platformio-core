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

Teensy 2.0 and USB
------------------

If you want to implement USB functionality using Teensy 2.0, you need to
add special macros/define using :ref:`projectconf_build_flags`:

* ``-D USB_HID``
* ``-D USB_SERIAL_HID``
* ``-D USB_DISK``
* ``-D USB_DISK_SDFLASH``
* ``-D USB_MIDI``
* ``-D USB_RAWHID``
* ``-D USB_FLIGHTSIM``
* ``-D USB_DISABLED``

Example:

.. code-block:: ini

    [env:teensy_hid_device]
    platform = teensy
    framework = arduino
    board = teensy20
    build_flags = -D USB_RAWHID

See `Teensy USB Examples <https://www.pjrc.com/teensy/usb_debug_only.html>`_.

Examples
--------

All project examples are located in PlatformIO repository
`Examples for Teensy platform <https://github.com/platformio/platformio-examples/tree/develop/teensy>`_.

* `Wiring Blink <https://github.com/platformio/platformio-examples/tree/develop/wiring-blink>`_
* `HID Mouse <https://github.com/platformio/platformio-examples/tree/develop/teensy/teensy-hid-usb-mouse>`_
* `Chat Server <https://github.com/platformio/platformio-examples/tree/develop/teensy/teensy-internal-libs>`_
