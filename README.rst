PlatformIO
==========

**Platformio** is a console tool to build code with different development
platforms.

You have no need to install any *IDE* or compile any toolchains. *Platformio*
has pre-built different development platforms including: compiler, debugger,
flasher (for embedded) and many other useful tools.

**Platformio** allows developer to compile the same code with different
platforms using only one command ``platformio run``. This happens due to
``platformio.ini`` project's file (see
`default template <https://github.com/ivankravets/platformio/blob/develop/platformio/projectconftpl.ini>`)
where you can setup different environments with specific settings: platform,
firmware uploading options, pre-built framework and many more.

Each platform consists of packages which are located in own repository.
Due to ``platformio update`` command you will have up-to-date development
instruments.

**Platformio** is well suited for **embedded development**. It can:

* Compile frameworks and libraries sources to static libraries
* Build *ELF* (executable and linkable firmware)
* Convert *ELF* to *HEX* or *BIN* file
* Extract *EEPROM* data
* Upload firmware to your device

It has support for many popular embedded platforms like these:

* ``atmelavr`` `Atmel AVR <http://en.wikipedia.org/wiki/Atmel_AVR>`_
  (including `Arduino <http://www.arduino.cc>`_ based boards)
* ``timsp430`` `TI MSP430 <http://www.ti.com/lsds/ti/microcontroller/16-bit_msp430/overview.page>`_
  (including `MSP430 LaunchPads <http://www.ti.com/ww/en/launchpad/launchpads-msp430.html>`_)
* ``titiva`` `TI TIVA C <http://www.ti.com/lsds/ti/microcontroller/tiva_arm_cortex/c_series/overview.page>`_
  (including `TIVA C Series LaunchPads <http://www.ti.com/ww/en/launchpad/launchpads-connected.html>`_)


See project `examples with screenshots <https://github.com/ivankravets/platformio/tree/develop/examples>`_.


Python & OS Support
-------------------

**Platformio** is written in `Python <https://www.python.org>`_ and works with
versions 2.6 and 2.7 on Unix/Linux, OS X, and Windows.


Quickstart
----------

.. code-block:: bash

    # Install platformio
    $ pip install platformio && pip install --egg scons

    # Print all availalbe development platforms for installing
    $ platformio search all

    # Install new development platform
    $ platformio install SomePlatform

    # Initialize new platformio based project
    $ cd /path/to/empty/directory
    $ platformio init

    # Process the project's environments
    $ platformio run

For more detailed information please follow to `Installation <#installation>`_
and `User Guide <#user-guide>`_ sections.


Installation
------------

All commands below should be executed in
`Command-line <http://en.wikipedia.org/wiki/Command-line_interface>`_
application in your OS:

* *Unix/Linux/OS X* this is *Terminal* application.
* *Windows* this is
  `Command Prompt <http://en.wikipedia.org/wiki/Command_Prompt>`_ (``cmd.exe``)
  application.

2. Check a ``python`` version:

.. code-block:: bash

    $ python --version

Windows OS Users only:

    * `Download Python <https://www.python.org/downloads/>`_ and install it.
    * Add to PATH system variable ``;C:\Python27;C:\Python27\Scripts;`` and
       reopen *Command Prompt* (``cmd.exe``) application. Please read this
       article `How to set the path and environment variables in Windows
       <http://www.computerhope.com/issues/ch000549.htm>`_.


2. Check a ``pip`` tool for installing and managing Python packages:

.. code-block:: bash

    $ pip search platformio

You should see short information about ``platformio`` package.

If your computer does not recognize ``pip`` command, try to install it first
using `these instructions <http://www.pip-installer.org/en/latest/installing.html>`_.

3. Install a ``platformio`` and related packages:

.. code-block:: bash

    $ pip install platformio && pip install --egg scons

For upgrading the ``platformio`` to new version please use this command:

.. code-block:: bash

    $ pip install -U platformio


User Guide
----------

To print all available commands and options:

