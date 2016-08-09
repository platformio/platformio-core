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

.. _ide_qtcreator:

Qt Creator
==========

The `Qt Creator <https://github.com/qtproject/qt-creator>`_ is an open source cross-platform integrated development environment. The editor includes such features as syntax highlighting for various languages, project manager, integrated version control systems, rapid code navigation tools and code autocompletion.

Refer to the `Qt-creator Manual <http://doc.qt.io/qtcreator/>`_
page for more detailed information.

.. image:: ../_static/ide-platformio-qtcreator-7.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-7.png

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

    platformio init --ide qtcreator --board %TYPE%

    # For example, generate project for Arduino UNO
    platformio init --ide qtcreator --board uno

Then:

1. Import project via ``File > Open File or Project`` and select
   ``platformio.pro`` from the folder where is located :ref:`projectconf`
2. Select default desktop kit and click on ``Configure Project`` (``Projects``
   mode, left panel)
3. Set ``General > Build directory`` to the project directory where
   is located :ref:`projectconf`
4. Remove all items from ``Build Steps``, click on
   ``Build Steps > Add Build Step > Custom Process Step`` and set:

   * **Command**: ``platformio``
   * **Arguments**: ``-f -c qtcreator run``
   * **Working directory**: ``%{buildDir}``

5. Remove all items from ``Clean Steps``, click on
   ``Clean Steps > Add Clean Step > Custom Process Step`` and set:

   * **Command**: ``platformio``
   * **Arguments**: ``-f -c qtcreator run --target clean``
   * **Working directory**: ``%{buildDir}``

6. Update ``PATH`` in ``Build Environment > PATH > EDIT`` with the result of
   this command (paste in Terminal):

.. code-block:: shell

    # Linux, Mac
    echo $PATH

    # Windows
    echo %PATH%

7. Switch to ``Edit`` mode (left panel) and open source file from ``src``
   directory (``*.c, *.cpp, *.ino, etc.``)
8. Build project: ``Menu: Build > Build All``.

.. image:: ../_static/ide-platformio-qtcreator-3.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-3.png

.. warning::
    The libraries which are added, installed or used in the project
    after generating process wont be reflected in IDE. To fix it you
    need to reinitialize project using :ref:`cmd_init` (repeat it).

Manual Integration
^^^^^^^^^^^^^^^^^^

Setup New Project
~~~~~~~~~~~~~~~~~

First of all, let's create new project from Qt Creator Start Page: ``New Project`` or using ``Menu: File > New File or Project``, then select project with ``Empty Qt Project`` type (``Other Project > Empty Qt Project``), fill ``Name``, ``Create in``.

.. image:: ../_static/ide-platformio-qtcreator-1.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-1.png

On the next steps select any available kit and click Finish button.

.. image:: ../_static/ide-platformio-qtcreator-2.png

Secondly, we need to delete default build and clean steps and configure project with PlatformIO Build System (click on Projects label on left menu or ``Ctrl+5`` shortcut):

.. image:: ../_static/ide-platformio-qtcreator-3.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-3.png

Thirdly, change project file by adding path to directories with header files. Please edit project file to match the following contents:

.. code-block:: none

    win32 {
        HOMEDIR += $$(USERPROFILE)
    }
    else {
        HOMEDIR += $$(HOME)
    }

    INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduinoavr/cores/arduino"
    INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/toolchain-atmelavr/avr/include"

.. image:: ../_static/ide-platformio-qtcreator-4.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-4.png

First program in Qt Creator
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Simple "Blink" project will consist from two files:
1. In the console, navigate to the root of your project folder and initialize platformio project with ``platformio init``
2. The main "C" source file named ``main.c`` must be located in the ``src`` directory.
Let's create new text file named ``main.c`` using ``Menu: New File or Project > General > Text File``:

.. image:: ../_static/ide-platformio-qtcreator-5.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-5.png

Copy the source code which is described below to file ``main.c``.

.. code-block:: c

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

3. Locate the project configuration file named ``platformio.ini`` at the root of the project directory and open it.

.. image:: ../_static/ide-platformio-qtcreator-6.png
    :target: http://docs.platformio.org/en/stable/_static/ide-platformio-qtcreator-6.png

Edit the content to match the code described below.

.. code-block:: ini

    ; PlatformIO Project Configuration File
    ;
    ;   Build options: build flags, source filter, extra scripting
    ;   Upload options: custom port, speed and extra flags
    ;   Library options: dependencies, extra library storages
    ;
    ; Please visit documentation for the other options and examples
    ; http://docs.platformio.org/en/stable/projectconf.html

    [env:arduino_uno]
    platform = atmelavr
    framework = arduino
    board = uno

Conclusion
~~~~~~~~~~

Taking everything into account, we can build project with shortcut ``Ctrl+Shift+B`` or using ``Menu: Build > Build All``.

Examples
--------

"Blink" Project
^^^^^^^^^^^^^^^

Source code of `Qt Creator "Blink" Project <https://github.com/platformio/platformio-examples/tree/develop/ide/qtcreator>`_.
