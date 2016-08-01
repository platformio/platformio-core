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

.. _cmd_platform_uninstall:

platformio platform uninstall
=============================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platform uninstall [PLATFORM...]

    # uninstall specific platform version using Semantic Versioning
    platformio platform uninstall PLATFORM@X.Y.Z


Description
-----------

Uninstall specified :ref:`platforms`


Examples
--------

.. code-block:: bash

    $ platformio platform uninstall atmelavr
    Uninstalling platform atmelavr @ 0.0.0:    [OK]
    Uninstalling package tool-scons @ 2.4.1:    [OK]
    Uninstalling package toolchain-atmelavr @ 1.40801.0:    [OK]
    The platform 'atmelavr' has been successfully uninstalled!