.. code-block:: bash

    $ platformio --help
    $ platformio COMMAND --help

    # Example
    $ platformio --help
    Usage: platformio [OPTIONS] COMMAND [ARGS]...

    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.

    Commands:
      init       Initialize new platformio based project
      install    Install new platforms
      list       List installed platforms
      run        Process project environments
      search     Search for development platforms
      show       Show details about an installed platforms
      uninstall  Uninstall the platforms
      update     Update installed platforms


``platformio search``
~~~~~~~~~~~~~~~~~~~~~

Search for development platforms:

.. code-block:: bash

    # Print all available development platforms
    $ platformio search all

    # Filter platforms by "Query"
    $ platformio search "Query"

    # Example
    $ platformio search ti
    timsp430 - An embedded platform for TI MSP430 microcontrollers (with Energia Framework)
    titiva   - An embedded platform for TI TIVA C ARM microcontrollers (with Energia Framework)

    $ platformio search arduino
    atmelavr - An embedded platform for Atmel AVR microcontrollers (with Arduino Framework)


``platformio install``
~~~~~~~~~~~~~~~~~~~~~~

*Platformio* has pre-built development platforms with related packages. You
can install one of them:

.. code-block:: bash

    $ platformio install SomePlatform
    $ platformio install SomePlatform --with-package=PackageName
    $ platformio install SomePlatform --without-package=PackageName

    # Example
    $ platformio install timsp430 --with-package=framework-energiamsp430
    Installing toolchain-timsp430 package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing tool-mspdebug package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing framework-energiamsp430 package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The platform 'timsp430' has been successfully installed!


``platformio list``
~~~~~~~~~~~~~~~~~~~

To list installed platforms:

.. code-block:: bash

    $ platformio list

    # Example
    $ platformio list
    timsp430    with packages: toolchain-timsp430, tool-mspdebug, framework-energiamsp430


``platformio show``
~~~~~~~~~~~~~~~~~~~

To show details about an installed platform:

.. code-block:: bash

    $ platformio show SomePlatform

    # Example
    $ platformio show timsp430
    timsp430    - An embedded platform for TI MSP430 microcontrollers (with Energia Framework)
    ----------
    Package: toolchain-timsp430
    Location: /Users/ikravets/.platformio/timsp430/tools/toolchain
    Version: 1
    ----------
    Package: tool-mspdebug
    Location: /Users/ikravets/.platformio/timsp430/tools/mspdebug
    Version: 1
    ----------
    Package: framework-energiamsp430
    Location: /Users/ikravets/.platformio/timsp430/frameworks/energia
    Version: 1


``platformio uninstall``
~~~~~~~~~~~~~~~~~~~~~~~~

To uninstall platform:

.. code-block:: bash

    $ platformio uninstall SomePlatform

    # Example
    $ platformio uninstall timsp430
    Uninstalling toolchain-timsp430 package:        [OK]
    Uninstalling tool-mspdebug package:             [OK]
    Uninstalling framework-energiamsp430 package:   [OK]
    The platform 'timsp430' has been successfully uninstalled!


``platformio init``
~~~~~~~~~~~~~~~~~~~

Initialize new platformio based project.

.. code-block:: bash

    # Change directory to future project
    $ cd /path/to/empty/directory
    $ platformio init

    # Example
    $ platformio init
    Project successfully initialized.
    Please put your source code to `src` directory, external libraries to `libs`
    and setup environments in `platformio.ini` file.
    Then process project with `platformio run` command.

After this command ``platformio`` will create:

* ``.pioenvs`` - a temporary working directory.
* ``libs`` - a directory for project specific libraries. Platformio will
  compile their to static libraries and link to executable file
* ``src`` - a source directory. Put code here.
* ``platformio.ini`` - a configuration file for project


``platformio run``
~~~~~~~~~~~~~~~~~~

Process the project's environments defined in ``platformio.ini`` file:

.. code-block:: bash

    $ platformio run

    # Example
    $ platformio run
    Processing arduino_pro5v environment:
    scons: `.pioenvs/arduino_pro5v/firmware.elf' is up to date.
    scons: `.pioenvs/arduino_pro5v/firmware.hex' is up to date.

    Processing launchpad_msp430g2 environment:
    scons: `.pioenvs/launchpad_msp430g2/firmware.elf' is up to date.
    scons: `.pioenvs/launchpad_msp430g2/firmware.hex' is up to date.

    Processing launchpad_lm4f120 environment:
    scons: `.pioenvs/launchpad_lm4f120/firmware.elf' is up to date.
    scons: `.pioenvs/launchpad_lm4f120/firmware.hex' is up to date

