..  Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _faq:

Frequently Asked Questions
==========================

.. contents::

General
-------

.. _faq_what_is_platformio:

What is PlatformIO?
~~~~~~~~~~~~~~~~~~~

`PlatformIO <http://platformio.org>`_ is an open source ecosystem for IoT
development.

PlatformIO is independent from the platform, in which it is running. In fact,
the only requirement is Python, which exists pretty much everywhere. What this
means is that PlatformIO projects can be easily moved from one computer to
another, as well as that PlatformIO allows for the easy sharing of projects
between team members, regardless of operating system they prefer to work with.
Beyond that, PlatformIO can be run not only on commonly used desktops/laptops
but also on the servers without X Window System. While PlatformIO itself is a
console application, it can be used in combination with one's favorite
:ref:`ide` or text editor such as :ref:`ide_arduino`, :ref:`ide_atom`,
:ref:`ide_clion`, :ref:`ide_eclipse`, :ref:`ide_qtcreator`,
:ref:`ide_sublimetext`, :ref:`ide_vim`, :ref:`ide_visualstudio`, etc.

Alright, so PlatformIO can run on different operating systems. But more
importantly, from development perspective at least, is a list of supported
boards and MCUs. To keep things short: PlatformIO supports approximately 200
`Embedded Boards <http://platformio.org/#!/boards>`_ and all major
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

Command completion in Terminal
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bash completion
'''''''''''''''

Bash completion support will complete subcommands and parameters. To enable
Bash completion for `platformio` subcommands you need to put into your `.bashrc`:

.. code-block:: bash

    eval "$(_PLATFORMIO_COMPLETE=source platformio)"

ZSH completion
''''''''''''''

To enable ``zsh`` completion please run these commands:

.. code-block:: bash

    autoload bashcompinit && bashcompinit
    eval "$(_PLATFORMIO_COMPLETE=source platformio)"

.. note::

    For permanent command completion you need to place commands above to
    ``~/.bashrc`` or ``~/.zshrc`` file.

.. _faq_troubleshooting:

Troubleshooting
---------------

Installation
~~~~~~~~~~~~

[Errno 1] Operation not permitted
'''''''''''''''''''''''''''''''''

Answered in `issue #295 <https://github.com/platformio/platformio/issues/295#issuecomment-143772005>`_.

Windows AttributeError: 'module' object has no attribute 'packages'
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Answered in `issue #252 <https://github.com/platformio/platformio/issues/252#issuecomment-127072039>`_.

.. _faq_troubleshooting_pionotfoundinpath:

Program "platformio" not found in PATH
''''''''''''''''''''''''''''''''''''''

Where is ``platformio`` binary installed? Run this command in Terminal

.. code-block:: bash

    # for Unix
    which platformio
    echo $PATH

    # for Windows OS
    where platformio
    echo %PATH%

For example, ``which platformio`` is equal to ``/usr/local/bin/platformio``,
then `PATH (wiki) <https://en.wikipedia.org/wiki/PATH_(variable)>`_
should contain ``/usr/local/bin`` directory.

**Unix Users**: You can make "symlinks" from ``platformio`` program to the
``bin`` directory which is included in ``$PATH``. For example,
see `issue #272 <https://github.com/platformio/platformio/issues/272#issuecomment-133626112>`_.

Windows UnicodeDecodeError: 'ascii' codec can't decode byte
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Answered in `issue #143 <https://github.com/platformio/platformio/issues/143#issuecomment-88060906>`_.

PlatformIO: command not found || An error "pkg_resources.DistributionNotFound"
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Please upgrade *SetupTools* package:

.. code-block:: bash

    [sudo] pip uninstall setuptools
    [sudo] pip install setuptools

    # Then re-install PlatformIO
    [sudo] pip uninstall platformio
    [sudo] pip install platformio

Miscellaneous
~~~~~~~~~~~~~

.. _faq_troubleshooting_pioblocksprompt:

PlatformIO blocks command execution using user prompt
'''''''''''''''''''''''''''''''''''''''''''''''''''''

If you are going to run *PlatformIO* from **subprocess**, you **MUST
DISABLE** all prompts. It will allow you to avoid blocking.
There are a few options:

- using :option:`platformio --force` option before each command
- using environment variable :envvar:`PLATFORMIO_SETTING_ENABLE_PROMPTS=No <PLATFORMIO_SETTING_ENABLE_PROMPTS>`
- disable global setting ``enable_prompts`` via :ref:`cmd_settings` command
- masking under Continuous Integration system via environment variable
  :envvar:`CI=true <CI>`.

Serial does not work with panStampAVR board
'''''''''''''''''''''''''''''''''''''''''''

Answered in `issue #144 <https://github.com/platformio/platformio/issues/144#issuecomment-87388038>`_.

Building
~~~~~~~~

Can not compile a library that compiles without issue with Arduino IDE
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

* `#298: Unable to use Souliss library <https://github.com/platformio/platformio/issues/298>`_
* `#331: Unable to use MySensors library <https://github.com/platformio/platformio/issues/331>`_

ARM toolchain: cc1plus: error while loading shared libraries
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

See related answers for
`error while loading shared libraries <https://github.com/platformio/platformio/issues?utf8=✓&q=error+while+loading+shared+libraries>`_.

Archlinux: libncurses.so.5: cannot open shared object file
''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Answered in `issue #291 <https://github.com/platformio/platformio/issues/291>`_.

Monitoring a serial port breaks upload
''''''''''''''''''''''''''''''''''''''

Answered in `issue #384 <https://github.com/platformio/platformio/issues/384>`_.
