Release Notes
=============

PlatformIO 3.0
--------------

3.6.2 (2018-??-??)
~~~~~~~~~~~~~~~~~~

* Improved IntelliSense for `PlatformIO IDE for VSCode <http://docs.platformio.org/page/ide/vscode.html>`__ via passing extra compiler information for C/C++ Code Parser (resolves issues with spurious project's "Problems")
* Fixed an issue with VSCode IntelliSense warning about the missed headers located in `include <http://docs.platformio.org/page/projectconf/section_platformio.html#include-dir>`__ folder
* Fixed incorrect wording when initializing/updating project
* Fixed an issue with incorrect order for library dependencies ``CPPPATH``
  (`issue #1914 <https://github.com/platformio/platformio-core/issues/1914>`_)
* Fixed an issue when Library Dependency Finder (LDF) does not handle project `src_filter <http://docs.platformio.org/page/projectconf/section_env_build.html#src-filter>`__
  (`issue #1905 <https://github.com/platformio/platformio-core/issues/1905>`_)
* Fixed an issue when Library Dependency Finder (LDF) finds spurious dependencies in ``chain+`` and ``deep+`` modes
  (`issue #1930 <https://github.com/platformio/platformio-core/issues/1930>`_)

3.6.1 (2018-10-29)
~~~~~~~~~~~~~~~~~~

* Generate an `include <http://docs.platformio.org/page/projectconf/section_platformio.html#include-dir>`__ and `test <http://docs.platformio.org/page/projectconf/section_platformio.html#test-dir>`__ directories with a README file when initializing a new project
* Support in-line comments for multi-line value (``lib_deps``, ``build_flags``, etc) in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
* Added ``$PROJECT_HASH`` template variable for `build_dir <http://docs.platformio.org/en/latest/projectconf/section_platformio.html#projectconf-pio-build-dir>`__. One of the use cases is setting a global storage for project artifacts using `PLATFORMIO_BUILD_DIR <http://docs.platformio.org/en/latest/envvars.html#envvar-PLATFORMIO_BUILD_DIR>`__ system environment variable. For example, ``/tmp/pio-build/$PROJECT_HASH`` (Unix) or ``%TEMP%/pio-build/$PROJECT_HASH`` (Windows)
* Improved a loading speed of PIO Home "Recent News"
* Improved `PIO Unified Debugger <https://docs.platformio.org/en/page/plus/debugging.html>`__ for "mbed" framework and fixed issue with missed local variables
* Introduced `"Release" and "Debug" Build Configurations <http://docs.platformio.org/page/projectconf/build_configurations.html>`__
* Build project in "Debug Mode" including debugging information with a new ``debug`` target using `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__ command or `targets <http://docs.platformio.org/page/projectconf/section_env_general.html#targets>`__ option in ``platformio.ini``. The last option allows avoiding project rebuilding between "Run/Debug" modes.
  (`issue #1833 <https://github.com/platformio/platformio-core/issues/1833>`_)
* Process ``build_unflags`` for the cloned environment when building a static library
* Report on outdated `99-platformio-udev.rules <http://docs.platformio.org/page/faq.html#platformio-udev-rules>`__
  (`issue #1823 <https://github.com/platformio/platformio-core/issues/1823>`_)
* Show a valid error when the Internet is off-line while initializing a new project
  (`issue #1784 <https://github.com/platformio/platformio-core/issues/1784>`_)
* Do not re-create ".gitignore" and ".travis.yml" files if they were removed from a project
* Fixed an issue when dynamic build flags were not handled correctly
  (`issue #1799 <https://github.com/platformio/platformio-core/issues/1799>`_)
* Fixed an issue when ``pio run -t monitor`` always uses the first ``monitor_port`` even with multiple environments
  (`issue #1841 <https://github.com/platformio/platformio-core/issues/1841>`_)
* Fixed an issue with broken includes when generating ``.clang_complete`` and space is used in a path
  (`issue #1873 <https://github.com/platformio/platformio-core/issues/1873>`_)
* Fixed an issue with incorrect handling of a custom package name when using `platformio lib install <http://docs.platformio.org/page/userguide/lib/cmd_install.html>`__ or `platformio platform install <http://docs.platformio.org/page/userguide/platforms/cmd_install.html>`__ commands


3.6.0 (2018-08-06)
~~~~~~~~~~~~~~~~~~

* `Program Memory Usage <https://docs.platformio.org/page/faq.html#program-memory-usage>`_

  - Print human-readable memory usage information after a build and before uploading
  - Print detailed memory usage information with "sections" and "addresses"
    in `verbose mode <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption-platformio-run-v>`__
  - Check maximum allowed "program" and "data" sizes before uploading/programming
    (`issue #1412 <https://github.com/platformio/platformio-core/issues/1412>`_)

* `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__:

  - Documented `Project Shared Code <https://docs.platformio.org/page/plus/unit-testing.html#shared-code>`__
  - Force building of project source code using `test_build_project_src <https://docs.platformio.org/page/projectconf/section_env_test.html#test_build_project_src>`__ option
  - Fixed missed ``UNIT_TEST`` macro for unit test components/libraries

* Check package structure after unpacking and raise error when antivirus tool
  blocks PlatformIO package manager
  (`issue #1462 <https://github.com/platformio/platformio-core/issues/1462>`_)
* Lock interprocess requests to PlatformIO Package Manager for
  install/uninstall operations
  (`issue #1594 <https://github.com/platformio/platformio-core/issues/1594>`_)
* Fixed an issue with `PIO Remote <https://docs.platformio.org/page/plus/pio-remote.html>`__
  when upload process depends on the source code of a project framework
* Fixed an issue when ``srcFilter`` field in `library.json <https://docs.platformio.org/page/librarymanager/config.html>`__
  breaks a library build
  (`issue #1735 <https://github.com/platformio/platformio-core/issues/1735>`_)

3.5.4 (2018-07-03)
~~~~~~~~~~~~~~~~~~

* Improved removing of default build flags using `build_unflags <https://docs.platformio.org/page/projectconf/section_env_build.html#build-unflags>`__ option
  (`issue #1712 <https://github.com/platformio/platformio-core/issues/1712>`_)
* Export ``LIBS``, ``LIBPATH``, and ``LINKFLAGS`` data from project dependent
  libraries to the global build environment
* Don't export ``CPPPATH`` data of project dependent libraries to framework's
  build environment
  (`issue #1665 <https://github.com/platformio/platformio-core/issues/1665>`_)
* Handle "architectures" data from "library.properties" manifest in
  `lib_compat_mode = strict <https://docs.platformio.org/en/page/librarymanager/ldf.html#compatibility-mode>`__
* Added workaround for Python SemVer package's `issue #61 <https://github.com/rbarrois/python-semanticversion/issues/61>`_ with caret range and pre-releases
* Replaced conflicted "env" pattern by "sysenv" for `"platformio.ini" Dynamic Variables" <https://docs.platformio.org/page/projectconf/dynamic_variables.html>`__
  (`issue #1705 <https://github.com/platformio/platformio-core/issues/1705>`_)
* Removed "date&time" when processing project with `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__ command
  (`issue #1343 <https://github.com/platformio/platformio-core/issues/1343>`_)
* Fixed issue with invalid LD script if path contains space
* Fixed preprocessor for Arduino sketch when function returns certain type
  (`issue #1683 <https://github.com/platformio/platformio-core/issues/1683>`_)
* Fixed issue when `platformio lib uninstall <https://docs.platformio.org/page/userguide/lib/cmd_uninstall.html>`__
  removes initial source code
  (`issue #1023 <https://github.com/platformio/platformio-core/issues/1023>`_)

3.5.3 (2018-06-01)
~~~~~~~~~~~~~~~~~~

* `PlatformIO Home <https://docs.platformio.org/page/home/index.html>`__ -
  interact with PlatformIO ecosystem using modern and cross-platform GUI:

  - "Recent News" block on "Welcome" page
  - Direct import of development platform's example

* Simplify configuration for `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__: separate main program from a test build process, drop
  requirement for ``#ifdef UNIT_TEST`` guard
* Override any option from board manifest in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf/section_env_board.html#more-options>`__
  (`issue #1612 <https://github.com/platformio/platformio-core/issues/1612>`_)
* Configure a custom path to SVD file using `debug_svd_path <https://docs.platformio.org/page/projectconf/section_env_debug.html#debug-svd-path>`__
  option
* Custom project `description <https://docs.platformio.org/en/page/projectconf/section_platformio.html#description>`_
  which will be used by `PlatformIO Home <https://docs.platformio.org/page/home/index.html>`_
* Updated Unity tool to 2.4.3
* Improved support for Black Magic Probe in "uploader" mode
* Renamed "monitor_baud" option to "monitor_speed"
* Fixed issue when a custom `lib_dir <https://docs.platformio.org/page/projectconf/section_platformio.html#lib-dir>`__
  was not handled correctly
  (`issue #1473 <https://github.com/platformio/platformio-core/issues/1473>`_)
* Fixed issue with useless project rebuilding for case insensitive file
  systems (Windows)
* Fixed issue with ``build_unflags`` option when a macro contains value
  (e.g., ``-DNAME=VALUE``)
* Fixed issue which did not allow to override runtime build environment using
  extra POST script
* Fixed "RuntimeError: maximum recursion depth exceeded" for library manager
  (`issue #1528 <https://github.com/platformio/platformio-core/issues/1528>`_)

3.5.2 (2018-03-13)
~~~~~~~~~~~~~~~~~~

* `PlatformIO Home <https://docs.platformio.org/page/home/index.html>`__ -
  interact with PlatformIO ecosystem using modern and cross-platform GUI:

  - Multiple themes (Dark & Light)
  - Ability to specify a name for new project

* Control `PIO Unified Debugger <https://docs.platformio.org/en/page/plus/debugging.html>`__
  and its firmware loading mode using
  `debug_load_mode <https://docs.platformio.org/en/page/projectconf/section_env_debug.html#debug-load-mode>`__ option
* Added aliases (off, light, strict) for
  `LDF Compatibility Mode <https://docs.platformio.org/page/librarymanager/ldf.html>`__
* Search for a library using PIO Library Registry ID ``id:X`` (e.g. ``pio lib search id:13``)
* Show device system information (MCU, Frequency, RAM, Flash, Debugging tools)
  in a build log
* Show all available upload protocols before firmware uploading in a build log
* Handle "os.mbed.com" URL as a Mercurial (hg) repository
* Improved support for old mbed libraries without manifest
* Fixed project generator for Qt Creator IDE
  (`issue #1303 <https://github.com/platformio/platformio-core/issues/1303>`_,
  `issue #1323 <https://github.com/platformio/platformio-core/issues/1323>`_)
* Mark project source and library directories for CLion IDE
  (`issue #1359 <https://github.com/platformio/platformio-core/issues/1359>`_,
  `issue #1345 <https://github.com/platformio/platformio-core/issues/1345>`_,
  `issue #897 <https://github.com/platformio/platformio-core/issues/897>`_)
* Fixed issue with duplicated "include" records when generating data for IDE
  (`issue #1301 <https://github.com/platformio/platformio-core/issues/1301>`_)

3.5.1 (2018-01-18)
~~~~~~~~~~~~~~~~~~

* New ``test_speed`` option to control a communication baudrate/speed between
  `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__
  engine and a target device
  (`issue #1273 <https://github.com/platformio/platformio-core/issues/1273>`_)
* Show full library version in "Library Dependency Graph" including VCS
  information
  (`issue #1274 <https://github.com/platformio/platformio-core/issues/1274>`_)
* Configure a custom firmware/program name in build directory (`example <https://docs.platformio.org/page/projectconf/advanced_scripting.html#custom-firmware-program-name>`__)
* Renamed ``envs_dir`` option to ``build_dir``
  in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf/section_platformio.html#build-dir>`__
* Refactored code without "arrow" dependency (resolve issue with "ImportError:
  No module named backports.functools_lru_cache")
* Improved support of PIO Unified Debugger for Eclipse Oxygen
* Improved a work in off-line mode
* Fixed project generator for CLion and Qt Creator IDE
  (`issue #1299 <https://github.com/platformio/platformio-core/issues/1299>`_)
* Fixed PIO Unified Debugger for mbed framework
* Fixed library updates when a version is declared in VCS format (not SemVer)

3.5.0 (2017-12-28)
~~~~~~~~~~~~~~~~~~

* `PlatformIO Home <https://docs.platformio.org/page/home/index.html>`__ -
  interact with PlatformIO ecosystem using modern and cross-platform GUI:

  - Library Manager:

    * Search for new libraries in PlatformIO Registry
    * "1-click" library installation, per-project libraries, extra storages
    * List installed libraries in multiple storages
    * List built-in libraries (by frameworks)
    * Updates for installed libraries
    * Multiple examples, trending libraries, and more.

  - PlatformIO Projects
  - PIO Account
  - Development platforms, frameworks and board explorer
  - Device Manager: serial, logical, and multicast DNS services

* Integration with `Jenkins CI <https://docs.platformio.org/page/ci/jenkins.html>`_
* New `include <https://docs.platformio.org/page/projectconf/section_platformio.html#include-dir>`__
  folder for project's header files
  (`issue #1107 <https://github.com/platformio/platformio-core/issues/1107>`_)
* Depend on development platform using VCS URL (Git, Mercurial and Subversion)
  instead of a name in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf/section_env_general.html#platform>`__.
  Drop support for ``*_stage`` dev/platform names (use VCS URL instead).
* Reinstall/redownload package with a new ``-f, --force`` option for
  `platformio lib install <https://docs.platformio.org/page/userguide/lib/cmd_install.html>`__
  and `platformio platform install <https://docs.platformio.org/page/userguide/platforms/cmd_install.html>`__
  commands
  (`issue #778 <https://github.com/platformio/platformio-core/issues/778>`_)
* Handle missed dependencies and provide a solution based on PlatformIO Library
  Registry
  (`issue #781 <https://github.com/platformio/platformio-core/issues/781>`_)
* New setting `projects_dir <https://docs.platformio.org/page/userguide/cmd_settings.html#projects-dir>`__
  that allows to override a default PIO Home Projects location
  (`issue #1161 <https://github.com/platformio/platformio-core/issues/1161>`_)

* `Library Dependency Finder (LDF) <https://docs.platformio.org/page/librarymanager/ldf.html>`__:

  - Search for dependencies used in `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__
    (`issue #953 <https://github.com/platformio/platformio-core/issues/953>`_)
  - Parse library source file in pair with a header when they have the same name
    (`issue #1175 <https://github.com/platformio/platformio-core/issues/1175>`_)
  - Handle library dependencies defined as VCS or SemVer in
    `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf/section_env_general.html#platform>`__
    (`issue #1155 <https://github.com/platformio/platformio-core/issues/1155>`_)
  - Added option to configure library `Compatible Mode <https://docs.platformio.org/page/librarymanager/ldf.html#compatibility-mode>`__
    using `library.json <https://docs.platformio.org/page/librarymanager/config.html>`__

* New options for `platformio device list <https://docs.platformio.org/page/userguide/cmd_device.html#platformio-device-list>`__
  command:

  - ``--serial`` list available serial ports (default)
  - ``--logical`` list logical devices
  - ``--mdns`` discover multicast DNS services
    (`issue #463 <https://github.com/platformio/platformio-core/issues/463>`_)

* Fixed platforms, packages, and libraries updating behind proxy
  (`issue #1061 <https://github.com/platformio/platformio-core/issues/1061>`_)
* Fixed missing toolchain include paths for project generator
  (`issue #1154 <https://github.com/platformio/platformio-core/issues/1154>`_)
* Fixed "Super-Quick (Mac / Linux)" installation in "get-platformio.py" script
  (`issue #1017 <https://github.com/platformio/platformio-core/issues/1017>`_)
* Fixed "get-platformio.py" script which hangs on Windows 10
  (`issue #1118 <https://github.com/platformio/platformio-core/issues/1118>`_)
* Other bug fixes and performance improvements

3.4.1 (2017-08-02)
~~~~~~~~~~~~~~~~~~

* Pre/Post extra scripting for advanced control of PIO Build System
  (`issue #891 <https://github.com/platformio/platformio-core/issues/891>`_)
* New `lib_archive <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-archive>`_
  option to control library archiving and linking behavior
  (`issue #993 <https://github.com/platformio/platformio-core/issues/993>`_)
* Add "inc" folder automatically to CPPPATH when "src" is available (works for project and library)
  (`issue #1003 <https://github.com/platformio/platformio-core/issues/1003>`_)
* Use a root of library when filtering source code using
  `library.json <https://docs.platformio.org/page/librarymanager/config.html>`__
  and ``srcFilter`` field
* Added ``monitor_*`` options to white-list for `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #982 <https://github.com/platformio/platformio-core/issues/982>`_)
* Do not ask for board ID when initialize project for desktop platform
* Handle broken PIO Core state and create new one
* Fixed an issue with a custom transport for `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__
  when multiple tests are present
* Fixed an issue when can not upload firmware to SAM-BA based board (Due)

3.4.0 (2017-06-26)
~~~~~~~~~~~~~~~~~~

* `PIO Unified Debugger <https://docs.platformio.org/page/plus/debugging.html>`__

  - "1-click" solution, zero configuration
  - Support for 100+ embedded boards
  - Multiple architectures and development platforms
  - Windows, MacOS, Linux (+ARMv6-8)
  - Built-in into `PlatformIO IDE for Atom <https://docs.platformio.org/page/ide/atom.html>`__ and `PlatformIO IDE for VScode <https://docs.platformio.org/page/ide/vscode.html>`__
  - Integration with `Eclipse <https://docs.platformio.org/page/ide/eclipse.html>`__ and `Sublime Text <https://docs.platformio.org/page/ide/sublimetext.html>`__

* Filter `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__
  tests using a new ``test_filter`` option in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  or `platformio test --filter <https://docs.platformio.org/page/userguide/cmd_test.html#cmdoption-platformio-test-f>`__ command
  (`issue #934 <https://github.com/platformio/platformio-core/issues/934>`_)
* Custom ``test_transport`` for `PIO Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__ Engine
* Configure Serial Port Monitor in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #787 <https://github.com/platformio/platformio-core/issues/787>`_)
* New `monitor <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption-platformio-run-t>`__
  target which allows to launch Serial Monitor automatically after successful
  "build" or "upload" operations
  (`issue #788 <https://github.com/platformio/platformio-core/issues/788>`_)
