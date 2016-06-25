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

.. _projectconf:

Project Configuration File ``platformio.ini``
=============================================

The Project configuration file is named ``platformio.ini``. This is a
`INI-style <http://en.wikipedia.org/wiki/INI_file>`_ file.

``platformio.ini`` has sections (each denoted by a ``[header]``) and
key / value pairs within the sections. Lines beginning with ``#`` or ``;``
are ignored and may be used to provide comments.

The sections and their allowable values are described below.

.. contents::

Section ``[platformio]``
------------------------

A ``platformio`` section is used for overriding default configuration options

.. note::
    Relative path is allowed for directory option:

    * ``~`` will be expanded to user's home directory
    * ``../`` or ``..\`` go up to one folder

Options
~~~~~~~

.. _projectconf_pio_home_dir:

``home_dir``
^^^^^^^^^^^^

Is used to store platform toolchains, frameworks, external libraries,
service data and etc.

A default value is User's home directory:

* Unix ``~/.platformio``
* Windows ``%HOMEPATH%\.platformio``

This option can be overridden by global environment variable
:envvar:`PLATFORMIO_HOME_DIR`.

.. _projectconf_pio_lib_dir:

``lib_dir``
^^^^^^^^^^^

This directory is used to store external libraries downloaded by
:ref:`librarymanager`.

A default value is ``%home_dir%/lib``.

This option can be overridden by global environment variable
:envvar:`PLATFORMIO_LIB_DIR`.

.. note::
    You can put here your own/private libraries. The source code of each
    library should be placed in separate directory. For example,
    ``%lib_dir%/private_lib/[here are source files]``.

.. _projectconf_pio_src_dir:

``src_dir``
^^^^^^^^^^^

A path to project's source directory. PlatformIO uses it for :ref:`cmd_run`
command.

A default value is ``src`` which means that folder is located in the root of
project.

This option can be overridden by global environment variable
:envvar:`PLATFORMIO_SRC_DIR`.

.. note::
    This option is useful for people who migrate from Arduino/Energia IDEs where
    source directory should have the same name like the main source file.
    See `example <https://github.com/platformio/platformio-examples/tree/develop/atmelavr-and-arduino/arduino-own-src_dir>`__ project with own source directory.

.. _projectconf_pio_envs_dir:

``envs_dir``
^^^^^^^^^^^^

This is a cache directory. *PlatformIO Build System* uses this folder for project
environments to store compiled object files, static libraries, firmwares and
other cached information. It allows PlatformIO to build source code extremely
fast!

*You can delete this folder without any risk!* If you modify :ref:`projectconf`,
then PlatformIO will remove this folder automatically. It will be created on the
next build operation.

A default value is ``.pioenvs`` which means that folder is located in the root of
project.

This option can be overridden by global environment variable
:envvar:`PLATFORMIO_ENVS_DIR`.

.. note::
    If you have any problems with building your Project environments which
    are defined in :ref:`projectconf`, then **TRY TO DELETE** this folder. In
    this situation you will remove all cached files without any risk.

.. _projectconf_pio_data_dir:

``data_dir``
^^^^^^^^^^^^

Data directory to store contents and :ref:`platform_espressif_uploadfs`.

A default value is ``data`` which means that folder is located in the root of
project.

This option can be overridden by global environment variable
:envvar:`PLATFORMIO_DATA_DIR`.

.. _projectconf_pio_test_dir:

``test_dir``
^^^^^^^^^^^^

Directory for :ref:`unit_testing`.

A default value is ``test`` which means that folder is located in the root of
project.

This option can be overridden by global environment variable
:envvar:`PLATFORMIO_TEST_DIR`.

.. _projectconf_pio_env_default:

``env_default``
^^^^^^^^^^^^^^^

:ref:`cmd_run` command processes all environments ``[env:***]`` by default
if :option:`platformio run --environment` option is not specified.
:ref:`projectconf_pio_env_default` allows to define environments which
should be processed by default.

Multiple environments are allowed if they are separated with ``,`` (comma).
For example.

.. code-block:: ini

    [platformio]
    env_default = uno, nodemcu

    [env:uno]
    platform = atmelavr
    framework = arduino
    board = uno

    [env:nodemcu]
    platform = espressif
    framework = arduino
    board = nodemcu

    [env:teensy31]
    platform = teensy
    framework = arduino
    board = teensy31

    [env:lpmsp430g2553]
    platform = timsp430
    framework = energia
    board = lpmsp430g2553
    build_flags = -D LED_BUILTIN=RED_LED

