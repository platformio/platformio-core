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

.. _installation:

Installation
============

.. note::

    Please note that you do not need to install **PlatformIO Core** if you
    are going to use :ref:`ide_atom`. **PlatformIO Core** is built into
    PlatformIO IDE and you will be able to use it within PlatformIO IDE Terminal.

    Also, PlatformIO IDE allows to install :ref:`core` Shell Commands
    (``pio``, ``platformio``) globally to your system via
    ``Menu: PlatformIO > Install Shell Commands``.

**PlatformIO Core** is written in `Python <https://www.python.org/downloads/>`_
and works on Windows, macOS, Linux, FreeBSD and *ARM*-based credit-card sized
computers (`Raspberry Pi <http://www.raspberrypi.org>`_,
`BeagleBone <http://beagleboard.org>`_,
`CubieBoard <http://cubieboard.org>`_).

.. contents::

System requirements
-------------------

:Operating System: Mac OS X, Linux (+ARM) or Windows
:Python Interpreter:

    Python 2.7 is required. PlatformIO **does not** support Python 3.

    .. attention::
        **Windows Users**: Please `Download the latest Python 2.7.x
        <https://www.python.org/downloads/>`_ and install it.
        **DON'T FORGET** to select ``Add python.exe to Path`` feature on the
        "Customize" stage, otherwise Python Package Manager ``pip`` command
        will not be available.

        .. image:: _static/python-installer-add-path.png

:Terminal Application:

    All commands below should be executed in
    `Command-line <http://en.wikipedia.org/wiki/Command-line_interface>`_
    application (Terminal). For Mac OS X and Linux OS - *Terminal* application,
    for Windows OS – ``cmd.exe`` application.


:Access to Serial Ports (USB/UART):

    **Windows Users:** Please check that you have correctly installed USB
    driver from board manufacturer

    **Linux Users**:

    * Ubuntu/Debian users may need to add own "username" to the "dialout"
      group if they are not "root", doing this issuing a
      ``sudo usermod -a -G dialout yourusername``.
    * Install "udev" rules file `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_
      (an instruction is located in the file).
    * Raspberry Pi users, please read this article
      `Enable serial port on Raspberry Pi <https://hallard.me/enable-serial-port-on-raspberry-pi/>`__.


Installation Methods
--------------------

Please *choose ONE of* the following methods:

.. contents::
    :local:

Python Package Manager
~~~~~~~~~~~~~~~~~~~~~~

The latest stable version of PlatformIO may be installed or upgraded via
Python Package Manager (`pip <https://pip.pypa.io>`_) as follows:

.. code-block:: bash

    pip install -U platformio

If ``pip`` command is not available run ``easy_install pip`` or use
:ref:`installation_installer_script` which will install ``pip`` and
``platformio`` automatically.

Note that you may run into permissions issues running these commands. You have
a few options here:

* Run with ``sudo`` to install PlatformIO and dependencies globally
* Specify the `pip install --user <https://pip.pypa.io/en/stable/user_guide.html#user-installs>`_
  option to install local to your user
* Run the command in a `virtualenv <https://virtualenv.pypa.io>`_ local to a
  specific project working set.

.. _installation_installer_script:

Installer Script
~~~~~~~~~~~~~~~~

Super-Quick (Mac / Linux)
'''''''''''''''''''''''''

To install or upgrade *PlatformIO* paste that at a *Terminal* prompt
(**MAY require** administrator access ``sudo``):

.. code-block:: bash

    python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"


Local Download (Mac / Linux / Windows)
''''''''''''''''''''''''''''''''''''''

To install or upgrade *PlatformIO*, download (save as...)
`get-platformio.py <https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py>`_
script. Then run the following (**MAY require** administrator access ``sudo``):

.. code-block:: bash

    # change directory to folder where is located downloaded "get-platformio.py"
    cd /path/to/dir/where/is/located/get-platformio.py/script

    # run it
    python get-platformio.py


On *Windows OS* it may look like:

.. code-block:: bash

    # change directory to folder where is located downloaded "get-platformio.py"
    cd C:\path\to\dir\where\is\located\get-platformio.py\script

    # run it
    C:\Python27\python.exe get-platformio.py


Mac OS X Homebrew
~~~~~~~~~~~~~~~~~

The latest stable version of PlatformIO may be installed or upgraded via
Mac OS X Homebrew Packages Manager (`brew <http://brew.sh/>`_) as follows:

.. code-block:: bash

    brew install platformio

Full Guide
~~~~~~~~~~

1. Check a ``python`` version (only Python 2.7 is supported):

.. code-block:: bash

    python --version

*Windows Users* only:

    * `Download Python 2.7 <https://www.python.org/downloads/>`_ and install it.
    * Add to PATH system variable ``;C:\Python27;C:\Python27\Scripts;`` and reopen *Command Prompt* (``cmd.exe``) application. Please read this article `How to set the path and environment variables in Windows <http://www.computerhope.com/issues/ch000549.htm>`_.

2. Install a ``platformio`` and related packages:

.. code-block:: bash

    pip install -U platformio

If your computer does not recognize ``pip`` command, try to install it first
using `these instructions <https://pip.pypa.io/en/latest/installing.html>`_.

For upgrading ``platformio`` to the latest version:

.. code-block:: bash

    pip install -U platformio

.. _installation_develop:

Development Version
~~~~~~~~~~~~~~~~~~~

.. warning::
    If you use :ref:`ide_atom`, please enable development version via
    ``Menu PlatformIO: Settings > PlatformIO IDE > Use development version of
    PlatformIO``.

Install the latest PlatformIO from the ``develop`` branch:

.. code-block:: bash

    # uninstall existing version
    pip uninstall platformio

    # install the latest development version of PlatformIO
    pip install -U https://github.com/platformio/platformio/archive/develop.zip

If you want to be up-to-date with the latest ``develop`` version of PlatformIO,
then you need to re-install PlatformIO each time if you see the new commits in
`PlatformIO GitHub repository (branch: develop) <https://github.com/platformio/platformio/commits/develop>`_.

To revert to the latest stable version

.. code-block:: bash

    pip uninstall platformio
    pip install -U platformio


Troubleshooting
---------------

.. note::
    **Linux OS**: Don't forget to install "udev" rules file
    `99-platformio-udev.rules <https://github.com/platformio/platformio/blob/develop/scripts/99-platformio-udev.rules>`_ (an instruction is located in the file).

    **Windows OS**: Please check that you have correctly installed USB driver
    from board manufacturer

For further details, frequently questions, known issues, please
refer to :ref:`faq`.
