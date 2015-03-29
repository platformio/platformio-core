.. _faq:

Frequently Asked Questions
==========================

.. contents::

General
-------

.. _faq_what_is_platformio:

What is PlatformIO?
~~~~~~~~~~~~~~~~~~~

`PlatformIO <http://platformio.org>`_ is a cross-platform code builder
and the missing library manager.

PlatformIO is independent from the platform, in which it is running. In fact,
the only requirement is Python, which exists pretty much everywhere. What this
means is that PlatformIO projects can be easily moved from one computer to
another, as well as that PlatformIO allows for the easy sharing of projects
between team members, regardless of operating system they prefer to work with.
Beyond that, PlatformIO can be run not only on commonly used desktops/laptops
but also on the servers without X Window System. While PlatformIO itself is a
console application, it can be used in combination with one's favorite
:ref:`ide` or text editor such as :ref:`ide_arduino`, :ref:`ide_eclipse`,
:ref:`ide_visualstudio`, :ref:`ide_vim`,  :ref:`ide_sublimetext`, etc.

Alright, so PlatformIO can run on different operating systems. But more
importantly, from development perspective at least, is a list of supported
boards and MCUs. To keep things short: PlatformIO supports over 100
:ref:`Embedded Boards <platforms>` and all major
:ref:`Development Platforms <platforms>`.

PlatformIO allows users to:

* Decide which operation system they want to run development process on.
  You can even use one OS at home and another at work.
* Choose which editor to use for writing the code. It can be pretty simple
  editor or powerful favorite :ref:`ide`.
* Focus on the code development, significantly simplifying support for the
  :ref:`platforms` and MCUs.


How does it work?
~~~~~~~~~~~~~~~~~

Without going too deep into PlatformIO implementation details, work cycle of
the project developed using PlatformIO is as follows:

* Users choose board(s) interested in :ref:`projectconf`
* Based on this list of boards, PlatformIO downloads required toolchains and
  installs them automatically.
* Users develop code and PlatformIO makes sure that it is compiled, prepared
  and uploaded to all the boards of interest.


Troubleshooting
---------------

Serial does not work with panStampAVR board
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Answered in an
`issue #144 <https://github.com/platformio/platformio/issues/144>`_.


