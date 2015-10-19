.. _ci_travis:

Travis CI
=========

`Travis CI <http://en.wikipedia.org/wiki/Travis_CI>`_ is an open-source hosted,
distributed continuous integration service used to build and test projects
hosted at `GitHub <http://en.wikipedia.org/wiki/GitHub>`_.

Travis CI is configured by adding a file named ``.travis.yml``, which is a
`YAML <http://en.wikipedia.org/wiki/YAML>`_ format text file, to the root
directory of the GitHub repository.

Travis CI automatically detects when a commit has been made and pushed to a
GitHub repository that is using Travis CI, and each time this happens, it will
try to build the project using :ref:`cmd_ci` command. This includes commits to
all branches, not just to the master branch. Travis CI will also build and run
pull requests. When that process has completed, it will notify a developer in
the way it has been configured to do so — for example, by sending an email
containing the build results (showing success or failure), or by posting a
message on an IRC channel. It can be configured to build project on a range of
different :ref:`platforms`.

.. contents::

Integration
-----------

Please make sure to read Travis CI `Getting Started <http://docs.travis-ci.com/user/getting-started/>`_
and `general build configuration <http://docs.travis-ci.com/user/customizing-the-build/>`_
guides first.

PlatformIO is written in Python and is recommended to be run within
`Travis CI Python isolated environment <http://docs.travis-ci.com/user/languages/python/#Travis-CI-Uses-Isolated-virtualenvs>`_:

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    # Cache PlatformIO packages using Travis CI container-based infrastructure
    sudo: false
    cache:
        directories:
            - "~/.platformio"

    env:
        - PLATFORMIO_CI_SRC=path/to/test/file.c
        - PLATFORMIO_CI_SRC=examples/file.ino
        - PLATFORMIO_CI_SRC=path/to/test/directory

    install:
        - pip install -U platformio

    script:
        - platformio ci --board=TYPE_1 --board=TYPE_2 --board=TYPE_N

Then perform steps 1, 2 and 4 from http://docs.travis-ci.com/user/getting-started/

For more details as for PlatformIO build process please look into :ref:`cmd_ci`.

Project as a library
~~~~~~~~~~~~~~~~~~~~

When project is written as a library (where own examples or testing code use
it), please use ``--lib="."`` option for :ref:`cmd_ci` command

.. code-block:: yaml

    script:
        - platformio ci --lib="." --board=TYPE_1 --board=TYPE_2 --board=TYPE_N

Library dependecies
~~~~~~~~~~~~~~~~~~~

There 2 options to test source code with dependent libraries:

Install dependent library using :ref:`librarymanager`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    install:
        - pip install -U platformio

        #
        # Libraries from PlatformIO Library Registry:
        #
        # http://platformio.org/#!/lib/show/1/OneWire
        platformio lib install 1

Manually download dependent library and include in build process via ``--lib`` option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    install:
        - pip install -U platformio

        # download library to the temporary directory
        wget https://github.com/PaulStoffregen/OneWire/archive/master.zip -O /tmp/onewire_source.zip
        unzip /tmp/onewire_source.zip -d /tmp/

    script:
        - platformio ci --lib="/tmp/OneWire-master" --board=TYPE_1 --board=TYPE_2 --board=TYPE_N

Custom Build Flags
~~~~~~~~~~~~~~~~~~

PlatformIO allows to specify own build flags using :envvar:`PLATFORMIO_BUILD_FLAGS` environment

.. code-block:: yaml

    env:
        - PLATFORMIO_CI_SRC=path/to/test/file.c PLATFORMIO_BUILD_FLAGS="-D SPECIFIC_MACROS_PER_TEST_ENV -I/extra/inc"
        - PLATFORMIO_CI_SRC=examples/file.ino
        - PLATFORMIO_CI_SRC=path/to/test/directory

    install:
        - pip install -U platformio

        export PLATFORMIO_BUILD_FLAGS=-D GLOBAL_MACROS_FOR_ALL_TEST_ENV


For the more details, please follow to
:ref:`available build flags/options <projectconf_build_flags>`.


Advanced configuration
~~~~~~~~~~~~~~~~~~~~~~

PlatformIO allows to configure multiple build environments for the single
source code using :ref:`projectconf`.

Instead of ``--board`` option, please use :option:`platformio ci --project-conf`

.. code-block:: yaml

    script:
        - platformio ci --project-conf=/path/to/platoformio.ini

Examples
--------

1. Integration for `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``.travis.yml`` configuration file:

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    # Cache PlatformIO packages using Travis CI container-based infrastructure
    sudo: false
    cache:
        directories:
            - "~/.platformio"

    env:
        - PLATFORMIO_CI_SRC=examples/acm/acm_terminal
        - PLATFORMIO_CI_SRC=examples/Bluetooth/WiiIRCamera PLATFORMIO_BUILD_FLAGS="-DWIICAMERA"
        - PLATFORMIO_CI_SRC=examples/ftdi/USBFTDILoopback
        - PLATFORMIO_CI_SRC=examples/Xbox/XBOXUSB
        # - ...

    install:
        - pip install -U platformio

        #
        # Libraries from PlatformIO Library Registry:
        #
        # http://platformio.org/#!/lib/show/416/TinyGPS
        # http://platformio.org/#!/lib/show/417/SPI4Teensy3
        - platformio lib install 416 417

    script:
        - platformio ci --board=uno --board=teensy31 --board=due --lib="."

* Configuration file: https://github.com/felis/USB_Host_Shield_2.0/blob/master/.travis.yml
* Build History: https://travis-ci.org/felis/USB_Host_Shield_2.0
