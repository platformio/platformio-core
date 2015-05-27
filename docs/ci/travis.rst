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

Integration
-----------

Please put ``.travis.yml`` to the root directory of the GitHub repository.

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    env:
        - PLATFORMIO_CI_SRC=path/to/source/file.c
        - PLATFORMIO_CI_SRC=path/to/source/file.ino
        - PLATFORMIO_CI_SRC=path/to/source/directory

    install:
        - python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"

    script:
        - platformio ci --board=TYPE_1 --board=TYPE_2 --board=TYPE_N


Then see step 1, 2, and step 4 here: http://docs.travis-ci.com/user/getting-started/

For more details as for PlatformIO build process please look into :ref:`cmd_ci`
command.

Examples
--------

1. Integration for `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``.travis.yml`` configuration file:

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    env:
        - PLATFORMIO_CI_SRC=examples/acm/acm_terminal
        - PLATFORMIO_CI_SRC=examples/Bluetooth/WiiIRCamera PLATFORMIO_BUILD_FLAGS="-DWIICAMERA"
        - PLATFORMIO_CI_SRC=examples/ftdi/USBFTDILoopback
        - PLATFORMIO_CI_SRC=examples/Xbox/XBOXUSB
        # - ...

    install:
        - python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"

        # Libraries from PlatformIO Library Registry
        # http://platformio.org/#!/lib/show/416/TinyGPS
        # http://platformio.org/#!/lib/show/417/SPI4Teensy3
        - platformio lib install 416 417

    script:
        - platformio ci --board=uno --board=teensy31 --board=due --lib="."

* Configuration file: https://github.com/felis/USB_Host_Shield_2.0/blob/master/.travis.yml
* Build History: https://travis-ci.org/felis/USB_Host_Shield_2.0
