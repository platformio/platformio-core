PlatformIO
==========

**Platformio** is a console tool to build code with different development
platforms.

You do not need to install any *IDE* or to compile any toolchains. *Platformio*
has pre-built different development platforms for your favorite *OS* that
including: compiler, debugger, flasher (for embedded) and many others useful
tools.

**Platformio** allows developer to compile single sources with different
platforms with only one command ``platformio run``. This is due to
``platformio.ini`` project's file where you can setup different environments
with specific settings (platform, compiler or firmware uploading options,
include pre-built framework and many more)

Each platform consists of packages that are located in own repository.
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


See project `examples <https://github.com/ivankravets/platformio/tree/develop/examples>`_


Python & OS Support
-------------------

**Platformio** written in `Python <https://www.python.org>`_ and works with
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

For more detailed information please follow to "Installation" and "User Guide"
sections.


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


``platformio search``
~~~~~~~~~~~~~~~~~~~~~

Search for development platforms:

.. code-block:: bash

    # Print all available development platforms
    $ platformio search all

    # Filter platforms by "Query"
    $ platformio search "Query"


``platformio install``
~~~~~~~~~~~~~~~~~~~~~~

*Platformio* has pre-built development platforms with related packages. You
can install one of them:

.. code-block:: bash

    $ platformio install SomePlatform
    $ platformio install SomePlatform --with-package=PackageName
    $ platformio install SomePlatform --without-package=PackageName


``platformio list``
~~~~~~~~~~~~~~~~~~~

To list installed platforms:

.. code-block:: bash

    $ platformio list


``platformio show``
~~~~~~~~~~~~~~~~~~~

To show details about an installed platform:

.. code-block:: bash

    $ platformio show SomePlatform


``platformio uninstall``
~~~~~~~~~~~~~~~~~~~~~~~~

To uninstall platform:

.. code-block:: bash

    $ platformio uninstall SomePlatform


``platformio init``
~~~~~~~~~~~~~~~~~~~

Initialize new platformio based project.

.. code-block:: bash

    # Change directory to future project
    $ cd /path/to/empty/directory
    $ platformio init

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

Process specific environments:

.. code-block:: bash

    $ platformio run -e myenv1 -e myenv2

Process specific target:

.. code-block:: bash

    $ platformio run -t clean
    $ platformio run -t upload

Mix environments and targets:

.. code-block:: bash

    $ platformio run -e myembeddeddevice -t upload


Questions & Bugs
----------------

Please use the
`issue tracker <https://github.com/ivankravets/platformio/issues>`_
to ask questions or report bugs.


Licence
-------

Copyright (C) 2014 Ivan Kravets

Licenced under the MIT Licence.
