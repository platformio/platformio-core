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

.. _board_creating:

Custom Board
============

*PlatformIO* has pre-built settings for the most popular embedded boards. This
list is available:

* `Embedded Boards Explorer <http://platformio.org/#!/boards>`_ (Web)
* :ref:`cmd_boards` (CLI command)

Nevertheless, PlatformIO allows to create own board or override existing
board's settings. All data is declared using
`JSON-style <http://en.wikipedia.org/wiki/JSON>`_ via
`associative array <http://en.wikipedia.org/wiki/Associative_array>`_
(name/value pairs).

.. contents::

JSON Structure
--------------

The key fields:

* ``build`` data will be used by :ref:`Platforms <platforms>` and
  :ref:`frameworks` builders
* ``frameworks`` is the list with supported :ref:`frameworks`
* ``platform`` main type of :ref:`Platforms <platforms>`
* ``upload`` upload settings which depend on the ``platform``

.. code-block:: json

    {
        "myboard": {
            "build": {},
            "frameworks": ["%LIST_WITH_SUPPORTED_FRAMEWORKS%"],
            "name": "My test board",
            "platform": "%PLATFORM_TYPE_HERE%",
            "upload": {},
            "url": "http://example.com",
            "vendor": "My Company Ltd."
        }
    }

Installation
------------

1. Create ``boards`` directory in :ref:`projectconf_pio_home_dir` if it
   doesn't exist.
2. Create ``my_own_boards.json`` file and put to ``boards`` directory.
3. Search available boards via :ref:`cmd_boards` command. You should see
   ``myboard`` board.

Now, you can use ``myboard`` for the :ref:`projectconf_env_board` option in
:ref:`projectconf`.


Examples
--------

For the examples, please look into built-in ``*.json`` files with boards
settings: https://github.com/platformio/platformio/tree/develop/platformio/boards.