* Project generator for `VIM <https://docs.platformio.org/page/ide/vim.html>`__
* Multi-line support for the different options in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__,
  such as: ``build_flags``, ``build_unflags``, etc.
  (`issue #889 <https://github.com/platformio/platformio-core/issues/889>`_)
* Handle dynamic ``SRC_FILTER`` environment variable from
  `library.json extra script <https://docs.platformio.org/page/librarymanager/config.html#extrascript>`__
* Notify about multiple installations of PIO Core
  (`issue #961 <https://github.com/platformio/platformio-core/issues/961>`_)
* Improved auto-detecting of mbed-enabled media disks
* Automatically update Git-submodules for development platforms and libraries
  that were installed from repository
* Add support for ``.*cc`` extension
  (`issue #939 <https://github.com/platformio/platformio-core/issues/939>`_)
* Handle ``env_default`` in `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  when re-initializing a project
  (`issue #950 <https://github.com/platformio/platformio-core/issues/950>`_)
* Use root directory for PIO Home when path contains non-ascii characters
  (`issue #951 <https://github.com/platformio/platformio-core/issues/951>`_,
  `issue #952 <https://github.com/platformio/platformio-core/issues/952>`_)
* Don't warn about known ``boards_dir`` option
  (`pull #949 <https://github.com/platformio/platformio-core/pull/949>`_)
* Escape non-valid file name characters when installing a new package (library)
  (`issue #985 <https://github.com/platformio/platformio-core/issues/985>`_)
* Fixed infinite dependency installing when repository consists of multiple
  libraries
  (`issue #935 <https://github.com/platformio/platformio-core/issues/935>`_)
* Fixed linter error "unity.h does not exist" for Unit Testing
  (`issue #947 <https://github.com/platformio/platformio-core/issues/947>`_)
* Fixed issue when `Library Dependency Finder (LDF) <https://docs.platformio.org/page/librarymanager/ldf.html>`__
  does not handle custom ``src_dir``
  (`issue #942 <https://github.com/platformio/platformio-core/issues/942>`_)
* Fixed cloning a package (library) from a private Git repository with
  custom user name and SSH port
  (`issue #925 <https://github.com/platformio/platformio-core/issues/925>`_)

3.3.1 (2017-05-27)
~~~~~~~~~~~~~~~~~~

* Hotfix for recently updated Python Requests package (2.16.0)

3.3.0 (2017-03-27)
~~~~~~~~~~~~~~~~~~

* PlatformIO Library Registry statistics with new
  `pio lib stats <https://docs.platformio.org/page/userguide/lib/cmd_stats.html>`__ command

  - Recently updated and added libraries
  - Recent and popular keywords
  - Featured libraries (today, week, month)

* List built-in libraries based on development platforms with a new
  `pio lib builtin <https://docs.platformio.org/page/userguide/lib/cmd_builtin.html>`__ command
* Show detailed info about a library using `pio lib show <https://docs.platformio.org/page/userguide/lib/cmd_show.html>`__
  command
  (`issue #430 <https://github.com/platformio/platformio-core/issues/430>`_)
* List supported frameworks, SDKs with a new
  `pio platform frameworks <https://docs.platformio.org/page/userguide/platforms/cmd_frameworks.html>`__ command
* Visual Studio Code extension for PlatformIO
  (`issue #619 <https://github.com/platformio/platformio-core/issues/619>`_)
* Added new options ``--no-reset``, ``--monitor-rts`` and ``--monitor-dtr``
  to `pio test <https://docs.platformio.org/page/userguide/cmd_test.html>`__
  command (allows to avoid automatic board's auto-reset when gathering test results)
* Added support for templated methods in ``*.ino to *.cpp`` converter
  (`pull #858 <https://github.com/platformio/platformio-core/pull/858>`_)
* Package version as "Repository URL" in manifest of development version
  (``"version": "https://github.com/user/repo.git"``)
* Produce less noisy output when ``-s/--silent`` options are used for
  `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`__
  and `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__
  commands
  (`issue #850 <https://github.com/platformio/platformio-core/issues/850>`_)
* Use C++11 by default for CLion IDE based projects
  (`pull #873 <https://github.com/platformio/platformio-core/pull/873>`_)
* Escape project path when Glob matching is used
* Do not overwrite project configuration variables when system environment
  variables are set
* Handle dependencies when installing non-registry package/library (VCS, archive, local folder)
  (`issue #913 <https://github.com/platformio/platformio-core/issues/913>`_)
* Fixed package installing with VCS branch for Python 2.7.3
  (`issue #885 <https://github.com/platformio/platformio-core/issues/885>`_)

3.2.1 (2016-12-07)
~~~~~~~~~~~~~~~~~~

* Changed default `LDF Mode <https://docs.platformio.org/page/librarymanager/ldf.html#ldf-mode>`__
  from ``chain+`` to ``chain``

3.2.0 (2016-12-07)
~~~~~~~~~~~~~~~~~~

* `PIO Remote™ <https://docs.platformio.org/page/plus/pio-remote.html>`__.
  **Your devices are always with you!**

  + Over-The-Air (OTA) Device Manager
  + OTA Serial Port Monitor
  + OTA Firmware Updates
  + Continuous Deployment
  + Continuous Delivery

* Integration with `Cloud IDEs <https://docs.platformio.org/page/ide.html#cloud-ide>`__

  + Cloud9
  + Codeanywhere
  + Eclipse Che

* `PIO Account <https://docs.platformio.org/page/userguide/account/index.html>`__
  and `PLATFORMIO_AUTH_TOKEN <https://docs.platformio.org/page/envvars.html#envvar-PLATFORMIO_AUTH_TOKEN>`__
  environment variable for CI systems
  (`issue #808 <https://github.com/platformio/platformio-core/issues/808>`_,
  `issue #467 <https://github.com/platformio/platformio-core/issues/467>`_)
* Inject system environment variables to configuration settings in
  `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #792 <https://github.com/platformio/platformio-core/issues/792>`_)
* Custom boards per project with ``boards_dir`` option in
  `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #515 <https://github.com/platformio/platformio-core/issues/515>`_)
* Unix shell-style wildcards for `upload_port <https://docs.platformio.org/page/projectconf/section_env_upload.html#upload-port>`_
  (`issue #839 <https://github.com/platformio/platformio-core/issues/839>`_)
* Refactored `Library Dependency Finder (LDF) <https://docs.platformio.org/page/librarymanager/ldf.html>`__
  C/C++ Preprocessor for conditional syntax (``#ifdef``, ``#if``, ``#else``,
  ``#elif``, ``#define``, etc.)
  (`issue #837 <https://github.com/platformio/platformio-core/issues/837>`_)
* Added new `LDF Modes <https://docs.platformio.org/page/librarymanager/ldf.html#ldf-mode>`__:
  ``chain+`` and ``deep+`` and set ``chain+`` as default
* Added global ``lib_extra_dirs`` option to ``[platformio]`` section for
  `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #842 <https://github.com/platformio/platformio-core/issues/842>`_)
