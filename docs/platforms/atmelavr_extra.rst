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

.. _atmelavr_upload_via_programmer:

Upload using Programmer
-----------------------

To upload firmware using programmer you need to use ``program`` target instead
``upload`` for :option:`platformio run --target` command. For example,
``platformio run -t program``.

Configuration for the programmers:

*   AVR ISP

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = stk500v1
        upload_flags = -P$UPLOAD_PORT

        # edit this line with valid upload port
        upload_port = SERIAL_PORT_HERE

*   AVRISP mkII

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = stk500v2
        upload_flags = -Pusb

*   USBtinyISP

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = usbtiny

*   USBasp

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = usbasp
        upload_flags = -Pusb

*   Parallel Programmer

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = dapa
        upload_flags = -F

*   Arduino as ISP

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = stk500v1
        upload_flags = -P$UPLOAD_PORT -b$UPLOAD_SPEED

        # edit these lines
        upload_port = SERIAL_PORT_HERE
        upload_speed = 19200

Examples
--------

All project examples are located in PlatformIO repository
`Examples for Atmel AVR platform <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino>`_.

* `Wiring Blink <https://github.com/platformio/platformio/tree/develop/examples/wiring-blink>`_
* `Arduino with external libraries <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/arduino-external-libs>`_
* `Arduino with internal libraries <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/arduino-internal-libs>`_
* `Project uses source file name for "src" directory (Arduino project structure) <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/arduino-own-src_dir>`_
* `Atmel AVR Native blink <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/atmelavr-native-blink>`_
* `Digitstump Mouse <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/digitstump-mouse>`_
* `Engduino magnetometer <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/engduino-magnetometer>`_
* `PanStamp blink <https://github.com/platformio/platformio/tree/develop/examples/atmelavr-and-arduino/panstamp-blink>`_
