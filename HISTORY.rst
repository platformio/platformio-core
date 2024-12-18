Release Notes
=============

.. |PIOCONF| replace:: `"platformio.ini" <https://docs.platformio.org/en/latest/projectconf.html>`__ configuration file
.. |LIBRARYJSON| replace:: `library.json <https://docs.platformio.org/en/latest/manifests/library-json/index.html>`__
.. |LDF| replace:: `LDF <https://docs.platformio.org/en/latest/librarymanager/ldf.html>`__
.. |INTERPOLATION| replace:: `Interpolation of Values <https://docs.platformio.org/en/latest/projectconf/interpolation.html>`__
.. |UNITTESTING| replace:: `Unit Testing <https://docs.platformio.org/en/latest/advanced/unit-testing/index.html>`__
.. |DEBUGGING| replace:: `Debugging <https://docs.platformio.org/en/latest/plus/debugging.html>`__
.. |STATICCODEANALYSIS| replace:: `Static Code Analysis <https://docs.platformio.org/en/latest/advanced/static-code-analysis/index.html>`__

.. _release_notes_6:

PlatformIO Core 6
-----------------

Unlock the true potential of embedded software development with
PlatformIO's collaborative ecosystem, embracing declarative principles,
test-driven methodologies, and modern toolchains for unrivaled success.

6.1.17 (2024-??-??)
~~~~~~~~~~~~~~~~~~~

* Added support for ``tar.xz`` tarball dependencies (`pull #4974 <https://github.com/platformio/platformio-core/pull/4974>`_)
* Ensured that dependencies of private libraries are no longer unnecessarily re-installed, optimizing dependency management and reducing redundant operations (`issue #4987 <https://github.com/platformio/platformio-core/issues/4987>`_)
* Resolved an issue where the ``compiledb`` target failed to properly escape compiler executable paths containing spaces (`issue #4998 <https://github.com/platformio/platformio-core/issues/4998>`_)
* Resolved an issue with incorrect path resolution when linking static libraries via the `build_flags <https://docs.platformio.org/en/latest/projectconf/sections/env/options/build/build_flags.html>`__ option (`issue #5004 <https://github.com/platformio/platformio-core/issues/5004>`_)
* Resolved an issue where the ``--project-dir`` flag did not function correctly with the `pio check <https://docs.platformio.org/en/latest/core/userguide/cmd_check.html>`__ and `pio debug <https://docs.platformio.org/en/latest/core/userguide/cmd_debug.html>`__ commands (`issue #5029 <https://github.com/platformio/platformio-core/issues/5029>`_)
* Resolved an issue where the |LDF| occasionally excluded bundled platform libraries from the dependency graph (`pull #4941 <https://github.com/platformio/platformio-core/pull/4941>`_)

6.1.16 (2024-09-26)
~~~~~~~~~~~~~~~~~~~

* Added support for Python 3.13
* Introduced the `PLATFORMIO_SYSTEM_TYPE <https://docs.platformio.org/en/latest/envvars.html#envvar-PLATFORMIO_SYSTEM_TYPE>`__ environment variable, enabling manual override of the detected system type for greater flexibility and control in custom build environments
* Enhanced internet connection checks by falling back to HTTPS protocol when HTTP (port 80) fails (`issue #4980 <https://github.com/platformio/platformio-core/issues/4980>`_)
* Upgraded the build engine to the latest version of SCons (4.8.1) to improve build performance, reliability, and compatibility with other tools and systems (`release notes <https://github.com/SCons/scons/releases/tag/4.8.1>`__)
* Upgraded the `Doctest <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/doctest.html>`__ testing framework to version 2.4.11, the `GoogleTest <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/doctest.html>`__ to version 1.15.2, and the `Unity <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/unity.html>`__ to version 2.6.0, incorporating the latest features and improvements for enhanced testing capabilities
* Corrected an issue where the incorrect public class was imported for the ``DoctestTestRunner`` (`issue #4949 <https://github.com/platformio/platformio-core/issues/4949>`_)

6.1.15 (2024-04-25)
~~~~~~~~~~~~~~~~~~~