* Enabled caching by default for API requests and Library Manager (see `enable_cache <https://docs.platformio.org/page/userguide/cmd_settings.html#enable-cache>`__ setting)
* Native integration with VIM/Neovim using `neomake-platformio <https://github.com/coddingtonbear/neomake-platformio>`__ plugin
* Changed a default exit combination for Device Monitor from ``Ctrl+]`` to ``Ctrl+C``
* Improved detecting of ARM mbed media disk for uploading
* Improved Project Generator for CLion IDE when source folder contains nested items
* Improved handling of library dependencies specified in ``library.json`` manifest
  (`issue #814 <https://github.com/platformio/platformio-core/issues/814>`_)
* Improved `Library Dependency Finder (LDF) <https://docs.platformio.org/page/librarymanager/ldf.html>`__
  for circular dependencies
* Show vendor version of a package for `platformio platform show <https://docs.platformio.org/page/userguide/platforms/cmd_show.html>`__ command
  (`issue #838 <https://github.com/platformio/platformio-core/issues/838>`_)
* Fixed unable to include SSH user in ``lib_deps`` repository url
  (`issue #830 <https://github.com/platformio/platformio-core/issues/830>`_)
* Fixed merging of ".gitignore" files when re-initialize project
  (`issue #848 <https://github.com/platformio/platformio-core/issues/848>`_)
* Fixed issue with ``PATH`` auto-configuring for upload tools
* Fixed ``99-platformio-udev.rules`` checker for Linux OS

3.1.0 (2016-09-19)
~~~~~~~~~~~~~~~~~~

* New! Dynamic variables/templates for `“platformio.ini” (Project Configuration File) <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #705 <https://github.com/platformio/platformio-core/issues/705>`_)
* Summary about processed environments
  (`issue #777 <https://github.com/platformio/platformio-core/issues/777>`_)
* Implemented LocalCache system for API and improved a work in off-line mode
* Improved Project Generator when custom ``--project-option`` is passed to
  `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`__
  command
* Deprecated ``lib_force`` option, please use `lib_deps <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-deps>`__ instead
* Return valid exit code from ``plaformio test`` command
* Fixed Project Generator for CLion IDE using Windows OS
  (`issue #785 <https://github.com/platformio/platformio-core/issues/785>`_)
* Fixed SSL Server-Name-Indication for Python < 2.7.9
  (`issue #774 <https://github.com/platformio/platformio-core/issues/774>`_)

3.0.1 (2016-09-08)
~~~~~~~~~~~~~~~~~~

* Disabled temporary SSL for PlatformIO services
  (`issue #772 <https://github.com/platformio/platformio-core/issues/772>`_)

3.0.0 (2016-09-07)
~~~~~~~~~~~~~~~~~~

* `PlatformIO Plus <https://pioplus.com>`__

  + Local and Embedded `Unit Testing <https://docs.platformio.org/page/plus/unit-testing.html>`__
    (`issue #408 <https://github.com/platformio/platformio-core/issues/408>`_,
    `issue #519 <https://github.com/platformio/platformio-core/issues/519>`_)

* Decentralized Development Platforms

  + Development platform manifest "platform.json" and
    `open source development platforms <https://github.com/platformio?utf8=✓&query=platform->`__
  + `Semantic Versioning <http://semver.org/>`__ for platform commands,
    development platforms and dependent packages
  + Custom package repositories
  + External embedded board configuration files, isolated build scripts
    (`issue #479 <https://github.com/platformio/platformio-core/issues/479>`_)
  + Embedded Board compatibility with more than one development platform
    (`issue #456 <https://github.com/platformio/platformio-core/issues/456>`_)

* Library Manager 3.0

  + Project dependencies per build environment using `lib_deps <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-deps>`__ option
    (`issue #413 <https://github.com/platformio/platformio-core/issues/413>`_)
  + `Semantic Versioning <http://semver.org/>`__ for library commands and
    dependencies
    (`issue #410 <https://github.com/platformio/platformio-core/issues/410>`_)
  + Multiple library storages: Project's Local, PlatformIO's Global or Custom
    (`issue #475 <https://github.com/platformio/platformio-core/issues/475>`_)
  + Install library by name
    (`issue #414 <https://github.com/platformio/platformio-core/issues/414>`_)
  + Depend on a library using VCS URL (GitHub, Git, ARM mbed code registry, Hg, SVN)
    (`issue #498 <https://github.com/platformio/platformio-core/issues/498>`_)
  + Strict search for library dependencies
    (`issue #588 <https://github.com/platformio/platformio-core/issues/588>`_)
  + Allowed ``library.json`` to specify sources other than PlatformIO's Repository
    (`issue #461 <https://github.com/platformio/platformio-core/issues/461>`_)
  + Search libraries by headers/includes with ``platformio lib search --header`` option

* New Intelligent Library Build System

  + `Library Dependency Finder <https://docs.platformio.org/page/faq.html#how-works-library-dependency-finder-ldf>`__
    that interprets C/C++ Preprocessor conditional macros with deep search behavior
  + Check library compatibility with project environment before building
    (`issue #415 <https://github.com/platformio/platformio-core/issues/415>`_)
  + Control Library Dependency Finder for compatibility using
    `lib_compat_mode <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-compat-mode>`__
    option
  + Custom library storages/directories with
    `lib_extra_dirs <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-extra-dirs>`__ option
    (`issue #537 <https://github.com/platformio/platformio-core/issues/537>`_)
  + Handle extra build flags, source filters and build script from
    `library.json <https://docs.platformio.org/page/librarymanager/config.html>`__
    (`issue #289 <https://github.com/platformio/platformio-core/issues/289>`_)
  + Allowed to disable library archiving (``*.ar``)
    (`issue #719 <https://github.com/platformio/platformio-core/issues/719>`_)
  + Show detailed build information about dependent libraries
    (`issue #617 <https://github.com/platformio/platformio-core/issues/617>`_)
  + Support for the 3rd party manifests (Arduino IDE "library.properties"
    and ARM mbed "module.json")

* Removed ``enable_prompts`` setting. Now, all PlatformIO CLI is non-blocking!
* Switched to SSL PlatformIO API
* Renamed ``platformio serialports`` command to ``platformio device``
* Build System: Attach custom Before/Pre and After/Post actions for targets
  (`issue #542 <https://github.com/platformio/platformio-core/issues/542>`_)
* Allowed passing custom project configuration options to ``platformio ci``
  and ``platformio init`` commands using ``-O, --project-option``.
* Print human-readable information when processing environments without
  ``-v, --verbose`` option
  (`issue #721 <https://github.com/platformio/platformio-core/issues/721>`_)
* Improved INO to CPP converter
  (`issue #659 <https://github.com/platformio/platformio-core/issues/659>`_,
  `issue #765 <https://github.com/platformio/platformio-core/issues/765>`_)
* Added ``license`` field to `library.json <https://docs.platformio.org/page/librarymanager/config.html>`__
  (`issue #522 <https://github.com/platformio/platformio-core/issues/522>`_)
* Warn about unknown options in project configuration file ``platformio.ini``
  (`issue #740 <https://github.com/platformio/platformio-core/issues/740>`_)
* Fixed wrong line number for INO file when ``#warning`` directive is used
  (`issue #742 <https://github.com/platformio/platformio-core/issues/742>`_)
* Stopped supporting Python 2.6

PlatformIO 2.0
--------------

2.11.2 (2016-08-02)
~~~~~~~~~~~~~~~~~~~

* Improved support for `Microchip PIC32 <https://docs.platformio.org/page/platforms/microchippic32.html>`__ development platform and ChipKIT boards
  (`issue #438 <https://github.com/platformio/platformio-core/issues/438>`_)
* Added support for Pinoccio Scout board
  (`issue #52 <https://github.com/platformio/platformio-core/issues/52>`_)
* Added support for `Teensy USB Features <https://docs.platformio.org/page/platforms/teensy.html#usb-features>`__
  (HID, SERIAL_HID, DISK, DISK_SDFLASH, MIDI, etc.)
  (`issue #722 <https://github.com/platformio/platformio-core/issues/722>`_)
* Switched to built-in GCC LwIP library for Espressif development platform
* Added support for local ``--echo`` for Serial Port Monitor
  (`issue #733 <https://github.com/platformio/platformio-core/issues/733>`_)
* Updated ``udev`` rules for the new STM32F407DISCOVERY boards
  (`issue #731 <https://github.com/platformio/platformio-core/issues/731>`_)
* Implemented firmware merging with base firmware for Nordic nRF51 development platform
  (`issue #500 <https://github.com/platformio/platformio-core/issues/500>`_,
  `issue #533 <https://github.com/platformio/platformio-core/issues/533>`_)
* Fixed Project Generator for ESP8266 and ARM mbed based projects
  (resolves incorrect linter errors)
* Fixed broken LD Script for Element14 chipKIT Pi board
  (`issue #725 <https://github.com/platformio/platformio-core/issues/725>`_)
* Fixed firmware uploading to Atmel SAMD21-XPRO board using ARM mbed framework
  (`issue #732 <https://github.com/platformio/platformio-core/issues/732>`_)

2.11.1 (2016-07-12)
~~~~~~~~~~~~~~~~~~~

* Added support for Arduino M0, M0 Pro and Tian boards
  (`issue #472 <https://github.com/platformio/platformio-core/issues/472>`_)
* Added support for Microchip chipKIT Lenny board
* Updated Microchip PIC32 Arduino framework to v1.2.1
* Documented `uploading of EEPROM data <https://docs.platformio.org/page/platforms/atmelavr.html#upload-eeprom-data>`__
  (from EEMEM directive)
* Added ``Rebuild C/C++ Project Index`` target to CLion and Eclipse IDEs
* Improved project generator for `CLion IDE <https://docs.platformio.org/page/ide/clion.html>`__
* Added ``udev`` rules for OpenOCD CMSIS-DAP adapters
  (`issue #718 <https://github.com/platformio/platformio-core/issues/718>`_)
* Auto-remove project cache when PlatformIO is upgraded
* Keep user changes for ``.gitignore`` file when re-generate/update project data
* Ignore ``[platformio]`` section from custom project configuration file when
  `platformio ci --project-conf <https://docs.platformio.org/page/userguide/cmd_ci.html>`__
  command is used
* Fixed missed ``--boot`` flag for the firmware uploader for ATSAM3X8E
  Cortex-M3 MCU based boards (Arduino Due, etc)
  (`issue #710 <https://github.com/platformio/platformio-core/issues/710>`_)
* Fixed missing trailing ``\`` for the source files list when generate project
  for `Qt Creator IDE <https://docs.platformio.org/page/ide/qtcreator.html>`__
  (`issue #711 <https://github.com/platformio/platformio-core/issues/711>`_)
* Split source files to ``HEADERS`` and ``SOURCES`` when generate project
  for `Qt Creator IDE <https://docs.platformio.org/page/ide/qtcreator.html>`__
  (`issue #713 <https://github.com/platformio/platformio-core/issues/713>`_)

2.11.0 (2016-06-28)
~~~~~~~~~~~~~~~~~~~

* New ESP8266-based boards: Generic ESP8285 Module, Phoenix 1.0 & 2.0, WifInfo
* Added support for Arduino M0 Pro board
  (`issue #472 <https://github.com/platformio/platformio-core/issues/472>`_)
* Added support for Arduino MKR1000 board
  (`issue #620 <https://github.com/platformio/platformio-core/issues/620>`_)
* Added support for Adafruit Feather M0, SparkFun SAMD21 and SparkFun SAMD21
  Mini Breakout boards
  (`issue #520 <https://github.com/platformio/platformio-core/issues/520>`_)
* Updated Arduino ESP8266 core for Espressif platform to 2.3.0
* Better removing unnecessary flags using ``build_unflags`` option
  (`issue #698 <https://github.com/platformio/platformio-core/issues/698>`_)
* Fixed issue with ``platformio init --ide`` command for Python 2.6

2.10.3 (2016-06-15)
~~~~~~~~~~~~~~~~~~~

* Fixed issue with ``platformio init --ide`` command

2.10.2 (2016-06-15)
~~~~~~~~~~~~~~~~~~~

* Added support for ST Nucleo L031K6 board to ARM mbed framework
* Process ``build_unflags`` option for ARM mbed framework
* Updated Intel ARC32 Arduino framework to v1.0.6
  (`issue #695 <https://github.com/platformio/platformio-core/issues/695>`_)
* Improved a check of program size before uploading to the board
* Fixed issue with ARM mbed framework ``-u _printf_float`` and
  ``-u _scanf_float`` when parsing ``$LINKFLAGS``
* Fixed issue with ARM mbed framework and extra includes for the custom boards,
  such as Seeeduino Arch Pro

