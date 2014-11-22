Release History
===============

0.9.0 (?)
---------

* Refactored *Package Manager*
* Download Manager: fixed SHA1 verification within *Cygwin Environment*
  (`issue #26 <https://github.com/ivankravets/platformio/issues/26>`_)

0.8.0 (2014-10-19)
------------------

* Avoided trademark issues in ``library.json`` with new fields:
  ``frameworks``, ``platforms`` and ``dependencies`` (`issue #17 <https://github.com/ivankravets/platformio/issues/17>`_)
* Switched logic from "Library Name" to "Library Registry ID" for all
  ``platformio lib`` commands (install, uninstall, update and etc.)
* Renamed ``author`` field to ``authors`` and allowed to setup multiple authors
  per library in ``library.json``
* Added option to specify "maintainer" status in ``authors`` field
* New filters/options for ``platformio lib search`` command: ``--framework``
  and ``--platform``

0.7.1 (2014-10-06)
------------------

* Fixed bug with order for includes in conversation from INO/PDE to CPP
* Automatic detection of port on upload (`issue #15 <https://github.com/ivankravets/platformio/issues/15>`_)
* Fixed lib update crashing when no libs are installed (`issue #19 <https://github.com/ivankravets/platformio/issues/19>`_)


0.7.0 (2014-09-24)
------------------

* Implemented new ``[platformio]`` section for Configuration File with ``home_dir``
  option (`issue #14 <https://github.com/ivankravets/platformio/issues/14>`_)
* Implemented *Library Manager* (`issue #6 <https://github.com/ivankravets/platformio/issues/6>`_)

0.6.0 (2014-08-09)
------------------

* Implemented ``serialports monitor`` (`issue #10 <https://github.com/ivankravets/platformio/issues/10>`_)
* Fixed an issue ``ImportError: No module named platformio.util`` (`issue #9 <https://github.com/ivankravets/platformio/issues/9>`_)
* Fixed bug with auto-conversation from Arduino \*.ino to \*.cpp

0.5.0 (2014-08-04)
------------------

* Improved nested lookups for libraries
* Disabled default warning flag "-Wall"
* Added auto-conversation from \*.ino to valid \*.cpp for Arduino/Energia
  frameworks (`issue #7 <https://github.com/ivankravets/platformio/issues/7>`_)
* Added `Arduino example <https://github.com/ivankravets/platformio/tree/develop/examples/arduino-adafruit-library>`_
  with external library (Adafruit CC3000)
* Implemented ``platformio upgrade`` command and "auto-check" for the latest
  version (`issue #8 <https://github.com/ivankravets/platformio/issues/8>`_)
* Fixed an issue with "auto-reset" for Raspduino board
* Fixed a bug with nested libs building

0.4.0 (2014-07-31)
------------------

* Implemented ``serialports`` command
* Allowed to put special build flags only for ``src`` files via
  ``srcbuild_flags`` environment option
* Allowed to override some of settings via system environment variables
  such as: ``$PIOSRCBUILD_FLAGS`` and ``$PIOENVS_DIR``
* Added ``--upload-port`` option for ``platformio run`` command
* Implemented (especially for `SmartAnthill <http://smartanthill.ikravets.com/>`_)
  ``platformio run -t uploadlazy`` target (no dependencies to framework libs,
  ELF and etc.)
* Allowed to skip default packages via ``platformio install --skip-default-package`` flag
* Added tools for Raspberry Pi platform
* Added support for Microduino and Raspduino boards in ``atmelavr`` platform


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
