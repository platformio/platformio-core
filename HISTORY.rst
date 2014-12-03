Release History
===============

0.9.1 (2014-12-03)
------------------

* Fixed "*OSError: [Errno 2] No such file or directory*" when PlatformIO isn't
  installed properly
* Fixed example for `Eclipse IDE with Tiva board <https://github.com/ivankravets/platformio/tree/develop/examples/ide-eclipse>`_
  (`issue #32 <https://github.com/ivankravets/platformio/issues/32>`_)

0.9.0 (2014-12-01)
------------------

* Implemented `platformio settings <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_settings.html>`_ command
* Improved `platformio init <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_init.html>`_ command.
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

* Avoided trademark issues in `library.json <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html>`_
  with the new fields: `frameworks <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html#frameworks>`_,
  `platforms <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html#platforms>`_
  and `dependencies <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html#dependencies>`_
  (`issue #17 <https://github.com/ivankravets/platformio/issues/17>`_)
* Switched logic from "Library Name" to "Library Registry ID" for all
  `platformio lib <http://docs.platformio.ikravets.com/en/latest/userguide/lib/index.html>`_
  commands (install, uninstall, update and etc.)
* Renamed ``author`` field to `authors <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html#authors>`_
  and allowed to setup multiple authors per library in `library.json <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html>`_
* Added option to specify "maintainer" status in `authors <http://docs.platformio.ikravets.com/en/latest/librarymanager/config.html#authors>`_ field
* New filters/options for `platformio lib search <http://docs.platformio.ikravets.com/en/latest/userguide/lib/cmd_search.html>`_
  command: ``--framework`` and ``--platform``

0.7.1 (2014-10-06)
------------------

* Fixed bug with order for includes in conversation from INO/PDE to CPP
* Automatic detection of port on upload (`issue #15 <https://github.com/ivankravets/platformio/issues/15>`_)
* Fixed lib update crashing when no libs are installed (`issue #19 <https://github.com/ivankravets/platformio/issues/19>`_)


0.7.0 (2014-09-24)
------------------

* Implemented new `[platformio] <http://docs.platformio.ikravets.com/en/latest/projectconf.html#platformio>`_
  section for Configuration File with `home_dir <http://docs.platformio.ikravets.com/en/latest/projectconf.html#home-dir>`_
  option (`issue #14 <https://github.com/ivankravets/platformio/issues/14>`_)
* Implemented *Library Manager* (`issue #6 <https://github.com/ivankravets/platformio/issues/6>`_)

0.6.0 (2014-08-09)
------------------

* Implemented `platformio serialports monitor <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ (`issue #10 <https://github.com/ivankravets/platformio/issues/10>`_)
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
* Implemented `platformio upgrade <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_upgrade.html>`_
  command and "auto-check" for the latest
  version (`issue #8 <https://github.com/ivankravets/platformio/issues/8>`_)
* Fixed an issue with "auto-reset" for *Raspduino* board
* Fixed a bug with nested libs building

0.4.0 (2014-07-31)
------------------

* Implemented `platformio serialports <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_serialports.html>`_ command
* Allowed to put special build flags only for ``src`` files via
  `srcbuild_flags <http://docs.platformio.ikravets.com/en/latest/projectconf.html#srcbuild-flags>`_
  environment option
* Allowed to override some of settings via system environment variables
  such as: ``$PIOSRCBUILD_FLAGS`` and ``$PIOENVS_DIR``
* Added ``--upload-port`` option for `platformio run <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_run.html#cmdoption--upload-port>`_ command
* Implemented (especially for `SmartAnthill <http://smartanthill.ikravets.com/>`_)
  `platformio run -t uploadlazy <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_run.html>`_
  target (no dependencies to framework libs, ELF and etc.)
* Allowed to skip default packages via `platformio install --skip-default-package <http://docs.platformio.ikravets.com/en/latest/userguide/cmd_install.html#cmdoption--skip-default>`_
  option
* Added tools for *Raspberry Pi* platform
* Added support for *Microduino* and *Raspduino* boards in
  `atmelavr <http://docs.platformio.ikravets.com/en/latest/platforms/atmelavr.html>`_ platform


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
