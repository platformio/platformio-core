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

Custom CPU Frequency or Upload Speed
------------------------------------

See :ref:`projectconf_board_f_cpu` and :ref:`projectconf_upload_speed` options
from :ref:`projectconf`

.. code-block:: ini

    [env:myenv]
    # set frequency to 40MHz
    board_f_cpu = 40000000L

    upload_speed = 9600

.. _platform_espressif_customflash:

Custom Flash Size
-----------------

.. warning::
    Please make sure to read `ESP8266 Flash layout <https://github.com/esp8266/Arduino/blob/master/doc/filesystem.md#flash-layout>`_
    information first.

The list with preconfigured LD scripts is located in public repository
`platformio-pkg-ldscripts <https://github.com/platformio/platformio-pkg-ldscripts>`_.

* ``esp8266.flash.512k0.ld`` 512K (no SPIFFS)
* ``esp8266.flash.512k64.ld`` 512K (64K SPIFFS)
* ``esp8266.flash.1m64.ld`` 1M (64K SPIFFS)
* ``esp8266.flash.1m128.ld`` 1M (128K SPIFFS)
* ``esp8266.flash.1m256.ld`` 1M (256K SPIFFS)
* ``esp8266.flash.1m512.ld`` 1M (512K SPIFFS)
* ``esp8266.flash.2m.ld`` 2M (1M SPIFFS)
* ``esp8266.flash.4m1m.ld`` 4M (1M SPIFFS)
* ``esp8266.flash.4m.ld`` 4M (3M SPIFFS)

To override default LD script please use :ref:`projectconf_build_flags` from
:ref:`projectconf`.

.. code-block:: ini

    [env:myenv]
    build_flags = -Wl,-Tesp8266.flash.4m.ld

.. _platform_espressif_uploadfs:

Uploading files to file system SPIFFS
-------------------------------------

.. warning::
    Please make sure to read `ESP8266 Flash layout <https://github.com/esp8266/Arduino/blob/master/doc/filesystem.md#flash-layout>`_
    information first.

1. Initialise project :ref:`cmd_init` (if you have not initialized yet)
2. Create :ref:`projectconf_pio_data_dir` and put files here
3. Run target ``uploadfs`` using  :option:`platformio run --target` command.

To upload SPIFFS image using OTA update please specify ``upload_port`` /
``--upload-port`` as IP address or mDNS host name (ending with the ``*.local``).
For the details please follow to :ref:`platform_espressif_ota`.

By default, will be used default LD Script for the board where is specified
SPIFFS offsets (start, end, page, block). You can override it using
:ref:`platform_espressif_customflash`.

Active discussion is located in `issue #382 <https://github.com/platformio/platformio/issues/382>`_.

.. _platform_espressif_ota:

Over-the-Air (OTA) update
-------------------------

Firstly, please read `What is OTA? How to use it? <https://github.com/esp8266/Arduino/blob/master/doc/ota_updates/ota_updates.md>`_

There are 2 options:

* Directly specify :option:`platformio run --upload-port` in command line

.. code-block:: bash

    platformio run --target upload --upload-port IP_ADDRESS_HERE or mDNS_NAME.local

* Specify ``upload_port`` option in :ref:`projectconf`

.. code-block:: ini

   [env:myenv]
   ...
   upload_port = IP_ADDRESS_HERE or mDNS_NAME.local

For example,

* ``platformio run -t upload --upload-port 192.168.0.255``
* ``platformio run -t upload --upload-port myesp8266.local``

Authentication and upload options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass additional options/flags to OTA uploader using
``upload_flags`` option in :ref:`projectconf`

.. code-block:: ini

    [env:myenv]
    upload_flags = --port=8266

Available flags

* ``--port=ESP_PORT`` ESP8266 ota Port. Default 8266
* ``--auth=AUTH`` Set authentication password
* ``--spiffs`` Use this option to transmit a SPIFFS image and do not flash
  the module

For the full list with available options please run

.. code-block:: bash

    ~/.platformio/packages/framework-arduinoespressif/tools/espota.py -h

    Usage: espota.py [options]

    Transmit image over the air to the esp8266 module with OTA support.

    Options:
      -h, --help            show this help message and exit

      Destination:
        -i ESP_IP, --ip=ESP_IP
                            ESP8266 IP Address.
        -p ESP_PORT, --port=ESP_PORT
                            ESP8266 ota Port. Default 8266

      Authentication:
        -a AUTH, --auth=AUTH
                            Set authentication password.

      Image:
        -f FILE, --file=FILE
                            Image file.
        -s, --spiffs        Use this option to transmit a SPIFFS image and do not
                            flash the module.

      Output:
        -d, --debug         Show debug output. And override loglevel with debug.
        -r, --progress      Show progress output. Does not work for ArduinoIDE

Demo
~~~~

.. image:: ../_static/platformio-demo-ota-esp8266.jpg
    :target: https://www.youtube.com/watch?v=lXchL3hpDO4

Articles
--------

* Dec 22, 2015 - **Jan Penninkhof** - `Over-the-Air ESP8266 programming using PlatformIO <http://www.penninkhof.com/2015/12/1610-over-the-air-esp8266-programming-using-platformio/>`_
* Dec 01, 2015 - **Tateno Yuichi** - `ESP8266 を CUI で開発する (Develop a ESP8266 in CUI, Japanese) <http://jaywiggins.com/platformio/arduino/avr/es8266/2015/09/30/platformio-investigation/>`_

See more :ref:`articles`.

Examples
--------

All project examples are located in PlatformIO repository
`Examples for Espressif platform <https://github.com/platformio/platformio/tree/develop/examples/espressif>`_.

* `Native SDK <https://github.com/platformio/platformio/tree/develop/examples/espressif/esp8266-native>`_
* `WebServer <https://github.com/platformio/platformio/tree/develop/examples/espressif/esp8266-webserver>`_
* `WiFiScan <https://github.com/platformio/platformio/tree/develop/examples/espressif/esp8266-wifiscan>`_
