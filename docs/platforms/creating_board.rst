..  Copyright 2014-present Ivan Kravets <me@ikravets.com>
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

* `Embedded Boards Explorer <http://platformio.org/boards>`_ (Web)
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

* ``build`` data will be used by :ref:`platforms` and :ref:`frameworks` builders
* ``frameworks`` is the list with supported :ref:`frameworks`
* ``platform`` name of :ref:`platforms`
* ``upload`` upload settings which depend on the ``platform``

.. code-block:: json

    {
      "build": {
        "extra_flags": "-DHELLO_PLATFORMIO",
        "f_cpu": "16000000L",
        "hwids": [
          [
            "0x1234",
            "0x0013"
          ],
          [
            "0x4567",
            "0x0013"
          ]
        ],
        "mcu": "%MCU_TYPE_HERE%"
      },
      "frameworks": ["%LIST_WITH_SUPPORTED_FRAMEWORKS%"],
      "name": "My Test Board",
      "upload": {
        "maximum_ram_size": 2048,
        "maximum_size": 32256
      },
      "url": "http://example.com",
      "vendor": "MyCompany"
    }


Installation
------------

1. Create ``boards`` directory in :ref:`projectconf_pio_home_dir` if it
   doesn't exist.
2. Create ``myboard.json`` file and put to ``boards`` directory.
3. Search available boards via :ref:`cmd_boards` command. You should see
   ``myboard`` board.

Now, you can use ``myboard`` for the :ref:`projectconf_env_board` option in
:ref:`projectconf`.


Examples
--------

Please take a look at the source code of
`PlatformIO Development Platforms <https://github.com/platformio?query=platform->`_
and navigate to ``boards`` folder of the repository.
