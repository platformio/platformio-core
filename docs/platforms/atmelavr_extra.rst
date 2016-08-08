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

*   ArduinoISP

    .. code-block:: ini

        [env:myenv]
        platform = atmelavr
        framework = arduino
        upload_protocol = arduinoisp

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

Upload EEPROM data
------------------

To upload EEPROM data (from EEMEM directive) you need to use ``uploadeep``
target instead ``upload`` for :option:`platformio run --target` command.
For example, ``platformio run -t uploadeep``.

Articles
--------

* Dec 01, 2015 - **Michał Seroczyński** - `Push Notification from Arduino Yún with motion sensor <http://www.ches.pl/push-from-yun-1/>`_
* Nov 29, 2015 - **Keith Hughes** - `Using PlatformIO for Embedded Projects <http://smartspacestuff.blogspot.com/2015/11/using-platformio-for-embedded-projects.html>`_
* Nov 22, 2015 - **Michał Seroczyński** - `Using PlatformIO to get started with Arduino in CLion IDE <http://www.ches.pl/using-platformio-get-started-arduino-clion-ide/>`_
* Nov 09, 2015 - **ÁLvaro García Gómez** - `Programar con Arduino "The good way" (Programming with Arduino "The good way", Spanish) <http://congdegnu.es/2015/11/09/programar-con-arduino-the-good-way/>`_
* Oct 18, 2015 - **Nico Coetzee** - `First Arduino I2C Experience with PlatformIO <https://electronicventurer.wordpress.com/2015/10/18/first-arduino-i2c-experience/>`_
* Oct 10, 2015 - **Floyd Hilton** - `Programming Arduino with Atom <http://floydhilton.com/software/career/2015/10/10/Arduino_with_Atom.html>`_
* June 20, 2014 - **Ivan Kravets, Ph.D.** - `Building and debugging Atmel AVR (Arduino-based) project using Eclipse IDE+PlatformIO <http://www.ikravets.com/computer-life/programming/2014/06/20/building-and-debugging-atmel-avr-arduino-based-project-using-eclipse-ideplatformio>`_

See more :ref:`articles`.

Examples
--------

All project examples are located in PlatformIO repository
`Examples for Atmel AVR platform <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino>`_.

* `Wiring Blink <https://github.com/platformio/platformio-examples/tree/develop/wiring-blink>`_
* `Arduino with external libraries <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/arduino-external-libs>`_
* `Arduino with internal libraries <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/arduino-internal-libs>`_
* `Project uses source file name for "src" directory (Arduino project structure) <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/arduino-own-src_dir>`_
* `Atmel AVR Native blink <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/atmelavr-native-blink>`_
* `Digitstump Mouse <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/digitstump-mouse>`_
* `Engduino magnetometer <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/engduino-magnetometer>`_
* `PanStamp blink <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/panstamp-blink>`_
