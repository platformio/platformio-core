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

.. _ci_travis:

Travis CI
=========

.. image:: ../_static/ci-travis-logo.png
    :target: https://docs.travis-ci.com/user/integration/platformio/


**Travis CI** `officially supports <https://docs.travis-ci.com/user/integration/platformio/>`_
**PlatformIO for Embedded Builds.**

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
        # http://platformio.org/lib/show/1/OneWire
        - platformio lib install 1

Manually download dependent library and include in build process via ``--lib`` option
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    install:
        - pip install -U platformio

        # download library to the temporary directory
        - wget https://github.com/PaulStoffregen/OneWire/archive/master.zip -O /tmp/onewire_source.zip
        - unzip /tmp/onewire_source.zip -d /tmp/

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

        - export PLATFORMIO_BUILD_FLAGS=-D GLOBAL_MACROS_FOR_ALL_TEST_ENV


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

1. Custom build flags

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
        # http://platformio.org/lib/show/416/TinyGPS
        # http://platformio.org/lib/show/417/SPI4Teensy3
        - platformio lib install 416 417

    script:
        - platformio ci --board=uno --board=teensy31 --board=due --lib="."

* Configuration file: https://github.com/felis/USB_Host_Shield_2.0/blob/master/.travis.yml
* Build History: https://travis-ci.org/felis/USB_Host_Shield_2.0

2. Dependency on external libraries

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
        - PLATFORMIO_CI_SRC=examples/backSoon/backSoon.ino
        - PLATFORMIO_CI_SRC=examples/etherNode/etherNode.ino
        # -

    install:
        - pip install -U platformio

        - wget https://github.com/jcw/jeelib/archive/master.zip -O /tmp/jeelib.zip
        - unzip /tmp/jeelib.zip -d /tmp

        - wget https://github.com/Rodot/Gamebuino/archive/master.zip  -O /tmp/gamebuino.zip
        - unzip /tmp/gamebuino.zip -d /tmp

    script:
        - platformio ci --lib="." --lib="/tmp/jeelib-master" --lib="/tmp/Gamebuino-master/libraries/tinyFAT" --board=uno --board=megaatmega2560

* Configuration file: https://github.com/jcw/ethercard/blob/master/.travis.yml
* Build History: https://travis-ci.org/jcw/ethercard

3. Dynamic testing of the boards

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
        - PLATFORMIO_CI_SRC=examples/TimeArduinoDue PLATFORMIO_CI_EXTRA_ARGS="--board=due"
        - PLATFORMIO_CI_SRC=examples/TimeGPS
        - PLATFORMIO_CI_SRC=examples/TimeNTP
        - PLATFORMIO_CI_SRC=examples/TimeTeensy3 PLATFORMIO_CI_EXTRA_ARGS="--board=teensy31"
        # - ...

    install:
        - pip install -U platformio
        - rm -rf ./linux

        #
        # Libraries from PlatformIO Library Registry:
        #
        # http://platformio.org/lib/show/416/TinyGPS
        - platformio lib install 416 421 422

    script:
        - platformio ci --lib="." --board=uno --board=teensy20pp $PLATFORMIO_CI_EXTRA_ARGS

* Configuration file: https://github.com/ivankravets/Time/blob/master/.travis.yml
* Build History: https://travis-ci.org/ivankravets/Time
