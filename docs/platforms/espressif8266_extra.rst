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

Custom CPU Frequency
--------------------

See :ref:`projectconf_board_f_cpu` option from :ref:`projectconf`

.. code-block:: ini

    [env:myenv]
    ; set frequency to 160MHz
    board_f_cpu = 160000000L

Custom FLASH Frequency
----------------------

See :ref:`projectconf_board_f_flash` option from :ref:`projectconf`. Possible
values:

* ``20000000L``
* ``26000000L``
* ``40000000L``
* ``80000000L``

.. code-block:: ini

    [env:myenv]
    ; set frequency to 80MHz
    board_f_flash = 80000000L

Custom FLASH Mode
-----------------

Flash chip interface mode. This parameter is stored in the binary image
header, along with the flash size and flash frequency. The ROM bootloader
in the ESP chip uses the value of these parameters in order to know how to
talk to the flash chip.

See :ref:`projectconf_board_flash_mode` option from :ref:`projectconf`. Possible
values:

* ``qio``
* ``qout``
* ``dio``
* ``dout``

.. code-block:: ini

    [env:myenv]
    board_flash_mode = qio

Custom Reset Method
-------------------

You can set custom reset method using :ref:`projectconf_upload_resetmethod`
option from :ref:`projectconf`.

The `possible values <https://github.com/igrr/esptool-ck#supported-boards>`_ are:

* ``ck`` - RTS controls RESET or CH_PD, DTR controls GPIO0
* ``wifio`` - TXD controls GPIO0 via PNP transistor and DTR controls RESET via a capacitor
* ``nodemcu`` - GPIO0 and RESET controlled using two NPN transistors as in NodeMCU devkit.

See `default reset methods per board <https://github.com/platformio/platform-espressif8266/search?p=1&q=resetmethod>`_.

.. code-block:: ini

    [env:myenv]
    upload_resetmethod = ck

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

Custom Upload Speed
-------------------

You can set custom upload speed using  :ref:`projectconf_upload_speed` option
from :ref:`projectconf`

.. code-block:: ini

    [env:myenv]
    upload_speed = 9600

.. _platform_espressif_uploadfs:

Uploading files to file system SPIFFS
-------------------------------------

.. warning::
    Please make sure to read `ESP8266 Flash layout <https://github.com/esp8266/Arduino/blob/master/doc/filesystem.md#flash-layout>`_
    information first.

1. Initialize project :ref:`cmd_init` (if you have not initialized yet)
2. Create ``data`` folder (it should be on the same level as ``src`` folder)
   and put files here. Also, you can specify own location for :ref:`projectconf_pio_data_dir`
3. Run ``buildfs`` or ``uploadfs`` target using :option:`platformio run --target` command.

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

Firstly, please read `What is OTA? How to use it? <https://github.com/esp8266/Arduino/blob/master/doc/ota_updates/readme.md>`_

There are 2 options:

* Directly specify :option:`platformio run --upload-port` in command line

.. code-block:: bash

    platformio run --target upload --upload-port IP_ADDRESS_HERE or mDNS_NAME.local

* Specify ``upload_port`` option in :ref:`projectconf`

.. code-block:: ini

   [env:myenv]
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

* ``--port=ESP_PORT`` ESP8266 OTA Port. Default 8266
* ``--auth=AUTH`` Set authentication password
* ``--spiffs`` Use this option to transmit a SPIFFS image and do not flash
  the module

For the full list with available options please run

.. code-block:: bash

    ~/.platformio/packages/framework-arduinoespressif8266/tools/espota.py -h

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


Using Arduino Framework with Staging version
--------------------------------------------

1.  Install Espressif 8266 (Stage) development platform

    .. code::

        platformio platform install https://github.com/platformio/platform-espressif8266.git#feature/stage

2.  Set :ref:`projectconf_env_platform` to ``espressif8266_stage`` in
    :ref:`projectconf`. For example,

    .. code-block:: ini

        [env:nodemcuv2]
        platform = espressif8266_stage
        board = nodemcuv2
        framework = arduino

3.  Try to build project
4.  If you see build errors, then try to build this project using the same
    ``stage`` on Arduino IDE
