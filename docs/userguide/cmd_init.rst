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

.. option::
    --project-dir, -d

Specified path to the directory where *PlatformIO* will initialize new project.


Examples
--------

1. Create new project in the current working directory

.. code-block:: bash

    $ platformio init
    The current working directory *** will be used for the new project.
    You can specify another project directory via
    `platformio init -d %PATH_TO_PROJECT_DIR%` command.

    The next files/directories will be created in ***
    platformio.ini - Project Configuration File
    src - a source directory. Put your source code here
    lib - a directory for the project specific libraries
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Now you can process it with `platformio run` command.


2. Create new project in the specified directory

.. code-block:: bash

    $ platformio init -d %PATH_TO_DIR%
    The next files/directories will be created in ***
    platformio.ini - Project Configuration File
    src - a source directory. Put your source code here
    lib - a directory for the project specific libraries
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Now you can process it with `platformio run` command.