Process specific environments:

.. code-block:: bash

    $ platformio run -e myenv1 -e myenv2

    # Example
    $ platformio run -e arduino_pro5v -e launchpad_lm4f120
    Processing arduino_pro5v environment:
    scons: `.pioenvs/arduino_pro5v/firmware.elf' is up to date.
    scons: `.pioenvs/arduino_pro5v/firmware.hex' is up to date.

    Skipped launchpad_msp430g2 environment
    Processing launchpad_lm4f120 environment:
    scons: `.pioenvs/launchpad_lm4f120/firmware.elf' is up to date.
    scons: `.pioenvs/launchpad_lm4f120/firmware.hex' is up to date.

Process specific target:

.. code-block:: bash

    $ platformio run -t clean
    $ platformio run -t upload

    # Example
    platformio run -t clean
    Processing arduino_pro5v environment:
    Removed .pioenvs/arduino_pro5v/src/main.o
    ...
    Removed .pioenvs/arduino_pro5v/firmware.hex

    Processing launchpad_msp430g2 environment:
    Removed .pioenvs/launchpad_msp430g2/src/main.o
    ...
    Removed .pioenvs/launchpad_msp430g2/firmware.hex

    Processing launchpad_lm4f120 environment:
    Removed .pioenvs/launchpad_lm4f120/src/main.o
    ...
    Removed .pioenvs/launchpad_lm4f120/firmware.hex

Mix environments and targets:

.. code-block:: bash

    $ platformio run -e myembeddeddevice -t upload

    # Example
    $ platformio run -e launchpad_msp430g2 -t upload
    Skipped arduino_pro5v environment
    Processing launchpad_msp430g2 environment:
    /Users/ikravets/.platformio/timsp430/tools/mspdebug/mspdebug rf2500 --force-reset "prog .pioenvs/launchpad_msp430g2/firmware.hex"
    MSPDebug version 0.20 - debugging tool for MSP430 MCUs
    Copyright (C) 2009-2012 Daniel Beer <dlbeer@gmail.com>
    This is free software; see the source for copying conditions.  There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    Trying to open interface 1 on 009
    Initializing FET...
    FET protocol version is 30394216
    Configured for Spy-Bi-Wire
    Sending reset...
    Set Vcc: 3000 mV
    Device ID: 0x2553
      Code start address: 0xc000
      Code size         : 16384 byte = 16 kb
      RAM  start address: 0x200
      RAM  end   address: 0x3ff
      RAM  size         : 512 byte = 0 kb
    Device: MSP430G2553/G2403
    Code memory starts at 0xc000
    Number of breakpoints: 2
    Chip ID data: 25 53
    Erasing...
    Programming...
    Writing  646 bytes at c000...
    Writing   32 bytes at ffe0...
    Done, 678 bytes total

    Skipped launchpad_lm4f120 environment


``platformio update``
~~~~~~~~~~~~~~~~~~~~~~~~

To check or update installed platforms:

.. code-block:: bash

    $ platformio update

    # Example
    $ platformio update

    Platform atmelavr
    --------
    Updating toolchain-atmelavr package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-arduinoavr package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-avrdude package:
    Versions: Current=1, Latest=1 	 [Up-to-date]

    Platform timsp430
    --------
    Updating toolchain-timsp430 package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-mspdebug package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-energiamsp430 package:
    Versions: Current=1, Latest=1 	 [Up-to-date]

    Platform titiva
    --------
    Updating toolchain-gccarmnoneeabi package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-lm4flash package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-energiativa package:
    Versions: Current=1, Latest=1 	 [Up-to-date]


Questions & Bugs
----------------

Please use the
`issue tracker <https://github.com/ivankravets/platformio/issues>`_
to ask questions or report bugs.


Licence
-------

Copyright (C) 2014 Ivan Kravets

Licenced under the MIT Licence.
