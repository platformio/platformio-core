.. _ide_visualstudio:

Visual Studio
=============

The `Microsoft Visual Studio (Free) <http://visualstudio.com/free>`_ is an integrated development environment (IDE) from Microsoft. Visual Studio includes a code editor supporting IntelliSense (the code completion component) as well as code refactoring.

This software can be used with:

* all available :ref:`platforms`
* all available :ref:`frameworks`

Refer to the `Visual Studio Documentation <https://msdn.microsoft.com/library/vstudio>`_
page for more detailed information.

.. contents::

Integration
-----------

Project Generator
^^^^^^^^^^^^^^^^^

Since PlatformIO 2.0 you can generate Visual Studio compatible project using
:option:`platformio init --ide` command. Please choose board type using
:ref:`cmd_boards` command and run:

.. code-block:: shell

    platformio init --ide visualstudio --board %TYPE%

Then import this project via ``File->Open->Project/Solution`` and specify root
directory where is located :ref:`projectconf`.

Manual Integration
^^^^^^^^^^^^^^^^^^

Setup New Project
~~~~~~~~~~~~~~~~~

First of all, let's create new project from Visual Studio Start Page: ``Start > New Project`` or using ``Menu: File > New > Project``, then select project with ``Makefile`` type (``Visual C++ > General > Makefile Project``), fill ``Project name``, ``Solution name``, ``Location`` fields and press OK button.

.. image:: ../_static/ide-vs-platformio-newproject.png

Secondly, we need to configure project with PlatformIO source code builder:

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

1. Main "C" source file named ``main.c`` must be located in the ``src`` directory.
Let's create new file named ``main.c`` using ``Menu: File > New File`` or shortcut ``Ctrl+N``:

.. image:: ../_static/ide-vs-platformio-newproject-6.png

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
----------

Taking everything into account, we can build project with shortcut ``Ctrl+Shift+B`` or using ``Menu: Build > Build Solution``:

.. image:: ../_static/ide-vs-platformio-newproject-8.png
    :target: ../_static/ide-vs-platformio-newproject-8.png
