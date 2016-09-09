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

.. _cmd_init:

platformio init
===============

.. contents::

Usage
-----

.. code-block:: bash

    platformio init [OPTIONS]


Description
-----------

Initialize new PlatformIO based project or update existing with new data.


This command will create:

* :ref:`projectconf`
* ``src`` directory where you should place source code
  (``*.h, *.c, *.cpp, *.S, *.ino, etc.``)
* ``lib`` directory can be used for the project specific (private) libraries.
  More details are located in ``lib/readme.txt`` file.
* Miscellaneous files for VCS and :ref:`ci` support.

Options
-------

.. program:: platformio init

.. option::
    -d, --project-dir

A path to the directory where *PlatformIO* will initialize new project.

.. option::
    -b, --board

If you specify board ``ID`` (you can pass multiple ``--board`` options), then
*PlatformIO* will automatically generate environment for :ref:`projectconf` and
pre-fill these data:

* :ref:`projectconf_env_platform`
* :ref:`projectconf_env_framework`
* :ref:`projectconf_env_board`

The full list with pre-configured boards is available here :ref:`platforms`.

.. option::
    --ide

Initialize PlatformIO project for the specified IDE which can be imported later
via "Import Project" functionality.

A list with supported IDE is available within ``platformio init --help`` command.
Also, please take a look at :ref:`ide` page.

.. option::
    -O, --project-option

Initialize project with additional options from :ref:`projectconf`. For example,
``platformio init --project-option="lib_deps=ArduinoJSON"``.

.. option::
    --env-prefix

An environment prefix which will be used with pair in board type.
For example, the default environment name for ``teensy_31`` board will
be ``[env:teensy_31]``.



Examples
--------

1. Create new project in the current working directory

.. code-block:: bash

    $ platformio init

    The current working directory *** will be used for the new project.
    You can specify another project directory via
    `platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.

    The next files/directories will be created in ***
    platformio.ini - Project Configuration File. |-> PLEASE EDIT ME <-|
    src - Put your source files here
    lib - Put here project specific (private) libraries
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)


2. Create new project in the specified directory

.. code-block:: bash

    $ platformio init -d %PATH_TO_DIR%

    The next files/directories will be created in ***
     platformio.ini - Project Configuration File. |-> PLEASE EDIT ME <-|
    src - Put your source files here
    lib - Put here project specific (private) libraries
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)

3. Initialize project for Arduino Uno

.. code-block:: bash

    $ platformio init --board uno

    The current working directory *** will be used for the new project.
    You can specify another project directory via
    `platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.

    The next files/directories will be created in ***
    platformio.ini - Project Configuration File. |-> PLEASE EDIT ME <-|
    src - Put your source files here
    lib - Put here project specific (private) libraries
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)