* Resolved an issue where the |LDF| couldn't locate a library dependency declared via version control system repository (`issue #4885 <https://github.com/platformio/platformio-core/issues/4885>`_)
* Resolved an issue related to the inaccurate detection of the Clang compiler (`pull #4897 <https://github.com/platformio/platformio-core/pull/4897>`_)

6.1.14 (2024-03-21)
~~~~~~~~~~~~~~~~~~~

* Introduced the ``--json-output`` option to the `pio test <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html>`__ command, enabling users to generate test results in the JSON format
* Upgraded the build engine to the latest version of SCons (4.7.0) to improve build performance, reliability, and compatibility with other tools and systems (`release notes <https://github.com/SCons/scons/releases/tag/4.7.0>`__)
* Broadened version support for the ``pyelftools`` dependency, enabling compatibility with lower versions and facilitating integration with a wider range of third-party tools (`issue #4834 <https://github.com/platformio/platformio-core/issues/4834>`_)
* Addressed an issue where passing a relative path (``--project-dir``) to the `pio project init <https://docs.platformio.org/en/latest/core/userguide/project/cmd_init.html>`__ command resulted in an error (`issue #4847 <https://github.com/platformio/platformio-core/issues/4847>`_)
* Enhanced |STATICCODEANALYSIS| to accommodate scenarios where custom ``src_dir`` or ``include_dir`` are located outside the project folder (`pull #4874 <https://github.com/platformio/platformio-core/pull/4874>`_)
* Corrected the validation of ``symlink://`` `package specifications <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_install.html#local-folder>`__ , resolving an issue that caused the package manager to repeatedly reinstall dependencies (`pull #4870 <https://github.com/platformio/platformio-core/pull/4870>`_)
* Resolved an issue related to the relative package path in the `pio pkg publish <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_publish.html>`__ command
* Resolved an issue where the |LDF| selected an incorrect library version (`issue #4860 <https://github.com/platformio/platformio-core/issues/4860>`_)
* Resolved an issue with the ``hexlify`` filter in the `device monitor <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html>`__ command, ensuring proper representation of characters with Unicode code points higher than 127 (`issue #4732 <https://github.com/platformio/platformio-core/issues/4732>`_)

6.1.13 (2024-01-12)
~~~~~~~~~~~~~~~~~~~

* Expanded support for SCons variables declared in the legacy format ``${SCONS_VARNAME}`` (`issue #4828 <https://github.com/platformio/platformio-core/issues/4828>`_)

6.1.12 (2024-01-10)
~~~~~~~~~~~~~~~~~~~

* Added support for Python 3.12
* Introduced the capability to launch the debug server in a separate process (`issue #4722 <https://github.com/platformio/platformio-core/issues/4722>`_)
* Introduced a warning during the verification of MCU maximum RAM usage, signaling when the allocated RAM surpasses 100% (`issue #4791 <https://github.com/platformio/platformio-core/issues/4791>`_)
* Drastically enhanced the speed of project building when operating in verbose mode (`issue #4783 <https://github.com/platformio/platformio-core/issues/4783>`_)
* Upgraded the build engine to the latest version of SCons (4.6.0) to improve build performance, reliability, and compatibility with other tools and systems (`release notes <https://github.com/SCons/scons/releases/tag/4.6.0>`__)
* Enhanced the handling of built-in variables in |PIOCONF| during |INTERPOLATION| (`issue #4695 <https://github.com/platformio/platformio-core/issues/4695>`_)
* Enhanced PIP dependency declarations for improved reliability and extended support to include Python 3.6 (`issue #4819 <https://github.com/platformio/platformio-core/issues/4819>`_)
* Implemented automatic installation of missing dependencies when utilizing a SOCKS proxy (`issue #4822 <https://github.com/platformio/platformio-core/issues/4822>`_)
* Implemented a fail-safe mechanism to terminate a debugging session if an unknown CLI option is passed (`issue #4699 <https://github.com/platformio/platformio-core/issues/4699>`_)
* Rectified an issue where ``${platformio.name}`` erroneously represented ``None`` as the default `project name <https://docs.platformio.org/en/latest/projectconf/sections/platformio/options/generic/name.html>`__ (`issue #4717 <https://github.com/platformio/platformio-core/issues/4717>`_)
* Resolved an issue where the ``COMPILATIONDB_INCLUDE_TOOLCHAIN`` setting was not correctly applying to private libraries (`issue #4762 <https://github.com/platformio/platformio-core/issues/4762>`_)
* Resolved an issue where ``get_systype()`` inaccurately returned the architecture when executed within a Docker container on a 64-bit kernel with a 32-bit userspace (`issue #4777 <https://github.com/platformio/platformio-core/issues/4777>`_)
* Resolved an issue with incorrect handling of the ``check_src_filters`` option when used in multiple environments (`issue #4788 <https://github.com/platformio/platformio-core/issues/4788>`_)
* Resolved an issue where running `pio project metadata <https://docs.platformio.org/en/latest/core/userguide/project/cmd_metadata.html>`__ resulted in duplicated "include" entries (`issue #4723 <https://github.com/platformio/platformio-core/issues/4723>`_)
* Resolved an issue where native debugging failed on the host machine (`issue #4745 <https://github.com/platformio/platformio-core/issues/4745>`_)
* Resolved an issue where custom debug configurations were being inadvertently overwritten in VSCode's ``launch.json`` (`issue #4810 <https://github.com/platformio/platformio-core/issues/4810>`_)

