Release Notes
=============

.. |PIOCONF| replace:: `"platformio.ini" <https://docs.platformio.org/en/latest/projectconf.html>`__ configuration file

.. _release_notes_6:

PlatformIO Core 6
-----------------

**A professional collaborative platform for embedded development**

6.0.0 (2022-??-??)
~~~~~~~~~~~~~~~~~~

Please check `Migration guide from 5.x to 6.0 <https://docs.platformio.org/en/latest/core/migration.html>`__.

* **Package Management**

  - New unified Package Management CLI (``pio pkg``):

    * `pio pkg exec <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_exec.html>`_ - run command from package tool (`issue #4163 <https://github.com/platformio/platformio-core/issues/4163>`_)
    * `pio pkg install <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_install.html>`_ - install the project dependencies or custom packages
    * `pio pkg list <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_list.html>`__ - list installed packages
    * `pio pkg outdated <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_outdated.html>`__ - check for project outdated packages
    * `pio pkg search <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_search.html>`__ - search for packages
    * `pio pkg show <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_show.html>`__ - show package information
    * `pio pkg uninstall <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_uninstall.html>`_ - uninstall the project dependencies or custom packages
    * `pio pkg update <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_update.html>`__ - update the project dependencies or custom packages

  - Package Manifest

    * Added support for `"scripts" <https://docs.platformio.org/en/latest/librarymanager/config.html#scripts>`__ (`issue #485 <https://github.com/platformio/platformio-core/issues/485>`_)
    * Added support for `multi-licensed <https://docs.platformio.org/en/latest/librarymanager/config.html#license>`__ packages using SPDX Expressions (`issue #4037 <https://github.com/platformio/platformio-core/issues/4037>`_)
    * Added support for `"dependencies" <https://docs.platformio.org/en/latest/librarymanager/config.html#dependencies>`__ declared in a "tool" package manifest

  - Added support for `symbolic links <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_install.html#local-folder>`__ allowing pointing the local source folder to the Package Manager (`issue #3348 <https://github.com/platformio/platformio-core/issues/3348>`_)
  - Automatically install dependencies of the local (private) project libraries (`issue #2910 <https://github.com/platformio/platformio-core/issues/2910>`_)
  - Improved detection of a package type from the tarball archive (`issue #3828 <https://github.com/platformio/platformio-core/issues/3828>`_)
  - Ignore files according to the patterns declared in ".gitignore" when using the `pio package pack <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_pack.html>`__ command (`issue #4188 <https://github.com/platformio/platformio-core/issues/4188>`_)
  - Dropped automatic updates of global libraries and development platforms (`issue #4179 <https://github.com/platformio/platformio-core/issues/4179>`_)
  - Dropped support for the "pythonPackages" field in "platform.json" manifest in favor of `Extra Python Dependencies <https://docs.platformio.org/en/latest/scripting/examples/extra_python_packages.html>`__
  - Fixed an issue when manually removed dependencies from the |PIOCONF| were not uninstalled from the storage (`issue #3076 <https://github.com/platformio/platformio-core/issues/3076>`_)

* **Unit Testing**

  - Generate reports in JUnit and JSON formats using the `pio test --output-format <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html#cmdoption-pio-test-output-format>`__ option  (`issue #2891 <https://github.com/platformio/platformio-core/issues/2891>`_)
  - Added support for test hierarchies (nested test suites) (`issue #4135 <https://github.com/platformio/platformio-core/issues/4135>`_)
  - Provide more information when the native program crashed on a host (errored with a negative return code) (`issue #3429 <https://github.com/platformio/platformio-core/issues/3429>`_)
  - Fixed an issue when command line parameters ("--ignore", "--filter") do not override values defined in the |PIOCONF| (`issue #3845 <https://github.com/platformio/platformio-core/issues/3845>`_)

* **Static Code Analysis**

  - Added support for the custom `Clang-Tidy <https://docs.platformio.org/en/latest/plus/check-tools/clang-tidy.html>`__ configuration file (`issue #4186 <https://github.com/platformio/platformio-core/issues/4186>`_)
  - Added ability to override a tool version using the `platform_packages <https://docs.platformio.org/en/latest/projectconf/section_env_platform.html#platform-packages>`__ option (`issue #3798 <https://github.com/platformio/platformio-core/issues/3798>`_)

* **Build System**

  - Show project dependency licenses when building in the verbose mode
  - Fixed an issue when `LDF <https://docs.platformio.org/en/latest/librarymanager/ldf.html>`__ ignores the project `lib_deps <https://docs.platformio.org/en/latest/projectconf/section_env_library.html#lib-deps>`__ while resolving library dependencies (`issue #3598 <https://github.com/platformio/platformio-core/issues/3598>`_)
  - Fixed an issue with calling an extra script located outside a project (`issue #4220 <https://github.com/platformio/platformio-core/issues/4220>`_)
  - Fixed an issue when GCC preprocessor was applied to the ".s" assembly files on case-sensitive OS such as Window OS (`issue #3917 <https://github.com/platformio/platformio-core/issues/3917>`_)

* **Integration**

  - Added a new build variable (``COMPILATIONDB_INCLUDE_TOOLCHAIN``) to include toolchain paths in the compilation database (`issue #3735 <https://github.com/platformio/platformio-core/issues/3735>`_)
  - Changed default path for compilation database `compile_commands.json <https://docs.platformio.org/en/latest/integration/compile_commands.html>`__ to the project root

* **Project Configuration**

  - Extended `Interpolation of Values <https://docs.platformio.org/en/latest/projectconf/interpolation.html>`__  with ``${this}`` pattern (`issue #3953 <https://github.com/platformio/platformio-core/issues/3953>`_)
  - Embed environment name of the current section in the |PIOCONF| using ``${this.__env__}`` pattern

* **Miscellaneous**

  - Improved PIO Remote setup on credit-card sized computers (Raspberry Pi, BeagleBon, etc) (`issue #3865 <https://github.com/platformio/platformio-core/issues/3865>`_)
  - Better handling of the failed tests using the `Unit Testing <https://docs.platformio.org/en/latest/plus/unit-testing.html>`__ solution
  - Finally removed all tracks to the Python 2.7, the Python 3.6 is the minimum supported version.

.. _release_notes_5:

PlatformIO Core 5
-----------------

See `PlatformIO Core 5.0 history <https://github.com/platformio/platformio-core/blob/v5.2.5/HISTORY.rst>`__.

.. _release_notes_4:

PlatformIO Core 4
-----------------

See `PlatformIO Core 4.0 history <https://github.com/platformio/platformio-core/blob/v4.3.4/HISTORY.rst>`__.

PlatformIO Core 3
-----------------

See `PlatformIO Core 3.0 history <https://github.com/platformio/platformio-core/blob/v3.6.7/HISTORY.rst>`__.

PlatformIO Core 2
-----------------

See `PlatformIO Core 2.0 history <https://github.com/platformio/platformio-core/blob/v2.11.2/HISTORY.rst>`__.

PlatformIO Core 1
-----------------

See `PlatformIO Core 1.0 history <https://github.com/platformio/platformio-core/blob/v1.5.0/HISTORY.rst>`__.

PlatformIO Core Preview
-----------------------

See `PlatformIO Core Preview history <https://github.com/platformio/platformio-core/blob/v0.10.2/HISTORY.rst>`__.
