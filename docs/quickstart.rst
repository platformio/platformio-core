.. _quickstart:

Quickstart
==========

.. note::
    Please read `Get Started <http://platformio.ikravets.com/#!/get-started>`_
    article from the official WebSite.

First, :ref:`Install PlatformIO <installation>`.

Print all available development platforms for installing

.. code-block:: bash

    $ platformio search all
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

    $ cd /path/to/empty/directory
    $ platformio init
    Project has been initialized!
    Please put your source code to `src` directory, external libraries to `lib`
    and setup environments in `platformio.ini` file.
    Then process project with `platformio run` command.


Setup environments in ``platformio.ini``. For more examples go to
:ref:`projectconf`

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
