Release Notes
=============

.. _release_notes_5:

PlatformIO Core 5
-----------------

**A professional collaborative platform for embedded development**

5.2.0 (2021-??-??)
~~~~~~~~~~~~~~~~~~

* **PlatformIO Debugging**

  - Boosted `PlatformIO Debugging <https://docs.platformio.org/page/plus/debugging.html>`__  performance thanks to migrating the codebase to the pure Python 3 Asynchronous I/O stack
  - `Debug unit tests <https://docs.platformio.org/page/plus/debugging.html#debug-unit-tests>`__ created with `PlatformIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__ solution  (`issue #948 <https://github.com/platformio/platformio-core/issues/948>`_)
  - Debug native (desktop) applications on a host machine (`issue #980 <https://github.com/platformio/platformio-core/issues/980>`_)
  - Support debugging on Windows using Windows CMD/CLI (`pio debug <https://docs.platformio.org/page/core/userguide/cmd_debug.html>`__) (`issue #3793 <https://github.com/platformio/platformio-core/issues/3793>`_)
  - Configure a custom pattern to determine when debugging server is started with a new `debug_server_ready_pattern <https://docs.platformio.org/page/projectconf/section_env_debug.html#debug-server-ready-pattern>`__ option
  - Fixed an issue with silent hanging when a custom debug server is not found (`issue #3756 <https://github.com/platformio/platformio-core/issues/3756>`_)

* **Static Code Analysis**

  - Updated analysis tools:

    * `Cppcheck <https://docs.platformio.org/page/plus/check-tools/cppcheck.html>`__ v2.4.1 with new checks and MISRA improvements
    * `PVS-Studio <https://docs.platformio.org/page/plus/check-tools/pvs-studio.html>`__ v7.12 with new diagnostics and extended capabilities for security and safety standards

* **Package Management**

  - Improved a package publishing process:

    * Show package details
    * Check for conflicting names in the PlatformIO Trusted Registry
    * Check for duplicates and used version
    * Validate package manifest

  - Added a new option ``--non-interactive`` to `pio package publish <https://docs.platformio.org/page/core/userguide/package/cmd_publish.html>`__ command

* **Miscellaneous**

  - Ensure that a serial port is ready before running unit tests on a remote target (`issue #3742 <https://github.com/platformio/platformio-core/issues/3742>`_)
  - Fixed an error "Unknown development platform" when running unit tests on a clean machine (`issue #3901 <https://github.com/platformio/platformio-core/issues/3901>`_)
  - Fixed an issue when "main.cpp" was generated for a new project for 8-bit development platforms (`issue #3872 <https://github.com/platformio/platformio-core/issues/3872>`_)
  - Fixed an issue with broken binary file extension when a custom ``PROGNAME`` contains dot symbols (`issue #3906 <https://github.com/platformio/platformio-core/issues/3906>`_)

5.1.1 (2021-03-17)
~~~~~~~~~~~~~~~~~~

* Fixed a "The command line is too long" issue with a linking process on Windows (`issue #3827 <https://github.com/platformio/platformio-core/issues/3827>`_)
* Fixed an issue with `device monitor <https://docs.platformio.org/page/core/userguide/device/cmd_monitor.html>`__ when the "send_on_enter" filter didn't send EOL chars (`issue #3787 <https://github.com/platformio/platformio-core/issues/3787>`_)
* Fixed an issue with silent mode when unwanted data is printed to stdout (`issue #3837 <https://github.com/platformio/platformio-core/issues/3837>`_)
* Fixed an issue when code inspection fails with "Bad JSON" (`issue #3790 <https://github.com/platformio/platformio-core/issues/3790>`_)
* Fixed an issue with overriding user-specified debugging configuration information in VSCode (`issue #3824 <https://github.com/platformio/platformio-core/issues/3824>`_)

5.1.0 (2021-01-28)
~~~~~~~~~~~~~~~~~~

