.. _projectconf:

Project Configuration File ``platformio.ini``
=============================================

The Project configuration file is named ``platformio.ini``. This is a
`INI-style <http://en.wikipedia.org/wiki/INI_file>`_ file.

``platformio.ini`` has sections (each denoted by a ``[header]``) and
key / value pairs within the sections. A sign ``#`` at the beginning of the
line indicates a comment. Comment lines are ignored.

The sections and their allowable values are described below.

.. contents::

[platformio]
------------

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

Is used to store platform tool chains, frameworks, external libraries,
service data and etc.

A default value is User's home directory:

* Unix ``~/.platformio``
* Windows ``%HOMEPATH%\.platformio``

This option can be overridden by global environment variable
:ref:`envvar_PLATFORMIO_HOME_DIR`.

.. _projectconf_pio_lib_dir:

``lib_dir``
^^^^^^^^^^^

This directory is used to store external libraries downloaded by
:ref:`librarymanager`.

A default value is ``%home_dir%/lib``.

This option can be overridden by global environment variable
:ref:`envvar_PLATFORMIO_LIB_DIR`.

.. _projectconf_pio_src_dir:

``src_dir``
^^^^^^^^^^^

A path to project's source directory. PlatformIO uses it for :ref:`cmd_run`
command.

A default value is ``%project_dir%/src``.

This option can be overridden by global environment variable
:ref:`envvar_PLATFORMIO_SRC_DIR`.

.. note::
    This option is useful for people who migrate from Arduino/Energia IDEs where
    source directory should have the same name like the main source file.
    See `example <https://github.com/ivankravets/platformio/tree/develop/examples/atmelavr-and-arduino/arduino-own-src_dir>`__ project with own source directory.

.. _projectconf_pio_envs_dir:

``envs_dir``
^^^^^^^^^^^^

*PlatformIO Builder* within :ref:`cmd_run` command uses this folder for project
environments to store compiled object files, static libraries, firmwares and
other cached information. It allows PlatformIO to build source code extremely
fast!

*You can delete this folder without any risk!* If you modify :ref:`projectconf`,
then PlatformIO will remove this folder automatically. It will be created on the
next build operation.

A default value is ``%project_dir%/.pioenvs``.

This option can be overridden by global environment variable
:ref:`envvar_PLATFORMIO_ENVS_DIR`.

.. note::
    If you have any problems with building your Project environmets which
    are defined in :ref:`projectconf`, then **TRY TO DELETE** this folder. In
    this situation you will remove all cached files without any risk.

[env:NAME]
----------

A section with ``env:`` prefix is used to define virtual environment with
specific options that will be processed with :ref:`cmd_run` command. You can
define unlimited numbers of environments.

Each environment must have unique ``NAME``. The valid chars for ``NAME`` are

* letters ``a-z``
* numbers ``0-9``
* special char ``_`` (underscore)

For example, ``[env:hello_world]``.

Options
~~~~~~~

.. _projectconf_env_platform:

``platform``
^^^^^^^^^^^^

:ref:`Platform <platforms>` type


.. _projectconf_env_framework:

``framework``
^^^^^^^^^^^^^

See ``framework`` type in *Frameworks* section of :ref:`platforms`


.. _projectconf_env_board:

``board``
^^^^^^^^^

*PlatformIO* has pre-configured settings for the most popular boards. You don't
need to specify ``board_mcu``, ``board_f_cpu``, ``upload_protocol`` or
``upload_speed`` options. Just define a ``board`` type and *PlatformIO* will
pre-fill options described above with appropriate values.

You can find the ``board`` type in *Boards* section of each :ref:`platforms`.


``board_mcu``
^^^^^^^^^^^^^

``board_mcu`` is a microcontroller(MCU) type that is used by compiler to
recognize MCU architecture. The correct type of ``board_mcu`` depends on
platform library. For example, the list of ``board_mcu`` for "megaAVR Devices"
is described `here <http://www.nongnu.org/avr-libc/user-manual/>`_.

The full list of ``board_mcu`` for the popular embedded platforms you can find
in *Boards* section of :ref:`platforms`. See "Microcontroller" column.


``board_f_cpu``
^^^^^^^^^^^^^^^

An option ``board_f_cpu`` is used to define MCU frequency (Hertz, Clock). A
format of this option is ``C-like long integer`` value with ``L`` suffix. The
1 Hertz is equal to ``1L``, then 16 Mhz (Mega Hertz) is equal to ``16000000L``.

The full list of ``board_f_cpu`` for the popular embedded platforms you can
find in *Boards* section of :ref:`platforms`. See "Frequency" column.


``upload_port``
^^^^^^^^^^^^^^^

This option is used by "uploader" tool when sending firmware to board via
``upload_port``. For example,

* ``/dev/ttyUSB0`` - Unix-based OS
* ``COM3`` - Windows OS

