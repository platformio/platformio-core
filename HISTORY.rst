Release Notes
=============

.. _release_notes_5:

PlatformIO Core 5
-----------------

**A professional collaborative platform for embedded development**

5.0.0 (2020-??-??)
~~~~~~~~~~~~~~~~~~


* Integration with the new **PlatformIO Trusted Registry**

  - Enterprise-grade package storage with high availability (multi replicas)
  - Secure, fast, and reliable global content delivery network (CDN)
  - Universal support for all embedded packages:

    * Libraries
    * Development platforms
    * Toolchains

  - Built-in fine-grained access control (role based, teams, organizations)
  - Command Line Interface:

    * `pio package publish <https://docs.platformio.org/page/core/userguide/package/cmd_publish.html>`__ – publish a personal or organization package
    * `pio package unpublish <https://docs.platformio.org/page/core/userguide/package/cmd_unpublish.html>`__ – remove a pushed package from the registry
    * Grant package access to the team members or maintainers

* Integration with the new `Account Management System <https://docs.platformio.org/page/plus/pio-account.html>`__

  - Manage own organizations
  - Manage organization teams
  - Manage resource access

* New **Package Management System**

  - Integrated PlatformIO Core with the new PlatformIO Trusted Registry
  - Strict dependency declaration using owner name (resolves name conflicts) (`issue #1824 <https://github.com/platformio/platformio-core/issues/1824>`_)
  - Automatically save dependencies to `"platformio.ini" <https://docs.platformio.org/page/projectconf.html>`__ when installing using PlatformIO CLI (`issue #2964 <https://github.com/platformio/platformio-core/issues/2964>`_)

* **PlatformIO Build System**

  - Upgraded to `SCons 4.0 - a next-generation software construction tool <https://scons.org/>`__
  - New `Custom Targets <https://docs.platformio.org/page/projectconf/advanced_scripting.html#custom-targets>`__

    * Pre/Post processing based on a dependent sources (other target, source file, etc.)
    * Command launcher with own arguments
    * Launch command with custom options declared in `"platformio.ini" <https://docs.platformio.org/page/projectconf.html>`__
    * Python callback as a target (use the power of Python interpreter and PlatformIO Build API)
    * List available project targets (including dev-platform specific and custom targets) with a new `pio run --list-targets <https://docs.platformio.org/page/core/userguide/cmd_run.html#cmdoption-platformio-run-list-targets>`__ command (`issue #3544 <https://github.com/platformio/platformio-core/issues/3544>`_)

  - Enable "cyclic reference" for GCC linker only for the embedded dev-platforms (`issue #3570 <https://github.com/platformio/platformio-core/issues/3570>`_)
  - Automatically enable LDF dependency `chain+ mode (evaluates C/C++ Preprocessor conditional syntax) <https://docs.platformio.org/page/librarymanager/ldf.html#dependency-finder-mode>`__ for Arduino library when "library.property" has "depends" field (`issue #3607 <https://github.com/platformio/platformio-core/issues/3607>`_)
  - Fixed an issue with improper processing of source files added via multiple Build Middlewares (`issue #3531 <https://github.com/platformio/platformio-core/issues/3531>`_)
  - Fixed an issue with ``clean`` target on Windows when project and build directories are located on different logical drives (`issue #3542 <https://github.com/platformio/platformio-core/issues/3542>`_)

* **Project Management**

  - Added support for "globstar/`**`" (recursive) pattern for the different commands and configuration options (`pio ci <https://docs.platformio.org/page/core/userguide/cmd_ci.html>`__, `src_filter <https://docs.platformio.org/page/projectconf/section_env_build.html#src-filter>`__, `check_patterns <https://docs.platformio.org/page/projectconf/section_env_check.html#check-patterns>`__, `library.json > srcFilter <https://docs.platformio.org/page/librarymanager/config.html#srcfilter>`__). Python 3.5+ is required
  - Added a new ``-e, --environment`` option to `pio project init <https://docs.platformio.org/page/core/userguide/project/cmd_init.html#cmdoption-platformio-project-init-e>`__ command that helps to update a PlatformIO project using existing environment
  - Dump build system data intended for IDE extensions/plugins using a new `pio project data <https://docs.platformio.org/page/core/userguide/project/cmd_data.html>`__ command
  - Do not generate ".travis.yml" for a new project, let the user have a choice

* **Unit Testing**

  - Updated PIO Unit Testing support for Mbed framework and added compatibility with Mbed OS 6
  - Fixed an issue when running multiple test environments (`issue #3523 <https://github.com/platformio/platformio-core/issues/3523>`_)
  - Fixed an issue when Unit Testing engine fails with a custom project configuration file (`issue #3583 <https://github.com/platformio/platformio-core/issues/3583>`_)

* **Miscellaneous**

  - Display system-wide information using a new `pio system info <https://docs.platformio.org/page/core/userguide/system/cmd_info.html>`__ command (`issue #3521 <https://github.com/platformio/platformio-core/issues/3521>`_)
  - Remove unused data using a new `pio system prune <https://docs.platformio.org/page/core/userguide/system/cmd_prune.html>`__ command (`issue #3522 <https://github.com/platformio/platformio-core/issues/3522>`_)
  - Do not escape compiler arguments in VSCode template on Windows


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
