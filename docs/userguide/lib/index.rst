..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _userguide_lib:

Library Manager
===============

Usage
-----

.. code-block:: bash

    platformio lib [OPTIONS] COMMAND

    # To print all available commands and options use
    platformio lib --help
    platformio lib COMMAND --help

Options
-------

.. program:: platformio lib

.. option::
     -g, --global

.. versionadded:: 3.0


Manage global PlatformIO's library storage (
":ref:`projectconf_pio_home_dir`/lib") where :ref:`ldf` will look for
dependencies by default.

.. option::
    -d, --storage-dir

.. versionadded:: 3.0

Manage custom library storage. It can be used later for the
:ref:`projectconf_extra_script` option from :ref:`projectconf`.

Demo
----

.. image:: ../../_static/platformio-demo-lib.gif

Commands
--------

.. toctree::
    :maxdepth: 2

    cmd_install
    cmd_list
    cmd_register
    cmd_search
    cmd_show
    cmd_uninstall
    cmd_update
