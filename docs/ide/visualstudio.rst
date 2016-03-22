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

.. _ide_visualstudio:

Visual Studio
=============

The `Microsoft Visual Studio (Free) <http://visualstudio.com/free>`_ is an integrated development environment (IDE) from Microsoft. Visual Studio includes a code editor supporting IntelliSense (the code completion component) as well as code refactoring.

Refer to the `Visual Studio Documentation <https://msdn.microsoft.com/library/vstudio>`_
page for more detailed information.

.. image:: ../_static/ide-vs-platformio-newproject-8.png
    :target: http://docs.platformio.org/en/latest/_static/ide-vs-platformio-newproject-8.png

.. contents::

Integration
-----------

.. note::
    Please verify that folder where is located ``platformio`` program is added
    to `PATH (wiki) <https://en.wikipedia.org/wiki/PATH_(variable)>`_ environment
    variable. See FAQ: :ref:`faq_troubleshooting_pionotfoundinpath`.

Project Generator
^^^^^^^^^^^^^^^^^

Choose board ``type`` using :ref:`cmd_boards` or `Embedded Boards Explorer <http://platformio.org/boards>`_
command and generate project via :option:`platformio init --ide` command:

.. code-block:: shell

    platformio init --ide sublimetext --board %TYPE%

    # For example, generate project for Arduino UNO
    platformio init --ide visualstudio --board uno

Then:

1. Import this project via ``Menu: File > Open > Project/Solution``
   and specify root directory where is located :ref:`projectconf`
2. Open source file from ``src`` directory (``*.c, *.cpp, *.ino, etc.``)
3. Build project: ``Menu: Build > Build Solution``.

.. warning::
    The libraries which are added, installed or used in the project
    after generating process wont be reflected in IDE. To fix it you
    need to reinitialize project using :ref:`cmd_init` (repeat it).

Manual Integration
^^^^^^^^^^^^^^^^^^

Setup New Project
~~~~~~~~~~~~~~~~~

First of all, let's create new project from Visual Studio Start Page: ``Start > New Project`` or using ``Menu: File > New > Project``, then select project with ``Makefile`` type (``Visual C++ > General > Makefile Project``), fill ``Project name``, ``Solution name``, ``Location`` fields and press OK button.

.. image:: ../_static/ide-vs-platformio-newproject.png

Secondly, we need to configure project with PlatformIO Build System:

.. image:: ../_static/ide-vs-platformio-newproject-2.png

If we want to use native AVR programming, we have to specify additional preprocessor symbol ("Preprocessor definitions" field) about your MCU. For example, an Arduino Uno is based on the ATmega328 MCU. In this case We will add new definition  ``__AVR_ATmega328__``.

.. image:: ../_static/ide-vs-platformio-newproject-2-1.png

Release Configuration is the same as Debug, so on the next step we check "Same as Debug Configuration" and click "Finish" button.

.. image:: ../_static/ide-vs-platformio-newproject-3.png

Thirdly, we need to add directories with header files using project properties (right click on the project name or ``Alt-Enter`` shortcut) and add two directories to ``Configuration Properties > NMake > Include Search Path``:

.. code-block:: none

    $(HOMEDRIVE)$(HOMEPATH)\.platformio\packages\toolchain-atmelavr\avr\include
    $(HOMEDRIVE)$(HOMEPATH)\.platformio\packages\framework-arduinoavr\cores\arduino

.. image:: ../_static/ide-vs-platformio-newproject-5.png

First program in Visual Studio
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple "Blink" project will consist from two files:

1. Main "C++" source file named ``main.cpp`` must be located in the ``src`` directory.
Let's create new file named ``main.cpp`` using ``Menu: File > New File`` or shortcut ``Ctrl+N``:

.. image:: ../_static/ide-vs-platformio-newproject-6.png

Copy the source code which is described below to file ``main.cpp``.

.. code-block:: cpp

    #include "Arduino.h"
    #define WLED    13  // Most Arduino boards already have an LED attached to pin 13 on the board itself

    void setup()
    {
      pinMode(WLED, OUTPUT);  // set pin as output
    }

    void loop()
    {
      digitalWrite(WLED, HIGH);  // set the LED on
      delay(1000);               // wait for a second
      digitalWrite(WLED, LOW);   // set the LED off
      delay(1000);               // wait for a second
    }

2. Project Configuration File named ``platformio.ini`` must be located in the project root directory.

.. image:: ../_static/ide-vs-platformio-newproject-7.png

Copy the source code which is described below to it.

.. code-block:: none

    #
    # Project Configuration File
    #
    # A detailed documentation with the EXAMPLES is located here:
    # http://docs.platformio.org/en/latest/projectconf.html
    #

    # A sign `#` at the beginning of the line indicates a comment
    # Comment lines are ignored.

    [env:arduino_uno]
    platform = atmelavr
    framework = arduino
    board = uno


Conclusion
~~~~~~~~~~

Taking everything into account, we can build project with shortcut ``Ctrl+Shift+B`` or using ``Menu: Build > Build Solution``.

Examples
--------

"Blink" Project
^^^^^^^^^^^^^^^

Source code of `Visual Studio "Blink" Project <https://github.com/platformio/platformio/tree/develop/examples/ide/visualstudio>`_.

Known issues
------------

IntelliSense Errors
^^^^^^^^^^^^^^^^^^^

VS Studio does not allow to specify for project other toolchain which will
be used by IntelliSense. In this case, IntelliSense does not understand
GCC-specific definitions.

However, these errors does not have any influence on PlatformIO Build
System. It means that you can ignore them and rely on PlatformIO Build System
messages which will be shown in output console after build.

Nevertheless, you can provide an IntelliSense-friendly definition of problematic
GCC constructs and make sure that the GCC will ignore such definitions or
disable IntelliSense error reporting at all.
See details in `issue #543 <https://github.com/platformio/platformio/issues/543>`_

.. image:: ../_static/ide-vs-platformio-newproject-9.png
    :target: http://docs.platformio.org/en/latest/_static/ide-vs-platformio-newproject-9.png
