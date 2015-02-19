Release History
===============

1.0.0 (2015-?)
--------------

* Added support for *ARM*-based credit-card computers: `Raspberry Pi <http://www.raspberrypi.org>`_,
  `BeagleBoard <http://beagleboard.org>`_ and `CubieBoard <http://cubieboard.org>`_
* Added new boards to `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform: *Arduino NG, Arduino BT, Arduino Esplora, Arduino Ethernet,
  Arduino Robot Control, Arduino Robot Motor and Arduino Yun*
* Refactored *Library Dependency Finder* (issues
  `#48 <https://github.com/ivankravets/platformio/issues/48>`_,
  `#50 <https://github.com/ivankravets/platformio/issues/50>`_,
  `#55 <https://github.com/ivankravets/platformio/issues/55>`_)
* Added ``--json-output`` option to
  `platformio boards <http://docs.platformio.org/en/latest/userguide/cmd_boards.html>`__
  and `platformio search <http://docs.platformio.org/en/latest/userguide/cmd_search.html>`__
  commands which allow to return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format
  (`issue #42 <https://github.com/ivankravets/platformio/issues/42>`_)
* Allowed to ignore some libs from *Library Dependency Finder* via
  `ignore_libs <http://docs.platformio.org/en/latest/projectconf.html#ignore-libs>`_ option
* Improved `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  command: asynchronous output for build process, timing and detailed
  information about environment configuration (`issue #74 <https://github.com/ivankravets/platformio/issues/74>`_)
* Output compiled size and static memory usage with `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  command (`issue #59 <https://github.com/ivankravets/platformio/issues/59>`_)
* Updated `framework-arduino` AVR & SAM to 1.6 stable version
* Fixed an issue with the libraries that are git repositories (`issue #49 <https://github.com/ivankravets/platformio/issues/49>`_)
* Fixed handling of assembly files (`issue #58 <https://github.com/ivankravets/platformio/issues/58>`_)
* Fixed compiling error if space is in user's folder (`issue #56 <https://github.com/ivankravets/platformio/issues/56>`_)
* Fixed `AttributeError: 'module' object has no attribute 'disable_warnings'`
  when a version of `requests` package is less then 2.4.0
* Fixed bug with invalid process's "return code" when PlatformIO has internal
  error (`issue #81 <https://github.com/ivankravets/platformio/issues/81>`_)


0.10.2 (2015-01-06)
-------------------

* Fixed an issue with ``--json-output`` (`issue #42 <https://github.com/ivankravets/platformio/issues/42>`_)
* Fixed an exception during `platformio upgrade <http://docs.platformio.org/en/latest/userguide/cmd_upgrade.html>`__ under Windows OS (`issue #45 <https://github.com/ivankravets/platformio/issues/45>`_)

0.10.1 (2015-01-02)
-------------------

* Added ``--json-output`` option to
  `platformio list <http://docs.platformio.org/en/latest/userguide/cmd_list.html>`__,
  `platformio serialports list <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html>`__ and
  `platformio lib list <http://docs.platformio.org/en/latest/userguide/cmd_lib_list.html>`__
  commands which allows to return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format
  (`issue #42 <https://github.com/ivankravets/platformio/issues/42>`_)
* Fixed missing auto-uploading by default after `platformio init <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`__
  command

0.10.0 (2015-01-01)
-------------------

**Happy New Year!**

* Implemented `platformio boards <http://docs.platformio.org/en/latest/userguide/cmd_boards.html>`_
  command (`issue #11 <https://github.com/ivankravets/platformio/issues/11>`_)
* Added support of *Engduino* boards for
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#engduino>`__
  platform (`issue #38 <https://github.com/ivankravets/platformio/issues/38>`_)
* Added ``--board`` option to `platformio init <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`__
  command which allows to initialise project with the specified embedded boards
  (`issue #21 <https://github.com/ivankravets/platformio/issues/21>`_)
* Added `example with uploading firmware <http://docs.platformio.org/en/latest/projectconf.html#examples>`_
  via USB programmer (USBasp) for
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html>`_
  *MCUs* (`issue #35 <https://github.com/ivankravets/platformio/issues/35>`_)
