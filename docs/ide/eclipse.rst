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

This software can be used with:

* all available :ref:`platforms`
* all available :ref:`frameworks`

Refer to the `CDT Documentation <https://eclipse.org/cdt/documentation.php>`_
page for more detailed information.

.. contents::

Integration
-----------

Project Generator
^^^^^^^^^^^^^^^^^

Since PlatformIO 2.0 you can generate Eclipse compatible project using
:option:`platformio init --ide` command:

.. code-block:: shell

    platformio init --ide eclipse

Then import this project via ``File > Import... > General > Existing Projects
into Workspace > Next`` and specify root directory where is located
:ref:`projectconf`.

Manual Integration
^^^^^^^^^^^^^^^^^^

More detailed information is located in PlatformIO blog: `Building and debugging Atmel AVR (Arduino-based) project using Eclipse IDE+PlatformIO <http://www.ikravets.com/computer-life/programming/2014/06/20/building-and-debugging-atmel-avr-arduino-based-project-using-eclipse-ideplatformio>`_.

`More examples (TI MSP430, TI TIVA, etc.) <https://github.com/platformio/platformio/tree/develop/examples/ide-eclipse>`_

Screenshot
----------

.. image:: ../_static/ide-platformio-eclipse.png
	:target: http://www.ikravets.com/computer-life/programming/2014/06/20/building-and-debugging-atmel-avr-arduino-based-project-using-    eclipse-ideplatformio
