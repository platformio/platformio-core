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

.. _quickstart:

Quick Start
===========

.. note::
    If you are looking for a Quick Start for PlatformIO IDE please follow to
    :ref:`PlatformIO IDE Quick Start <atom_ide_quickstart>` page.

This tutorial introduces you to the basics of PlatformIO Command Line Interface
(CLI) workflow and shows you a creation process of a simple cross-platform
“Blink” Project. After finishing you will have a general understanding of how
to work with the multiple development platforms and embedded boards.

Setting Up the Project
----------------------

PlatformIO CLI provides special :ref:`cmd_init` command for configuring your projects.
It allows to initialize new empty project or update existing with the new data.

What is more, :ref:`cmd_init` can be used for :ref:`ide`. It means that you will
be able to import pre-generated PlatformIO project using favorite IDE and
extend it with the professional instruments for IoT development.

This tutorial is based on the next popular embedded boards and development
platforms using *Arduino Wiring-based Framework*:


.. list-table::
    :header-rows:  1

    * - Platform
      - Board
      - Framework

    * - Atmel AVR
      - Arduino Uno (8-bit ATmega328P)
      - Arduino Wiring-based Framework

    * - Espressif
      - NodeMCU 1.0 (32-bit ESP8266)
      - Arduino Wiring-based Framework

    * - Teensy
      - Teensy 3.1 (32-bit ARM MK20DX256)
      - Arduino Wiring-based Framework

Board Identifier
----------------

:ref:`cmd_init` command requires to specify board identifier (ID/TYPE). It can
be found using `Embedded Boards Explorer <http://platformio.org/boards>`_
or :ref:`cmd_boards` command. For example, using :ref:`cmd_boards` let's try
to find Teensy boards:

.. code-block:: bash

    > platformio boards teensy

    Platform: teensy
    ---------------------------------------------------------------------------
    Type                  MCU            Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    teensy20              atmega32u4     16Mhz     31kB    2.5kB  Teensy 2.0
    teensy30              mk20dx128      48Mhz     128kB   16kB   Teensy 3.0
    teensy31              mk20dx256      72Mhz     256kB   64kB   Teensy 3.1 / 3.2
    teensylc              mkl26z64       48Mhz     62kB    8kB    Teensy LC
    teensy20pp            at90usb1286    16Mhz     127kB   8kB    Teensy++ 2.0

According to the table above the ID/TYPE for Teensy 3.1 is ``teensy31``. Also,
the ID for Arduino UNO is ``uno`` and for NodeMCU 1.0 (ESP-12E Module)
is ``nodemcuv2``.

Initialize Project
------------------

PlatformIO ecosystem contains big database with pre-configured settings for the
most popular embedded boards. It helps you to forget about installing
toolchains, writing build scripts or configuring uploading process. Just tell
PlatformIO the Board ID and you will receive full working project with
pre-installed instruments for the professional development.

1.  Create empty folder where you are going to initialize new PlatformIO
    project. Then open system Terminal and change directory to it:

    .. code-block:: bash

        # create new direcotry
        > mkdir path_to_the_new_directory

        # go to it
        > cd path_to_the_new_directory

2.  Initialize project for the boards mentioned above (you can specify more
    than one board at time):

    .. code-block:: bash

        > platformio init --board uno --board nodemcuv2 --board teensy31

        The current working directory *** will be used for the new project.
        You can specify another project directory via
        `platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.

        The next files/directories will be created in ***
        platformio.ini - Project Configuration File. |-> PLEASE EDIT ME <-|
        src - Put your source files here
        lib - Put here project specific (private) libraries
        Do you want to continue? [y/N]: y
        Project has been successfully initialized!
        Useful commands:
        `platformio run` - process/build project from the current directory
        `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
        `platformio run --target clean` - clean project (remove compiled files)


Congrats! You have just created the first PlatformIO based Project with the
next structure:

* :ref:`projectconf`
* ``src`` directory where you should place source code
  (``*.h, *.c, *.cpp, *.S, *.ino, etc.``)
* ``lib`` directory can be used for the project specific (private) libraries.
  More details are located in ``lib/readme.txt`` file.
* Miscellaneous files for VCS and :ref:`ci` support.


.. note::
    If you need to add new board to the existing project please use
    :ref:`cmd_init` again.


The result of just generated ``platformio.ini``:

.. code-block:: ini

    ; PlatformIO Project Configuration File
    ;
    ;   Build options: build flags, source filter, extra scripting
    ;   Upload options: custom port, speed and extra flags
    ;   Library options: dependencies, extra library storages
    ;
    ; Please visit documentation for the other options and examples
    ; http://docs.platformio.org/en/stable/projectconf.html

    [env:uno]
    platform = atmelavr
    framework = arduino
    board = uno

    [env:nodemcuv2]
    platform = espressif8266
    framework = arduino
    board = nodemcuv2

    [env:teensy31]
    platform = teensy
    framework = arduino
    board = teensy31


Now, we need to create ``main.cpp`` file and place it to ``src`` folder of our
newly created project. The contents of ``src/main.cpp``:

.. code-block:: cpp

    /**
     * Blink
     *
     * Turns on an LED on for one second,
     * then off for one second, repeatedly.
     */
    #include "Arduino.h"

    void setup()
    {
      // initialize LED digital pin as an output.
      pinMode(LED_BUILTIN, OUTPUT);
    }

    void loop()
    {
      // turn the LED on (HIGH is the voltage level)
      digitalWrite(LED_BUILTIN, HIGH);

      // wait for a second
      delay(1000);

      // turn the LED off by making the voltage LOW
      digitalWrite(LED_BUILTIN, LOW);

       // wait for a second
      delay(1000);
    }


The final Project structure:

.. code-block:: bash

    project_dir
    ├── lib
    │   └── readme.txt
    ├── platformio.ini
    └── src
        └── main.cpp


Process Project
---------------

PlatformIO CLI provides special :ref:`cmd_run` command to process project. If
you call it without any arguments, PlatformIO Build System will process all
project environments (which were created per each board specified above). Here
are a few useful commands:

* ``platformio run``. Process (build) all environments specified in
  :ref:`projectconf`
* ``platformio run --target upload``. Build project and upload firmware to the
  all devices specified in :ref:`projectconf`
* ``platformio run --target clean``. Clean project (delete compiled objects)
* ``platformio run -e uno``. Process only ``uno`` environment
* ``platformio run -e uno -t upload``. Build project only for ``uno`` and upload
  firmware.

Please follow to :option:`platformio run --target` documentation for the other
targets.

Finally, demo which demonstrates building project and uploading firmware to
Arduino Uno:

.. image:: _static/platformio-demo-wiring.gif

Further Reading
---------------

* `Project examples <https://github.com/platformio/platformio-examples/tree/develop>`_
* :ref:`userguide` for PlatformIO CLI commands