6.1.11 (2023-08-31)
~~~~~~~~~~~~~~~~~~~

* Resolved a possible issue that may cause generated projects for `PlatformIO IDE for VSCode <https://docs.platformio.org/en/latest/integration/ide/vscode.html>`__ to fail to launch a debug session because of a missing "objdump" binary when GDB is not part of the toolchain package
* Resolved a regression issue that resulted in the malfunction of the Memory Inspection feature within `PIO Home <https://docs.platformio.org/en/latest/home/index.html>`__

6.1.10 (2023-08-11)
~~~~~~~~~~~~~~~~~~~

* Resolved an issue that caused generated projects for `PlatformIO IDE for VSCode <https://docs.platformio.org/en/latest/integration/ide/vscode.html>`__ to break when the ``-iprefix`` compiler flag was used
* Resolved an issue encountered while utilizing the `pio pkg exec <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_exec.html>`__ command on the Windows platform to execute Python scripts from a package
* Implemented a crucial improvement to the `pio run <https://docs.platformio.org/en/latest/core/userguide/cmd_run.html>`__ command, guaranteeing that the ``monitor`` target is not executed if any of the preceding targets, such as ``upload``, encounter failures
* `Cppcheck <https://docs.platformio.org/en/latest/plus/check-tools/cppcheck.html>`__ v2.11 with new checks, CLI commands and various analysis improvements
* Resolved a critical issue that arose on macOS ARM platforms due to the Python "requests" module, leading to a "ModuleNotFoundError: No module named 'chardet'" (`issue #4702 <https://github.com/platformio/platformio-core/issues/4702>`_)

6.1.9 (2023-07-06)
~~~~~~~~~~~~~~~~~~

* Rectified a regression bug that occurred when the ``-include`` flag was passed via the `build_flags <https://docs.platformio.org/en/latest/projectconf/sections/env/options/build/build_flags.html>`__ option as a relative path and subsequently expanded (`issue #4683 <https://github.com/platformio/platformio-core/issues/4683>`_)
* Resolved an issue that resulted in unresolved absolute toolchain paths when generating the `Compilation database "compile_commands.json" <https://docs.platformio.org/en/latest/integration/compile_commands.html>`__ (`issue #4684 <https://github.com/platformio/platformio-core/issues/4684>`_)

6.1.8 (2023-07-05)
~~~~~~~~~~~~~~~~~~

