.. _quickstart:

Quickstart
==========

.. note::
    Please read `Get Started <http://platformio.org/#!/get-started>`_
    article from the official WebSite.

1. :ref:`Install PlatformIO <installation>`.

2. Find board ``type`` from :ref:`platforms` (you can choose multiple board
   types).

3. Initialize new PlatformIO based project with the pre-configured
   environments for your boards:

.. code-block:: bash

    $ platformio init --board=TYPE1 --board=TYPE2

    The current working directory *** will be used for the new project.
    You can specify another project directory via
    `platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.

    The next files/directories will be created in ***
    `platformio.ini` - Project Configuration File
    `src` - a source directory. Put your source code here
    `lib` - a directory for the project specific libraries
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Now you can process it with `platformio run` command.

More detailed information about this command is here :ref:`cmd_init`.

4. Process the project's environments.

.. code-block:: bash

    $ platformio run

    # if you don't have specified `targets = upload` option for environment,
    # then you can upload firmware manually with this command:
    $ platformio run --target upload

    # clean project
    $ platformio run --target clean

If you don't have installed required platforms, then *PlatformIO* will propose
you to install them automatically.

Further examples can be found in the ``examples/`` directory in the source
distribution or `on the web <https://github.com/ivankravets/platformio/tree/develop/examples>`_.

Also, for more detailed information as for commands please go to
:ref:`userguide` sections.
