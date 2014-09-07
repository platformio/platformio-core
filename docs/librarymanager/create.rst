.. _library_create:
.. |PIOAPICR| replace:: *PlatformIO-API Crawler*

Creating Library
================

*PlatformIO* :ref:`librarymanager` doesn't has any requirements to a library
source code structure. The only one requirement is library's manifest file -
:ref:`library_config`. It can be located inside your library or in the another
location where |PIOAPICR| will have *HTTP* access.

.. contents::

Source Code Location
--------------------

There are a several ways how to share your library with the whole world
(see `examples <https://github.com/ivankravets/platformio-libmirror/tree/master/configs>`_).

Also, you can hold a lot of libraries inside the one repository/archive in the
different folders. In this case please use :ref:`libjson_include` field to
specify the relative path to your library's source code.


At GitHub
^^^^^^^^^

**Recommended**

If the library source code is located at `GitHub <https://github.com>`_, then
you **need to specify** only these fields in :ref:`library_config`:

* :ref:`libjson_name`
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_repository`

|PIOAPICR| will populate the rest fields, like :ref:`libjson_version` or
:ref:`libjson_author` with actual information from *GitHub*.

Example:

.. code-block:: javascript

    {
        "name": "Arduino-IRremote",
        "keywords": "infrared, ir, remote",
        "description": "Send and receive infrared signals with multiple protocols",
        "repository":
        {
            "type": "git",
            "url": "https://github.com/shirriff/Arduino-IRremote.git"
        }
    }

Under CVS (SVN/GIT)
^^^^^^^^^^^^^^^^^^^

|PIOAPICR| can operate with the library source code that is under *CVS* control.
The list of **required** fields in :ref:`library_config` will look like:

* :ref:`libjson_name`
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_author`
* :ref:`libjson_repository`

Example:

.. code-block:: javascript

    {
        "name": "Arduino-XBee",
        "keywords": "xbee, protocol, radio",
        "description": "Arduino library for communicating with XBees in API mode",
        "author":
        {
            "name": "Andrew Rapp",
            "email": "andrew.rapp@gmail.com",
            "url": "https://code.google.com/u/andrew.rapp@gmail.com/"
        },
        "repository":
        {
            "type": "git",
            "url": "https://code.google.com/p/xbee-arduino/"
        }
    }

Packed in achive (Zip, Tar.Gz)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can manually archive your library source code and host it in the *Internet*.
Then you should specify additional fields, like :ref:`libjson_version` and
:ref:`libjson_downloadurl`. The final list of **required** fields in
:ref:`library_config` will look like:

* :ref:`libjson_name`
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_author`
* :ref:`libjson_version`
* :ref:`libjson_downloadurl`

.. code-block:: javascript

    {
        "name": "Arduino-OneWire",
        "keywords": "onewire, 1-wire, bus, sensor, temperature, ibutton",
        "description": "Control devices (from Dallas Semiconductor) that use the One Wire protocol (DS18S20, DS18B20, DS2408 and etc)",
        "author":
        {
            "name": "Paul Stoffregen",
            "url": "http://www.pjrc.com/teensy/td_libs_OneWire.html"
        },
        "version": "2.2",
        "downloadUrl": "http://www.pjrc.com/teensy/arduino_libraries/OneWire.zip",
        "include": "OneWire"
    }


Register
--------

* The library must adhere to the :ref:`library_config` specification.
* There must be public *HTTP* access to library :ref:`library_config` file.

Now, you can :ref:`register <cmd_lib_register>` your library and allow others
to :ref:`install <cmd_lib_install>` it.