* Added a new ``--lint`` option to the `pio project config <https://docs.platformio.org/en/latest/core/userguide/project/cmd_config.html>`__ command, enabling users to efficiently perform linting on the |PIOCONF|
* Enhanced the parsing of the |PIOCONF| to provide comprehensive diagnostic information
* Expanded the functionality of the |LIBRARYJSON| manifest by allowing the use of the underscore symbol in the `keywords <https://docs.platformio.org/en/latest/manifests/library-json/fields/keywords.html>`__ field
* Optimized project integration templates to address the issue of long paths on Windows (`issue #4652 <https://github.com/platformio/platformio-core/issues/4652>`_)
* Refactored |UNITTESTING| engine to resolve compiler warnings with "-Wpedantic" option (`pull #4671 <https://github.com/platformio/platformio-core/pull/4671>`_)
* Eliminated erroneous warning regarding the use of obsolete PlatformIO Core when downgrading to the stable version (`issue #4664 <https://github.com/platformio/platformio-core/issues/4664>`_)
* Updated the `pio project metadata <https://docs.platformio.org/en/latest/core/userguide/project/cmd_metadata.html>`__ command to return C/C++ flags as parsed Unix shell arguments when dumping project build metadata
* Resolved a critical issue related to the usage of the ``-include`` flag within the `build_flags <https://docs.platformio.org/en/latest/projectconf/sections/env/options/build/build_flags.html>`__ option, specifically when employing dynamic variables (`issue #4682 <https://github.com/platformio/platformio-core/issues/4682>`_)
* Removed PlatformIO IDE for Atom from the documentation as `Atom has been deprecated <https://github.blog/2022-06-08-sunsetting-atom/>`__

6.1.7 (2023-05-08)
~~~~~~~~~~~~~~~~~~

* Introduced a new ``--sample-code`` option to the `pio project init <https://docs.platformio.org/en/latest/core/userguide/project/cmd_init.html>`__ command, which allows users to include sample code in the newly created project
* Added validation for `project working environment names <https://docs.platformio.org/en/latest/projectconf/sections/env/index.html#working-env-name>`__ to ensure that they only contain lowercase letters ``a-z``, numbers ``0-9``, and special characters ``_`` (underscore) and ``-`` (hyphen)
* Added the ability to show a detailed library dependency tree only in `verbose mode <https://docs.platformio.org/en/latest/core/userguide/cmd_run.html#cmdoption-pio-run-v>`__, which can help you understand the relationship between libraries and troubleshoot issues more effectively (`issue #4517 <https://github.com/platformio/platformio-core/issues/4517>`_)
* Added the ability to run only the `device monitor <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html>`__ when using the `pio run -t monitor <https://docs.platformio.org/en/latest/core/userguide/cmd_run.html>`__ command, saving you time and resources by skipping the build process
* Implemented a new feature to store device monitor logs in the project's ``logs`` folder, making it easier to access and review device monitor logs for your projects (`issue #4596 <https://github.com/platformio/platformio-core/issues/4596>`_)
* Improved support for projects located on Windows network drives, including Network Shared Folder, Dropbox, OneDrive, Google Drive, and other similar services (`issue #3417 <https://github.com/platformio/platformio-core/issues/3417>`_)
* Improved source file filtering functionality for the `Static Code Analysis <https://docs.platformio.org/en/latest/advanced/static-code-analysis/index.html>`__ feature, making it easier to analyze only the code you need to
* Upgraded the build engine to the latest version of SCons (4.5.2) to improve build performance, reliability, and compatibility with other tools and systems (`release notes <https://github.com/SCons/scons/releases/tag/4.5.2>`__)
* Implemented a fix for shell injection vulnerabilities when converting INO files to CPP, ensuring your code is safe and secure (`issue #4532 <https://github.com/platformio/platformio-core/issues/4532>`_)
* Restored the project generator for the `NetBeans IDE <https://docs.platformio.org/en/latest/integration/ide/netbeans.html>`__, providing you with more flexibility and options for your development workflow
* Resolved installation issues with PIO Remote on Raspberry Pi and other small form-factor PCs (`issue #4425 <https://github.com/platformio/platformio-core/issues/4425>`_, `issue #4493 <https://github.com/platformio/platformio-core/issues/4493>`_, `issue #4607 <https://github.com/platformio/platformio-core/issues/4607>`_)
* Resolved an issue where the `build_cache_dir <https://docs.platformio.org/en/latest/projectconf/sections/platformio/options/directory/build_cache_dir.html>`__ setting was not being recognized consistently across multiple environments (`issue #4574 <https://github.com/platformio/platformio-core/issues/4574>`_)
* Resolved an issue where organization details could not be updated using the `pio org update <https://docs.platformio.org/en/latest/core/userguide/org/cmd_update.html>`__ command
* Resolved an issue where the incorrect debugging environment was generated for VSCode in "Auto" mode (`issue #4597 <https://github.com/platformio/platformio-core/issues/4597>`_)
* Resolved an issue where native tests would fail if a custom program name was specified (`issue #4546 <https://github.com/platformio/platformio-core/issues/4546>`_)
* Resolved an issue where the PlatformIO |DEBUGGING| solution was not escaping the tool installation process into MI2 correctly (`issue #4565 <https://github.com/platformio/platformio-core/issues/4565>`_)
* Resolved an issue where multiple targets were not executed sequentially (`issue #4604 <https://github.com/platformio/platformio-core/issues/4604>`_)
* Resolved an issue where upgrading PlatformIO Core fails on Windows with Python 3.11 (`issue #4540 <https://github.com/platformio/platformio-core/issues/4540>`_)

