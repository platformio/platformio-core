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

Initialize new PlatformIO based project.


This command will create:

* :ref:`projectconf`
* ``src`` - a source directory. Put your source code here
* ``lib`` - a directory for the project specific libraries. PlatformIO will
  compile them to static libraries and link to executable file

Options
-------

.. program:: platformio init

.. option::
    --project-dir, -d

A path to the directory where *PlatformIO* will initialise new project.

.. option::
    --board, -b

If you specify board ``type`` (you can pass multiple ``--board`` options), then
*PlatformIO* will automatically generate environment for :ref:`projectconf` and
pre-fill these data:

* :ref:`projectconf_env_platform`
* :ref:`projectconf_env_framework`
* :ref:`projectconf_env_board`

The full list with pre-configured boards is available here :ref:`platforms`.

.. option::
    --disable-auto-uploading

If you initialise project with the specified
:option:`platformio init --board``, then *PlatformIO*
will create environment with enabled firmware auto-uploading. This option
allows you to disable firmware auto-uploading by default.

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
    src - Put your source code here
    lib - Put here project specific or 3-rd party libraries
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
    src - Put your source code here
    lib - Put here project specific or 3-rd party libraries
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)

3. Initialise project for Arduino Uno

.. code-block:: bash

    $ platformio init --board uno

    Would you like to enable firmware auto-uploading when project is successfully built using `platformio run` command?
    Don't forget that you can upload firmware manually using `platformio run --target upload` command. [y/N]: y

    The current working directory *** will be used for the new project.
    You can specify another project directory via
    `platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.

    The next files/directories will be created in ***
    platformio.ini - Project Configuration File. |-> PLEASE EDIT ME <-|
    src - Put your source code here
    lib - Put here project specific or 3-rd party libraries
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)
