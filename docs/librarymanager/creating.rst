.. _library_creating:
.. |PIOAPICR| replace:: *PlatformIO Library Registry Crawler*

Creating Library
================

*PlatformIO* :ref:`librarymanager` doesn't have any requirements to a library
source code structure. The only one requirement is library's manifest file -
:ref:`library_config`. It can be located inside your library or in the another
location where |PIOAPICR| will have *HTTP* access.

.. contents::

Source Code Location
--------------------

There are a several ways how to share your library with the whole world
(see `examples <https://github.com/platformio/platformio-libmirror/tree/master/configs>`_).

You can hold a lot of libraries (split into separated folders) inside one of
the repository/archive. In this case please use :ref:`libjson_include`
field to specify the relative path to your library's source code.


At GitHub
^^^^^^^^^

**Recommended**

If a library source code is located at `GitHub <https://github.com>`_, then
you **need to specify** only these fields in the :ref:`library_config`:

* :ref:`libjson_name`
* :ref:`libjson_keywords`
* :ref:`libjson_description`
* :ref:`libjson_repository`

|PIOAPICR| will populate the rest fields, like :ref:`libjson_version` or
:ref:`libjson_authors` with an actual information from *GitHub*.

Example:

.. code-block:: javascript

    {
        "name": "IRremote",
        "keywords": "infrared, ir, remote",
        "description": "Send and receive infrared signals with multiple protocols",
        "repository":
        {
            "type": "git",
            "url": "https://github.com/shirriff/Arduino-IRremote.git"
        },
        "frameworks": "arduino",
        "platforms": "atmelavr"
    }

Under CVS (SVN/GIT)
^^^^^^^^^^^^^^^^^^^

|PIOAPICR| can operate with a library source code that is under *CVS* control.
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
        "include": "OneWire",
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

Examples
--------

Create :ref:`platform_ststm32` based platform which uses GDB for uploading

First of all, we need to create new folder ``platforms`` :ref:`projectconf_pio_home_dir` and copy there two files:

1. Platform manifest file ``ststm32gdb.py`` with the next content:

.. code-block:: python

    import os

    from platformio.platforms.ststm32 import Ststm32Platform


    class Ststm32gdbPlatform(Ststm32Platform):

        """
        ST STM32 using GDB as uploader

        http://www.st.com/web/en/catalog/mmc/FM141/SC1169?sc=stm32
        """

        def get_build_script(self):

            return os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                "ststm32gdb-builder.py"
            )

2. Build script file ``ststm32gdb-builder.py`` with the next content:

.. code-block:: python

    """
        Builder for ST STM32 Series ARM microcontrollers with GDB upload.
    """

    from os.path import join

    from SCons.Script import (COMMAND_LINE_TARGETS, AlwaysBuild, Default,
                              DefaultEnvironment, SConscript)


    env = DefaultEnvironment()

    SConscript(env.subst(join("$PIOBUILDER_DIR", "scripts", "basearm.py")))

    env.Replace(
        UPLOADER=join(
            "$PIOPACKAGES_DIR", "toolchain-gccarmnoneeabi",
            "bin", "arm-none-eabi-gdb"
        ),
        UPLOADERFLAGS=[
            join("$BUILD_DIR", "firmware.elf"),
            "-batch",
            "-x", join("$PROJECT_DIR", "upload.gdb")
        ],

        UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
    )

    env.Append(
        CPPDEFINES=[
            "${BOARD_OPTIONS['build']['variant'].upper()}"
        ],

        LINKFLAGS=[
            "-nostartfiles",
            "-nostdlib"
        ]
    )

    #
    # Target: Build executable and linkable firmware
    #

    target_elf = env.BuildFirmware()

    #
    # Target: Build the .bin file
    #

    if "uploadlazy" in COMMAND_LINE_TARGETS:
        target_firm = join("$BUILD_DIR", "firmware.bin")
    else:
        target_firm = env.ElfToBin(join("$BUILD_DIR", "firmware"), target_elf)

    #
    # Target: Print binary size
    #

    target_size = env.Alias("size", target_elf, "$SIZEPRINTCMD")
    AlwaysBuild(target_size)

    #
    # Target: Upload by default .bin file
    #

    upload = env.Alias(
        ["upload", "uploadlazy"], target_firm, "$UPLOADCMD")
    AlwaysBuild(upload)

    #
    # Target: Define targets
    #

    Default([target_firm, target_size])

You should see ststm32gdb platform in ``platformio search`` command output.
Now, you can install new platform via :ref:`platformio install ststm32gdb <cmd_install>` command.

For more detailed information how to use this platform please follow to `issue 175 <https://github.com/platformio/platformio/issues/175>`_
