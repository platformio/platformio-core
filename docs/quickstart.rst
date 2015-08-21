.. _quickstart:

Quickstart
==========

.. note::
    Please read `Get Started <http://platformio.org/#!/get-started>`_
    article from the official WebSite.

1. :ref:`Install PlatformIO <installation>`.

2. Find board ``type`` using `Embedded Boards Explorer <http://platformio.org/#!/boards>`_
   or via :ref:`cmd_boards` command.

3. Initialize new PlatformIO based project via :ref:`cmd_init` command with the
   pre-configured environments for your boards:

.. code-block:: bash

    $ platformio init --board=TYPE_1 --board=TYPE_2 --board=TYPE_N

    Would you like to enable firmware auto-uploading when project is successfully built using `platformio run` command?
    Don't forget that you can upload firmware manually using `platformio run --target upload` command. [y/N]: y

    The current working directory *** will be used for the new project.
    You can specify another project directory via
    `platformio init -d %PATH_TO_THE_PROJECT_DIR%` command.

    The next files/directories will be created in ***
    platformio.ini - Project Configuration File. |-> PLEASE EDIT ME <-|
    src - Put your source code here
    lib - Put here project specific (private) libraries
    Do you want to continue? [y/N]: y
    Project has been successfully initialized!
    Useful commands:
    `platformio run` - process/build project from the current directory
    `platformio run --target upload` or `platformio run -t upload` - upload firmware to embedded board
    `platformio run --target clean` - clean project (remove compiled files)

Put your source code ``*.h, *.c, *.cpp or *.ino`` files to ``src`` directory.

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

If you don't have installed required platforms, then *PlatformIO* will propose
you to install them automatically.

Further examples can be found in `PlatformIO Repository <https://github.com/platformio/platformio/tree/develop/examples>`_.

Also, for more detailed information as for commands please go to
:ref:`userguide` sections.
