.. _ide_clion:

CLion
=====

The `CLion <https://www.jetbrains.com/clion/>`_ is a cross-platform C/C++ IDE
for Linux, OS X, and Windows integrated with the CMake build system. The
initial version will support the GCC and Clang compilers and GDB debugger.
Clion includes such features as a smart editor, code quality assurance,
automated refactorings, project manager, integrated version control systems.

This software can be used with:

* all available :ref:`platforms`
* all available :ref:`frameworks`

Refer to the `CDT Documentation <https://www.jetbrains.com/clion/documentation/>`_
page for more detailed information.

.. contents::

Integration
-----------

.. note::
    Please verify that folder where is located ``platformio`` program is added
    to `PATH (wiki) <https://en.wikipedia.org/wiki/PATH_(variable)>`_ environment
    variable. See FAQ: :ref:`faq_troubleshooting_pionotfoundinpath`.

Project Generator
^^^^^^^^^^^^^^^^^

Since PlatformIO 2.0 you can generate CLion compatible project using
:option:`platformio init --ide` command. Please choose board type using
:ref:`cmd_boards` command and run:

.. code-block:: shell

    platformio init --ide clion --board %TYPE%

Then import this project from start menu or via ``File > Import Project>`` and
specify root directory where is located :ref:`projectconf`.

.. warning::
    CLion is still in the development stage, so some of the features (like,
    auto-complete) probably will not work with PlatformIO. See
    `CLion issue #CPP-3977 <https://youtrack.jetbrains.com/issue/CPP-3977>`_.

    Active discussion located in
    `PlatformIO issue #132 <https://github.com/platformio/platformio/issues/132>`_.

Screenshot
----------

.. image:: ../_static/ide-platformio-clion.png
    :target: http://docs.platformio.org/en/latest/_static/ide-platformio-clion.png