6.1.6 (2023-01-23)
~~~~~~~~~~~~~~~~~~

* Added support for Python 3.11
* Added a new `name <https://docs.platformio.org/en/latest/projectconf/sections/platformio/options/generic/description.html>`__ configuration option to customize a project name (`pull #4498 <https://github.com/platformio/platformio-core/pull/4498>`_)
* Made assets (templates, ``99-platformio-udev.rules``) part of Python's module (`issue #4458 <https://github.com/platformio/platformio-core/issues/4458>`_)
* Updated `Clang-Tidy <https://docs.platformio.org/en/latest/plus/check-tools/clang-tidy.html>`__ check tool to v15.0.5 with new diagnostics and bugfixes
* Removed dependency on the "zeroconf" package and install it only when a user lists mDNS devices (issue with zeroconf's LGPL license)
* Show the real error message instead of "Can not remove temporary directory" when |PIOCONF| is broken (`issue #4480 <https://github.com/platformio/platformio-core/issues/4480>`_)
* Fixed an issue with an incorrect test summary when a testcase name includes a colon (`issue #4508 <https://github.com/platformio/platformio-core/issues/4508>`_)
* Fixed an issue when `extends <https://docs.platformio.org/en/latest/projectconf/sections/env/options/advanced/extends.html>`__ did not override options in the right order (`issue #4462 <https://github.com/platformio/platformio-core/issues/4462>`_)
* Fixed an issue when `pio pkg list <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_list.html>`__ and `pio pkg uninstall <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_uninstall.html>`__ commands fail if there are circular dependencies in the |LIBRARYJSON| manifests (`issue #4475 <https://github.com/platformio/platformio-core/issues/4475>`_)

6.1.5 (2022-11-01)
~~~~~~~~~~~~~~~~~~

* Added a new `enable_proxy_strict_ssl <https://docs.platformio.org/en/latest/core/userguide/cmd_settings.html>`__ setting to disable the proxy server certificate verification (`issue #4432 <https://github.com/platformio/platformio-core/issues/4432>`_)
* Documented `PlatformIO Core Proxy Configuration <https://docs.platformio.org/en/latest/core/installation/proxy-configuration.html>`__
* Speeded up device port finder by avoiding loading board HWIDs from development platforms
* Improved caching of build metadata in debug mode
* Fixed an issue when `pio pkg install --storage-dir <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_install.html>`__ command requires PlatformIO project (`issue #4410 <https://github.com/platformio/platformio-core/issues/4410>`_)

6.1.4 (2022-08-12)
~~~~~~~~~~~~~~~~~~

* Added support for accepting the original FileNode environment in a "callback" function when using `Build Middlewares <https://docs.platformio.org/en/latest/scripting/middlewares.html>`__ (`pull #4380 <https://github.com/platformio/platformio-core/pull/4380>`_)
* Improved device port finder when using dual channel UART converter (`issue #4367 <https://github.com/platformio/platformio-core/issues/4367>`_)
* Improved project dependency resolving when using the `pio project init --ide <https://docs.platformio.org/en/latest/core/userguide/project/cmd_init.html>`__ command
* Upgraded build engine to the SCons 4.4.0 (`release notes <https://github.com/SCons/scons/releases/tag/4.4.0>`__)
* Keep custom "unwantedRecommendations" when generating projects for VSCode (`issue #4383 <https://github.com/platformio/platformio-core/issues/4383>`_)
* Do not resolve project dependencies for the ``cleanall`` target (`issue #4344 <https://github.com/platformio/platformio-core/issues/4344>`_)
* Warn about calling "env.BuildSources" in a POST-type script (`issue #4385 <https://github.com/platformio/platformio-core/issues/4385>`_)
* Fixed an issue when escaping macros/defines for IDE integration (`issue #4360 <https://github.com/platformio/platformio-core/issues/4360>`_)
* Fixed an issue when the "cleanall" target removes dependencies from all working environments (`issue #4386 <https://github.com/platformio/platformio-core/issues/4386>`_)

6.1.3 (2022-07-18)
~~~~~~~~~~~~~~~~~~

* Fixed a regression bug when opening device monitor without any filters (`issue #4363 <https://github.com/platformio/platformio-core/issues/4363>`_)

6.1.2 (2022-07-18)
~~~~~~~~~~~~~~~~~~

* Export a ``PIO_UNIT_TESTING`` macro to the project source files and dependent libraries in the |UNITTESTING| mode
* Improved detection of Windows architecture (`issue #4353 <https://github.com/platformio/platformio-core/issues/4353>`_)
* Warn about unknown `device monitor filters <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html#filters>`__ (`issue #4362 <https://github.com/platformio/platformio-core/issues/4362>`_)
* Fixed a regression bug when `libArchive <https://docs.platformio.org/en/latest/manifests/library-json/fields/build/libarchive.html>`__ option declared in the |LIBRARYJSON| manifest was ignored (`issue #4351 <https://github.com/platformio/platformio-core/issues/4351>`_)
* Fixed an issue when the `pio pkg publish <https://docs.platformio.org/en/latest/core/userguide/pkg/cmd_publish.html>`__ command didn't work with Python 3.6 (`issue #4352 <https://github.com/platformio/platformio-core/issues/4352>`_)

6.1.1 (2022-07-11)
~~~~~~~~~~~~~~~~~~

* Added new ``monitor_encoding`` project configuration option to configure `Device Monitor <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html>`__ (`issue #4350 <https://github.com/platformio/platformio-core/issues/4350>`_)
* Allowed specifying project environments for `pio ci <https://docs.platformio.org/en/latest/core/userguide/cmd_ci.html>`__ command (`issue #4347 <https://github.com/platformio/platformio-core/issues/4347>`_)
* Show "TimeoutError" only in the verbose mode when can not find a serial port
* Fixed an issue when a serial port was not automatically detected if the board has predefined HWIDs
* Fixed an issue with endless scanning of project dependencies (`issue #4349 <https://github.com/platformio/platformio-core/issues/4349>`_)
* Fixed an issue with |LDF| when incompatible libraries were used for the working project environment with the missed framework (`pull #4346 <https://github.com/platformio/platformio-core/pull/4346>`_)

6.1.0 (2022-07-06)
~~~~~~~~~~~~~~~~~~

* **Device Manager**

  - Automatically reconnect device monitor if a connection fails
  - Added new `pio device monitor --no-reconnect <https://docs.platformio.org/en/latest/core/userguide/device/cmd_monitor.html#cmdoption-pio-device-monitor-no-reconnect>`__ option to disable automatic reconnection
  - Handle device monitor disconnects more gracefully (`issue #3939 <https://github.com/platformio/platformio-core/issues/3939>`_)
  - Improved a serial port finder for `Black Magic Probe <https://docs.platformio.org/en/latest/plus/debug-tools/blackmagic.html>`__ (`issue #4023 <https://github.com/platformio/platformio-core/issues/4023>`_)
  - Improved a serial port finder for a board with predefined HWIDs
  - Replaced ``monitor_flags`` with independent project configuration options: `monitor_parity <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-parity>`__, `monitor_eol <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-eol>`__, `monitor_raw <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-raw>`__, `monitor_echo <https://docs.platformio.org/en/latest/projectconf/section_env_monitor.html#monitor-echo>`__
  - Fixed an issue when the monitor filters were not applied in their order (`issue #4320 <https://github.com/platformio/platformio-core/issues/4320>`_)

* **Unit Testing**

  - Updated "Getting Started" documentation for `GoogleTest <https://docs.platformio.org/en/latest/advanced/unit-testing/frameworks/googletest.html>`__ testing and mocking framework
  - Export |UNITTESTING| flags only to the project build environment (``projenv``, files in "src" folder)
  - Merged the "building" stage with "uploading" for the embedded target (`issue #4307 <https://github.com/platformio/platformio-core/issues/4307>`_)
  - Do not resolve dependencies from the project "src" folder when the `test_build_src <https://docs.platformio.org/en/latest//projectconf/section_env_test.html#test-build-src>`__ option is not enabled
  - Do not immediately terminate a testing program when results are received
  - Fixed an issue when a custom `pio test --project-config <https://docs.platformio.org/en/latest/core/userguide/cmd_test.html#cmdoption-pio-test-c>`__ was not handled properly (`issue #4299 <https://github.com/platformio/platformio-core/issues/4299>`_)
  - Fixed an issue when testing results were wrong in the verbose mode (`issue #4336 <https://github.com/platformio/platformio-core/issues/4336>`_)

* **Build System**

  - Significantly improved support for `Pre & Post Actions <https://docs.platformio.org/en/latest/scripting/actions.html>`__

    * Allowed to declare actions in the `PRE-type scripts <https://docs.platformio.org/en/latest/scripting/launch_types.html>`__ even if the target is not ready yet
    * Allowed library maintainers to use Pre & Post Actions in the library `extraScript <https://docs.platformio.org/en/latest/manifests/library-json/fields/build/extrascript.html>`__

  - Documented `Stringification <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#stringification>`__ – converting a macro argument into a string constant (`issue #4310 <https://github.com/platformio/platformio-core/issues/4310>`_)
  - Added new `pio run --monitor-port <https://docs.platformio.org/en/latest/core/userguide/cmd_run.html#cmdoption-pio-run-monitor-port>`__ option to specify custom device monitor port to the ``monitor`` target (`issue #4337 <https://github.com/platformio/platformio-core/issues/4337>`_)
  - Added ``env.StringifyMacro(value)`` helper function for the `Advanced Scripting <https://docs.platformio.org/en/latest/scripting/index.html>`__
  - Allowed to ``Import("projenv")`` in a library extra script (`issue #4305 <https://github.com/platformio/platformio-core/issues/4305>`_)
  - Fixed an issue when the `build_unflags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-unflags>`__ operation ignores a flag value (`issue #4309 <https://github.com/platformio/platformio-core/issues/4309>`_)
  - Fixed an issue when the `build_unflags <https://docs.platformio.org/en/latest/projectconf/section_env_build.html#build-unflags>`__ option was not applied to the ``ASPPFLAGS`` scope
  - Fixed an issue on Windows OS when flags were wrapped to the temporary file while generating the `Compilation database "compile_commands.json" <https://docs.platformio.org/en/latest/integration/compile_commands.html>`__
  - Fixed an issue with the |LDF| when recursively scanning dependencies in the ``chain`` mode
  - Fixed a "PermissionError" on Windows when running "clean" or "cleanall" targets (`issue #4331 <https://github.com/platformio/platformio-core/issues/4331>`_)

* **Package Management**

  - Fixed an issue when library dependencies were installed for the incompatible project environment (`issue #4338 <https://github.com/platformio/platformio-core/issues/4338>`_)

* **Miscellaneous**

  - Warn about incompatible Bash version for the `Shell Completion <https://docs.platformio.org/en/latest/core/userguide/system/completion/index.html>`__ (`issue #4326 <https://github.com/platformio/platformio-core/issues/4326>`_)

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
