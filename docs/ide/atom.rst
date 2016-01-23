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

`Atom <https://atom.io>`_ is a text editor that's modern, approachable,
yet hackable to the core—a tool you can customize to do anything but also use
productively without ever touching a config file.

PlatformIO IDE for `Atom <https://atom.io>`_ is the missing integrated
development environment which provides comprehensive facilities
for IoT development:

* Cross-platform builder without external dependencies to the system
  software:

    - 200+ embedded boards
    - 15+ development platforms
    - 10+ frameworks

* C/C++ `Intelligent code completion <https://en.wikipedia.org/wiki/Intelligent_code_completion>`_
* C/C++ `Code Linter <https://en.wikipedia.org/wiki/Lint_(software)>`_
* Library Manager
* Built-in Terminal

.. contents::

Requirements
------------

The only one requirement is `Python Interpreter <https://www.python.org>`_.
PlatformIO is written in Python and works on Mac OS X, Linux, Windows OS and
ARM-based credit-card sized computers (Raspberry Pi, BeagleBone, CubieBoard).

.. attention::
    **Windows Users**: Please `Download the latest Python 2.7.x
    <https://www.python.org/downloads/>`_ and install it.
    **DON'T FORGET** to select ``Add python.exe to Path`` feature on the
    "Customize" stage, otherwise ``python`` command will not be available.

Installation
------------

1. Download and install `Atom <https://atom.io>`_ text editor
2. Install `platformio-ide <https://atom.io/packages/platformio-ide>`_ package
   using:

   - **Mac OS X**: ``Menu: Atom > Preferences > Install``
   - **Other OS**: ``Menu: File > Settings > Install``

User Guide
----------

Building / Uploading / etc.
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``cmd-alt-b`` / ``ctrl-alt-b`` / ``f9`` builds project without auto-uploading.
* ``cmd-alt-u`` / ``ctrl-alt-u`` builds and uploads (if no errors).
* ``cmd-alt-c`` / ``ctrl-alt-c`` cleans compiled objects.
* ``cmd-alt-t`` / ``ctrl-alt-t`` / ``f7`` run other targets (Upload using Programmer, Upload SPIFFS image, Update platforms and libraries).
* ``cmd-alt-g`` / ``ctrl-alt-g`` / ``f4`` cycles through causes of build error.
* ``cmd-alt-h`` / ``ctrl-alt-h`` / ``shift-f4`` goes to the first build error.
* ``cmd-alt-v`` / ``ctrl-alt-v`` / ``f8`` toggles the build panel.
* ``escape`` terminates build / closes the build window.

More details `Atom Build package <https://atom.io/packages/build>`_.

Code completion and Linting
~~~~~~~~~~~~~~~~~~~~~~~~~~~

PlatformIO IDE uses `clang <http://clang.llvm.org>`_ for the code completion
and linting. To check that ``clang`` is available in your system, please open
Terminal and run ``clang --version``. If ``clang`` is not installed, then install it:

- **Mac OS X**: Install the latest Xcode along with the latest Command Line Tools
  (they are installed automatically when you run ``clang`` in Terminal for the
  first time, or manually by running ``xcode-select --install``
- **Windows**: Download the latest `Clang for Windows <http://llvm.org/releases/download.html>`_.
  Please select "Add to PATH" option on the installation step.
- **Linux**: Using package managers: ``apt-get install clang`` or ``yum install clang``.
- **Other Systems**: Download the latest `Clang for the other systems <http://llvm.org/releases/download.html>`_.

**Warning**: If you have previously generated PlatformIO project you need to
reinitialize it using ``Menu: PlatformIO > Initialize new Project (or update existing)``
and specify for the which board should be activated Code completion and Linter.

Screenshot
----------

.. image:: ../_static/ide-atom-platformio.png
    :target: ../_static/ide-atom-platformio.png