2.10.1 (2016-06-13)
~~~~~~~~~~~~~~~~~~~

* Re-submit a package to PyPI

2.10.0 (2016-06-13)
~~~~~~~~~~~~~~~~~~~

* Added support for `emonPi <https://github.com/openenergymonitor/emonpi>`__,
  the OpenEnergyMonitor system
  (`issue #687 <https://github.com/platformio/platformio-core/issues/687>`_)
* Added support for `SPL <https://platformio.org/frameworks/spl>`__
  framework for STM32F0 boards
  (`issue #683 <https://github.com/platformio/platformio-core/issues/683>`_)
* Added support for `Arduboy DevKit <https://www.arduboy.com>`__, the game system
  the size of a credit card
* Updated ARM mbed framework package to v121
* Check program size before uploading to the board
  (`issue #689 <https://github.com/platformio/platformio-core/issues/689>`_)
* Improved firmware uploading to Arduino Leonardo based boards
  (`issue #691 <https://github.com/platformio/platformio-core/issues/691>`_)
* Fixed issue with ``-L relative/path`` when parsing ``build_flags``
  (`issue #688 <https://github.com/platformio/platformio-core/issues/688>`_)

2.9.4 (2016-06-04)
~~~~~~~~~~~~~~~~~~

* Show ``udev`` warning only for the Linux OS while uploading firmware

2.9.3 (2016-06-03)
~~~~~~~~~~~~~~~~~~

* Added support for `Arduboy <https://www.arduboy.com>`__, the game system
  the size of a credit card
* Updated `99-platformio-udev.rules <https://github.com/platformio/platformio-core/blob/develop/scripts/99-platformio-udev.rules>`__ for Linux OS
* Refactored firmware uploading to the embedded boards with SAM-BA bootloader

2.9.2 (2016-06-02)
~~~~~~~~~~~~~~~~~~

* Simplified `Continuous Integration with AppVeyor <https://docs.platformio.org/page/ci/appveyor.html>`__
  (`issue #671 <https://github.com/platformio/platformio-core/issues/671>`_)
* Automatically add source directory to ``CPPPATH`` of Build System
* Added support for Silicon Labs SLSTK3401A (Pearl Gecko) and
  MultiTech mDot F411 ARM mbed based boards
* Added support for MightyCore ATmega8535 board
  (`issue #585 <https://github.com/platformio/platformio-core/issues/585>`_)
* Added ``stlink`` as the default uploader for STM32 Discovery boards
  (`issue #665 <https://github.com/platformio/platformio-core/issues/665>`_)
* Use HTTP mirror for Package Manager in a case with SSL errors
  (`issue #645 <https://github.com/platformio/platformio-core/issues/645>`_)
* Improved firmware uploading to Arduino Leonardo/Due based boards
* Fixed bug with ``env_default`` when ``pio run -e`` is used
* Fixed issue with ``src_filter`` option for Windows OS
  (`issue #652 <https://github.com/platformio/platformio-core/issues/652>`_)
* Fixed configuration data for TI LaunchPads based on msp430fr4133 and
  msp430fr6989 MCUs
  (`issue #676 <https://github.com/platformio/platformio-core/issues/676>`_)
* Fixed issue with ARM mbed framework and multiple definition errors
  on FRDM-KL46Z board
  (`issue #641 <https://github.com/platformio/platformio-core/issues/641>`_)
* Fixed issue with ARM mbed framework when abstract class breaks compile
  for LPC1768
  (`issue #666 <https://github.com/platformio/platformio-core/issues/666>`_)

2.9.1 (2016-04-30)
~~~~~~~~~~~~~~~~~~

* Handle prototype pointers while converting ``*.ino`` to ``.cpp``
  (`issue #639 <https://github.com/platformio/platformio-core/issues/639>`_)

2.9.0 (2016-04-28)
~~~~~~~~~~~~~~~~~~

* Project generator for `CodeBlocks IDE <https://docs.platformio.org/page/ide/codeblocks.html>`__
  (`issue #600 <https://github.com/platformio/platformio-core/issues/600>`_)
* New `Lattice iCE40 FPGA <https://docs.platformio.org/page/platforms/lattice_ice40.html>`__
  development platform with support for Lattice iCEstick FPGA Evaluation
  Kit and BQ IceZUM Alhambra FPGA
  (`issue #480 <https://github.com/platformio/platformio-core/issues/480>`_)
* New `Intel ARC 32-bit <https://docs.platformio.org/page/platforms/intel_arc32.html>`_
  development platform with support for Arduino/Genuino 101 board
  (`issue #535 <https://github.com/platformio/platformio-core/issues/535>`_)
* New `Microchip PIC32 <https://docs.platformio.org/page/platforms/microchippic32.html>`__
  development platform with support for 20+ different PIC32 based boards
  (`issue #438 <https://github.com/platformio/platformio-core/issues/438>`_)
* New RTOS and build Framework named `Simba <https://docs.platformio.org/page/frameworks/simba.html>`__
  (`issue #412 <https://github.com/platformio/platformio-core/issues/412>`_)
* New boards for `ARM mbed <https://docs.platformio.org/page/frameworks/mbed.html>`__
  framework: ST Nucleo F410RB, ST Nucleo L073RZ and BBC micro:bit
* Added support for Arduino.Org boards: Arduino Leonardo ETH, Arduino Yun Mini,
  Arduino Industrial 101 and Linino One
  (`issue #472 <https://github.com/platformio/platformio-core/issues/472>`_)
* Added support for Generic ATTiny boards: ATTiny13, ATTiny24, ATTiny25,
  ATTiny45 and ATTiny85
  (`issue #636 <https://github.com/platformio/platformio-core/issues/636>`_)
* Added support for MightyCore boards: ATmega1284, ATmega644, ATmega324,
  ATmega164, ATmega32, ATmega16 and ATmega8535
  (`issue #585 <https://github.com/platformio/platformio-core/issues/585>`_)
* Added support for `TI MSP430 <https://docs.platformio.org/page/platforms/timsp430.html>`__
  boards: TI LaunchPad w/ msp430fr4133 and TI LaunchPad w/ msp430fr6989
* Updated Arduino core for Espressif platform to 2.2.0
  (`issue #627 <https://github.com/platformio/platformio-core/issues/627>`_)
* Updated native SDK for ESP8266 to 1.5
  (`issue #366 <https://github.com/platformio/platformio-core/issues/366>`_)
* PlatformIO Library Registry in JSON format! Implemented
  ``--json-output`` and ``--page`` options for
  `platformio lib search <https://docs.platformio.org/page/userguide/lib/cmd_search.html>`__
  command
  (`issue #604 <https://github.com/platformio/platformio-core/issues/604>`_)
* Allowed to specify default environments `env_default <https://docs.platformio.org/page/projectconf/section_platformio.html#env-default>`__
  which should be processed by default with ``platformio run`` command
  (`issue #576 <https://github.com/platformio/platformio-core/issues/576>`_)
* Allowed to unflag(remove) base/initial flags using
  `build_unflags <https://docs.platformio.org/page/projectconf/section_env_build.html#build-unflags>`__
  option
  (`issue #559 <https://github.com/platformio/platformio-core/issues/559>`_)
* Allowed multiple VID/PID pairs when detecting serial ports
  (`issue #632 <https://github.com/platformio/platformio-core/issues/632>`_)
* Automatically add ``-DUSB_MANUFACTURER`` with vendor's name
  (`issue #631 <https://github.com/platformio/platformio-core/issues/631>`_)
* Automatically reboot Teensy board after upload when Teensy Loader GUI is used
  (`issue #609 <https://github.com/platformio/platformio-core/issues/609>`_)
* Refactored source code converter from ``*.ino`` to ``*.cpp``
  (`issue #610 <https://github.com/platformio/platformio-core/issues/610>`_)
* Forced ``-std=gnu++11`` for Atmel SAM development platform
  (`issue #601 <https://github.com/platformio/platformio-core/issues/601>`_)
* Don't check OS type for ARM mbed-enabled boards and ST STM32 development
  platform before uploading to disk
  (`issue #596 <https://github.com/platformio/platformio-core/issues/596>`_)
* Fixed broken compilation for Atmel SAMD based boards except Arduino Due
  (`issue #598 <https://github.com/platformio/platformio-core/issues/598>`_)
* Fixed firmware uploading using serial port with spaces in the path
* Fixed cache system when project's root directory is used as ``src_dir``
  (`issue #635 <https://github.com/platformio/platformio-core/issues/635>`_)

2.8.6 (2016-03-22)
~~~~~~~~~~~~~~~~~~

* Launched `PlatformIO Community Forums <https://community.platformio.org>`_
  (`issue #530 <https://github.com/platformio/platformio-core/issues/530>`_)
* Added support for ARM mbed-enabled board Seed Arch Max (STM32F407VET6)
  (`issue #572 <https://github.com/platformio/platformio-core/issues/572>`_)
* Improved DNS lookup for PlatformIO API
* Updated Arduino Wiring-based framework to the latest version for
  Atmel AVR/SAM development platforms
* Updated "Teensy Loader CLI" and fixed uploading of large .hex files
  (`issue #568 <https://github.com/platformio/platformio-core/issues/568>`_)
* Updated the support for Sanguino Boards
  (`issue #586 <https://github.com/platformio/platformio-core/issues/586>`_)
* Better handling of used boards when re-initialize/update project
* Improved support for non-Unicode user profiles for Windows OS
* Disabled progress bar for download operations when prompts are disabled
* Fixed multiple definition errors for ST STM32 development platform and
  ARM mbed framework
  (`issue #571 <https://github.com/platformio/platformio-core/issues/571>`_)
* Fixed invalid board parameters (reset method and baudrate) for a few
  ESP8266 based boards
* Fixed "KeyError: 'content-length'" in PlatformIO Download Manager
  (`issue #591 <https://github.com/platformio/platformio-core/issues/591>`_)


2.8.5 (2016-03-07)
~~~~~~~~~~~~~~~~~~

* Project generator for `NetBeans IDE <https://docs.platformio.org/page/ide/netbeans.html>`__
  (`issue #541 <https://github.com/platformio/platformio-core/issues/541>`_)
* Created package for Homebrew Mac OS X Package Manager: ``brew install
  platformio``
  (`issue #395 <https://github.com/platformio/platformio-core/issues/395>`_)
* Updated Arduino core for Espressif platform to 2.1.0
  (`issue #544 <https://github.com/platformio/platformio-core/issues/544>`_)
* Added support for the ESP8266 ESP-07 board to
  `Espressif <https://docs.platformio.org/page/platforms/espressif.html>`__
  (`issue #527 <https://github.com/platformio/platformio-core/issues/527>`_)
* Improved handling of String-based ``CPPDEFINES`` passed to extra ``build_flags``
  (`issue #526 <https://github.com/platformio/platformio-core/issues/526>`_)
* Generate appropriate project for CLion IDE and CVS
  (`issue #523 <https://github.com/platformio/platformio-core/issues/523>`_)
* Use ``src_dir`` directory from `Project Configuration File platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  when initializing project otherwise create base ``src`` directory
  (`issue #536 <https://github.com/platformio/platformio-core/issues/536>`_)
* Fixed issue with incorrect handling of user's build flags where the base flags
  were passed after user's flags to GCC compiler
  (`issue #528 <https://github.com/platformio/platformio-core/issues/528>`_)
* Fixed issue with Project Generator when optional build flags were passed using
  system environment variables: `PLATFORMIO_BUILD_FLAGS <https://docs.platformio.org/page/envvars.html#platformio-build-flags>`__
  or `PLATFORMIO_BUILD_SRC_FLAGS <https://docs.platformio.org/page/envvars.html#platformio-build-src-flags>`__
* Fixed invalid detecting of compiler type
  (`issue #550 <https://github.com/platformio/platformio-core/issues/550>`_)
* Fixed issue with updating package which was deleted manually by user
  (`issue #555 <https://github.com/platformio/platformio-core/issues/555>`_)
* Fixed incorrect parsing of GCC ``-include`` flag
  (`issue #552 <https://github.com/platformio/platformio-core/issues/552>`_)

2.8.4 (2016-02-17)
~~~~~~~~~~~~~~~~~~

* Added support for the new ESP8266-based boards (ESPDuino, ESP-WROOM-02,
  ESPresso Lite 1.0 & 2.0, SparkFun ESP8266 Thing Dev, ThaiEasyElec ESPino) to
  `Espressif <https://docs.platformio.org/page/platforms/espressif.html>`__
  development platform
* Added ``board_f_flash`` option to `Project Configuration File platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  which allows to specify `custom flash chip frequency <https://docs.platformio.org/page/platforms/espressif.html#custom-flash-frequency>`_
  for Espressif development platform
  (`issue #501 <https://github.com/platformio/platformio-core/issues/501>`_)