* **PlatformIO Home**

  - Boosted `PlatformIO Home <https://docs.platformio.org/page/home/index.html>`__  performance thanks to migrating the codebase to the pure Python 3 Asynchronous I/O stack
  - Added a new ``--session-id`` option to `pio home <https://docs.platformio.org/page/core/userguide/cmd_home.html>`__ command that helps to keep PlatformIO Home isolated from other instances and protect from 3rd party access (`issue #3397 <https://github.com/platformio/platformio-core/issues/3397>`_)

* **Build System**

  - Upgraded build engine to the SCons 4.1 (`release notes <https://scons.org/scons-410-is-available.html>`_)
  - Refactored a workaround for a maximum command line character limitation (`issue #3792 <https://github.com/platformio/platformio-core/issues/3792>`_)
  - Fixed an issue with Python 3.8+ on Windows when a network drive is used (`issue #3417 <https://github.com/platformio/platformio-core/issues/3417>`_)

* **Package Management**

  - New options for `pio system prune <https://docs.platformio.org/page/core/userguide/system/cmd_prune.html>`__ command:

    + ``--dry-run`` option to show data that will be removed
    + ``--core-packages`` option to remove unnecessary core packages
    + ``--platform-packages`` option to remove unnecessary development platform packages (`issue #923 <https://github.com/platformio/platformio-core/issues/923>`_)

  - Added new `check_prune_system_threshold <https://docs.platformio.org/page/core/userguide/cmd_settings.html#check-prune-system-threshold>`__ setting
  - Disabled automatic removal of unnecessary development platform packages (`issue #3708 <https://github.com/platformio/platformio-core/issues/3708>`_, `issue #3770 <https://github.com/platformio/platformio-core/issues/3770>`_)
  - Fixed an issue when unnecessary packages were removed in  ``update --dry-run`` mode (`issue #3809 <https://github.com/platformio/platformio-core/issues/3809>`_)
  - Fixed a "ValueError: Invalid simple block" when uninstalling a package with a custom name and external source (`issue #3816 <https://github.com/platformio/platformio-core/issues/3816>`_)

* **Debugging**

  - Configure a custom debug adapter speed using a new `debug_speed <https://docs.platformio.org/page/projectconf/section_env_debug.html#debug-speed>`__ option (`issue #3799 <https://github.com/platformio/platformio-core/issues/3799>`_)
  - Handle debugging server's "ready_pattern" in "stderr" output

* **Miscellaneous**

  - Improved listing of `multicast DNS services <https://docs.platformio.org/page/core/userguide/device/cmd_list.html>`_
  - Fixed a "UnicodeDecodeError: 'utf-8' codec can't decode byte" when using J-Link for firmware uploading on Linux (`issue #3804 <https://github.com/platformio/platformio-core/issues/3804>`_)
  - Fixed an issue with a compiler driver for ".ccls" language server (`issue #3808 <https://github.com/platformio/platformio-core/issues/3808>`_)
  - Fixed an issue when `pio device monitor --eol <https://docs.platformio.org/page/core/userguide/device/cmd_monitor.html#cmdoption-pio-device-monitor-eol>`__ and "send_on_enter" filter do not work properly (`issue #3787 <https://github.com/platformio/platformio-core/issues/3787>`_)

5.0.4 (2020-12-30)
~~~~~~~~~~~~~~~~~~

- Added "Core" suffix when showing PlatformIO Core version using ``pio --version`` command
- Improved ".ccls" configuration file for Emacs, Vim, and Sublime Text integrations
- Updated analysis tools:

  * `Cppcheck <https://docs.platformio.org/page/plus/check-tools/cppcheck.html>`__ v2.3 with improved C++ parser and several new MISRA rules
  * `PVS-Studio <https://docs.platformio.org/page/plus/check-tools/pvs-studio.html>`__ v7.11 with new diagnostics and updated mass suppression mechanism

