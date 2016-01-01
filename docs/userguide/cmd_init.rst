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
* ``src`` - a source directory. Put your source files here
* ``lib`` - a directory for the project specific (private) libraries.
  PlatformIO will compile them to static libraries and link to executable file
* ``.travis.yml`` configuration file (template) for Continuous Integration
  with :ref:`ci_travis`

.. note::
    The source code of each library should be placed in separate directory.
    For example, ``lib/private_lib/[here are source files]``.

Options
-------

.. program:: platformio init

.. option::
    -d, --project-dir

A path to the directory where *PlatformIO* will initialise new project.

.. option::
    -b, --board

If you specify board ``type`` (you can pass multiple ``--board`` options), then
*PlatformIO* will automatically generate environment for :ref:`projectconf` and
pre-fill these data:

* :ref:`projectconf_env_platform`
* :ref:`projectconf_env_framework`
* :ref:`projectconf_env_board`

The full list with pre-configured boards is available here :ref:`platforms`.

.. option::
    --ide

Initialise PlatformIO project for the specified IDE which can be imported later
via "Import Project" functionality.

A list with supported IDE is available within ``platformio init --help`` command.
Also, please take a look at :ref:`ide` page.

.. option::
    --enable-auto-uploading

If you initialise project with the specified
:option:`platformio init --board`, then *PlatformIO*
will create environment with enabled firmware auto-uploading.

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
    Do you want to continue? [y/N]: y
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
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)

3. Initialise project for Arduino Uno

.. code-block:: bash

    $ platformio init --board uno

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