* Added ``board_flash_mode`` option to `Project Configuration File platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  which allows to specify `custom flash chip mode <https://docs.platformio.org/page/platforms/espressif.html#custom-flash-mode>`_
  for Espressif development platform
* Handle new environment variables
  `PLATFORMIO_UPLOAD_PORT <https://docs.platformio.org/page/envvars.html#platformio-upload-port>`_
  and `PLATFORMIO_UPLOAD_FLAGS <https://docs.platformio.org/page/envvars.html#platformio-upload-flags>`_
  (`issue #518 <https://github.com/platformio/platformio-core/issues/518>`_)
* Fixed issue with ``CPPDEFINES`` which contain space and break PlatformIO
  IDE Linter
  (`IDE issue #34 <https://github.com/platformio/platformio-atom-ide/issues/34>`_)
* Fixed unable to link C++ standard library to Espressif platform build
  (`issue #503 <https://github.com/platformio/platformio-core/issues/503>`_)
* Fixed issue with pointer (``char* myfunc()``) while converting from ``*.ino``
  to ``*.cpp``
  (`issue #506 <https://github.com/platformio/platformio-core/issues/506>`_)

2.8.3 (2016-02-02)
~~~~~~~~~~~~~~~~~~

* Better integration of PlatformIO Builder with PlatformIO IDE Linter
* Fixed issue with removing temporary file while converting ``*.ino`` to
  ``*.cpp``
* Fixed missing dependency (mbed framework) for Atmel SAM development platform
  (`issue #487 <https://github.com/platformio/platformio-core/issues/487>`_)

2.8.2 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* Corrected RAM size for NXP LPC1768 based boards
  (`issue #484 <https://github.com/platformio/platformio-core/issues/484>`_)
* Exclude only ``test`` and ``tests`` folders from build process
* Reverted ``-Wl,-whole-archive`` hook for ST STM32 and mbed

2.8.1 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* Fixed a bug with Project Initialization in PlatformIO IDE

2.8.0 (2016-01-29)
~~~~~~~~~~~~~~~~~~

* `PlatformIO IDE <https://docs.platformio.org/page/ide/atom.html>`_ for
  Atom
  (`issue #470 <https://github.com/platformio/platformio-core/issues/470>`_)
* Added ``pio`` command line alias for ``platformio`` command
  (`issue #447 <https://github.com/platformio/platformio-core/issues/447>`_)
* Added SPL-Framework support for Nucleo F401RE board
  (`issue #453 <https://github.com/platformio/platformio-core/issues/453>`_)
* Added ``upload_resetmethod`` option to `Project Configuration File platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  which allows to specify `custom upload reset method <https://docs.platformio.org/page/platforms/espressif.html#custom-reset-method>`_
  for Espressif development platform
  (`issue #444 <https://github.com/platformio/platformio-core/issues/444>`_)
* Allowed to force output of color ANSI-codes or to disable progress bar even
  if the output is a ``pipe`` (not a ``tty``) using `Environment variables <https://docs.platformio.org/page/envvars.html>`__
  (`issue #465 <https://github.com/platformio/platformio-core/issues/465>`_)
* Set 1Mb SPIFFS for Espressif boards by default
  (`issue #458 <https://github.com/platformio/platformio-core/issues/458>`_)
* Exclude ``test*`` folder by default from build process
* Generate project for IDEs with information about installed libraries
* Fixed builder for mbed framework and ST STM32 platform


2.7.1 (2016-01-06)
~~~~~~~~~~~~~~~~~~

* Initial support for Arduino Zero board
  (`issue #356 <https://github.com/platformio/platformio-core/issues/356>`_)
* Added support for completions to Atom text editor using ``.clang_complete``
* Generate default targets for `supported IDE <https://docs.platformio.org/page/ide.html>`__
  (CLion, Eclipse IDE, Emacs, Sublime Text, VIM): Build,
  Clean, Upload, Upload SPIFFS image, Upload using Programmer, Update installed
  platforms and libraries
  (`issue #427 <https://github.com/platformio/platformio-core/issues/427>`_)
* Updated Teensy Arduino Framework to 1.27
  (`issue #434 <https://github.com/platformio/platformio-core/issues/434>`_)
* Fixed uploading of EEPROM data using ``uploadeep`` target for Atmel AVR
  development platform
* Fixed project generator for CLion IDE
  (`issue #422 <https://github.com/platformio/platformio-core/issues/422>`_)
* Fixed package ``shasum`` validation on Mac OS X 10.11.2
  (`issue #429 <https://github.com/platformio/platformio-core/issues/429>`_)
* Fixed CMakeLists.txt ``add_executable`` has only one source file
  (`issue #421 <https://github.com/platformio/platformio-core/issues/421>`_)

2.7.0 (2015-12-30)
~~~~~~~~~~~~~~~~~~

**Happy New Year!**

* Moved SCons to PlatformIO packages. PlatformIO does not require SCons to be
  installed in your system. Significantly simplified installation process of
  PlatformIO. ``pip install platformio`` rocks!
* Implemented uploading files to file system of ESP8266 SPIFFS (including OTA)
  (`issue #382 <https://github.com/platformio/platformio-core/issues/382>`_)
* Added support for the new Adafruit boards Bluefruit Micro and Feather
  (`issue #403 <https://github.com/platformio/platformio-core/issues/403>`_)
* Added support for RFDuino
  (`issue #319 <https://github.com/platformio/platformio-core/issues/319>`_)
* Project generator for `Emacs <https://docs.platformio.org/page/ide/emacs.html>`__
  text editor
  (`pull #404 <https://github.com/platformio/platformio-core/pull/404>`_)
* Updated Arduino framework for Atmel AVR development platform to 1.6.7
* Documented `firmware uploading for Atmel AVR development platform using
  Programmers <https://docs.platformio.org/page/platforms/atmelavr.html#upload-using-programmer>`_:
  AVR ISP, AVRISP mkII, USBtinyISP, USBasp, Parallel Programmer and Arduino as ISP
* Fixed issue with current Python interpreter for Python-based tools
  (`issue #417 <https://github.com/platformio/platformio-core/issue/417>`_)

2.6.3 (2015-12-21)
~~~~~~~~~~~~~~~~~~

* Restored support for Espressif ESP8266 ESP-01 1MB board (ready for OTA)
* Fixed invalid ROM size for ESP8266-based boards
  (`issue #396 <https://github.com/platformio/platformio-core/issues/396>`_)

2.6.2 (2015-12-21)
~~~~~~~~~~~~~~~~~~

* Removed ``SCons`` from requirements list. PlatformIO will try to install it
  automatically, otherwise users need to install it manually
* Fixed ``ChunkedEncodingError`` when SF connection is broken
  (`issue #356 <https://github.com/platformio/platformio-core/issues/356>`_)

2.6.1 (2015-12-18)
~~~~~~~~~~~~~~~~~~

* Added support for the new ESP8266-based boards (SparkFun ESP8266 Thing,
  NodeMCU 0.9 & 1.0, Olimex MOD-WIFI-ESP8266(-DEV), Adafruit HUZZAH ESP8266,
  ESPino, SweetPea ESP-210, WeMos D1, WeMos D1 mini) to
  `Espressif <https://docs.platformio.org/page/platforms/espressif.html>`__
  development platform
* Created public `platformio-pkg-ldscripts <https://github.com/platformio/platformio-pkg-ldscripts.git>`_
  repository for LD scripts. Moved common configuration for ESP8266 MCU to
  ``esp8266.flash.common.ld``
  (`issue #379 <https://github.com/platformio/platformio-core/issues/379>`_)
* Improved documentation for `Espressif <https://docs.platformio.org/page/platforms/espressif.html>`__
  development platform: OTA update, custom Flash Size, Upload Speed and CPU
  frequency
* Fixed reset method for Espressif NodeMCU (ESP-12E Module)
  (`issue #380 <https://github.com/platformio/platformio-core/issues/380>`_)
* Fixed issue with code builder when build path contains spaces
  (`issue #387 <https://github.com/platformio/platformio-core/issues/387>`_)
* Fixed project generator for Eclipse IDE and "duplicate path entries found
  in project path"
  (`issue #383 <https://github.com/platformio/platformio-core/issues/383>`_)


2.6.0 (2015-12-15)
~~~~~~~~~~~~~~~~~~

* Install only required packages depending on build environment
  (`issue #308 <https://github.com/platformio/platformio-core/issues/308>`_)
* Added support for Raspberry Pi `WiringPi <https://docs.platformio.org/page/frameworks/wiringpi.html>`__
  framework
  (`issue #372 <https://github.com/platformio/platformio-core/issues/372>`_)
* Implemented Over The Air (OTA) upgrades for `Espressif <https://docs.platformio.org/page/platforms/espressif.html>`__
  development platform.
  (`issue #365 <https://github.com/platformio/platformio-core/issues/365>`_)
* Updated `CMSIS framework <https://docs.platformio.org/page/frameworks/cmsis.html>`__
  and added CMSIS support for Nucleo F401RE board
  (`issue #373 <https://github.com/platformio/platformio-core/issues/373>`_)
* Added support for Espressif ESP8266 ESP-01-1MB board (ready for OTA)
* Handle ``upload_flags`` option in `platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #368 <https://github.com/platformio/platformio-core/issues/368>`_)
* Improved PlatformIO installation on the Mac OS X El Capitan

2.5.0 (2015-12-08)
~~~~~~~~~~~~~~~~~~

* Improved code builder for parallel builds (up to 4 times faster than before)
* Generate `.travis.yml <https://docs.platformio.org/page/ci/travis.html>`__
  CI and `.gitignore` files for embedded projects by default
  (`issue #354 <https://github.com/platformio/platformio-core/issues/354>`_)
* Removed prompt with "auto-uploading" from `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`__
  command and added ``--enable-auto-uploading`` option
  (`issue #352 <https://github.com/platformio/platformio-core/issues/352>`_)
* Fixed incorrect behaviour of `platformio serialports monitor <https://docs.platformio.org/page/userguide/cmd_serialports.html#platformio-serialports-monitor>`__
  in pair with PySerial 3.0

2.4.1 (2015-12-01)
~~~~~~~~~~~~~~~~~~

* Restored ``PLATFORMIO`` macros with the current version

2.4.0 (2015-12-01)
~~~~~~~~~~~~~~~~~~

* Added support for the new boards: Atmel ATSAMR21-XPRO, Atmel SAML21-XPRO-B,
  Atmel SAMD21-XPRO, ST 32F469IDISCOVERY, ST 32L476GDISCOVERY, ST Nucleo F031K6,
  ST Nucleo F042K6, ST Nucleo F303K8 and ST Nucleo L476RG
* Updated Arduino core for Espressif platform to 2.0.0
  (`issue #345 <https://github.com/platformio/platformio-core/issues/345>`_)
* Added to FAQ explanation of `Can not compile a library that compiles without issue
  with Arduino IDE <https://docs.platformio.org/page/faq.html#building>`_
  (`issue #331 <https://github.com/platformio/platformio-core/issues/331>`_)
* Fixed ESP-12E flash size
  (`pull #333 <https://github.com/platformio/platformio-core/pull/333>`_)
* Fixed configuration for LowPowerLab MoteinoMEGA board
  (`issue #335 <https://github.com/platformio/platformio-core/issues/335>`_)
* Fixed "LockFailed: failed to create appstate.json.lock" error for Windows
* Fixed relative include path for preprocessor using ``build_flags``
  (`issue #271 <https://github.com/platformio/platformio-core/issues/271>`_)

2.3.5 (2015-11-18)
~~~~~~~~~~~~~~~~~~

* Added support of `libOpenCM3 <https://docs.platformio.org/page/frameworks/libopencm3.html>`_
  framework for Nucleo F103RB board
  (`issue #309 <https://github.com/platformio/platformio-core/issues/309>`_)
* Added support for Espressif ESP8266 ESP-12E board (NodeMCU)
  (`issue #310 <https://github.com/platformio/platformio-core/issues/310>`_)
* Added support for pySerial 3.0
  (`issue #307 <https://github.com/platformio/platformio-core/issues/307>`_)
* Updated Arduino AVR/SAM frameworks to 1.6.6
  (`issue #321 <https://github.com/platformio/platformio-core/issues/321>`_)
* Upload firmware using external programmer via `platformio run --target program <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption-platformio-run-t>`__
  target
  (`issue #311 <https://github.com/platformio/platformio-core/issues/311>`_)
* Fixed handling of upload port when ``board`` option is not specified in
  `platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  (`issue #313 <https://github.com/platformio/platformio-core/issues/313>`_)
