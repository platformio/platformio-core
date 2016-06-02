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

.. _cmd_platforms_install:

platformio platforms install
============================

.. contents::

Usage
-----

.. code-block:: bash

    platformio platforms install [OPTIONS] [PLATFORMS]


Description
-----------

Install pre-built development :ref:`platforms` with related packages.

There are several predefined aliases for packages, such as:

* ``toolchain``
* ``uploader``

Options
-------

.. program:: platformio platforms install

.. option::
    --with-package

Install specified package (or alias)


.. option::
    --without-package

Do not install specified package (or alias)

.. option::
    --skip-default

Skip default packages

Examples
--------

1. Install :ref:`platform_timsp430` with default packages

.. code-block:: bash

    $ platformio platforms install timsp430
    Installing toolchain-timsp430 package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing tool-mspdebug package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing framework-energiamsp430 package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The platform 'timsp430' has been successfully installed!


2. Install :ref:`platform_timsp430` with ``uploader`` utility only and skip
   default packages

.. code-block:: bash

    $ platformio platforms install timsp430 --skip-default-package --with-package=uploader
    Installing tool-mspdebug package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The platform 'timsp430' has been successfully installed!
