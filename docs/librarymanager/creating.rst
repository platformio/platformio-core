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

.. _library_creating:
.. |PIOAPICR| replace:: *PlatformIO Library Registry Crawler*

Creating Library
================

*PlatformIO* :ref:`librarymanager` doesn't have any requirements to a library
source code structure. The only one requirement is library's manifest file -
:ref:`library_config`. It can be located inside your library or in the another
location where |PIOAPICR| will have *HTTP* access.

Updates to existing libraries are done every 24 hours. In case a more urgent
update is required, you can post a request on PlatformIO `community <https://community.platformio.org/>`_.

.. contents::

Source Code Location
--------------------

There are a several ways how to share your library with the whole world
(see `examples <https://github.com/platformio/platformio-libmirror/tree/master/configs>`_).

You can hold a lot of libraries (split into separated folders) inside one of
the repository/archive. In this case, you need to specify ``include`` option of
:ref:`libjson_export` field to relative path to your library's source code.

At GitHub
^^^^^^^^^

**Recommended**

If a library source code is located at `GitHub <https://github.com>`_, then
you **need to specify** only these fields in the :ref:`library_config`:

* :ref:`libjson_name`
* :ref:`libjson_version` (is not required, but highly recommended for new :ref:`librarymanager`)
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_repository`

|PIOAPICR| will populate the rest fields, like :ref:`libjson_authors` with an
actual information from *GitHub*.

Example, `DallasTemperature <http://platformio.org/lib/show/54/DallasTemperature/manifest>`_:

.. code-block:: javascript

    {
      "name": "DallasTemperature",
      "keywords": "onewire, 1-wire, bus, sensor, temperature",
      "description": "Arduino Library for Dallas Temperature ICs (DS18B20, DS18S20, DS1822, DS1820)",
      "repository":
      {
        "type": "git",
        "url": "https://github.com/milesburton/Arduino-Temperature-Control-Library.git"
      },
      "authors":
      [
        {
          "name": "Miles Burton",
          "email": "miles@mnetcs.com",
          "url": "http://www.milesburton.com",
          "maintainer": true
        },
        {
          "name": "Tim Newsome",
          "email": "nuisance@casualhacker.net"
        },
        {
          "name": "Guil Barros",
          "email": "gfbarros@bappos.com"
        },
        {
          "name": "Rob Tillaart",
          "email": "rob.tillaart@gmail.com"
        }
      ],
      "dependencies":
      {
        "name": "OneWire",
        "authors": "Paul Stoffregen",
        "frameworks": "arduino"
      },
      "version": "3.7.7",
      "frameworks": "arduino",
      "platforms": "*"
    }

Under VCS (SVN/GIT)
^^^^^^^^^^^^^^^^^^^

|PIOAPICR| can operate with a library source code that is under *VCS* control.
The list of **required** fields in the :ref:`library_config` will look like:

* :ref:`libjson_name`
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_authors`
* :ref:`libjson_repository`

Example:

.. code-block:: javascript

    {
        "name": "XBee",
        "keywords": "xbee, protocol, radio",
        "description": "Arduino library for communicating with XBees in API mode",
        "authors":
        {
            "name": "Andrew Rapp",
            "email": "andrew.rapp@gmail.com",
            "url": "https://code.google.com/u/andrew.rapp@gmail.com/"
        },
        "repository":
        {
            "type": "git",
            "url": "https://code.google.com/p/xbee-arduino/"
        },
        "frameworks": "arduino",
        "platforms": "atmelavr"
    }

Self-hosted
^^^^^^^^^^^

You can manually archive (*Zip, Tar.Gz*) your library source code and host it
in the *Internet*. Then you should specify the additional fields,
like :ref:`libjson_version` and :ref:`libjson_downloadurl`. The final list
of **required** fields in the :ref:`library_config` will look like:

* :ref:`libjson_name`
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_authors`
* :ref:`libjson_version`
* :ref:`libjson_downloadurl`

.. code-block:: javascript

    {
        "name": "OneWire",
        "keywords": "onewire, 1-wire, bus, sensor, temperature, ibutton",
        "description": "Control devices (from Dallas Semiconductor) that use the One Wire protocol (DS18S20, DS18B20, DS2408 and etc)",
        "authors":
        {
            "name": "Paul Stoffregen",
            "url": "http://www.pjrc.com/teensy/td_libs_OneWire.html"
        },
        "version": "2.2",
        "downloadUrl": "http://www.pjrc.com/teensy/arduino_libraries/OneWire.zip",
        "export": {
            "include": "OneWire"
        },
        "frameworks": "arduino",
        "platforms": "atmelavr"
    }


Register
--------

The registration requirements:

* A library must adhere to the :ref:`library_config` specification.
* There must be public *HTTP* access to the library :ref:`library_config` file.

Now, you can :ref:`register <cmd_lib_register>` your library and allow others
to :ref:`install <cmd_lib_install>` it.


.. _library_creating_examples:

Examples
--------

Command:

.. code-block:: bash

    $ platformio lib register http://my.example.com/library.json

* `GitHub + fixed release <http://platformio.org/lib/show/552/ACNoblex>`_
* `Dependencies by author and framework <http://platformio.org/lib/show/3/PID-AutoTune>`_
* `Multiple libraries in the one repository <https://github.com/jrowberg/i2cdevlib/tree/master/Arduino>`_
