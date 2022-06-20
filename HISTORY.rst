Release Notes
=============

.. |PIOCONF| replace:: `"platformio.ini" <https://docs.platformio.org/en/latest/projectconf.html>`__ configuration file
.. |LDF| replace:: `LDF <https://docs.platformio.org/en/latest/librarymanager/ldf.html>`__
.. |INTERPOLATION| replace:: `Interpolation of Values <https://docs.platformio.org/en/latest/projectconf/interpolation.html>`__
.. |UNITTESTING| replace:: `Unit Testing <https://docs.platformio.org/en/latest/advanced/unit-testing/index.html>`__

.. _release_notes_6:

PlatformIO Core 6
-----------------

**A professional collaborative platform for declarative, safety-critical, and test-driven embedded development.**

6.0.3 (2022-??-??)
~~~~~~~~~~~~~~~~~~

* **Device Monitor**

  - Automatically reconnect if a connection fails
  - Added new `pio device monitor --no-reconnect <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html#cmdoption-pio-device-monitor-no-reconnect>`__ option to disable automatic reconnection
  - Handle disconnects more gracefully (`issue #3939 <https://github.com/platformio/platformio-core/issues/3939>`_)
  - Replaced ``monitor_flags`` with independent project configuration options: `monitor_parity <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-parity>`__, `monitor_eol <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-eol>`__, `monitor_raw <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-raw>`__, `monitor_echo <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-echo>`__
  - Fixed an issue when the monitor filters were not applied in their order (`issue #4320 <https://github.com/platformio/platformio-core/issues/4320>`_)

* **Unit Testing**

  - Merged the |UNITTESTING| "building" stage with "uploading" for the embedded target (`issue #4307 <https://github.com/platformio/platformio-core/issues/4307>`_)
  - Do not resolve dependencies from the project "src" folder when the `test_build_src <https://docs.platformio.org/en/latest//projectconf/section_env_test.html#test-build-src>`__ option is not enabled
  - Fixed an issue when a custom `pio test --project-config <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html#cmdoption-pio-test-c>`__ was not handled properly (`issue #4299 <https://github.com/platformio/platformio-core/issues/4299>`_)

* Documented `Stringification <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#stringification>`__  – converting a macro argument into a string constant (`issue #4310 <https://github.com/platformio/platformio-core/issues/4310>`_)
* Added ``env.StringifyMacro(value)`` helper function for the `Advanced Scripting <https://docs.platformio.org/en/latest/scripting/index.html>`__
* Allowed to ``Import("projenv")`` in a library extra script (`issue #4305 <https://github.com/platformio/platformio-core/issues/4305>`_)
* Improved a serial port finder for `Black Magic Probe <https://docs.platformio.org/en/latest/plus/debug-tools/blackmagic.html>`__ (`issue #4023 <https://github.com/platformio/platformio-core/issues/4023>`_)
* Improved a serial port finder for a board with predefined HWIDs
* Warn about incompatible Bash version for the `Shell Completion <https://docs.platformio.org/en/latest/core/userguide/system/completion/index.html>`__ (`issue #4326 <https://github.com/platformio/platformio-core/issues/4326>`_)
* Fixed an issue when the `build_unflags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-unflags>`__ operation ignores a flag value (`issue #4309 <https://github.com/platformio/platformio-core/issues/4309>`_)
* Fixed an issue when the `build_unflags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-unflags>`__ option was not applied to the ``ASPPFLAGS`` scope
* Fixed an issue on Windows OS when flags were wrapped to the temporary file while generating the `Compilation database "compile_commands.json" <https://docs.platformio.org/en/latest/integration/compile_commands.html>`__

6.0.2 (2022-06-01)
~~~~~~~~~~~~~~~~~~