- Show a warning message about deprecated support for Python 2 and Python 3.5
- Do not provide "intelliSenseMode" option when generating configuration for VSCode C/C++ extension
- Fixed a "git-sh-setup: file not found" error when installing project dependencies from Git VCS (`issue #3740 <https://github.com/platformio/platformio-core/issues/3740>`_)
- Fixed an issue with package publishing on Windows when Unix permissions are not preserved (`issue #3776 <https://github.com/platformio/platformio-core/issues/3776>`_)

5.0.3 (2020-11-12)
~~~~~~~~~~~~~~~~~~

- Added an error selector for `Sublime Text <https://docs.platformio.org/page/integration/ide/sublimetext.html>`__ build runner (`issue #3733 <https://github.com/platformio/platformio-core/issues/3733>`_)
- Generate a working "projectEnvName" for PlatformIO IDE's debugger for VSCode
- Force VSCode's intelliSenseMode to "gcc-x64" when GCC toolchain is used
- Print ignored test suites and environments in the test summary report only in verbose mode (`issue #3726 <https://github.com/platformio/platformio-core/issues/3726>`_)
- Fixed an issue when the package manager tries to install a built-in library from the registry (`issue #3662 <https://github.com/platformio/platformio-core/issues/3662>`_)
- Fixed an issue when `pio package pack <https://docs.platformio.org/page/core/userguide/package/cmd_pack.html>`__ ignores some folders (`issue #3730 <https://github.com/platformio/platformio-core/issues/3730>`_)

5.0.2 (2020-10-30)
~~~~~~~~~~~~~~~~~~

- Initialize a new project or update the existing passing working environment name and its options (`issue #3686 <https://github.com/platformio/platformio-core/issues/3686>`_)
- Automatically build PlatformIO Core extra Python dependencies on a host machine if they are missed in the registry (`issue #3700 <https://github.com/platformio/platformio-core/issues/3700>`_)
- Improved "core.call" RPC for PlatformIO Home (`issue #3671 <https://github.com/platformio/platformio-core/issues/3671>`_)
- Fixed a "PermissionError: [WinError 5]" on Windows when an external repository is used with `lib_deps <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-deps>`__ option (`issue #3664 <https://github.com/platformio/platformio-core/issues/3664>`_)
- Fixed a "KeyError: 'versions'" when dependency does not exist in the registry (`issue #3666 <https://github.com/platformio/platformio-core/issues/3666>`_)
- Fixed an issue with GCC linker when "native" dev-platform is used in pair with library dependencies (`issue #3669 <https://github.com/platformio/platformio-core/issues/3669>`_)
- Fixed an "AssertionError: ensure_dir_exists" when checking library updates from simultaneous subprocesses (`issue #3677 <https://github.com/platformio/platformio-core/issues/3677>`_)
- Fixed an issue when `pio package publish <https://docs.platformio.org/page/core/userguide/package/cmd_publish.html>`__ command removes original archive after submitting to the registry (`issue #3716 <https://github.com/platformio/platformio-core/issues/3716>`_)
- Fixed an issue when multiple `pio lib install <https://docs.platformio.org/page/core/userguide/lib/cmd_install.html>`__ command with the same local library results in duplicates in ``lib_deps`` (`issue #3715 <https://github.com/platformio/platformio-core/issues/3715>`_)
- Fixed an issue with a "wrong" timestamp in device monitor output using `"time" filter <https://docs.platformio.org/page/core/userguide/device/cmd_monitor.html#filters>`__ (`issue #3712 <https://github.com/platformio/platformio-core/issues/3712>`_)

5.0.1 (2020-09-10)
~~~~~~~~~~~~~~~~~~