If ``upload_port`` isn't specified, then *PlatformIO* will try to detect it
automatically.

To print all available serial ports use :ref:`cmd_serialports` command.


``upload_protocol``
^^^^^^^^^^^^^^^^^^^

A protocol that "uploader" tool uses to talk to the board.


``upload_speed``
^^^^^^^^^^^^^^^^

A connection speed (`baud rate <http://en.wikipedia.org/wiki/Baud>`_)
which "uploader" tool uses when sending firmware to board.


``targets``
^^^^^^^^^^^

A list with targets which will be processed by :ref:`cmd_run` command by
default. You can enter more then one target separated with "space".

When no targets are defined, *PlatformIO* will build only sources by default.

.. note::
    This option is useful to enable "auto-uploading" after building operation
    (``targets = upload``).


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
    * - ``Wp,option``
      - CPPFLAGS
      - Bypass the compiler driver and pass *option* directly  through to the
        preprocessor
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
    * - ``-Wa,option``
      - ASFLAGS, CCFLAGS
      - Pass *option* as an option to the assembler. If *option* contains
        commas, it is split into multiple options at the commas.
    * - ``-llibrary``
      - LIBS
      - Search the *library* named library when linking
    * - ``-Ldir``
      - LIBPATH
      - Add directory *dir* to the list of directories to be searched for
        ``-l``.
    * - ``-Idir``
      - CPPPATH
      - Add the directory *dir* to the list of directories to be searched
        for header files.

Example:

.. code-block::   ini

    [env:specific_defines]
    build_flags = -O2 -Dfoo -Dbar=1

    [env:specific_inclibs]
    build_flags = -I/opt/include -L/opt/lib -lfoo


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

.. _projectconf_srcbuild_flags:

``srcbuild_flags``
^^^^^^^^^^^^^^^^^^

An option ``srcbuild_flags`` has the same behaviour like ``build_flags``
but will be applied only for the project source code from
:ref:`projectconf_pio_src_dir` directory.

This option can be overridden by global environment variable
:ref:`envvar_PLATFORMIO_SRCBUILD_FLAGS`.

``ignore_libs``
^^^^^^^^^^^^^^^

Specify libraries which should be ignored by ``Library Dependency Finder``

Example:

.. code-block::   ini

    [env:ignore_some_libs]
    ignore_libs = SPI,EngduinoV3_ID123


.. _projectconf_examples:

Examples
--------

.. note::
    A full list with project examples can be found in
    `PlatformIO Repository <https://github.com/ivankravets/platformio/tree/develop/examples>`_.

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


2. :ref:`platform_atmelavr`: Microduino Core (ATmega168P, 3.3V) board with
   auto pre-configured ``board_*`` and ``upload_*`` options (use only
   ``board`` option) and Arduino Wiring-based Framework

.. code-block:: ini

    [env:atmelavr_microduino_core_board]
    platform = atmelavr
    framework = arduino
    board = 168pa8m

    # enable auto-uploading
    targets = upload


3. :ref:`platform_atmelavr`: Raspduino board with
   auto pre-configured ``board_*`` and ``upload_*`` options (use only
   ``board`` option) and Arduino Wiring-based Framework

.. code-block:: ini

    [env:atmelavr_raspduino_board]
    platform = atmelavr
    framework = arduino
    board = raspduino

    upload_port = /dev/ttyS0

    # enable auto-uploading
    targets = upload


4. :ref:`platform_atmelavr`: Embedded board that is based on ATmega168 MCU with
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


5. Upload firmware via USB programmer (USBasp) to :ref:`platform_atmelavr`
   microcontrollers

.. code-block:: ini

    [env:atmelavr_usbasp]
    platform = atmelavr
    framework = arduino
    board = pro8MHzatmega328
    upload_protocol = usbasp -B5


6. :ref:`platform_timsp430`: TI MSP430G2553 LaunchPad with auto pre-configured
   ``board_*`` and ``upload_*`` options (use only ``board`` option) and Energia
   Wiring-based Framework

.. code-block:: ini

    [env:timsp430_g2553_launchpad]
    platform = timsp430
    framework = energia
    board = lpmsp430g2553


7. :ref:`platform_timsp430`: Embedded board that is based on MSP430G2553 MCU

.. code-block:: ini

    [env:timsp430_g2553_board]
    platform = timsp430
    board_mcu = msp430g2553
    board_f_cpu = 16000000L

    upload_protocol = rf2500

    # enable auto-uploading
    targets = upload


8. :ref:`platform_titiva`: TI Tiva C ARM Series TM4C123G LaunchPad with auto
   pre-configured ``board_*`` and ``upload_*`` options (use only ``board``
   option) and Energia Wiring-based Framework

.. code-block:: ini

    [env:titiva_tm4c1230c3pm_launchpad]
    platform = titiva
    framework = energia
    board = lptm4c1230c3pm

