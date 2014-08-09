.. _cmd_init:

platformio init
===============

.. contents::

Usage
-----

.. code-block:: bash

    platformio init


Description
-----------

Initialize new PlatformIO based project.


This command will create:

* ``.pioenvs`` - a temporary working directory.
* ``lib`` - a directory for project specific libraries. PlatformIO will
  compile them to static libraries and link to executable file
* ``src`` - a source directory. Put your source code here.
* :ref:`projectconf`


Examples
--------

.. code-block:: bash

    # Change directory to the future project
    $ cd /path/to/empty/directory
    $ platformio init
    Project has been initialized!
    Please put your source code to `src` directory, external libraries to `lib`
    and setup environments in `platformio.ini` file.
    Then process project with `platformio run` command.