- Added support for "owner" requirement when declaring ``dependencies`` using `library.json <https://docs.platformio.org/page/librarymanager/config.html#dependencies>`__
- Fixed an issue when using a custom git/ssh package with `platform_packages <https://docs.platformio.org/page/projectconf/section_env_platform.html#platform-packages>`__ option (`issue #3624 <https://github.com/platformio/platformio-core/issues/3624>`_)
- Fixed an issue with "ImportError: cannot import name '_get_backend' from 'cryptography.hazmat.backends'" when using `Remote Development <https://docs.platformio.org/page/plus/pio-remote.html>`__ on RaspberryPi device (`issue #3652 <https://github.com/platformio/platformio-core/issues/3652>`_)
- Fixed an issue when `pio package unpublish <https://docs.platformio.org/page/core/userguide/package/cmd_unpublish.html>`__ command crashes (`issue #3660 <https://github.com/platformio/platformio-core/issues/3660>`_)
- Fixed an issue when the package manager tries to install a built-in library from the registry (`issue #3662 <https://github.com/platformio/platformio-core/issues/3662>`_)
- Fixed an issue with incorrect value for C++ language standard in IDE projects when an in-progress language standard is used (`issue #3653 <https://github.com/platformio/platformio-core/issues/3653>`_)
- Fixed an issue with "Invalid simple block (semantic_version)" from library dependency that refs to an external source (repository, ZIP/Tar archives) (`issue #3658 <https://github.com/platformio/platformio-core/issues/3658>`_)
- Fixed an issue when can not remove update or remove external dev-platform using PlatformIO Home (`issue #3663 <https://github.com/platformio/platformio-core/issues/3663>`_)

5.0.0 (2020-09-03)
~~~~~~~~~~~~~~~~~~

Please check `Migration guide from 4.x to 5.0 <https://docs.platformio.org/page/core/migration.html>`__.

* Integration with the new **PlatformIO Trusted Registry**

  - Enterprise-grade package storage with high availability (multi replicas)
  - Secure, fast, and reliable global content delivery network (CDN)
  - Universal support for all packages:

    * Libraries
    * Development platforms
    * Toolchains

  - Built-in fine-grained access control (role-based, teams, organizations)
  - New CLI commands:

    * `pio package <https://docs.platformio.org/page/core/userguide/package/index.html>`__ – manage packages in the registry
    * `pio access <https://docs.platformio.org/page/core/userguide/access/index.html>`__ – manage package access for users, teams, and maintainers

* Integration with the new **Account Management System**

  - `Manage organizations <https://docs.platformio.org/page/core/userguide/org/index.html>`__
  - `Manage teams and team memberships <https://docs.platformio.org/page/core/userguide/team/index.html>`__

* New **Package Management System**

  - Integrated PlatformIO Core with the new PlatformIO Registry
  - Support for owner-based dependency declaration (resolves name conflicts) (`issue #1824 <https://github.com/platformio/platformio-core/issues/1824>`_)
  - Automatically save dependencies to `"platformio.ini" <https://docs.platformio.org/page/projectconf.html>`__ when installing using PlatformIO CLI (`issue #2964 <https://github.com/platformio/platformio-core/issues/2964>`_)
  - Follow SemVer complaint version constraints when checking library updates `issue #1281 <https://github.com/platformio/platformio-core/issues/1281>`_)
  - Dropped support for "packageRepositories" section in "platform.json" manifest (please publish packages directly to the registry)