* Fixed firmware uploading for `nordicrf51 <https://docs.platformio.org/page/platforms/nordicnrf51.html>`__
  development platform
  (`issue #316 <https://github.com/platformio/platformio-core/issues/316>`_)
* Fixed installation on Mac OS X El Capitan
  (`issue #312 <https://github.com/platformio/platformio-core/issues/312>`_)
* Fixed project generator for CLion IDE under Windows OS with invalid path to
  executable
  (`issue #326 <https://github.com/platformio/platformio-core/issues/326>`_)
* Fixed empty list with serial ports on Mac OS X
  (`isge #294 <https://github.com/platformio/platformio-core/issues/294>`_)
* Fixed compilation error ``TWI_Disable not declared`` for Arduino Due board
  (`issue #329 <https://github.com/platformio/platformio-core/issues/329>`_)

2.3.4 (2015-10-13)
~~~~~~~~~~~~~~~~~~

* Full support of `CLion IDE <https://docs.platformio.org/page/ide/clion.html>`_
  including code auto-completion
  (`issue #132 <https://github.com/platformio/platformio-core/issues/132>`_)
* PlatformIO `command completion in Terminal <https://docs.platformio.org/page/faq.html#command-completion-in-terminal>`_ for ``bash`` and ``zsh``
* Added support for ubIQio Ardhat board
  (`pull #302 <https://github.com/platformio/platformio-core/pull/302>`_)
* Install SCons automatically and avoid ``error: option --single-version-externally-managed not recognized``
  (`issue #279 <https://github.com/platformio/platformio-core/issues/279>`_)
* Use Teensy CLI Loader for upload of .hex files on Mac OS X
  (`issue #306 <https://github.com/platformio/platformio-core/issues/306>`_)
* Fixed missing `framework-mbed <https://docs.platformio.org/page/frameworks/mbed.html>`_
  package for `teensy <https://docs.platformio.org/page/platforms/teensy.html>`_
  platform
  (`issue #305 <https://github.com/platformio/platformio-core/issues/305>`_)

2.3.3 (2015-10-02)
~~~~~~~~~~~~~~~~~~

* Added support for LightBlue Bean board
  (`pull #292 <https://github.com/platformio/platformio-core/pull/292>`_)
* Added support for ST Nucleo F446RE board
  (`pull #293 <https://github.com/platformio/platformio-core/pull/293>`_)
* Fixed broken lock file for "appstate" storage
  (`issue #288 <https://github.com/platformio/platformio-core/issues/288>`_)
* Fixed ESP8266 compile errors about RAM size when adding 1 library
  (`issue #296 <https://github.com/platformio/platformio-core/issues/296>`_)

2.3.2 (2015-09-10)
~~~~~~~~~~~~~~~~~~

* Allowed to use ST-Link uploader for mbed-based projects
* Explained how to use ``lib`` directory from the PlatformIO based project in
  ``readme.txt`` which will be automatically generated using
  `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`__
  command
  (`issue #273 <https://github.com/platformio/platformio-core/issues/273>`_)
* Found solution for "pip/scons error: option --single-version-externally-managed not
  recognized" when install PlatformIO using ``pip`` package manager
  (`issue #279 <https://github.com/platformio/platformio-core/issues/279>`_)
* Fixed firmware uploading to Arduino Leonardo board using Mac OS
  (`issue #287 <https://github.com/platformio/platformio-core/issues/287>`_)
* Fixed `SConsNotInstalled` error for Linux Debian-based distributives

2.3.1 (2015-09-06)
~~~~~~~~~~~~~~~~~~

* Fixed critical issue when `platformio init --ide <https://docs.platformio.org/page/userguide/cmd_init.html>`__ command hangs PlatformIO
  (`issue #283 <https://github.com/platformio/platformio-core/issues/283>`_)

2.3.0 (2015-09-05)
~~~~~~~~~~~~~~~~~~

* Added
  `native <https://docs.platformio.org/page/platforms/native.html>`__,
  `linux_arm <https://docs.platformio.org/page/platforms/linux_arm.html>`__,
  `linux_i686 <https://docs.platformio.org/page/platforms/linux_i686.html>`__,
  `linux_x86_64 <https://docs.platformio.org/page/platforms/linux_x86_64.html>`__,
  `windows_x86 <https://docs.platformio.org/page/platforms/windows_x86.html>`__
  development platforms
  (`issue #263 <https://github.com/platformio/platformio-core/issues/263>`_)
* Added `PlatformIO Demo <https://docs.platformio.org/page/userguide/demo.html>`_
  page to documentation
* Simplified `installation <https://docs.platformio.org/page/installation.html>`__
  process of PlatformIO
  (`issue #274 <https://github.com/platformio/platformio-core/issues/274>`_)
* Significantly improved `Project Generator <https://docs.platformio.org/page/userguide/cmd_init.html#cmdoption-platformio-init--ide>`__ which allows to integrate with `the most popular
  IDE <https://docs.platformio.org/page/ide.html>`__
* Added short ``-h`` help option for PlatformIO and sub-commands
* Updated `mbed <https://docs.platformio.org/page/frameworks/mbed.html>`__
  framework
* Updated ``tool-teensy`` package for `Teensy <https://docs.platformio.org/page/platforms/teensy.html>`__
  platform
  (`issue #268 <https://github.com/platformio/platformio-core/issues/268>`_)
* Added FAQ answer when `Program "platformio" not found in PATH <https://docs.platformio.org/page/faq.html#faq-troubleshooting-pionotfoundinpath>`_
  (`issue #272 <https://github.com/platformio/platformio-core/issues/272>`_)
* Generate "readme.txt" for project "lib" directory
  (`issue #273 <https://github.com/platformio/platformio-core/issues/273>`_)
* Use toolchain's includes pattern ``include*`` for Project Generator
  (`issue #277 <https://github.com/platformio/platformio-core/issues/277>`_)
* Added support for Adafruit Gemma board to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform
  (`pull #256 <https://github.com/platformio/platformio-core/pull/256>`_)
* Fixed includes list for Windows OS when generating project for `Eclipse IDE <https://docs.platformio.org/page/ide/eclipse.html>`__
  (`issue #270 <https://github.com/platformio/platformio-core/issues/270>`_)
* Fixed ``AttributeError: 'module' object has no attribute 'packages'``
  (`issue #252 <https://github.com/platformio/platformio-core/issues/252>`_)

2.2.2 (2015-07-30)
~~~~~~~~~~~~~~~~~~

* Integration with `Atom IDE <https://docs.platformio.org/page/ide/atom.html>`__
* Support for off-line/unpublished/private libraries
  (`issue #260 <https://github.com/platformio/platformio-core/issues/260>`_)
* Disable project auto-clean while building/uploading firmware using
  `platformio run --disable-auto-clean <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption--disable-auto-clean>`_ option
  (`issue #255 <https://github.com/platformio/platformio-core/issues/255>`_)
* Show internal errors from "Miniterm" using `platformio serialports monitor <https://docs.platformio.org/page/userguide/cmd_serialports.html#platformio-serialports-monitor>`__ command
  (`issue #257 <https://github.com/platformio/platformio-core/issues/257>`_)
* Fixed `platformio serialports monitor --help <https://docs.platformio.org/page/userguide/cmd_serialports.html#platformio-serialports-monitor>`__ information with HEX char for hotkeys
  (`issue #253 <https://github.com/platformio/platformio-core/issues/253>`_)
* Handle "OSError: [Errno 13] Permission denied" for PlatformIO installer script
  (`issue #254 <https://github.com/platformio/platformio-core/issues/254>`_)

2.2.1 (2015-07-17)
~~~~~~~~~~~~~~~~~~

* Project generator for `CLion IDE <https://docs.platformio.org/page/ide/clion.html>`__
  (`issue #132 <https://github.com/platformio/platformio-core/issues/132>`_)
* Updated ``tool-bossac`` package to 1.5 version for `atmelsam <https://docs.platformio.org/page/platforms/atmelsam.html>`__ platform
  (`issue #251 <https://github.com/platformio/platformio-core/issues/251>`_)
* Updated ``sdk-esp8266`` package for `espressif <https://docs.platformio.org/page/platforms/espressif.html>`__ platform
* Fixed incorrect arguments handling for `platformio serialports monitor <https://docs.platformio.org/page/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ command
  (`issue #248 <https://github.com/platformio/platformio-core/issues/248>`_)

2.2.0 (2015-07-01)
~~~~~~~~~~~~~~~~~~

* Allowed to exclude/include source files from build process using
  `src_filter <https://docs.platformio.org/page/projectconf/section_env_build.html#src-filter>`__
  (`issue #240 <https://github.com/platformio/platformio-core/issues/240>`_)
* Launch own extra script before firmware building/uploading processes
  (`issue #239 <https://github.com/platformio/platformio-core/issues/239>`_)
* Specify own path to the linker script (ld) using
  `build_flags <https://docs.platformio.org/page/projectconf/section_env_build.html#build-flags>`__
  option
  (`issue #233 <https://github.com/platformio/platformio-core/issues/233>`_)
* Specify library compatibility with the all platforms/frameworks
  using ``*`` symbol in
  `library.json <https://docs.platformio.org/page/librarymanager/config.html>`__
* Added support for new embedded boards: *ST 32L0538DISCOVERY and Delta DFCM-NNN40*
  to `Framework mbed <https://docs.platformio.org/page/frameworks/mbed.html>`__
* Updated packages for
  `Framework Arduino (AVR, SAM, Espressif and Teensy cores <https://docs.platformio.org/page/frameworks/arduino.html>`__,
  `Framework mbed <https://docs.platformio.org/page/frameworks/mbed.html>`__,
  `Espressif ESP8266 SDK <https://docs.platformio.org/page/platforms/espressif.html>`__
  (`issue #246 <https://github.com/platformio/platformio-core/issues/246>`_)
* Fixed ``stk500v2_command(): command failed``
  (`issue #238 <https://github.com/platformio/platformio-core/issues/238>`_)
* Fixed IDE project generator when board is specified
  (`issue #242 <https://github.com/platformio/platformio-core/issues/242>`_)
* Fixed relative path for includes when generating project for IDE
  (`issue #243 <https://github.com/platformio/platformio-core/issues/243>`_)
* Fixed ESP8266 native SDK exception
  (`issue #245 <https://github.com/platformio/platformio-core/issues/245>`_)

2.1.2 (2015-06-21)
~~~~~~~~~~~~~~~~~~

* Fixed broken link to SCons installer

2.1.1 (2015-06-09)
~~~~~~~~~~~~~~~~~~

* Automatically detect upload port using VID:PID board settings
  (`issue #231 <https://github.com/platformio/platformio-core/issues/231>`_)
* Improved detection of build changes
* Avoided ``LibInstallDependencyError`` when more than 1 library is found
  (`issue #229 <https://github.com/platformio/platformio-core/issues/229>`_)

2.1.0 (2015-06-03)
~~~~~~~~~~~~~~~~~~

* Added Silicon Labs EFM32 `siliconlabsefm32 <https://docs.platformio.org/page/platforms/siliconlabsefm32.html>`_
  development platform
  (`issue #226 <https://github.com/platformio/platformio-core/issues/226>`_)
* Integrate PlatformIO with `Circle CI <https://circleci.com>`_ and
  `Shippable CI <https://www.shippable.com/>`_
* Described in documentation how to `create/register own board <https://docs.platformio.org/page/platforms/creating_board.html>`_ for PlatformIO
* Disabled "nano.specs" for ARM-based platforms
  (`issue #219 <https://github.com/platformio/platformio-core/issues/219>`_)
* Fixed "ConnectionError" when PlatformIO SF Storage is off-line
* Fixed resolving of C/C++ std libs by Eclipse IDE
  (`issue #220 <https://github.com/platformio/platformio-core/issues/220>`_)
* Fixed firmware uploading using USB programmer (USBasp) for
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html>`_
  platform
  (`issue #221 <https://github.com/platformio/platformio-core/issues/221>`_)

2.0.2 (2015-05-27)
~~~~~~~~~~~~~~~~~~

* Fixed libraries order for "Library Dependency Finder" under Linux OS

2.0.1 (2015-05-27)
~~~~~~~~~~~~~~~~~~

* Handle new environment variable
  `PLATFORMIO_BUILD_FLAGS <https://docs.platformio.org/page/envvars.html#platformio-build-flags>`_
* Pass to API requests information about Continuous Integration system. This
  information will be used by PlatformIO-API.
* Use ``include`` directories from toolchain when initialising project for IDE
  (`issue #210 <https://github.com/platformio/platformio-core/issues/210>`_)
* Added support for new WildFire boards from
  `Wicked Device <http://wickeddevice.com>`_ to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform
