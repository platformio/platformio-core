Release Notes
=============

.. _release_notes_5:

PlatformIO Core 5
-----------------

**A professional collaborative platform for embedded development**

5.0.1 (2020-??-??)
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
  - Do not escape compiler arguments in VSCode template on Windows.

.. _release_notes_4:

PlatformIO Core 4
-----------------

See `PlatformIO Core 4.0 history <https://docs.platformio.org/en/v4.3.4/core/history.html#platformio-core-4>`__.

PlatformIO Core 3
-----------------

See `PlatformIO Core 3.0 history <https://docs.platformio.org/en/v4.3.4/core/history.html#platformio-core-3>`__.

PlatformIO Core 2
-----------------

See `PlatformIO Core 2.0 history <https://docs.platformio.org/en/v4.3.4/core/history.html#platformio-core-2>`__.

PlatformIO Core 1
-----------------

See `PlatformIO Core 1.0 history <https://docs.platformio.org/en/v4.3.4/core/history.html#platformio-core-1>`__.

PlatformIO Core Preview
-----------------------

See `PlatformIO Core Preview history <https://docs.platformio.org/en/v4.3.4/core/history.html#platformio-core-preview>`__.