* Control |UNITTESTING| verbosity with a new multilevel `pio test -v <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html#cmdoption-pio-test-v>`__ command option (`issue #4276 <https://github.com/platformio/platformio-core/issues/4276>`_)
* Follow symbolic links during searching for the unit test suites (`issue #4288 <https://github.com/platformio/platformio-core/issues/4288>`_)
* Show a warning when testing an empty project without a test suite (`issue #4278 <https://github.com/platformio/platformio-core/issues/4278>`_)
* Improved support for `Asking for input (prompts) <https://docs.platformio.org/en/latest/scripting/examples/asking_for_input.html>`_
* Fixed an issue when the `build_src_flags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-src-flags>`__ option was applied outside the project scope (`issue #4277 <https://github.com/platformio/platformio-core/issues/4277>`_)
* Fixed an issue with debugging assembly files without preprocessor (".s")

6.0.1 (2022-05-17)
~~~~~~~~~~~~~~~~~~

* Improved support for the renamed configuration options (`issue #4270 <https://github.com/platformio/platformio-core/issues/4270>`_)
* Fixed an issue when calling the built-in `pio device monitor <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html#filters>`__ filters
* Fixed an issue when using |INTERPOLATION| and merging str+int options (`issue #4271 <https://github.com/platformio/platformio-core/issues/4271>`_)

6.0.0 (2022-05-16)
~~~~~~~~~~~~~~~~~~

Please check the `Migration guide from 5.x to 6.0 <https://docs.platformio.org/en/latest/core/migration.html>`__.

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

  - Refactored from scratch |UNITTESTING| solution and its documentation
  - New: `Test Hierarchy <https://docs.platformio.org/en/latest/advanced/unit-testing/structure.html>`_ (`issue #4135 <https://github.com/platformio/platformio-core/issues/4135>`_)
  - New: `Doctest <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/doctest.html>`__ testing framework (`issue #4240 <https://github.com/platformio/platformio-core/issues/4240>`_)
  - New: `GoogleTest <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/googletest.html>`__ testing and mocking framework (`issue #3572 <https://github.com/platformio/platformio-core/issues/3572>`_)
  - New: `Semihosting <https://docs.platformio.org/en/latest/advanced/unit-testing/semihosting.html>`__ (`issue #3516 <https://github.com/platformio/platformio-core/issues/3516>`_)
  - New: Hardware `Simulators <https://docs.platformio.org/en/latest/advanced/unit-testing/simulators/index.html>`__ for Unit Testing (QEMU, Renode, SimAVR, and custom solutions)
  - New: ``test`` `build configuration <https://docs.platformio.org/en/latest/projectconf/build_configurations.html>`__
  - Added support for a `custom testing framework <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/custom/index.html>`_
  - Added support for a custom `testing command <https://docs.platformio.org/en/latest/projectconf/section_env_test.html#test-testing-command>`__
  - Added support for a `custom Unity library <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/custom/examples/custom_unity_library.html>`__ (`issue #3980 <https://github.com/platformio/platformio-core/issues/3980>`_)
  - Added support for the ``socket://`` and ``rfc2217://`` protocols using `test_port <https://docs.platformio.org/en/latest/projectconf/section_env_test.html#test-port>`__ option (`issue #4229 <https://github.com/platformio/platformio-core/issues/4229>`_)
  - List available project tests with a new `pio test --list-tests <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html#cmdoption-pio-test-list-tests>`__ option
  - Pass extra arguments to the testing program with a new `pio test --program-arg <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html#cmdoption-pio-test-a>`__ option (`issue #3132 <https://github.com/platformio/platformio-core/issues/3132>`_)
  - Generate reports in JUnit and JSON formats using the `pio test <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html>`__ command (`issue #2891 <https://github.com/platformio/platformio-core/issues/2891>`_)
  - Provide more information when the native program crashed on a host (errored with a non-zero return code) (`issue #3429 <https://github.com/platformio/platformio-core/issues/3429>`_)
  - Improved automatic detection of a testing serial port (`issue #4076 <https://github.com/platformio/platformio-core/issues/4076>`_)
  - Fixed an issue when command line parameters (``--ignore``, ``--filter``) do not override values defined in the |PIOCONF| (`issue #3845 <https://github.com/platformio/platformio-core/issues/3845>`_)
  - Renamed the "test_build_project_src" project configuration option to the `test_build_src <https://docs.platformio.org/en/latest//projectconf/section_env_test.html#test-build-src>`__
  - Removed the "test_transport" option in favor of the `Custom "unity_config.h" <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/unity.html>`_