* Automatic detection of port on `platformio serialports monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_
  (`issue #37 <https://github.com/ivankravets/platformio/issues/37>`_)
* Allowed auto-installation of platforms when prompts are disabled (`issue #43 <https://github.com/ivankravets/platformio/issues/43>`_)
* Fixed urllib3's *SSL* warning under Python <= 2.7.2 (`issue #39 <https://github.com/ivankravets/platformio/issues/39>`_)
* Fixed bug with *Arduino USB* boards (`issue #40 <https://github.com/ivankravets/platformio/issues/40>`_)

0.9.2 (2014-12-10)
------------------

* Replaced "dark blue" by "cyan" colour for the texts (`issue #33 <https://github.com/ivankravets/platformio/issues/33>`_)
* Added new setting `enable_prompts <http://docs.platformio.org/en/latest/userguide/cmd_settings.html>`_
  and allowed to disable all *PlatformIO* prompts (useful for cloud compilers)
  (`issue #34 <https://github.com/ivankravets/platformio/issues/34>`_)
* Fixed compilation bug on *Windows* with installed *MSVC* (`issue #18 <https://github.com/ivankravets/platformio/issues/18>`_)

0.9.1 (2014-12-05)
------------------

* Ask user to install platform (when it hasn't been installed yet) within
  `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  and `platformio show <http://docs.platformio.org/en/latest/userguide/cmd_show.html>`_ commands
* Improved main `documentation <http://docs.platformio.org>`_
* Fixed "*OSError: [Errno 2] No such file or directory*" within
  `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  command when PlatformIO isn't installed properly
* Fixed example for `Eclipse IDE with Tiva board <https://github.com/ivankravets/platformio/tree/develop/examples/ide-eclipse>`_
  (`issue #32 <https://github.com/ivankravets/platformio/issues/32>`_)
* Upgraded `Eclipse Project Examples <https://github.com/ivankravets/platformio/tree/develop/examples/ide-eclipse>`_
  to latest *Luna* and *PlatformIO* releases

0.9.0 (2014-12-01)
------------------

* Implemented `platformio settings <http://docs.platformio.org/en/latest/userguide/cmd_settings.html>`_ command
* Improved `platformio init <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`_ command.
  Added new option ``--project-dir`` where you can specify another path to
  directory where new project will be initialized (`issue #31 <https://github.com/ivankravets/platformio/issues/31>`_)
* Added *Migration Manager* which simplifies process with upgrading to a
  major release
* Added *Telemetry Service* which should help us make *PlatformIO* better
* Implemented *PlatformIO AppState Manager* which allow to have multiple
  ``.platformio`` states.
* Refactored *Package Manager*
* Download Manager: fixed SHA1 verification within *Cygwin Environment*
  (`issue #26 <https://github.com/ivankravets/platformio/issues/26>`_)
* Fixed bug with code builder and built-in Arduino libraries
  (`issue #28 <https://github.com/ivankravets/platformio/issues/28>`_)

0.8.0 (2014-10-19)
------------------

* Avoided trademark issues in `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`_
  with the new fields: `frameworks <http://docs.platformio.org/en/latest/librarymanager/config.html#frameworks>`_,
  `platforms <http://docs.platformio.org/en/latest/librarymanager/config.html#platforms>`_
  and `dependencies <http://docs.platformio.org/en/latest/librarymanager/config.html#dependencies>`_
  (`issue #17 <https://github.com/ivankravets/platformio/issues/17>`_)
* Switched logic from "Library Name" to "Library Registry ID" for all
  `platformio lib <http://docs.platformio.org/en/latest/userguide/lib/index.html>`_
  commands (install, uninstall, update and etc.)
* Renamed ``author`` field to `authors <http://docs.platformio.org/en/latest/librarymanager/config.html#authors>`_
  and allowed to setup multiple authors per library in `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`_
* Added option to specify "maintainer" status in `authors <http://docs.platformio.org/en/latest/librarymanager/config.html#authors>`_ field
* New filters/options for `platformio lib search <http://docs.platformio.org/en/latest/userguide/lib/cmd_search.html>`_
  command: ``--framework`` and ``--platform``

0.7.1 (2014-10-06)
------------------

* Fixed bug with order for includes in conversation from INO/PDE to CPP
* Automatic detection of port on upload (`issue #15 <https://github.com/ivankravets/platformio/issues/15>`_)
* Fixed lib update crashing when no libs are installed (`issue #19 <https://github.com/ivankravets/platformio/issues/19>`_)


0.7.0 (2014-09-24)
------------------

* Implemented new `[platformio] <http://docs.platformio.org/en/latest/projectconf.html#platformio>`_
  section for Configuration File with `home_dir <http://docs.platformio.org/en/latest/projectconf.html#home-dir>`_
  option (`issue #14 <https://github.com/ivankravets/platformio/issues/14>`_)
* Implemented *Library Manager* (`issue #6 <https://github.com/ivankravets/platformio/issues/6>`_)

0.6.0 (2014-08-09)
------------------

* Implemented `platformio serialports monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ (`issue #10 <https://github.com/ivankravets/platformio/issues/10>`_)
* Fixed an issue ``ImportError: No module named platformio.util`` (`issue #9 <https://github.com/ivankravets/platformio/issues/9>`_)
* Fixed bug with auto-conversation from Arduino \*.ino to \*.cpp

0.5.0 (2014-08-04)
------------------

* Improved nested lookups for libraries
* Disabled default warning flag "-Wall"
* Added auto-conversation from \*.ino to valid \*.cpp for Arduino/Energia
  frameworks (`issue #7 <https://github.com/ivankravets/platformio/issues/7>`_)
* Added `Arduino example <https://github.com/ivankravets/platformio/tree/develop/examples/arduino-adafruit-library>`_
  with external library (*Adafruit CC3000*)
* Implemented `platformio upgrade <http://docs.platformio.org/en/latest/userguide/cmd_upgrade.html>`_
  command and "auto-check" for the latest
  version (`issue #8 <https://github.com/ivankravets/platformio/issues/8>`_)
* Fixed an issue with "auto-reset" for *Raspduino* board
* Fixed a bug with nested libs building

0.4.0 (2014-07-31)
------------------

* Implemented `platformio serialports <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html>`_ command
* Allowed to put special build flags only for ``src`` files via
  `srcbuild_flags <http://docs.platformio.org/en/latest/projectconf.html#srcbuild-flags>`_
  environment option
* Allowed to override some of settings via system environment variables
  such as: ``$PIOSRCBUILD_FLAGS`` and ``$PIOENVS_DIR``
* Added ``--upload-port`` option for `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html#cmdoption--upload-port>`__ command
* Implemented (especially for `SmartAnthill <http://smartanthill.ikravets.com/>`_)
  `platformio run -t uploadlazy <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`_
  target (no dependencies to framework libs, ELF and etc.)
* Allowed to skip default packages via `platformio install --skip-default-package <http://docs.platformio.org/en/latest/userguide/cmd_install.html#cmdoption--skip-default>`_
  option
* Added tools for *Raspberry Pi* platform
* Added support for *Microduino* and *Raspduino* boards in
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html>`_ platform


0.3.1 (2014-06-21)
------------------

* Fixed auto-installer for Windows OS (bug with %PATH% customisations)


0.3.0 (2014-06-21)
------------------

* Allowed to pass multiple "SomePlatform" to install/uninstall commands
* Added "IDE Integration" section to README with Eclipse project examples
* Created auto installer script for *PlatformIO* (`issue #3 <https://github.com/ivankravets/platformio/issues/3>`_)
* Added "Super-Quick" way to Installation section (README)
* Implemented "build_flags" option for environments (`issue #4 <https://github.com/ivankravets/platformio/issues/4>`_)


0.2.0 (2014-06-15)
------------------

* Resolved `issue #1 "Build referred libraries" <https://github.com/ivankravets/platformio/issues/1>`_
* Renamed project's "libs" directory to "lib"
* Added `arduino-internal-library <https://github.com/ivankravets/platformio/tree/develop/examples/arduino-internal-library>`_ example
* Changed to beta status


0.1.0 (2014-06-13)
------------------

* Birth! First alpha release
