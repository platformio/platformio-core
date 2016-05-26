..  Copyright 2014-present Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _what_is_pio:

What is PlatformIO?
===================

.. contents::

Press about PlatformIO
----------------------

"Different microcontrollers normally have different developing tools .
For instance Arduino rely on Arduino IDE. Few more advanced users set up different
graphical interfaces like Eclipse for better project management. Sometimes
it may be hard to keep up with different microcontrollers and tools. You
probably thought that single unified development tool could be great. Well
this is what PlatformIO open source ecosystem is for.

This is cross platform code builder and library manager with platforms like
Arduino or MBED support. They took care of toolchains, debuggers, frameworks
that work on most popular platforms like Windows, Mac and Linux. It supports
more than 200 development boards along with more than 15 development platforms
and 10 frameworks. So most of popular boards are covered. They’ve done hard
work in organizing and managing hundreds of libraries that can be included
in to your project. Also lots of examples allow you to start developing
quickly. PlatformIO initially was developed with Command line philosophy.
It’s been successfully used with other IDE’s like Eclipse or Visual Studio.
Recently they’ve released a version with built in IDE based on Atom text editor", -
[Embedds]_.

Awards
------

PlatformIO was nominated for the year's `best Software and Tools in the 2015/16 IoT Awards <http://iotawards.postscapes.com/2015-16/best-iot-software-and-tools>`_.

Problematic
-----------

* The main problem which repulses people from embedded world is a complicated
  process to setup development software for a specific MCU/board: toolchains,
  proprietary vendor’s IDE (which sometimes isn’t free) and what is more,
  to get a computer with OS where that software is supported.
* Multiple hardware platforms (MCUs, boards) require different toolchains,
  IDEs, etc, and, respectively, spending time on learning new development environments.
* Finding proper libraries and code samples showing how to use popular
  sensors, actuators, etc.
* Sharing embedded projects between team members, regardless of operating
  system they prefer to work with.

Overview
--------

PlatformIO is independent from the platform, in which it is running. In fact,
the only requirement is Python, which exists pretty much everywhere. What this
means is that PlatformIO projects can be easily moved from one computer to
another, as well as that PlatformIO allows for the easy sharing of projects
between team members, regardless of operating system they prefer to work with.
Beyond that, PlatformIO can be run not only on commonly used desktops/laptops
but also on the servers without X Window System. While PlatformIO itself is a
console application, it can be used in combination with one's favorite
:ref:`ide` or text editor such as :ref:`ide_atom`, :ref:`ide_clion`,
:ref:`ide_eclipse`, :ref:`ide_emacs`, :ref:`ide_netbeans`, :ref:`ide_qtcreator`,
:ref:`ide_sublimetext`, :ref:`ide_vim`, :ref:`ide_visualstudio`, etc.

Alright, so PlatformIO can run on different operating systems. But more
importantly, from development perspective at least, is a list of supported
boards and MCUs. To keep things short: PlatformIO supports approximately 200
`Embedded Boards <http://platformio.org/boards>`_ and all major
:ref:`platforms`.

User SHOULD have a choice
-------------------------

* Decide which operation system they want to run development process on.
  You can even use one OS at home and another at work.
* Choose which editor to use for writing the code. It can be pretty simple
  editor or powerful favorite :ref:`ide`.
* Focus on the code development, significantly simplifying support for the
  :ref:`platforms` and MCUs.


How does it work?
-----------------

Without going too deep into PlatformIO implementation details, work cycle of
the project developed using PlatformIO is as follows:

* Users choose board(s) interested in :ref:`projectconf`
* Based on this list of boards, PlatformIO downloads required toolchains and
  installs them automatically.
* Users develop code and PlatformIO makes sure that it is compiled, prepared
  and uploaded to all the boards of interest.


.. [Embedds] Embedds.com: `Develop easier with PlatformIO ecosystem <http://www.embedds.com/develop-easier-with-platformio-ecosystem/>`_