* **Static Code Analysis**

  - Updated analysis tools:

    * `Cppcheck <https://docs.platformio.org/en/latest/plus/check-tools/cppcheck.html>`__ v2.7 with various checker improvements and fixed false positives
    * `PVS-Studio <https://docs.platformio.org/en/latest/plus/check-tools/pvs-studio.html>`__ v7.18 with improved and updated semantic analysis system

  - Added support for the custom `Clang-Tidy <https://docs.platformio.org/en/latest/plus/check-tools/clang-tidy.html>`__ configuration file (`issue #4186 <https://github.com/platformio/platformio-core/issues/4186>`_)
  - Added ability to override a tool version using the `platform_packages <https://docs.platformio.org/en/latest/projectconf/section_env_platform.html#platform-packages>`__ option (`issue #3798 <https://github.com/platformio/platformio-core/issues/3798>`_)
  - Fixed an issue with improper handling of defects that don't specify a source file (`issue #4237 <https://github.com/platformio/platformio-core/issues/4237>`_)

* **Build System**

  - Show project dependency licenses when building in the verbose mode
  - Fixed an issue when |LDF| ignores the project `lib_deps <https://docs.platformio.org/en/latest/projectconf/section_env_library.html#lib-deps>`__ while resolving library dependencies (`issue #3598 <https://github.com/platformio/platformio-core/issues/3598>`_)
  - Fixed an issue with calling an extra script located outside a project (`issue #4220 <https://github.com/platformio/platformio-core/issues/4220>`_)
  - Fixed an issue when GCC preprocessor was applied to the ".s" assembly files on case-sensitive OS such as Window OS (`issue #3917 <https://github.com/platformio/platformio-core/issues/3917>`_)
  - Fixed an issue when |LDF| ignores `build_src_flags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-src-flags>`__ in the "deep+" mode (`issue #4253 <https://github.com/platformio/platformio-core/issues/4253>`_)

* **Integration**

  - Added a new build variable (``COMPILATIONDB_INCLUDE_TOOLCHAIN``) to include toolchain paths in the compilation database (`issue #3735 <https://github.com/platformio/platformio-core/issues/3735>`_)
  - Changed a default path for compilation database `compile_commands.json <https://docs.platformio.org/en/latest/integration/compile_commands.html>`__ to the project root
  - Enhanced integration for Qt Creator (`issue #3046 <https://github.com/platformio/platformio-core/issues/3046>`_)

* **Project Configuration**

  - Extended |INTERPOLATION| with ``${this}`` pattern (`issue #3953 <https://github.com/platformio/platformio-core/issues/3953>`_)
  - Embed environment name of the current section in the |PIOCONF| using ``${this.__env__}`` pattern
  - Renamed the "src_build_flags" project configuration option to the `build_src_flags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-src-flags>`__
  - Renamed the "src_filter" project configuration option to the `build_src_filter <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-src-filter>`__

* **Miscellaneous**

  - Pass extra arguments to the `native <https://docs.platformio.org/en/latest/platforms/native.html>`__ program with a new `pio run --program-arg <https://docs.platformio.org/en/latest/core/userguide/cmd_run.html#cmdoption-pio-run-a>`__ option (`issue #4246 <https://github.com/platformio/platformio-core/issues/4246>`_)
  - Improved PIO Remote setup on credit-card sized computers (Raspberry Pi, BeagleBon, etc) (`issue #3865 <https://github.com/platformio/platformio-core/issues/3865>`_)
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