----------

Section ``[env:NAME]``
----------------------

A section with ``env:`` prefix is used to define virtual environment with
specific options that will be processed with :ref:`cmd_run` command. You can
define unlimited numbers of environments.

Each environment must have unique ``NAME``. The valid chars for ``NAME`` are

* letters ``a-z``
* numbers ``0-9``
* special char ``_`` (underscore)

For example, ``[env:hello_world]``.

General options
~~~~~~~~~~~~~~~

.. _projectconf_env_platform:

``platform``
^^^^^^^^^^^^

:ref:`platforms` name.

PlatformIO allows to use specific platform versions using
`Semantic Versioning <http://semver.org>`_ (X.Y.Z=MAJOR.MINOR.PATCH).
Version specifications can take any of the following forms:

* ``0.1.2``: an exact version number. Use only this exact version
* ``^0.1.2``: any compatible version (exact version for ``0.x.x`` versions
* ``~0.1.2``: any version with the same major and minor versions, and an
  equal or greater patch version
* ``>0.1.2``: any version greater than ``0.1.2``. ``>=``, ``<``, and ``<=``
  are also possible
* ``>0.1.0,!=0.2.0,<0.3.0``: any version greater than ``0.1.0``, not equal to
  ``0.2.0`` and less than ``0.3.0``

Examples:

.. code-block:: ini

    [env:the_latest_version]
    platform = atmelavr

    [env:specific_major_version]
    platform = atmelavr@^0.1.2

    [env:specific_major_and_minor_version]
    platform = atmelavr@~0.1.2

.. _projectconf_env_framework:

``framework``
^^^^^^^^^^^^^

:ref:`frameworks` name.

The multiple frameworks are allowed, split them with comma ``,`` separator.

.. _projectconf_env_board:

``board``
^^^^^^^^^

*PlatformIO* has pre-configured settings for the most popular boards. You don't
need to specify ``board_mcu``, ``board_f_cpu``, ``upload_protocol`` or
``upload_speed`` options. Just define a ``board`` type and *PlatformIO* will
pre-fill options described above with appropriate values.

You can find the ``board`` type in *Boards* section of each :ref:`platforms` or
using `PlatformIO Embedded Boards Explorer <http://platformio.org/boards>`_.


Board options
~~~~~~~~~~~~~

``board_mcu``
^^^^^^^^^^^^^

``board_mcu`` is a microcontroller(MCU) type that is used by compiler to
recognize MCU architecture. The correct type of ``board_mcu`` depends on
platform library. For example, the list of ``board_mcu`` for "megaAVR Devices"
is described `here <http://www.nongnu.org/avr-libc/user-manual/>`_.

The full list of ``board_mcu`` for the popular embedded platforms you can find
in *Boards* section of :ref:`platforms`. See "Microcontroller" column.

.. _projectconf_board_f_cpu:

``board_f_cpu``
^^^^^^^^^^^^^^^

An option ``board_f_cpu`` is used to define MCU frequency (Hertz, Clock). A
format of this option is ``C-like long integer`` value with ``L`` suffix. The
1 Hertz is equal to ``1L``, then 16 Mhz (Mega Hertz) is equal to ``16000000L``.

The full list of ``board_f_cpu`` for the popular embedded platforms you can
find in *Boards* section of :ref:`platforms`. See "Frequency" column. You can
overclock a board by specifying a ``board_f_cpu`` value other than the default.

.. _projectconf_board_f_flash:

``board_f_flash``
^^^^^^^^^^^^^^^^^

An option ``board_f_flash`` is used to define FLASH chip frequency (Hertz, Clock). A
format of this option is ``C-like long integer`` value with ``L`` suffix. The
1 Hertz is equal to ``1L``, then 40 Mhz (Mega Hertz) is equal to ``40000000L``.

This option isn't available for the all development platforms. The only
:ref:`platform_espressif` supports it.

.. _projectconf_board_flash_mode:

``board_flash_mode``
^^^^^^^^^^^^^^^^^^^^

Flash chip interface mode. This option isn't available for the all development
platforms. The only :ref:`platform_espressif` supports it.

Building options
~~~~~~~~~~~~~~~~

.. _projectconf_build_flags:

``build_flags``
^^^^^^^^^^^^^^^

These flags/options control preprocessing, compilation, assembly and linking
processes:

.. list-table::
    :header-rows:  1

    * - Format
      - Scope
      - Description
    * - ``-D name``
      - CPPDEFINES
      - Predefine *name* as a macro, with definition 1.
    * - ``-D name=definition``
      - CPPDEFINES
      - The contents of *definition* are tokenized and processed as if they
        appeared during translation phase three in a ``#define`` directive.
    * - ``-U name``
      - CPPDEFINES
      - Cancel any previous definition of *name*, either built in or provided
        with a ``-D`` option.
    * - ``-Wp,option``
      - CPPFLAGS
      - Bypass the compiler driver and pass *option* directly  through to the
        preprocessor
    * - ``-Wall``
      - CCFLAGS
      - Turns on all optional warnings which are desirable for normal code.
    * - ``-Werror``
      - CCFLAGS
      - Make all warnings into hard errors. Source code which triggers warnings will be rejected.
    * - ``-w``
      - CCFLAGS
      - Suppress all warnings, including those which GNU CPP issues by default.
    * - ``-include file``
      - CCFLAGS
      - Process *file* as if ``#include "file"`` appeared as the first line of
        the primary source file.
    * - ``-Idir``
      - CPPPATH
      - Add the directory *dir* to the list of directories to be searched
        for header files.
    * - ``-Wa,option``
      - ASFLAGS, CCFLAGS
      - Pass *option* as an option to the assembler. If *option* contains
        commas, it is split into multiple options at the commas.
    * - ``-Wl,option``
      - LINKFLAGS
      - Pass *option* as an option to the linker. If *option* contains
        commas, it is split into multiple options at the commas.
    * - ``-llibrary``
      - LIBS
      - Search the *library* named library when linking
    * - ``-Ldir``
      - LIBPATH
      - Add directory *dir* to the list of directories to be searched for
        ``-l``.

This option can be set by global environment variable
:envvar:`PLATFORMIO_BUILD_FLAGS`.

Example:

.. code-block::   ini

    [env:specific_defines]
    build_flags = -DFOO -DBAR=1 -DFLOAT_VALUE=1.23457e+07

    [env:string_defines]
    build_flags = '-DHELLO="World!"' '-DWIFI_PASS="My password"'

    [env:specific_inclibs]
    build_flags = -I/opt/include -L/opt/lib -lfoo

    [env:specific_ld_script]
    build_flags = -Wl,-T/path/to/ld_script.ld


For more detailed information about available flags/options go to:

* `Options to Request or Suppress Warnings
  <https://gcc.gnu.org/onlinedocs/gcc/Warning-Options.html>`_
* `Options for Debugging Your Program
  <https://gcc.gnu.org/onlinedocs/gcc/Debugging-Options.html>`_
* `Options That Control Optimization
  <https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html>`_
* `Options Controlling the Preprocessor
  <https://gcc.gnu.org/onlinedocs/gcc/Preprocessor-Options.html>`_
* `Passing Options to the Assembler
  <https://gcc.gnu.org/onlinedocs/gcc/Assembler-Options.html>`_
* `Options for Linking <https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html>`_
* `Options for Directory Search
  <https://gcc.gnu.org/onlinedocs/gcc/Directory-Options.html>`_

.. _projectconf_src_build_flags:

``src_build_flags``
^^^^^^^^^^^^^^^^^^^

An option ``src_build_flags`` has the same behavior like ``build_flags``
but will be applied only for the project source code from
:ref:`projectconf_pio_src_dir` directory.

This option can be set by global environment variable
:envvar:`PLATFORMIO_SRC_BUILD_FLAGS`.

``build_unflags``
^^^^^^^^^^^^^^^^^

Remove base/initial flags which were set by development platform.

.. code-block:: ini

   [env:unflags]
   build_unflags = -Os -std=gnu++11
   build_flags = -O2

.. _projectconf_src_filter:

``src_filter``
^^^^^^^^^^^^^^

This option allows to specify which source files should be included/excluded
from build process. Filter supports 2 templates:

* ``+<PATH>`` include template
* ``-<PATH>`` exclude template

``PATH`` MAST BE related from :ref:`projectconf_pio_src_dir`. All patterns will
be applied in theirs order.
`GLOB Patterns <http://en.wikipedia.org/wiki/Glob_(programming)>`_ are allowed.

By default, ``src_filter`` is predefined to
``+<*> -<.git/> -<svn/> -<example/> -<examples/> -<test/> -<tests/>``,
which means "includes ALL files, then
exclude ``.git`` and ``svn`` repository folders, ``example`` ... folder.

This option can be set by global environment variable
:envvar:`PLATFORMIO_SRC_FILTER`.

.. _projectconf_extra_script:

``extra_script``
^^^^^^^^^^^^^^^^

Allows to launch extra script using `SCons <http://www.scons.org>`_ software
construction tool. For more details please follow to "Construction Environments"
section of
`SCons documentation <http://www.scons.org/doc/production/HTML/scons-user.html#chap-environments>`_.

This option can be set by global environment variable
:envvar:`PLATFORMIO_EXTRA_SCRIPT`.

Example, specify own upload command for :ref:`platform_atmelavr`:

``platformio.ini``:

.. code-block:: ini

    [env:env_with_specific_extra_script]
    platform = atmelavr
    extra_script = /path/to/extra_script.py
    custom_option = hello

``extra_script.py``:

.. code-block:: python

    from SCons.Script import DefaultEnvironment

    env = DefaultEnvironment()

    env.Replace(UPLOADHEXCMD='"$UPLOADER" ${ARGUMENTS.get("custom_option")} --uploader --flags')

    # uncomment line below to see environment variables
    # print env.Dump()
    # print ARGUMENTS


* see built-in examples of `PlatformIO build scripts <https://github.com/platformio/platformio/tree/develop/platformio/builder/scripts>`_.
* take a look at the multiple snippets/answers for the user questions:

  - `#462 Split C/C++ build flags <https://github.com/platformio/platformio/issues/462#issuecomment-172667342>`_
  - `#365 Extra configuration for ESP8266 uploader <https://github.com/platformio/platformio/issues/365#issuecomment-163695011>`_
  - `#351 Specific reset method for ESP8266 <https://github.com/platformio/platformio/issues/351#issuecomment-161789165>`_
  - `#247 Specific options for avrdude <https://github.com/platformio/platformio/issues/247#issuecomment-118169728>`_.

``targets``
^^^^^^^^^^^

A list with targets which will be processed by :ref:`cmd_run` command by
default. You can enter more than one target separated with "space".

The list with available targets is located in :option:`platformio run --target`.

**Tip!** You can use these targets like an option to
:option:`platformio run --target` command. For example:

.. code-block:: bash

    # clean project
    platformio run -t clean

    # dump curent build environment
    platformio run --target envdump

When no targets are defined, *PlatformIO* will build only sources by default.


Uploading options
~~~~~~~~~~~~~~~~~

.. _projectconf_upload_port:

``upload_port``
^^^^^^^^^^^^^^^

This option is used by "uploader" tool when sending firmware to board via
``upload_port``. For example,

* ``/dev/ttyUSB0`` - Unix-based OS
* ``COM3`` - Windows OS
* ``192.168.0.13`` - IP address when using OTA

If ``upload_port`` isn't specified, then *PlatformIO* will try to detect it
automatically.

To print all available serial ports use :ref:`cmd_serialports` command.

This option can be set by global environment variable
:envvar:`PLATFORMIO_UPLOAD_PORT`.

``upload_protocol``
^^^^^^^^^^^^^^^^^^^

A protocol that "uploader" tool uses to talk to the board.

.. _projectconf_upload_speed:

``upload_speed``
^^^^^^^^^^^^^^^^

A connection speed (`baud rate <http://en.wikipedia.org/wiki/Baud>`_)
which "uploader" tool uses when sending firmware to board.

.. _projectconf_upload_flags:

``upload_flags``
^^^^^^^^^^^^^^^^

Extra flags for uploader. Will be added to the end of uploader command. If you
need to override uploader command or base flags please use :ref:`projectconf_extra_script`.

This option can be set by global environment variable
:envvar:`PLATFORMIO_UPLOAD_FLAGS`.

.. _projectconf_upload_resetmethod:

``upload_resetmethod``
^^^^^^^^^^^^^^^^^^^^^^

Specify reset method for "uploader" tool. This option isn't available for all
development platforms. The only :ref:`platform_espressif` supports it.

Library options
~~~~~~~~~~~~~~~

``lib_install``
^^^^^^^^^^^^^^^

Specify dependent libraries which should be installed before environment
process. The only library IDs are allowed. Multiple libraries can be passed
using comma ``,`` sign.

You can obtain library IDs using :ref:`cmd_lib_search` command.

Example:

.. code-block:: ini

    [env:depends_on_some_libs]
    lib_install = 1,13,19

``lib_force``
^^^^^^^^^^^^^

Force Library Build System to build specified libraries if even they are not
included in the project source code. Also, these libraries will be processed
in the first order.

Example:

.. code-block:: ini

    [env:myenv]
    lib_force = OneWire, SPI

``lib_ignore``
^^^^^^^^^^^^^^

Specify libraries which should be ignored by ``Library Dependency Finder (LDF)``

Example:

.. code-block:: ini

    [env:ignore_some_libs]
    lib_ignore = SPI, Ethernet

``lib_deep_search``
^^^^^^^^^^^^^^^^^^^

By default, this option is turned OFF (``lib_deep_search = false``) and means
that ``Library Dependency Finder (LDF)`` will look only for the libraries
that are mentioned (using ``#include <...>``) in the source files from the
project :ref:`projectconf_pio_src_dir`. Also, ``LDF`` analyzes nested
``#include <...>`` by default.

If you want to enable deep search, please set this option to ``true``.
Found library will be treated like the new source files and
``LDF`` will search dependencies for it.

For example, there are 2 libraries:

* Library "Foo" with files:

  - ``Foo/foo.h``
  - ``Foo/foo.cpp``

* Library "Bar" with files:

  - ``Bar/bar.h``
  - ``Bar/bar.cpp``

:Case 1:

  * ``lib_deep_search = false``
  * ``Foo/foo.h`` depends on "Bar" library (contains ``#include <bar.h>``)
  * ``#include <foo.h>`` is located in one of the project source files

  Here are nested includes (``project file > foo.h > bar.h``) and ``LDF`` will
  find both libraries "Foo" and "Bar".

:Case 2:

  * ``lib_deep_search = false``
  * ``Foo/foo.cpp`` depends on "Bar" library (contains ``#include <bar.h>``)
  * ``#include <foo.h>`` is located in one of the project source files

  In this case, ``LDF`` will not find "Bar" library because it doesn't know
  about CPP file (``Foo/foo.cpp``).

:Case 3:

  * ``lib_deep_search = true``
  * ``Foo/foo.cpp`` depends on "Bar" library (contains ``#include <bar.h>``)
  * ``#include <foo.h>`` is located in one of the project source files

  Firstly, ``LDF`` finds "Foo" library, then it parses all sources from "Foo"
  library and finds ``Foo/foo.cpp`` that depends on ``#include <bar.h>``.
  Secondly, it will parse all sources from "Bar" library and this operation
  continues until all dependent libraries will not be parsed.

-----------

.. _projectconf_examples:

Examples
--------

.. note::
    A full list with project examples can be found in
    `PlatformIO Repository <https://github.com/platformio/platformio-examples/tree/develop>`_.

1. :ref:`platform_atmelavr`: Arduino UNO board with auto pre-configured
   ``board_*`` and ``upload_*`` options (use only ``board`` option) and Arduino
   Wiring-based Framework

.. code-block:: ini

    [env:atmelavr_arduino_uno_board]
    platform = atmelavr
    framework = arduino
    board = uno

    # enable auto-uploading
    targets = upload


2. :ref:`platform_atmelavr`: Embedded board that is based on ATmega168 MCU with
   "arduino" bootloader

.. code-block:: ini

    [env:atmelavr_atmega168_board]
    platform = atmelavr
    board_mcu = atmega168
    board_f_cpu = 16000000L

    upload_port = /dev/ttyUSB0
    # for Windows OS
    # upload_port = COM3
    upload_protocol = arduino
    upload_speed = 19200

    # enable auto-uploading
    targets = upload


3. Upload firmware via USB programmer (USBasp) to :ref:`platform_atmelavr`
   microcontrollers

.. code-block:: ini

    [env:atmelavr_usbasp]
    platform = atmelavr
    framework = arduino
    board = pro8MHzatmega328
    upload_protocol = usbasp
    upload_flags = -Pusb -B5

Then upload firmware using target ``program`` for :option:`platformio run --target`.
command. To use other programmers see :ref:`atmelavr_upload_via_programmer`.


4. :ref:`platform_ststm32`: Upload firmware using GDB script ``upload.gdb``,
   `issue #175 <https://github.com/platformio/platformio/issues/175>`_

.. code-block:: ini

    [env:st_via_gdb]
    platform = ststm32
    board = armstrap_eagle512
    upload_protocol = gdb

Also, take a look at this article `Armstrap Eagle and PlatformIO <http://isobit.io/2015/08/08/armstrap.html>`_.

5. :ref:`platform_ststm32`: Upload firmware using ST-Link instead mbed's media
   disk

.. code-block:: ini

    [env:stlink_for_mbed]
    platform = ststm32
    board = disco_f100rb
    upload_protocol = stlink