* **Build System**

  - Upgraded build engine to the `SCons 4.0 - a next-generation software construction tool <https://scons.org/>`__

    * `Configuration files are Python scripts <https://docs.platformio.org/page/projectconf/advanced_scripting.html>`__ – use the power of a real programming language to solve build problems
    * Built-in reliable and automatic dependency analysis
    * Improved support for parallel builds
    * Ability to `share built files in a cache <https://docs.platformio.org/page/projectconf/section_platformio.html#projectconf-pio-build-cache-dir>`__ to speed up multiple builds

  - New `Custom Targets <https://docs.platformio.org/page/projectconf/advanced_scripting.html#custom-targets>`__

    * Pre/Post processing based on dependent sources (another target, source file, etc.)
    * Command launcher with own arguments
    * Launch command with custom options declared in `"platformio.ini" <https://docs.platformio.org/page/projectconf.html>`__
    * Python callback as a target (use the power of Python interpreter and PlatformIO Build API)
    * List available project targets (including dev-platform specific and custom targets) with a new `pio run --list-targets <https://docs.platformio.org/page/core/userguide/cmd_run.html#cmdoption-platformio-run-list-targets>`__ command (`issue #3544 <https://github.com/platformio/platformio-core/issues/3544>`_)

  - Enable "cyclic reference" for GCC linker only for the embedded dev-platforms (`issue #3570 <https://github.com/platformio/platformio-core/issues/3570>`_)
  - Automatically enable LDF dependency `chain+ mode (evaluates C/C++ Preprocessor conditional syntax) <https://docs.platformio.org/page/librarymanager/ldf.html#dependency-finder-mode>`__ for Arduino library when "library.property" has "depends" field (`issue #3607 <https://github.com/platformio/platformio-core/issues/3607>`_)
  - Fixed an issue with improper processing of source files added via multiple Build Middlewares (`issue #3531 <https://github.com/platformio/platformio-core/issues/3531>`_)
  - Fixed an issue with the ``clean`` target on Windows when project and build directories are located on different logical drives (`issue #3542 <https://github.com/platformio/platformio-core/issues/3542>`_)

* **Project Management**

  - Added support for "globstar/`**`" (recursive) pattern for the different commands and configuration options (`pio ci <https://docs.platformio.org/page/core/userguide/cmd_ci.html>`__, `src_filter <https://docs.platformio.org/page/projectconf/section_env_build.html#src-filter>`__, `check_patterns <https://docs.platformio.org/page/projectconf/section_env_check.html#check-patterns>`__, `library.json > srcFilter <https://docs.platformio.org/page/librarymanager/config.html#srcfilter>`__). Python 3.5+ is required
  - Added a new ``-e, --environment`` option to `pio project init <https://docs.platformio.org/page/core/userguide/project/cmd_init.html#cmdoption-platformio-project-init-e>`__ command that helps to update a PlatformIO project using the existing environment
  - Dump build system data intended for IDE extensions/plugins using a new `pio project data <https://docs.platformio.org/page/core/userguide/project/cmd_data.html>`__ command
  - Do not generate ".travis.yml" for a new project, let the user have a choice

* **Unit Testing**

  - Updated PIO Unit Testing support for Mbed framework and added compatibility with Mbed OS 6
  - Fixed an issue when running multiple test environments (`issue #3523 <https://github.com/platformio/platformio-core/issues/3523>`_)
  - Fixed an issue when Unit Testing engine fails with a custom project configuration file (`issue #3583 <https://github.com/platformio/platformio-core/issues/3583>`_)

* **Static Code Analysis**

  - Updated analysis tools:

    * `Cppcheck <https://docs.platformio.org/page/plus/check-tools/cppcheck.html>`__ v2.1 with a new "soundy" analysis option and improved code parser
    * `PVS-Studio <https://docs.platformio.org/page/plus/check-tools/pvs-studio.html>`__ v7.09 with a new file list analysis mode and an extended list of analysis diagnostics

  - Added Cppcheck package for ARM-based single-board computers (`issue #3559 <https://github.com/platformio/platformio-core/issues/3559>`_)
  - Fixed an issue with PIO Check when a defect with a multiline error message is not reported in verbose mode (`issue #3631 <https://github.com/platformio/platformio-core/issues/3631>`_)

* **Miscellaneous**

  - Display system-wide information using a new `pio system info <https://docs.platformio.org/page/core/userguide/system/cmd_info.html>`__ command (`issue #3521 <https://github.com/platformio/platformio-core/issues/3521>`_)
  - Remove unused data using a new `pio system prune <https://docs.platformio.org/page/core/userguide/system/cmd_prune.html>`__ command (`issue #3522 <https://github.com/platformio/platformio-core/issues/3522>`_)
  - Show ignored project environments only in the verbose mode (`issue #3641 <https://github.com/platformio/platformio-core/issues/3641>`_)
  - Do not escape compiler arguments in VSCode template on Windows
  - Drop support for Python 2 and 3.5.

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
