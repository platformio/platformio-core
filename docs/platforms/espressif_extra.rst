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

OTA firmware uploading
----------------------

There are 2 options:

* Directly specify :option:`platformio run --upload-port` in command line

.. code-block:: bash

    platformio run --target upload --upload-port IP_ADDRESS_HERE

* Specify ``upload_port`` option in :ref:`projectconf`

.. code-block:: ini

   [env:***]
   ...
   upload_port = IP_ADDRESS_HERE

Authentication and upload options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can pass additional options/flags to OTA uploader using
``upload_flags`` option in :ref:`projectconf`

.. code-block:: ini

    [env:***]
    upload_flags = --port=8266

Availalbe flags

* ``--port=ESP_PORT`` ESP8266 ota Port. Default 8266
* ``--auth=AUTH`` Set authentication password
* ``--spiffs`` Use this option to transmit a SPIFFS image and do not flash
  the module

For the full list with availalbe options please run

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

Examples
--------

All project examples are located in PlatformIO repository
`Examples for Espressif platform <https://github.com/platformio/platformio/tree/develop/examples/espressif>`_.

* `Native SDK <https://github.com/platformio/platformio/tree/develop/examples/espressif/esp8266-native>`_
* `WebServer <https://github.com/platformio/platformio/tree/develop/examples/espressif/esp8266-webserver>`_
* `WiFiScan <https://github.com/platformio/platformio/tree/develop/examples/espressif/esp8266-wifiscan>`_
