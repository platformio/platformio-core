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

.. _ide_atom:

Atom
====

`Atom <https://atom.io>`_ is a text editor that's modern, approachable,
yet hackable to the core—a tool you can customize to do anything but also use
productively without ever touching a config file.

This software can be used with:

* all available :ref:`platforms`
* all available :ref:`frameworks`

Refer to the `Atom Documentation <https://atom.io/docs>`_
page for more detailed information.

.. contents::

Integration
-----------

There is Atom based `platomformio <https://atom.io/packages/platomformio>`_
package which can be installed `Using Atom Packages <https://atom.io/docs/v1.0.2/using-atom-atom-packages>`_.

If you have ``clang`` installed in your system (is installed by default in Mac
OS X), you can enable completions using
`autocomplete-clang <https://github.com/yasuyuky/autocomplete-clang>`_ package.
This package requires ``.clang_complete`` file and PlatformIO can generate it.

Choose board ``type`` using :ref:`cmd_boards` or `Embedded Boards Explorer <http://platformio.org/#!/boards>`_
command and generate project via :option:`platformio init --ide` command:

.. code-block:: shell

    platformio init --ide atom --board %TYPE%

    # For example, generate project for Arduino UNO
    platformio init --ide atom --board uno

.. warning::
    The libraries which are added, installed or used in the project
    after generating process wont be reflected in IDE. To fix it you
    need to reinitialize project using :ref:`cmd_init` (repeat it).

Articles / Manuals
------------------

* Jan 16, 2016 - **Dani Eichhorn** - `ESP8266 Arduino IDE Alternative: PlatformIO <http://blog.squix.ch/2016/01/esp8266-arduino-ide-alternative.html>`_
* Dec 22, 2015 - **Jan Penninkhof** - `Over-the-Air ESP8266 programming using PlatformIO <http://www.penninkhof.com/2015/12/1610-over-the-air-esp8266-programming-using-platformio/>`_
* Jul 20, 2015 - **Eli Fatsi** - `Arduino Development in Atom Editor <http://viget.com/extend/arduino-development-in-atom-editor>`_

See more :ref:`articles`.

Screenshot
----------

Building
^^^^^^^^

.. image:: ../_static/ide-platformio-atom-1.gif
    :target: https://atom.io/packages/platomformio

Uploading
^^^^^^^^^

.. image:: ../_static/ide-platformio-atom-2.gif
    :target: https://atom.io/packages/platomformio
