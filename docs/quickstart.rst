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

.. _quickstart:

Quickstart
==========

.. note::
    Please read `Get Started <http://platformio.org/#!/get-started>`_
    from the official WebSite.

PlatformIO IDE
--------------

Please follow to the Quickstart section of :ref:`ide_atom`.

PlatformIO CLI
--------------

1. :ref:`installation`.

2. Find board ``type`` using `Embedded Boards Explorer <http://platformio.org/#!/boards>`_
   or via :ref:`cmd_boards` command.

3. Initialize new PlatformIO based project via :ref:`cmd_init` command with the
   pre-configured environments for your boards:

.. code-block:: bash

    $ platformio init --board=TYPE_1 --board=TYPE_2 --board=TYPE_N

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

Put your source files ``*.h, *.c, *.cpp or *.ino`` to ``src`` directory.

4. Process the project's environments.

Change working directory to the project's root where is located
:ref:`Project Configuration File (platformio.ini) <projectconf>` and run:

.. code-block:: bash

    $ platformio run

    # if you don't have specified `targets = upload` option for environment,
    # then you can upload firmware manually with this command:
    $ platformio run --target upload

    # clean project
    $ platformio run --target clean


Useful links:

* `Project examples <https://github.com/platformio/platformio/tree/develop/examples>`_
* :ref:`userguide` for PlatformIO commands
* `Quickstart for Espressif ESP8266 <https://github.com/esp8266/Arduino/blob/master/doc/platformio.md>`_
