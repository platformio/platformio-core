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

.. _migration:

Migrating from 2.x to 3.0
=========================

Guidance on how to upgrade from PlatformIO v2.x to v3.x with emphasis on major
changes, what is new, and what is been removed.

PlatformIO 3 is not backwards compatible with v2.x. Use this section as a
general guide to upgrading from v2.x to v3.0. For a broader overview, see
`what is new <https://community.platformio.org/c/announcements>`_ in the v3.0
release announcement.

.. contents::

Major PlatformIO CLI changes
----------------------------

.. note::
	PlatformIO 3.x is 100% non-blocking! You do not need to use ``--force``
	option or setup special ``PLATOFMRIO_SETTING_ENABLE_PROMPTS`` environment.
	Use PlatformIO 3.0 with sub-processing without any risk!

This table shows the CLI changes between v2.x and v3.0.

.. list-table::
    :header-rows:  1

    * - PlatformIO 2.x
      - PlatformIO 3.x
    * - platformio platforms
      - :ref:`platformio platform <userguide_platform>`
    * - platformio serialports
      - :ref:`cmd_device`
    * - platformio settings set enable_prompts false
      - Removed! Now, all PlatformIO 3.0 CLI is 100% non-blocking!


PlatformIO 2.x commands will be converted to PlatformIO 3.x automatically.
Nevertheless, we recommend to use PlatformIO 3.x commands for the new projects.

What is new
-----------

Development Platforms
~~~~~~~~~~~~~~~~~~~~~

We have introduced :ref:`platform_creating_manifest_file` and ported
PlatformIO 2.x development platforms according PlatformIO 3.0 decentralized
architecture. Now, platform related things (build scrips, LD scripts, board
configs, package requirements) are located in own repository. Here is the full
list with `PlatformIO 3.0 open source development platforms <https://github.com/platformio?utf8=✓&query=platform->`__. You can fork it, modify or create custom.
See :ref:`platform_creating` guide for details.

* :ref:`platform_creating_manifest_file`
* ``espressif`` development platform has been renamed to :ref:`platform_espressif8266`
* PlatformIO 3.0 :ref:`userguide_platform`
* Custom package repositories
* External embedded board configuration files, isolated build scripts
* Embedded Board compatibility with more than one development platform

Library Manager and Intelligent Build System
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Powerful and super-fast :ref:`ldf` that interprets C/C++ Preprocessor
  conditional macros with deep search behavior
* Project dependencies per build environment using `projectconf_lib_deps` option
* Depend on a library using VCS URL (GitHub, Git, ARM mbed code registry, Hg, SVN)
* Install library by name
* Strict search for library dependencies
* Multiple library storages: Project's Local, PlatformIO's Global or Custom
* Allowed :ref:`library_config` to specify sources other than PlatformIO's Repository
* Check library compatibility with project environment before building
* Control Library Dependency Finder for compatibility using :ref:`projectconf_lib_compat_mode` option
* Custom library storages/directories with :ref:`projectconf_lib_extra_dirs` option
* Handle extra build flags, source filters and build script from :ref:`library_config`
* Allowed to disable library archiving (``*.ar``)
* Show detailed build information about dependent libraries (Library Dependency Graph)
* Support for the 3rd party manifests (Arduino IDE "library.properties" and
  ARM mbed "module.json")
* Build System: Attach custom Before/Pre and After/Post actions for targets using :ref:`projectconf_extra_script`

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

We have added new commands and changed some existing ones. Here are the new or
updated commands and options.

.. list-table::
    :header-rows:  1

    * - Command
      - Description
    * - :ref:`cmd_boards`
      - Returns all supported boards by PlatformIO
    * - :option:`platformio boards --installed`
      - Returns currently installed boards
    * - :option:`platformio ci --project-option`
      - Pass custom option from :ref:`projectconf`
    * - :option:`platformio ci --verbose`
      - Print detailed information about build process
    * - :option:`platformio init --project-option`
      - Pass custom option from :ref:`projectconf`
    * - :option:`platformio lib --global`
      - Manage PlatformIO :ref:`Global Library Storage <ldf_storage>`
    * - :option:`platformio lib --storage-dir`
      - Manage :ref:`Custom Library Storage <ldf_storage>`
    * - :ref:`cmd_lib_install`
      - New PlatformIO 3.0 Library Manager! Semantic Versioning, VCS support and external URL support
    * - :option:`platformio lib install --silent`
      - Suppress progress reporting when install library
    * - :option:`platformio lib install --interactive`
      - Allow to make a choice for all prompts when install library
    * - :option:`platformio lib search --header`
      - Search library by specific header file name (include)
    * - :option:`platformio lib update --only-check`
      - Do not update, only check for new version
    * - :ref:`platformio platform <userguide_platform>`
      - New PlatformIO 3.0 Platform Manager! Semantic Versioning, VCS support and external URL support.
    * - :option:`platformio platform update --only-packages`
      - Update only platform packages
    * - :option:`platformio platform update --only-check`
      - Do not update, only check for new version
    * - :ref:`cmd_run`
      - By default, prints only human-readable information when processing environments
    * - :option:`platformio run --verbose`
      - Print detailed processing information
    * - :ref:`platformio settings set force_verbose true <setting_force_verbose>`
      - Force verbose output when processing environments (globally)
    * - :ref:`cmd_test`
      - PlatformIO Plus Unit Testing
    * - :option:`platformio update --only-check`
      - Do not update, only check for new version

:ref:`projectconf`
~~~~~~~~~~~~~~~~~~

We have added new options and changed some existing ones. Here are the new or
updated options.

.. list-table::
    :header-rows:  1

    * - Section
      - Option
      - Description
    * - platformio
      - :ref:`projectconf_pio_libdeps_dir`
      - Internal storage where :ref:`librarymanager` will install project dependencies
    * - platformio
      - :ref:`projectconf_pio_test_dir`
      - Directory where :ref:`unit_testing` engine will look for the tests
    * - env
      - :ref:`projectconf_lib_deps`
      - Specify project dependencies that should be installed automatically to :ref:`projectconf_pio_libdeps_dir` before environment processing.
    * - env
      - :ref:`projectconf_env_platform`
      - PlatformIO 3.0 allows to use specific version of platform using `Semantic Versioning <http://semver.org>`_ (X.Y.Z=MAJOR.MINOR.PATCH).
    * - env
      - :ref:`projectconf_lib_extra_dirs`
      - A list with extra directories/storages where :ref:`ldf` will look for dependencies
    * - env
      - :ref:`projectconf_lib_ldf_mode`
      - This option specifies how does :ref:`ldf` should analyze dependencies (``#include`` directives)
    * - env
      - :ref:`projectconf_lib_compat_mode`
      - Library compatibility mode allows to control strictness of :ref:`ldf`
    * - env
      - :ref:`projectconf_test_ignore`
      - Ignore tests where the name matches specified patterns

What is removed
---------------

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~~

The following commands have been dropped or changed in v3.0.

.. list-table::
    :header-rows:  1

    * - Command
      - Description
    * - platformio init --enable-auto-uploading
      - Use :option:`platformio init --project-option` instead of it with ``targets = upload`` value

:ref:`projectconf`
~~~~~~~~~~~~~~~~~~

The following options have been dropped or changed in v3.0.

.. list-table::
    :header-rows:  1

    * - Section
      - Option
      - Description
    * - platformio
      - :ref:`projectconf_pio_lib_dir`
      - Changed: Project's own/private libraries, where in PlatformIO 2.x it was global library storage

