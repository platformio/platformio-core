.. _cmd_ci:

platformio ci
=============

.. contents::

Usage
-----

.. code-block:: bash

    platformio ci [OPTIONS] [SRC]


Description
-----------

`Continuous integration (CI, wiki) <http://en.wikipedia.org/wiki/Continuous_integration>`_
is the practice, in software engineering, of merging all developer working
copies with a shared mainline several times a day.

:ref:`cmd_ci` command is conceived of as "hot key" for building project with
arbitrary source code structure. In a nutshell, using ``SRC`` and
:option:`platformio ci --lib` contents PlatformIO initialises via
:ref:`cmd_init` new project in :option:`platformio ci --build-dir`
with the build environments (using :option:`platformio ci --board` or
:option:`platformio ci --project-conf`) and processes them via :ref:`cmd_run`
command.

:ref:`cmd_ci` command is intended to be used in combination with the build
servers and the popular
`Continuous Integration Software <http://en.wikipedia.org/wiki/Comparison_of_continuous_integration_software>`_.

By integrating regularly, you can detect errors quickly, and locate them more
easily.

.. note::
    :ref:`cmd_ci` command accepts **multiple** ``SRC`` arguments,
    :option:`platformio ci --lib` and :option:`platformio ci --exclude` options
    which can be a path to directory, file or
    `Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_.

Options
-------

.. program:: platformio ci

.. option::
    -l, --lib

Source code which will be copied to ``%build_dir%/lib`` directly.

If :option:`platformio ci --lib` is a path to file (not to directory), then
PlatformIO will create temporary directory within ``%build_dir%/lib`` and copy
the rest files into it.


.. option::
    --exclude

Exclude directories and/-or files from :option:`platformio ci --build-dir`. The
path must be relative to PlatformIO project within
:option:`platformio ci --build-dir`.

For example, exclude from project ``src`` directory:

* ``examples`` folder
* ``*.h`` files from ``foo`` folder

.. code-block:: bash

    platformio ci --exclude=src/examples --exclude=src/foo/*.h [SRC]

.. option::
    --board, -b

Build project with automatically pre-generated environments based on board
settings.

For more details please look into :option:`platformio init --board`.

.. option::
    --build-dir

Path to directory where PlatformIO will initialise new project. By default it's
temporary directory within your operation system.

.. note::

    This directory will be removed at the end of build process. If you want to
    keep it, please use :option:`platformio ci --keep-build-dir`.

.. option::
    --keep-build-dir

Don't remove :option:`platformio ci --build-dir` after build process.

.. option::
    --project-conf

Buid project using pre-configured :ref:`projectconf`.

Examples
--------

1. Integration `Travis.CI <http://travis-ci.org/>`_ for GitHub
   `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``.travis.yml`` configuration file:

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    env:
        - PLATFORMIO_CI_SRC=examples/Bluetooth/PS3SPP/PS3SPP.ino
        - PLATFORMIO_CI_SRC=examples/pl2303/pl2303_gps/pl2303_gps.ino

    install:
        - python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"

    script:
        - platformio ci --lib="." --board=uno --board=teensy31 --board=due
