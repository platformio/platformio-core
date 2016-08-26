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

.. _ide_eclipse:

Eclipse
=======

The `Eclipse CDT (C/C++ Development Tooling) <https://eclipse.org/cdt/>`_
Project provides a fully functional C and C++ Integrated Development
Environment based on the Eclipse platform. Features include: support for
project creation and managed build for various toolchains, standard make
build, source navigation, various source knowledge tools, such as type
hierarchy, call graph, include browser, macro definition browser, code editor
with syntax highlighting, folding and hyperlink navigation, source code
refactoring and code generation, visual debugging tools, including memory,
registers, and disassembly viewers.

Refer to the `CDT Documentation <https://eclipse.org/cdt/documentation.php>`_
page for more detailed information.

.. image:: ../_static/ide-platformio-eclipse.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-eclipse.png

.. contents::

Integration
-----------

Choose board ``ID`` using :ref:`cmd_boards` or `Embedded Boards Explorer <http://platformio.org/boards>`_
command and generate project via :option:`platformio init --ide` command:

.. code-block:: shell

    platformio init --ide eclipse --board %ID%

    # For example, generate project for Arduino UNO
    platformio init --ide eclipse --board uno

Then:

1. Import this project via
   ``Menu: File > Import... > General > Existing Projects into Workspace > Next``
   and specify root directory where is located :ref:`projectconf`
2. Open source file from ``src`` directory (``*.c, *.cpp, *.ino, etc.``)
3. Build project using ``Menu: Project > Build Project`` or pre-configured
   Make Targets (see screenshot below):

   + ``PlatformIO: Build`` - Build project without auto-uploading
   + ``PlatformIO: Clean`` - Clean compiled objects.
   + ``PlatformIO: Upload`` - Build and upload (if no errors)
   + ``PlatformIO: Upload using Programmer`` see :ref:`atmelavr_upload_via_programmer`
   + ``PlatformIO: Upload SPIFFS image`` see :ref:`platform_espressif_uploadfs`
   + ``PlatformIO: Update platforms and libraries`` - Update installed
     platforms and libraries via :ref:`cmd_update`
   + ``PlatformIO: Rebuild C/C++ Project Index`` - Rebuild C/C++ Index for the Project.
     Allows to fix code completion and code linting issues.

If you have some problems with unresolved includes, defines, etc., then

1. Rebuild PlatformIO Project Index:
   ``PlatformIO: Rebuild C/C++ Project Index`` target
2. Rebuild Eclipse Project Index: ``Menu: Project > C/C++ Index > Rebuild``
3. Refresh Project, right click on the project ``Project > Refresh`` (F5) or
   restart Eclipse IDE.

.. warning::
    The libraries which are added, installed or used in the project
    after generating process wont be reflected in IDE. To fix it please run
    ``PlatformIO: Rebuild C/C++ Project Index`` target and right click on the
    project and ``Project > Refresh`` (F5).

Live Integration
----------------

Eclipse Virtual IoT Meetup: `PlatformIO: a cross-platform IoT solution to build them all! <http://www.meetup.com/Virtual-IoT/events/229964142/>`_

.. image:: ../_static/ide-eclipse-virtualiot.jpg
    :target: https://www.youtube.com/watch?v=6t7UbX812Yw

Articles / Manuals
------------------

* May 05, 2016 - **Ivan Kravets, Ph.D. / Eclipse Virtual IoT Meetup** - `PlatformIO: a cross-platform IoT solution to build them all! <http://www.meetup.com/Virtual-IoT/events/229964142/>`_
* Sep 01, 2015 - **Thomas P. Weldon, Ph.D.** - `Improvised MBED FRDM-K64F Eclipse/PlatformIO Setup and Software Installation <http://thomasweldon.com/tpw/courses/embeddsp/p00pcFrdmK64_eclipsePlatformioSetup.html>`_
* Jul 11, 2015 - **TrojanC** - `Learning Arduino GitHub Repository <http://www.trojanc.co.za/2015/07/11/learning-arduino-github-repository/>`_
* June 20, 2014 - **Ivan Kravets, Ph.D.** - `Building and debugging Atmel AVR (Arduino-based) project using Eclipse IDE+PlatformIO <http://www.ikravets.com/computer-life/programming/2014/06/20/building-and-debugging-atmel-avr-arduino-based-project-using-eclipse-ideplatformio>`_

See a full list with :ref:`articles`.

Examples
--------

"Blink" Project
^^^^^^^^^^^^^^^

Source code of `Eclipse "Blink" Project <https://github.com/platformio/platformio-examples/tree/develop/ide/eclipse>`_.
