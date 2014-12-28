.. _quickstart:

Quickstart
==========

.. note::
    Please read `Get Started <http://platformio.ikravets.com/#!/get-started>`_
    article from the official WebSite.

First, :ref:`Install PlatformIO <installation>`.

Print all available development platforms for installing

.. code-block:: bash

    $ platformio search
    [ ... ]


Install new development platform

.. code-block:: bash

Does not work for Mac OS X 10.6.8; returns
$ ./platformio install atmelavr
Installing toolchain-atmelavr package:
Error: The package 'toolchain-atmelavr' is not available for your system 'darwin_i386'

    $ platformio install PLATFORM
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing .....
    [ ... ]
    The platform 'PLATFORM' has been successfully installed!


Initialize new PlatformIO based project

.. code-block:: bash

    $ platformio init
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


Setup environments in ``platformio.ini``. For more examples go to
:ref:`Project Configuration File <projectconf_examples>`

.. code-block:: ini

    # Simple and base environment
    [env:mybaseenv]
    platform = %INSTALLED_PLATFORM_NAME_HERE%


Process the project's environments

.. code-block:: bash

    $ platformio run

    # if embedded project then upload firmware
    $ platformio run --target upload

    # clean project
    $ platformio run --target clean


Further examples can be found in the ``examples/`` directory in the source
distribution or `on the web <https://github.com/ivankravets/platformio/tree/develop/examples>`_.

Also, for more detailed information as for commands please go to
:ref:`userguide` sections.
