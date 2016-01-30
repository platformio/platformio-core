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

PlatformIO IDE for Atom
=======================

PlatformIO IDE is the next generation integrated development environment for IoT:

* Cross-platform code builder without external dependencies to the system
  software:

    - 200+ embedded boards
    - 15+ development platforms
    - 10+ frameworks

* C/C++ Intelligent code completion
* C/C++ Smart code linter for super-fast coding
* Library Manager for the hundreds popular libraries
* Multi-projects workflow with multiple panes
* Multiple panes
* Themes support with dark and light colors
* Serial Port Monitor
* Built-in Terminal with :ref:`PlatformIO CLI <userguide>` tool (``pio``, ``platformio``)

PlatformIO IDE is based on GitHub's `Atom <https://atom.io>`_ source
code editor that's modern, approachable, yet hackable to the core—a tool you
can customize to do anything but also use productively without ever touching a
config file.


.. contents::

Installation
------------

1. Download and install Atom source code editor

    - `Download for Mac <https://atom.io/download/mac>`_
    - `Download for Windows <https://atom.io/download/windows>`_
    - `Download .deb <https://atom.io/download/deb>`_
    - `Download .rpm <https://atom.io/download/rpm>`_
    - `Other platforms <https://github.com/atom/atom/releases/latest>`_


2. Open Atom Package Manager and search for `platformio-ide <https://atom.io/packages/platformio-ide>`_

    - **Mac OS X**: ``Menu: Atom > Preferences > Install``
    - **Windows**: ``Menu: File > Settings > Install``
    - **Linux**: ``Menu: Edit > Preferences > Install``

.. image:: ../_static/ide-atom-platformio-install.png

User Guide
----------

.. image:: ../_static/ide-atom-platformio.png
    :target: http://docs.platformio.org/en/latest/_images/ide-atom-platformio.png

Menu item ``PlatformIO``
~~~~~~~~~~~~~~~~~~~~~~~~

`platformio-ide <https://atom.io/packages/platformio-ide>`_ package adds to Atom
new menu item named ``Menu: PlatformIO`` (after ``Menu: Help`` item).

.. image:: ../_static/ide-atom-platformio-menu-item.png

PlatformIO Toolbar
~~~~~~~~~~~~~~~~~~


PlatformIO IDE Toolbar contains the quick access button to the popular commands.
Each button contains hint (delay mouse on it).

.. image:: ../_static/ide-atom-platformio-toolbar.png

* PlatformIO: Build
* PlatformIO: Upload
* PlatformIO: Clean
* Toggle build panel
* ||
* New File
* Add/Open Project Folder...
* Find in Project...
* ||
* Terminal
* Serial Ports
* Serial Monitor
* ||
* Settings
* PlatformIO Documentation

.. _ide_atom_quickstart:

Quickstart
~~~~~~~~~~

:Step 1:

    Create empty directory for the future project. Add it to PlatformIO IDE
    using (folder) button on the Toolbar or ``Menu: File > Add Project
    Folder...``

:Step 2:

    Initialize new PlatformIO based project using ``Menu: PlatformIO >
    Initialize new Project (or update existing)`` and select boards.
    Put your source code ``*.h, *.c, *.cpp, *.S, *.ino, etc``. files to ``src``
    directory.

:Step 3:

    Process the project environments. More details :ref:`ide_atom_building_targets`.


.. _ide_atom_building_targets:

Building / Uploading / Targets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``cmd-alt-b`` / ``ctrl-alt-b`` / ``f9`` builds project without auto-uploading.
* ``cmd-alt-u`` / ``ctrl-alt-u`` builds and uploads (if no errors).
* ``cmd-alt-c`` / ``ctrl-alt-c`` cleans compiled objects.
* ``cmd-alt-t`` / ``ctrl-alt-t`` / ``f7`` run other targets (Upload using Programmer, Upload SPIFFS image, Update platforms and libraries).
* ``cmd-alt-g`` / ``ctrl-alt-g`` / ``f4`` cycles through causes of build error.
* ``cmd-alt-h`` / ``ctrl-alt-h`` / ``shift-f4`` goes to the first build error.
* ``cmd-alt-v`` / ``ctrl-alt-v`` / ``f8`` toggles the build panel.
* ``escape`` terminates build / closes the build window.

More details `Atom Build package <https://atom.io/packages/build>`_.

Code completion
~~~~~~~~~~~~~~~

PlatformIO IDE uses `clang <http://clang.llvm.org>`_ for the code completion.
To check that ``clang`` is available in your system, please open
Terminal and run ``clang --version``. If ``clang`` is not installed, then install it:

- **Mac OS X**: Install the latest Xcode along with the latest Command Line Tools
  (they are installed automatically when you run ``clang`` in Terminal for the
  first time, or manually by running ``xcode-select --install``
- **Windows**: Download the latest `Clang for Windows <http://llvm.org/releases/download.html>`_.
  Please select "Add LLVM to the system PATH" option on the installation step.
- **Linux**: Using package managers: ``apt-get install clang`` or ``yum install clang``.
- **Other Systems**: Download the latest `Clang for the other systems <http://llvm.org/releases/download.html>`_.

.. warning::
    The libraries which are added/installed after initializing process will
    not be reflected in code linter. You need ``Menu: PlatformIO >
    Rebuild C/C++ Project Index (Autocomplete, Linter)``.

Code linter
~~~~~~~~~~~

PlatformIO IDE uses PlatformIO's pre-built GCC toolchains for code linting. The
settings for Linter are located in ``.gcc-flags.json``. This file will be
automatically created and preconfigured when you initialize project using
``Menu: PlatformIO > Initialize new Project (or update existing)``.

.. warning::
    The libraries which are added/installed after initializing process will
    not be reflected in code linter. You need ``Menu: PlatformIO >
    Rebuild C/C++ Project Index (Autocomplete, Linter)``.


.. error::
    If you have error like ``linter-gcc: Executable not found`` and
    ``"***/.platformio/packages/toolchain-atmelavr/bin/avr-g++" not found``
    please ``Menu: PlatformIO > Initialize new Project (or update existing)``.

Install Shell Commands
~~~~~~~~~~~~~~~~~~~~~~

To install ``platformio`` and ``pio`` shell commands please use ``Menu:
PlatformIO > Install Shell Commands``. It will allow you to call PlatformIO from
other process, terminal and etc.

Known issues
~~~~~~~~~~~~

* Built-in Terminal doesn't support ``STDIN`` interaction