5.  If it works with Arduino IDE but doesn't work with PlatformIO, then please
    `open new issue <https://github.com/platformio/platformio/issues>`_ with
    attached information:

    - test project/files
    - detailed log of build process from Arduino IDE (please copy it from
      console to http://pastebin.com)
    - detailed log of build process from PlatformIO Build System (
      please copy it from console to http://pastebin.com)

Articles
--------

* Sep 12, 2016 - **Pedro Minatel** - `OTA – Como programar o ESP8266 pelo WiFi no platformIO (OTA programming for ESP8266 via Wi-Fi using PlatformIO, Portuguese) <http://pedrominatel.com.br/esp8266/ota-como-programar-o-esp8266-pelo-wifi-no-platformio/>`_
* Sep 2, 2016 - **Tinkerman** `Optimizing files for SPIFFS with Gulp <http://tinkerman.cat/optimizing-files-for-spiffs-with-gulp/>`_
* Jul 15, 2016 - **Jaime** - `ESP8266 Mobile Rick Roll Captive Portal <https://hackaday.io/project/12709-esp8266-mobile-rick-roll-captive-portal>`_
* Jun 13, 2016 - **Daniel Eichhorn** - `New Weather Station Demo on Github <http://blog.squix.org/2016/06/new-weather-station-demo-on-github.html>`_
* Jun 3, 2016 - **Daniel Eichhorn** - `ESP8266: Continuous Delivery Pipeline – Push To Production <http://blog.squix.org/2016/06/esp8266-continuous-delivery-pipeline-push-to-production.html>`_
* May 29, 2016 - **Chris Synan** - `Reverse Engineer RF Remote Controller for IoT! <http://www.instructables.com/id/Reverse-Engineer-RF-Remote-Controller-for-IoT/?ALLSTEPS>`_
* May 22, 2016 - **Pedro Minatel** - `Estação meteorológica com ESP8266 (Weather station with ESP8266, Portuguese) <http://pedrominatel.com.br/esp8266/estacao-meteorologica-com-esp8266/>`_
* May 16, 2016 - **Pedro Minatel** - `Controle remoto WiFi com ESP8266 (WiFi remote control using ESP8266, Portuguese) <http://pedrominatel.com.br/esp8266/controle-remoto-wifi-com-esp8266/>`_
* May 08, 2016 - **Radoslaw Bob** - `Touch controlled buzzer (Nodemcu ESP8266) <https://gettoknowthebob.wordpress.com/2016/05/08/touch-controlled-buzzer-nodemcu-esp8266/>`_
* Mar 07, 2016 - **Joran Jessurun** - `Nieuwe wereld met PlatformIO (New world with PlatformIO, Dutch) <http://blog.wisclub.nl/#post178>`_
* Feb 25, 2016 - **NutDIY** - `PlatformIO Blink On Nodemcu Dev Kit V1.0 (ESP 12-E) <http://nutdiy.blogspot.com/2016/02/platformio-blink-on-nodemcu-dev-kit-v10.html>`_
* Feb 23, 2016 - **Ptarmigan Labs** - `ESP8266 Over The Air updating – what are the options? <https://ptarmiganlabs.com/blog/2016/02/23/esp8266-over-the-air-updating-what-are-the-options/>`_
* Jan 16, 2016 - **Dani Eichhorn** - `ESP8266 Arduino IDE Alternative: PlatformIO <http://blog.squix.ch/2016/01/esp8266-arduino-ide-alternative.html>`_
* Dec 22, 2015 - **Jan Penninkhof** - `Over-the-Air ESP8266 programming using PlatformIO <http://www.penninkhof.com/2015/12/1610-over-the-air-esp8266-programming-using-platformio/>`_
* Dec 01, 2015 - **Tateno Yuichi** - `ESP8266 を CUI で開発する (Develop a ESP8266 in CUI, Japanese) <http://jaywiggins.com/platformio/arduino/avr/es8266/2015/09/30/platformio-investigation/>`_

See more :ref:`articles`.

Examples
--------

All project examples are located in PlatformIO repository
`Examples for Espressif platform <https://github.com/platformio/platformio-examples/tree/develop/espressif>`_.

* `Native SDK <https://github.com/platformio/platformio-examples/tree/develop/espressif/esp8266-native>`_
* `WebServer <https://github.com/platformio/platformio-examples/tree/develop/espressif/esp8266-webserver>`_
* `WiFiScan <https://github.com/platformio/platformio-examples/tree/develop/espressif/esp8266-wifiscan>`_