* Updated `Arduino Framework <https://docs.platformio.org/page/frameworks/arduino.html>`__ to
  1.6.4 version (`issue #212 <https://github.com/platformio/platformio-core/issues/212>`_)
* Handle Atmel AVR Symbols when initialising project for IDE
  (`issue #216 <https://github.com/platformio/platformio-core/issues/216>`_)
* Fixed bug with converting ``*.ino`` to ``*.cpp``
* Fixed failing with ``platformio init --ide eclipse`` without boards
  (`issue #217 <https://github.com/platformio/platformio-core/issues/217>`_)

2.0.0 (2015-05-22)
~~~~~~~~~~~~~~~~~~

*Made in* `Paradise <https://twitter.com/ikravets/status/592356377185619969>`_

* PlatformIO as `Continuous Integration <https://docs.platformio.org/page/ci/index.html>`_
  (CI) tool for embedded projects
  (`issue #108 <https://github.com/platformio/platformio-core/issues/108>`_)
* Initialise PlatformIO project for the specified IDE
  (`issue #151 <https://github.com/platformio/platformio-core/issues/151>`_)
* PlatformIO CLI 2.0: "platform" related commands have been
  moved to ``platformio platforms`` subcommand
  (`issue #158 <https://github.com/platformio/platformio-core/issues/158>`_)
* Created `PlatformIO gitter.im <https://gitter.im/platformio/platformio>`_ room
  (`issue #174 <https://github.com/platformio/platformio-core/issues/174>`_)
* Global ``-f, --force`` option which will force to accept any
  confirmation prompts
  (`issue #152 <https://github.com/platformio/platformio-core/issues/152>`_)
* Run project with `platformio run --project-dir <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption--project-dir>`_ option without changing the current working
  directory
  (`issue #192 <https://github.com/platformio/platformio-core/issues/192>`_)
* Control verbosity of `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption-platformio-run-v>`_ command via ``-v/--verbose`` option
* Add library dependencies for build environment using
  `lib_install <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-deps>`_
  option in ``platformio.ini``
  (`issue #134 <https://github.com/platformio/platformio-core/issues/134>`_)
* Specify libraries which are compatible with build environment using
  `lib_use <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-deps>`_
  option in ``platformio.ini``
  (`issue #148 <https://github.com/platformio/platformio-core/issues/148>`_)
* Add more boards to PlatformIO project with
  `platformio init --board <https://docs.platformio.org/page/userguide/cmd_init.html#cmdoption--board>`__
  command
  (`issue #167 <https://github.com/platformio/platformio-core/issues/167>`_)
* Choose which library to update
  (`issue #168 <https://github.com/platformio/platformio-core/issues/168>`_)
* Specify `platformio init --env-prefix <https://docs.platformio.org/page/userguide/cmd_init.html#cmdoption--env-prefix>`__ when initialise/update project
  (`issue #182 <https://github.com/platformio/platformio-core/issues/182>`_)
* Added new Armstrap boards
  (`issue #204 <https://github.com/platformio/platformio-core/issues/204>`_)
* Updated SDK for `espressif <https://docs.platformio.org/page/platforms/espressif.html>`__
  development platform to v1.1
  (`issue #179 <https://github.com/platformio/platformio-core/issues/179>`_)
* Disabled automatic updates by default for platforms, packages and libraries
  (`issue #171 <https://github.com/platformio/platformio-core/issues/171>`_)
* Fixed bug with creating copies of source files
  (`issue #177 <https://github.com/platformio/platformio-core/issues/177>`_)

PlatformIO 1.0
--------------

1.5.0 (2015-05-15)
~~~~~~~~~~~~~~~~~~

* Added support of `Framework mbed <https://platformio.org/frameworks/mbed>`_
  for Teensy 3.1
  (`issue #183 <https://github.com/platformio/platformio-core/issues/183>`_)
* Added GDB as alternative uploader to `ststm32 <https://docs.platformio.org/page/platforms/ststm32.html>`__ platform
  (`issue #175 <https://github.com/platformio/platformio-core/issues/174>`_)
* Added `examples <https://github.com/platformio/platformio-examples/tree/develop>`__
  with preconfigured IDE projects
  (`issue #154 <https://github.com/platformio/platformio-core/issues/154>`_)
* Fixed firmware uploading under Linux OS for Arduino Leonardo board
  (`issue #178 <https://github.com/platformio/platformio-core/issues/178>`_)
* Fixed invalid "mbed" firmware for Nucleo F411RE
  (`issue #185 <https://github.com/platformio/platformio-core/issues/185>`_)
* Fixed parsing of includes for PlatformIO Library Dependency Finder
  (`issue #189 <https://github.com/platformio/platformio-core/issues/189>`_)
* Fixed handling symbolic links within source code directory
  (`issue #190 <https://github.com/platformio/platformio-core/issues/190>`_)
* Fixed cancelling any previous definition of name, either built in or provided
  with a ``-D`` option
  (`issue #191 <https://github.com/platformio/platformio-core/issues/191>`_)

1.4.0 (2015-04-11)
~~~~~~~~~~~~~~~~~~

* Added `espressif <https://docs.platformio.org/page/platforms/espressif.html>`_
  development platform with ESP01 board
* Integrated PlatformIO with AppVeyor Windows based Continuous Integration system
  (`issue #149 <https://github.com/platformio/platformio-core/issues/149>`_)
* Added support for Teensy LC board to
  `teensy <https://docs.platformio.org/page/platforms/teensy.html>`__
  platform
* Added support for new Arduino based boards by *SparkFun, BQ, LightUp,
  LowPowerLab, Quirkbot, RedBearLab, TinyCircuits* to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform
* Upgraded `Arduino Framework <https://docs.platformio.org/page/frameworks/arduino.html>`__ to
  1.6.3 version (`issue #156 <https://github.com/platformio/platformio-core/issues/156>`_)
* Upgraded `Energia Framework <https://docs.platformio.org/page/frameworks/energia.html>`__ to
  0101E0015 version (`issue #146 <https://github.com/platformio/platformio-core/issues/146>`_)
* Upgraded `Arduino Framework with Teensy Core <https://docs.platformio.org/page/frameworks/arduino.html>`_
  to 1.22 version
  (`issue #162 <https://github.com/platformio/platformio-core/issues/162>`_,
  `issue #170 <https://github.com/platformio/platformio-core/issues/170>`_)
* Fixed exceptions with PlatformIO auto-updates when Internet connection isn't
  active


1.3.0 (2015-03-27)
~~~~~~~~~~~~~~~~~~

* Moved PlatformIO source code and repositories from `Ivan Kravets <https://github.com/ivankravets>`_
  account to `PlatformIO Organisation <https://github.com/platformio>`_
  (`issue #138 <https://github.com/platformio/platformio-core/issues/138>`_)
* Added support for new Arduino based boards by *SparkFun, RepRap, Sanguino* to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform
  (`issue #127 <https://github.com/platformio/platformio-core/issues/127>`_,
  `issue #131 <https://github.com/platformio/platformio-core/issues/131>`_)
* Added integration instructions for `Visual Studio <https://docs.platformio.org/page/ide/visualstudio.html>`_
  and `Sublime Text <https://docs.platformio.org/page/ide/sublimetext.html>`_ IDEs
* Improved handling of multi-file ``*.ino/pde`` sketches
  (`issue #130 <https://github.com/platformio/platformio-core/issues/130>`_)
* Fixed wrong insertion of function prototypes converting ``*.ino/pde``
  (`issue #137 <https://github.com/platformio/platformio-core/issues/137>`_,
  `issue #140 <https://github.com/platformio/platformio-core/issues/140>`_)



1.2.0 (2015-03-20)
~~~~~~~~~~~~~~~~~~

* Added full support of `mbed <https://docs.platformio.org/page/frameworks/mbed.html>`__
  framework including libraries: *RTOS, Ethernet, DSP, FAT, USB*.
* Added `freescalekinetis <https://docs.platformio.org/page/platforms/freescalekinetis.html>`_
  development platform with Freescale Kinetis Freedom boards
* Added `nordicnrf51 <https://docs.platformio.org/page/platforms/nordicnrf51.html>`_
  development platform with supported boards from *JKSoft, Nordic, RedBearLab,
  Switch Science*
* Added `nxplpc <https://docs.platformio.org/page/platforms/nxplpc.html>`_
  development platform with supported boards from *CQ Publishing, Embedded
  Artists, NGX Technologies, NXP, Outrageous Circuits, SeeedStudio,
  Solder Splash Labs, Switch Science, u-blox*
* Added support for *ST Nucleo* boards to
  `ststm32 <https://docs.platformio.org/page/platforms/ststm32.html>`__
  development platform
* Created new `Frameworks <https://docs.platformio.org/page/frameworks/index.html>`__
  page in documentation and added to `PlatformIO Web Site <https://platformio.org>`_
  (`issue #115 <https://github.com/platformio/platformio-core/issues/115>`_)
* Introduced online `Embedded Boards Explorer <https://platformio.org/boards>`_
* Automatically append define ``-DPLATFORMIO=%version%`` to
  builder (`issue #105 <https://github.com/platformio/platformio-core/issues/105>`_)
* Renamed ``stm32`` development platform to
  `ststm32 <https://docs.platformio.org/page/platforms/ststm32.html>`__
* Renamed ``opencm3`` framework to
  `libopencm3 <https://docs.platformio.org/page/frameworks/libopencm3.html>`__
* Fixed uploading for `atmelsam <https://docs.platformio.org/page/platforms/atmelsam.html>`__
  development platform
* Fixed re-arranging the ``*.ino/pde`` files when converting to ``*.cpp``
  (`issue #100 <https://github.com/platformio/platformio-core/issues/100>`_)

1.1.0 (2015-03-05)
~~~~~~~~~~~~~~~~~~

* Implemented ``PLATFORMIO_*`` environment variables
  (`issue #102 <https://github.com/platformio/platformio-core/issues/102>`_)
* Added support for *SainSmart* boards to
  `atmelsam <https://docs.platformio.org/page/platforms/atmelsam.html#boards>`__
  development platform
* Added
  `Project Configuration <https://docs.platformio.org/page/projectconf.html>`__
  option named `envs_dir <https://docs.platformio.org/page/projectconf/section_platformio.html#envs-dir>`__
* Disabled "prompts" automatically for *Continuous Integration* systems
  (`issue #103 <https://github.com/platformio/platformio-core/issues/103>`_)
* Fixed firmware uploading for
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  boards which work within ``usbtiny`` protocol
* Fixed uploading for *Digispark* board (`issue #106 <https://github.com/platformio/platformio-core/issues/106>`_)

1.0.1 (2015-02-27)
~~~~~~~~~~~~~~~~~~

**PlatformIO 1.0 - recommended for production**

* Changed development status from ``beta`` to ``Production/Stable``
* Added support for *ARM*-based credit-card sized computers:
  `Raspberry Pi <http://www.raspberrypi.org>`_,
  `BeagleBone <http://beagleboard.org>`_ and `CubieBoard <http://cubieboard.org>`_
* Added `atmelsam <https://docs.platformio.org/page/platforms/atmelsam.html>`__
  development platform with supported boards: *Arduino Due and Digistump DigiX*
  (`issue #71 <https://github.com/platformio/platformio-core/issues/71>`_)
* Added `ststm32 <https://docs.platformio.org/page/platforms/ststm32.html>`__
  development platform with supported boards: *Discovery kit for STM32L151/152,
  STM32F303xx, STM32F407/417 lines* and `libOpenCM3 Framework <http://www.libopencm3.org>`_
  (`issue #73 <https://github.com/platformio/platformio-core/issues/73>`_)
* Added `teensy <https://docs.platformio.org/page/platforms/teensy.html>`_
  development platform with supported boards: *Teensy 2.x & 3.x*
  (`issue #72 <https://github.com/platformio/platformio-core/issues/72>`_)
* Added new *Arduino* boards to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform: *Arduino NG, Arduino BT, Arduino Esplora, Arduino Ethernet,
  Arduino Robot Control, Arduino Robot Motor and Arduino Yun*
* Added support for *Adafruit* boards to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform: *Adafruit Flora and Adafruit Trinkets*
  (`issue #65 <https://github.com/platformio/platformio-core/issues/65>`_)
* Added support for *Digispark* boards to
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#boards>`__
  platform: *Digispark USB Development Board and Digispark Pro*
  (`issue #47 <https://github.com/platformio/platformio-core/issues/47>`_)
* Covered code with tests (`issue #2 <https://github.com/platformio/platformio-core/issues/2>`_)
* Refactored *Library Dependency Finder* (issues
  `#48 <https://github.com/platformio/platformio-core/issues/48>`_,
  `#50 <https://github.com/platformio/platformio-core/issues/50>`_,
  `#55 <https://github.com/platformio/platformio-core/pull/55>`_)
