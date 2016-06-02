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

.. _cmd_platforms_update:

platformio platforms update
===========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platforms update


Description
-----------

Check or update installed :ref:`platforms`


Examples
--------

.. code-block:: bash

    $ platformio platforms update

    Platform atmelavr
    --------
    Updating toolchain-atmelavr package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-avrdude package:
    Versions: Current=2, Latest=2 	 [Up-to-date]
    Updating framework-arduinoavr package:
    Versions: Current=12, Latest=12 	 [Up-to-date]
    Updating tool-micronucleus package:
    Versions: Current=1, Latest=1 	 [Up-to-date]

    Platform atmelsam
    --------
    Updating framework-arduinosam package:
    Versions: Current=3, Latest=3 	 [Up-to-date]
    Updating ldscripts package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating toolchain-gccarmnoneeabi package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-bossac package:
    Versions: Current=1, Latest=1 	 [Up-to-date]

    Platform stm32
    --------
    Updating toolchain-gccarmnoneeabi package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-stlink package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-spl package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-cmsis package:
    Versions: Current=2, Latest=2 	 [Up-to-date]
    Updating framework-opencm3 package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating ldscripts package:
    Versions: Current=1, Latest=1 	 [Up-to-date]

    Platform teensy
    --------
    Updating toolchain-atmelavr package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating ldscripts package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-arduinoteensy package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating toolchain-gccarmnoneeabi package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-teensy package:
    Versions: Current=1, Latest=1 	 [Up-to-date]

    Platform timsp430
    --------
    Updating toolchain-timsp430 package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-mspdebug package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-energiamsp430 package:
    Versions: Current=2, Latest=2 	 [Up-to-date]

    Platform titiva
    --------
    Updating ldscripts package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating toolchain-gccarmnoneeabi package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating tool-lm4flash package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-opencm3 package:
    Versions: Current=1, Latest=1 	 [Up-to-date]
    Updating framework-energiativa package:
    Versions: Current=4, Latest=4 	 [Up-to-date]
