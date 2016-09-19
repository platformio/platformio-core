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

.. _cmd_lib_show:

platformio lib show
===================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib [STORAGE_OPTIONS] show [LIBRARY]

    # show info about project dependent library
    # (run it from a project root where is located "platformio.ini")
    platformio lib show [LIBRARY]

    # show info about library from global storage
    platformio lib --global show [LIBRARY]
    platformio lib -g show [LIBRARY]

    # show info about library from custom storage
    platformio lib --storage-dir /path/to/dir show [LIBRARY]
    platformio lib -d /path/to/dir show [LIBRARY]

    # [LIBRARY] forms
    platformio lib [STORAGE_OPTIONS] show <id>
    platformio lib [STORAGE_OPTIONS] show <id>
    platformio lib [STORAGE_OPTIONS] show <id>@<version>
    platformio lib [STORAGE_OPTIONS] show <id>@<version range>
    platformio lib [STORAGE_OPTIONS] show <name>
    platformio lib [STORAGE_OPTIONS] show <name>@<version>
    platformio lib [STORAGE_OPTIONS] show <name>@<version range>

Description
-----------

Show details about the installed library.

The ``version`` supports `Semantic Versioning <http://semver.org>`_ (
``<major>.<minor>.<patch>``) and can take any of the following forms:

* ``0.1.2`` - an exact version number. Use only this exact version
* ``^0.1.2`` - any compatible version (exact version for ``0.x.x`` versions
* ``~0.1.2`` - any version with the same major and minor versions, and an
  equal or greater patch version
* ``>0.1.2`` - any version greater than ``0.1.2``. ``>=``, ``<``, and ``<=``
  are also possible
* ``>0.1.0,!=0.2.0,<0.3.0`` - any version greater than ``0.1.0``, not equal to
  ``0.2.0`` and less than ``0.3.0``

Storage Options
---------------

See base options for :ref:`cmd_lib`.

Examples
--------

.. code::

    platformio lib -g show Json

    Library Storage: /storage/dir/...
    Json
    ====
    An elegant and efficient JSON library for embedded systems

    Authors: Benoit Blanchon http://blog.benoitblanchon.fr
    Keywords: json, rest, http, web
    Frameworks: arduino
    Platforms: atmelavr, atmelsam, timsp430, titiva, teensy, freescalekinetis, ststm32, nordicnrf51, nxplpc, espressif8266, siliconlabsefm32, linux_arm, native, intel_arc32
    Version: 5.4.0