* Added `src_dir <https://docs.platformio.org/page/projectconf/section_platformio.html#src-dir>`__
  option to ``[platformio]`` section of
  `platformio.ini <https://docs.platformio.org/page/projectconf.html>`__
  which allows to redefine location to project's source directory
  (`issue #83 <https://github.com/platformio/platformio-core/issues/83>`_)
* Added ``--json-output`` option to
  `platformio boards <https://docs.platformio.org/page/userguide/cmd_boards.html>`__
  and `platformio search <https://docs.platformio.org/page/userguide/platforms/cmd_search.html>`__
  commands which allows to return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format
  (`issue #42 <https://github.com/platformio/platformio-core/issues/42>`_)
* Allowed to ignore some libs from *Library Dependency Finder* via
  `lib_ignore <https://docs.platformio.org/page/projectconf/section_env_library.html#lib-ignore>`_ option
* Improved `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__
  command: asynchronous output for build process, timing and detailed
  information about environment configuration
  (`issue #74 <https://github.com/platformio/platformio-core/issues/74>`_)
* Output compiled size and static memory usage with
  `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__
  command (`issue #59 <https://github.com/platformio/platformio-core/issues/59>`_)
* Updated `framework-arduino` AVR & SAM to 1.6 stable version
* Fixed an issue with the libraries that are git repositories
  (`issue #49 <https://github.com/platformio/platformio-core/issues/49>`_)
* Fixed handling of assembly files
  (`issue #58 <https://github.com/platformio/platformio-core/issues/58>`_)
* Fixed compiling error if space is in user's folder
  (`issue #56 <https://github.com/platformio/platformio-core/issues/56>`_)
* Fixed `AttributeError: 'module' object has no attribute 'disable_warnings'`
  when a version of `requests` package is less then 2.4.0
* Fixed bug with invalid process's "return code" when PlatformIO has internal
  error (`issue #81 <https://github.com/platformio/platformio-core/issues/81>`_)
* Several bug fixes, increased stability and performance improvements

PlatformIO 0.0
--------------

0.10.2 (2015-01-06)
~~~~~~~~~~~~~~~~~~~

* Fixed an issue with ``--json-output``
  (`issue #42 <https://github.com/platformio/platformio-core/issues/42>`_)
* Fixed an exception during
  `platformio upgrade <https://docs.platformio.org/page/userguide/cmd_upgrade.html>`__
  under Windows OS (`issue #45 <https://github.com/platformio/platformio-core/issues/45>`_)

0.10.1 (2015-01-02)
~~~~~~~~~~~~~~~~~~~

* Added ``--json-output`` option to
  `platformio list <https://docs.platformio.org/page/userguide/platforms/cmd_list.htmll>`__,
  `platformio serialports list <https://docs.platformio.org/page/userguide/cmd_serialports.html>`__ and
  `platformio lib list <https://docs.platformio.org/page/userguide/lib/cmd_list.html>`__
  commands which allows to return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format
  (`issue #42 <https://github.com/platformio/platformio-core/issues/42>`_)
* Fixed missing auto-uploading by default after `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`__
  command

0.10.0 (2015-01-01)
~~~~~~~~~~~~~~~~~~~

**Happy New Year!**

* Implemented `platformio boards <https://docs.platformio.org/page/userguide/cmd_boards.html>`_
  command (`issue #11 <https://github.com/platformio/platformio-core/issues/11>`_)
* Added support of *Engduino* boards for
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html#engduino>`__
  platform (`issue #38 <https://github.com/platformio/platformio-core/issues/38>`_)
* Added ``--board`` option to `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`__
  command which allows to initialise project with the specified embedded boards
  (`issue #21 <https://github.com/platformio/platformio-core/issues/21>`_)
* Added `example with uploading firmware <https://docs.platformio.org/page/projectconf.html#examples>`_
  via USB programmer (USBasp) for
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html>`_
  *MCUs* (`issue #35 <https://github.com/platformio/platformio-core/issues/35>`_)
* Automatic detection of port on `platformio serialports monitor <https://docs.platformio.org/page/userguide/cmd_serialports.html#platformio-serialports-monitor>`_
  (`issue #37 <https://github.com/platformio/platformio-core/issues/37>`_)
* Allowed auto-installation of platforms when prompts are disabled (`issue #43 <https://github.com/platformio/platformio-core/issues/43>`_)
* Fixed urllib3's *SSL* warning under Python <= 2.7.2 (`issue #39 <https://github.com/platformio/platformio-core/issues/39>`_)
* Fixed bug with *Arduino USB* boards (`issue #40 <https://github.com/platformio/platformio-core/issues/40>`_)

0.9.2 (2014-12-10)
~~~~~~~~~~~~~~~~~~

* Replaced "dark blue" by "cyan" colour for the texts (`issue #33 <https://github.com/platformio/platformio-core/issues/33>`_)
* Added new setting ``enable_prompts`` and allowed to disable all *PlatformIO* prompts (useful for cloud compilers)
  (`issue #34 <https://github.com/platformio/platformio-core/issues/34>`_)
* Fixed compilation bug on *Windows* with installed *MSVC* (`issue #18 <https://github.com/platformio/platformio-core/issues/18>`_)

0.9.1 (2014-12-05)
~~~~~~~~~~~~~~~~~~

* Ask user to install platform (when it hasn't been installed yet) within
  `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__
  and `platformio show <https://docs.platformio.org/page/userguide/platforms/cmd_show.html>`_ commands
* Improved main `documentation <https://docs.platformio.org>`_
* Fixed "*OSError: [Errno 2] No such file or directory*" within
  `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html>`__
  command when PlatformIO isn't installed properly
* Fixed example for Eclipse IDE with Tiva board
  (`issue #32 <https://github.com/platformio/platformio-core/pull/32>`_)
* Upgraded Eclipse Project Examples
  to latest *Luna* and *PlatformIO* releases

0.9.0 (2014-12-01)
~~~~~~~~~~~~~~~~~~

* Implemented `platformio settings <https://docs.platformio.org/page/userguide/cmd_settings.html>`_ command
* Improved `platformio init <https://docs.platformio.org/page/userguide/cmd_init.html>`_ command.
  Added new option ``--project-dir`` where you can specify another path to
  directory where new project will be initialized (`issue #31 <https://github.com/platformio/platformio-core/issues/31>`_)
* Added *Migration Manager* which simplifies process with upgrading to a
  major release
* Added *Telemetry Service* which should help us make *PlatformIO* better
* Implemented *PlatformIO AppState Manager* which allow to have multiple
  ``.platformio`` states.
* Refactored *Package Manager*
* Download Manager: fixed SHA1 verification within *Cygwin Environment*
  (`issue #26 <https://github.com/platformio/platformio-core/issues/26>`_)
* Fixed bug with code builder and built-in Arduino libraries
  (`issue #28 <https://github.com/platformio/platformio-core/issues/28>`_)

0.8.0 (2014-10-19)
~~~~~~~~~~~~~~~~~~

* Avoided trademark issues in `library.json <https://docs.platformio.org/page/librarymanager/config.html>`_
  with the new fields: `frameworks <https://docs.platformio.org/page/librarymanager/config.html#frameworks>`_,
  `platforms <https://docs.platformio.org/page/librarymanager/config.html#platforms>`_
  and `dependencies <https://docs.platformio.org/page/librarymanager/config.html#dependencies>`_
  (`issue #17 <https://github.com/platformio/platformio-core/issues/17>`_)
* Switched logic from "Library Name" to "Library Registry ID" for all
  `platformio lib <https://docs.platformio.org/page/userguide/lib/index.html>`_
  commands (install, uninstall, update and etc.)
* Renamed ``author`` field to `authors <https://docs.platformio.org/page/librarymanager/config.html#authors>`_
  and allowed to setup multiple authors per library in `library.json <https://docs.platformio.org/page/librarymanager/config.html>`_
* Added option to specify "maintainer" status in `authors <https://docs.platformio.org/page/librarymanager/config.html#authors>`_ field
* New filters/options for `platformio lib search <https://docs.platformio.org/page/userguide/lib/cmd_search.html>`_
  command: ``--framework`` and ``--platform``

0.7.1 (2014-10-06)
~~~~~~~~~~~~~~~~~~

* Fixed bug with order for includes in conversation from INO/PDE to CPP
* Automatic detection of port on upload (`issue #15 <https://github.com/platformio/platformio-core/issues/15>`_)
* Fixed lib update crashing when no libs are installed (`issue #19 <https://github.com/platformio/platformio-core/issues/19>`_)


0.7.0 (2014-09-24)
~~~~~~~~~~~~~~~~~~

* Implemented new `[platformio] <https://docs.platformio.org/page/projectconf.html#platformio>`_
  section for Configuration File with `home_dir <https://docs.platformio.org/page/projectconf.html#home-dir>`_
  option (`issue #14 <https://github.com/platformio/platformio-core/issues/14>`_)
* Implemented *Library Manager* (`issue #6 <https://github.com/platformio/platformio-core/issues/6>`_)

0.6.0 (2014-08-09)
~~~~~~~~~~~~~~~~~~

* Implemented `platformio serialports monitor <https://docs.platformio.org/page/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ (`issue #10 <https://github.com/platformio/platformio-core/issues/10>`_)
* Fixed an issue ``ImportError: No module named platformio.util`` (`issue #9 <https://github.com/platformio/platformio-core/issues/9>`_)
* Fixed bug with auto-conversation from Arduino \*.ino to \*.cpp

0.5.0 (2014-08-04)
~~~~~~~~~~~~~~~~~~

* Improved nested lookups for libraries
* Disabled default warning flag "-Wall"
* Added auto-conversation from \*.ino to valid \*.cpp for Arduino/Energia
  frameworks (`issue #7 <https://github.com/platformio/platformio-core/issues/7>`_)
* Added `Arduino example <https://github.com/platformio/platformio-examples/tree/develop/>`_
  with external library (*Adafruit CC3000*)
* Implemented `platformio upgrade <https://docs.platformio.org/page/userguide/cmd_upgrade.html>`_
  command and "auto-check" for the latest
  version (`issue #8 <https://github.com/platformio/platformio-core/issues/8>`_)
* Fixed an issue with "auto-reset" for *Raspduino* board
* Fixed a bug with nested libs building

0.4.0 (2014-07-31)
~~~~~~~~~~~~~~~~~~

* Implemented `platformio serialports <https://docs.platformio.org/page/userguide/cmd_serialports.html>`_ command
* Allowed to put special build flags only for ``src`` files via
  `src_build_flags <https://docs.platformio.org/page/projectconf.html#src_build-flags>`_
  environment option
* Allowed to override some of settings via system environment variables
  such as: ``PLATFORMIO_SRC_BUILD_FLAGS`` and ``PLATFORMIO_ENVS_DIR``
* Added ``--upload-port`` option for `platformio run <https://docs.platformio.org/page/userguide/cmd_run.html#cmdoption--upload-port>`__ command
* Implemented (especially for `SmartAnthill <http://docs.smartanthill.ikravets.com/>`_)
  `platformio run -t uploadlazy <https://docs.platformio.org/page/userguide/cmd_run.html>`_
  target (no dependencies to framework libs, ELF and etc.)
* Allowed to skip default packages via `platformio install --skip-default-package <https://docs.platformio.org/page/userguide/platforms/cmd_install.html#cmdoption-platformio-platform-install-skip-default>`_
  option
* Added tools for *Raspberry Pi* platform
* Added support for *Microduino* and *Raspduino* boards in
  `atmelavr <https://docs.platformio.org/page/platforms/atmelavr.html>`_ platform

0.3.1 (2014-06-21)
~~~~~~~~~~~~~~~~~~

* Fixed auto-installer for Windows OS (bug with %PATH% custom installation)


0.3.0 (2014-06-21)
~~~~~~~~~~~~~~~~~~

* Allowed to pass multiple "SomePlatform" to install/uninstall commands
* Added "IDE Integration" section to README with Eclipse project examples
* Created auto installer script for *PlatformIO* (`issue #3 <https://github.com/platformio/platformio-core/issues/3>`_)
* Added "Super-Quick" way to Installation section (README)
* Implemented "build_flags" option for environments (`issue #4 <https://github.com/platformio/platformio-core/issues/4>`_)


0.2.0 (2014-06-15)
~~~~~~~~~~~~~~~~~~

* Resolved `issue #1 "Build referred libraries" <https://github.com/platformio/platformio-core/issues/1>`_
* Renamed project's "libs" directory to "lib"
* Added `arduino-internal-library <https://github.com/platformio/platformio-examples/tree/develop/>`_ example
* Changed to beta status


0.1.0 (2014-06-13)
~~~~~~~~~~~~~~~~~~

* Birth! First alpha release
