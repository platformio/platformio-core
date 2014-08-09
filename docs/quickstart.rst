.. _quickstart:

Quickstart
==========

First, :ref:`Install PlatformIO <installation>`.

Print all available development platforms for installing

.. code-block:: bash

    $ platformio search all
    [ ... ]


Install new development platform

.. code-block:: bash

    $ platformio install PLATFORM
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing .....
    [ ... ]
    The platform 'PLATFORM' has been successfully installed!


Initialize new PlatformIO based project

.. code-block:: bash

    $ cd /path/to/empty/directory
    $ platformio init
    Project has been initialized!
    Please put your source code to `src` directory, external libraries to `lib`
    and setup environments in `platformio.ini` file.
    Then process project with `platformio run` command.

Process the project's environments

.. code-block:: bash

    $ platformio run

    # if embedded project then upload firmware
    $ platformio run --target upload

    # clean project
    $ platformio run --target clean


For more detailed information please go to :ref:`userguide` sections.
