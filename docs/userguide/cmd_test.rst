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

.. _cmd_test:

platformio test
===============

.. versionadded:: 3.0

.. contents::

Usage
-----

.. code-block:: bash

    platformio test [OPTIONS]

Description
-----------

Run tests from PlatformIO based project. More details about PlatformIO
:ref:`unit_testing`.

This command allows you to apply the tests for the environments specified
in :ref:`projectconf`.

Options
-------

.. program:: platformio test

.. option::
    -e, --environment

Process specified environments. More details :option:`platformio run --environment`

.. option::
    --skip

Skip over tests where the name matches specified patterns. More than one
option/pattern is allowed.

.. list-table::
    :header-rows:  1

    * - Pattern
      - Meaning

    * - ``*``
      - matches everything

    * - ``?``
      - matches any single character

    * - ``[seq]``
      - matches any character in seq

    * - ``[!seq]``
      - matches any character not in seq

For example, ``platformio test --skip "mytest*" -i "test[13]"``

.. option::
    --upload-port

Upload port of embedded board. To print all available ports use
:ref:`cmd_serialports` command.

If upload port is not specified, PlatformIO will try to detect it automatically.

.. option::
    -d, --project-dir

Specify the path to project directory. By default, ``--project-dir`` is equal
to current working directory (``CWD``).

.. option::
    -v, --verbose

Shows detailed information when processing environments.

This option can be set globally using :ref:`setting_force_verbose` setting
or by environment variable :envvar:`PLATFORMIO_SETTING_FORCE_VERBOSE`.

Examples
--------

For the examples please follow to :ref:`unit_testing` page.
