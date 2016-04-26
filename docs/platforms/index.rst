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

.. _platforms:

Platforms & Embedded Boards
===========================

*PlatformIO* has pre-built different development platforms for popular OS
(*Mac OS X, Linux (+ARM) and Windows*). Each of them include compiler,
debugger, uploader (for embedded) and many other useful tools.

Also it has pre-configured settings for most popular **Embedded Platform
Boards**. You have no need to specify in :ref:`projectconf` type or frequency of
MCU, upload protocol or etc. Please use ``board`` option.

Embedded
--------

.. toctree::
    :maxdepth: 2

    atmelavr
    atmelsam
    espressif
    freescalekinetis
    lattice_ice40
    nordicnrf51
    nxplpc
    siliconlabsefm32
    ststm32
    teensy
    timsp430
    titiva

Desktop
-------

.. toctree::
    :maxdepth: 2

    native
    linux_arm
    linux_i686
    linux_x86_64
    windows_x86

Custom Platform & Board
-----------------------

.. toctree::
    :maxdepth: 2

    creating_platform
    creating_board
