.. _userguide:

User Guide
==========

.. contents::

Usage
-----

.. code-block:: bash

    platformio [OPTIONS] COMMAND

Options
-------

.. option::
    --force, - f

Force to accept any confirmation prompts. This option allows to avoid an issue
with :ref:`faq_troubleshooting_pioblocksprompt`

.. option::
    --version

Show the version of PlatformIO

.. option::
    --help

Show help for the available options and commands

.. code-block:: bash

    $ platformio --help
    $ platformio COMMAND --help


Commands
--------

.. toctree::
    :maxdepth: 2

    cmd_boards
    cmd_ci
    cmd_init
    platformio lib <lib/index>
    platformio platforms <platforms/index>
    cmd_run
    cmd_serialports
    cmd_settings
    cmd_update
    cmd_upgrade
