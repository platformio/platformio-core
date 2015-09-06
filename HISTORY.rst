Release History
===============

PlatformIO 2.0
--------------

2.3.1 (2015-09-06)
~~~~~~~~~~~~~~~~~~

* Fixed critical issue when `platformio init --ide <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`__ command hangs PlatformIO
  (`issue #283 <https://github.com/platformio/platformio/issues/283>`_)

2.3.0 (2015-09-05)
~~~~~~~~~~~~~~~~~~

* Added
  `native <http://docs.platformio.org/en/latest/platforms/native.html>`__,
  `linux_arm <http://docs.platformio.org/en/latest/platforms/linux_arm.html>`__,
  `linux_i686 <http://docs.platformio.org/en/latest/platforms/linux_i686.html>`__,
  `linux_x86_64 <http://docs.platformio.org/en/latest/platforms/linux_x86_64.html>`__,
  `windows_x86 <http://docs.platformio.org/en/latest/platforms/windows_x86.html>`__
  development platforms
  (`issue #263 <https://github.com/platformio/platformio/issues/263>`_)
* Added `PlatformIO Demo <http://docs.platformio.org/en/latest/demo.html>`_
  page to documentation
* Simplified `installation <http://docs.platformio.org/en/latest/installation.html>`__
  process of PlatformIO
  (`issue #274 <https://github.com/platformio/platformio/issues/274>`_)
* Significantly improved `Project Generator <http://docs.platformio.org/en/latest/userguide/cmd_init.html#cmdoption-platformio-init--ide>`__ which allows to integrate with `the most popular
  IDE <http://docs.platformio.org/en/latest/ide.html>`__
* Added short ``-h`` help option for PlatformIO and sub-commands
* Updated `mbed <http://docs.platformio.org/en/latest/frameworks/mbed.html>`__
  framework
* Updated ``tool-teensy`` package for `Teensy <http://docs.platformio.org/en/latest/platforms/teensy.html>`__
  platform
  (`issue #268 <https://github.com/platformio/platformio/issues/268>`_)
* Added FAQ answer when `Program "platformio" not found in PATH <http://docs.platformio.org/en/latest/faq.html#faq-troubleshooting-pionotfoundinpath>`_
  (`issue #272 <https://github.com/platformio/platformio/issues/272>`_)
* Generate "readme.txt" for project "lib" directory
  (`issue #273 <https://github.com/platformio/platformio/issues/273>`_)
* Use toolchain's includes pattern ``include*`` for Project Generator
  (`issue #277 <https://github.com/platformio/platformio/issues/277>`_)
* Added support for Adafruit Gemma board to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform
  (`pull #256 <https://github.com/platformio/platformio/pull/256>`_)
* Fixed includes list for Windows OS when generating project for `Eclipse IDE <http://docs.platformio.org/en/latest/ide/eclipse.html>`__
  (`issue #270 <https://github.com/platformio/platformio/issues/270>`_)
* Fixed ``AttributeError: 'module' object has no attribute 'packages'``
  (`issue #252 <https://github.com/platformio/platformio/issues/252>`_)

2.2.2 (2015-07-30)
~~~~~~~~~~~~~~~~~~

* Integration with `Atom IDE <http://docs.platformio.org/en/latest/ide/atom.html>`__
* Support for off-line/unpublished/private libraries
  (`issue #260 <https://github.com/platformio/platformio/issues/260>`_)
* Disable project auto-clean while building/uploading firmware using
  `platformio run --disable-auto-clean <http://docs.platformio.org/en/latest/userguide/cmd_run.html#cmdoption--disable-auto-clean>`_ option
  (`issue #255 <https://github.com/platformio/platformio/issues/255>`_)
* Show internal errors from "Miniterm" using `platformio serialports monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`__ command
  (`issue #257 <https://github.com/platformio/platformio/issues/257>`_)
* Fixed `platformio serialports monitor --help <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`__ information with HEX char for hotkeys
  (`issue #253 <https://github.com/platformio/platformio/issues/253>`_)
* Handle "OSError: [Errno 13] Permission denied" for PlatformIO installer script
  (`issue #254 <https://github.com/platformio/platformio/issues/254>`_)

2.2.1 (2015-07-17)
~~~~~~~~~~~~~~~~~~

* Project generator for `CLion IDE <http://docs.platformio.org/en/latest/ide/clion.html>`__
  (`issue #132 <https://github.com/platformio/platformio/issues/132>`_)
* Updated ``tool-bossac`` package to 1.5 version for `atmelsam <http://docs.platformio.org/en/latest/platforms/atmelsam.html>`__ platform
  (`issue #251 <https://github.com/platformio/platformio/issues/251>`_)
* Updated ``sdk-esp8266`` package for `espressif <http://docs.platformio.org/en/latest/platforms/espressif.html>`__ platform
* Fixed incorrect arguments handling for `platformio serialports monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ command
  (`issue #248 <https://github.com/platformio/platformio/issues/248>`_)

2.2.0 (2015-07-01)
~~~~~~~~~~~~~~~~~~

* Allowed to exclude/include source files from build process using
  `src_filter <http://docs.platformio.org/en/latest/projectconf.html#src-filter>`__
  (`issue #240 <https://github.com/platformio/platformio/issues/240>`_)
* Launch own extra script before firmware building/uploading processes
  (`issue #239 <https://github.com/platformio/platformio/issues/239>`_)
* Specify own path to the linker script (ld) using
  `build_flags <http://docs.platformio.org/en/latest/projectconf.html#build-flags>`__
  option
  (`issue #233 <https://github.com/platformio/platformio/issues/233>`_)
* Specify library compatibility with the all platforms/frameworks
  using ``*`` symbol in
  `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`__
* Added support for new embedded boards: *ST 32L0538DISCOVERY and Delta DFCM-NNN40*
  to `Framework mbed <http://docs.platformio.org/en/latest/frameworks/mbed.html>`__
* Updated packages for
  `Framework Arduino (AVR, SAM, Espressif and Teensy cores <http://docs.platformio.org/en/latest/frameworks/arduino.html>`__,
  `Framework mbed <http://docs.platformio.org/en/latest/frameworks/mbed.html>`__,
  `Espressif ESP8266 SDK <http://docs.platformio.org/en/latest/platforms/espressif.html>`__
  (`issue #246 <https://github.com/platformio/platformio/issues/246>`_)
* Fixed ``stk500v2_command(): command failed``
  (`issue #238 <https://github.com/platformio/platformio/issues/238>`_)
* Fixed IDE project generator when board is specified
  (`issue #242 <https://github.com/platformio/platformio/issues/242>`_)
* Fixed relative path for includes when generating project for IDE
  (`issue #243 <https://github.com/platformio/platformio/issues/243>`_)
* Fixed ESP8266 native SDK exception
  (`issue #245 <https://github.com/platformio/platformio/issues/245>`_)

2.1.2 (2015-06-21)
~~~~~~~~~~~~~~~~~~

* Fixed broken link to SCons installer

2.1.1 (2015-06-09)
~~~~~~~~~~~~~~~~~~

* Automatically detect upload port using VID:PID board settings
  (`issue #231 <https://github.com/platformio/platformio/issues/231>`_)
* Improved detection of build changes
* Avoided ``LibInstallDependencyError`` when more then 1 library is found
  (`issue #229 <https://github.com/platformio/platformio/issues/229>`_)

2.1.0 (2015-06-03)
~~~~~~~~~~~~~~~~~~

* Added Silicon Labs EFM32 `siliconlabsefm32 <http://docs.platformio.org/en/latest/platforms/siliconlabsefm32.html>`_
  development platform
  (`issue #226 <https://github.com/platformio/platformio/issues/226>`_)
* Integrate PlatformIO with `Circle CI <https://circleci.com>`_ and
  `Shippable CI <https://shippable.com>`_
* Described in documentation how to `create/register own board <http://docs.platformio.org/en/latest/platforms/creating_board.html>`_ for PlatformIO
* Disabled "nano.specs" for ARM-based platforms
  (`issue #219 <https://github.com/platformio/platformio/issues/219>`_)
* Fixed "ConnectionError" when PlatformIO SF Storage is off-line
* Fixed resolving of C/C++ std libs by Eclipse IDE
  (`issue #220 <https://github.com/platformio/platformio/issues/220>`_)
* Fixed firmware uploading using USB programmer (USBasp) for
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html>`_
  platform
  (`issue #221 <https://github.com/platformio/platformio/issues/221>`_)

2.0.2 (2015-05-27)
~~~~~~~~~~~~~~~~~~

* Fixed libraries order for "Library Dependency Finder" under Linux OS

2.0.1 (2015-05-27)
~~~~~~~~~~~~~~~~~~

* Handle new environment variable
  `PLATFORMIO_BUILD_FLAGS <http://docs.platformio.org/en/latest/envvars.html#platformio-build-flags>`_
* Pass to API requests information about Continuous Integration system. This
  information will be used by PlatformIO-API.
* Use ``include`` directories from toolchain when initialising project for IDE
  (`issue #210 <https://github.com/platformio/platformio/issues/210>`_)
* Added support for new WildFire boards from
  `Wicked Device <http://wickeddevice.com>`_ to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform
* Updated `Arduino Framework <http://docs.platformio.org/en/latest/frameworks/arduino.html>`__ to
  1.6.4 version (`issue #212 <https://github.com/platformio/platformio/issues/212>`_)
* Handle Atmel AVR Symbols when initialising project for IDE
  (`issue #216 <https://github.com/platformio/platformio/issues/216>`_)
* Fixed bug with converting ``*.ino`` to ``*.cpp``
* Fixed failing with ``platformio init --ide eclipse`` without boards
  (`issue #217 <https://github.com/platformio/platformio/issues/217>`_)

2.0.0 (2015-05-22)
~~~~~~~~~~~~~~~~~~

*Made in* `Paradise <https://twitter.com/ikravets/status/592356377185619969>`_

* PlatformIO as `Continuous Integration <http://docs.platformio.org/en/latest/ci/index.html>`_
  (CI) tool for embedded projects
  (`issue #108 <https://github.com/platformio/platformio/issues/108>`_)
* Initialise PlatformIO project for the specified IDE
  (`issue #151 <https://github.com/platformio/platformio/issues/151>`_)
* PlatformIO CLI 2.0: "platform" related commands have been
  moved to ``platformio platforms`` subcommand
  (`issue #158 <https://github.com/platformio/platformio/issues/158>`_)
* Created `PlatformIO gitter.im <https://gitter.im/platformio/platformio>`_ room
  (`issue #174 <https://github.com/platformio/platformio/issues/174>`_)
* Global ``-f, --force`` option which will force to accept any
  confirmation prompts
  (`issue #152 <https://github.com/platformio/platformio/issues/152>`_)
* Run project with `platformio run --project-dir <http://docs.platformio.org/en/latest/userguide/cmd_run.html#cmdoption--project-dir>`_ option without changing the current working
  directory
  (`issue #192 <https://github.com/platformio/platformio/issues/192>`_)
* Control verbosity of `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html#cmdoption-platformio-run-v>`_ command via ``-v/--verbose`` option
* Add library dependencies for build environment using
  `lib_install <http://docs.platformio.org/en/latest/projectconf.html#lib-install>`_
  option in ``platformio.ini``
  (`issue #134 <https://github.com/platformio/platformio/issues/134>`_)
* Specify libraries which are compatible with build environment using
  `lib_use <http://docs.platformio.org/en/latest/projectconf.html#lib-use>`_
  option in ``platformio.ini``
  (`issue #148 <https://github.com/platformio/platformio/issues/148>`_)
* Add more boards to PlatformIO project with
  `platformio init --board <http://docs.platformio.org/en/latest/userguide/cmd_init.html#cmdoption--board>`__
  command
  (`issue #167 <https://github.com/platformio/platformio/issues/167>`_)
* Choose which library to update
  (`issue #168 <https://github.com/platformio/platformio/issues/168>`_)
* Specify `platformio init --env-prefix <http://docs.platformio.org/en/latest/userguide/cmd_init.html#cmdoption--env-prefix>`__ when initialise/update project
  (`issue #182 <https://github.com/platformio/platformio/issues/182>`_)
* Added new Armstrap boards
  (`issue #204 <https://github.com/platformio/platformio/issues/204>`_)
* Updated SDK for `espressif <http://docs.platformio.org/en/latest/platforms/espressif.html>`__
  development platform to v1.1
  (`issue #179 <https://github.com/platformio/platformio/issues/179>`_)
* Disabled automatic updates by default for platforms, packages and libraries
  (`issue #171 <https://github.com/platformio/platformio/issues/171>`_)
* Fixed bug with creating copies of source files
  (`issue #177 <https://github.com/platformio/platformio/issues/177>`_)

PlatformIO 1.0
--------------

1.5.0 (2015-05-15)
~~~~~~~~~~~~~~~~~~

* Added support of `Framework mbed <http://platformio.org/#!/frameworks/mbed>`_
  for Teensy 3.1
  (`issue #183 <https://github.com/platformio/platformio/issues/183>`_)
* Added GDB as alternative uploader to `ststm32 <http://docs.platformio.org/en/latest/platforms/ststm32.html>`__ platform
  (`issue #175 <https://github.com/platformio/platformio/issues/174>`_)
* Added `examples <https://github.com/platformio/platformio/tree/develop/examples>`__
  with preconfigured IDE projects
  (`issue #154 <https://github.com/platformio/platformio/issues/154>`_)
* Fixed firmware uploading under Linux OS for Arduino Leonardo board
  (`issue #178 <https://github.com/platformio/platformio/issues/178>`_)
* Fixed invalid "mbed" firmware for Nucleo F411RE
  (`issue #185 <https://github.com/platformio/platformio/issues/185>`_)
* Fixed parsing of includes for PlatformIO Library Dependency Finder
  (`issue #189 <https://github.com/platformio/platformio/issues/189>`_)
* Fixed handling symbolic links within source code directory
  (`issue #190 <https://github.com/platformio/platformio/issues/190>`_)
* Fixed cancelling any previous definition of name, either built in or provided
  with a ``-D`` option
  (`issue #191 <https://github.com/platformio/platformio/issues/191>`_)

1.4.0 (2015-04-11)
~~~~~~~~~~~~~~~~~~

* Added `espressif <http://docs.platformio.org/en/latest/platforms/espressif.html>`_
  development platform with ESP01 board
* Integrated PlatformIO with AppVeyor Windows based Continuous Integration system
  (`issue #149 <https://github.com/platformio/platformio/issues/149>`_)
* Added support for Teensy LC board to
  `teensy <http://docs.platformio.org/en/latest/platforms/teensy.html>`__
  platform
* Added support for new Arduino based boards by *SparkFun, BQ, LightUp,
  LowPowerLab, Quirkbot, RedBearLab, TinyCircuits* to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform
* Upgraded `Arduino Framework <http://docs.platformio.org/en/latest/frameworks/arduino.html>`__ to
  1.6.3 version (`issue #156 <https://github.com/platformio/platformio/issues/156>`_)
* Upgraded `Energia Framework <http://docs.platformio.org/en/latest/frameworks/energia.html>`__ to
  0101E0015 version (`issue #146 <https://github.com/platformio/platformio/issues/146>`_)
* Upgraded `Arduino Framework with Teensy Core <http://docs.platformio.org/en/latest/frameworks/arduino.html>`_
  to 1.22 version
  (`issue #162 <https://github.com/platformio/platformio/issues/162>`_,
  `issue #170 <https://github.com/platformio/platformio/issues/170>`_)
* Fixed exceptions with PlatformIO auto-updates when Internet connection isn't
  active


1.3.0 (2015-03-27)
~~~~~~~~~~~~~~~~~~

* Moved PlatformIO source code and repositories from `Ivan Kravets <https://github.com/ivankravets>`_
  account to `PlatformIO Organisation <https://github.com/platformio>`_
  (`issue #138 <https://github.com/platformio/platformio/issues/138>`_)
* Added support for new Arduino based boards by *SparkFun, RepRap, Sanguino* to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform
  (`issue #127 <https://github.com/platformio/platformio/issues/127>`_,
  `issue #131 <https://github.com/platformio/platformio/issues/131>`_)
* Added integration instructions for `Visual Studio <http://docs.platformio.org/en/latest/ide/visualstudio.html>`_
  and `Sublime Text <http://docs.platformio.org/en/latest/ide/sublimetext.html>`_ IDEs
* Improved handling of multi-file ``*.ino/pde`` sketches
  (`issue #130 <https://github.com/platformio/platformio/issues/130>`_)
* Fixed wrong insertion of function prototypes converting ``*.ino/pde``
  (`issue #137 <https://github.com/platformio/platformio/issues/137>`_,
  `issue #140 <https://github.com/platformio/platformio/issues/140>`_)



1.2.0 (2015-03-20)
~~~~~~~~~~~~~~~~~~

* Added full support of `mbed <http://docs.platformio.org/en/latest/frameworks/mbed.html>`__
  framework including libraries: *RTOS, Ethernet, DSP, FAT, USB*.
* Added `freescalekinetis <http://docs.platformio.org/en/latest/platforms/freescalekinetis.html>`_
  development platform with Freescale Kinetis Freedom boards
* Added `nordicnrf51 <http://docs.platformio.org/en/latest/platforms/nordicnrf51.html>`_
  development platform with supported boards from *JKSoft, Nordic, RedBearLab,
  Switch Science*
* Added `nxplpc <http://docs.platformio.org/en/latest/platforms/nxplpc.html>`_
  development platform with supported boards from *CQ Publishing, Embedded
  Artists, NGX Technologies, NXP, Outrageous Circuits, SeeedStudio,
  Solder Splash Labs, Switch Science, u-blox*
* Added support for *ST Nucleo* boards to
  `ststm32 <http://docs.platformio.org/en/latest/platforms/ststm32.html>`__
  development platform
* Created new `Frameworks <http://docs.platformio.org/en/latest/frameworks/index.html>`__
  page in documentation and added to `PlatformIO Web Site <http://platformio.org>`_
  (`issue #115 <https://github.com/platformio/platformio/issues/115>`_)
* Introduced online `Embedded Boards Explorer <http://platformio.org/#!/boards>`_
* Automatically append define ``-DPLATFORMIO=%version%`` to
  builder (`issue #105 <https://github.com/platformio/platformio/issues/105>`_)
* Renamed ``stm32`` development platform to
  `ststm32 <http://docs.platformio.org/en/latest/platforms/ststm32.html>`__
* Renamed ``opencm3`` framework to
  `libopencm3 <http://docs.platformio.org/en/latest/frameworks/libopencm3.html>`__
* Fixed uploading for `atmelsam <http://docs.platformio.org/en/latest/platforms/atmelsam.html>`__
  development platform
* Fixed re-arranging the ``*.ino/pde`` files when converting to ``*.cpp``
  (`issue #100 <https://github.com/platformio/platformio/issues/100>`_)

1.1.0 (2015-03-05)
~~~~~~~~~~~~~~~~~~

* Implemented ``PLATFORMIO_*`` environment variables
  (`issue #102 <https://github.com/platformio/platformio/issues/102>`_)
* Added support for *SainSmart* boards to
  `atmelsam <http://docs.platformio.org/en/latest/platforms/atmelsam.html#boards>`__
  development platform
* Added
  `Project Configuration <http://docs.platformio.org/en/latest/projectconf.html>`__
  option named `envs_dir <http://docs.platformio.org/en/latest/projectconf.html#envs-dir>`__
* Disabled "prompts" automatically for *Continuous Integration* systems
  (`issue #103 <https://github.com/platformio/platformio/issues/103>`_)
* Fixed firmware uploading for
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  boards which work within ``usbtiny`` protocol
* Fixed uploading for *Digispark* board (`issue #106 <https://github.com/platformio/platformio/issues/106>`_)

1.0.1 (2015-02-27)
~~~~~~~~~~~~~~~~~~

**PlatformIO 1.0 - recommended for production**

* Changed development status from ``beta`` to ``Production/Stable``
* Added support for *ARM*-based credit-card sized computers:
  `Raspberry Pi <http://www.raspberrypi.org>`_,
  `BeagleBone <http://beagleboard.org>`_ and `CubieBoard <http://cubieboard.org>`_
* Added `atmelsam <http://docs.platformio.org/en/latest/platforms/atmelsam.html>`__
  development platform with supported boards: *Arduino Due and Digistump DigiX*
  (`issue #71 <https://github.com/platformio/platformio/issues/71>`_)
* Added `ststm32 <http://docs.platformio.org/en/latest/platforms/ststm32.html>`__
  development platform with supported boards: *Discovery kit for STM32L151/152,
  STM32F303xx, STM32F407/417 lines* and `libOpenCM3 Framework <http://www.libopencm3.org>`_
  (`issue #73 <https://github.com/platformio/platformio/issues/73>`_)
* Added `teensy <http://docs.platformio.org/en/latest/platforms/teensy.html>`_
  development platform with supported boards: *Teensy 2.x & 3.x*
  (`issue #72 <https://github.com/platformio/platformio/issues/72>`_)
* Added new *Arduino* boards to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform: *Arduino NG, Arduino BT, Arduino Esplora, Arduino Ethernet,
  Arduino Robot Control, Arduino Robot Motor and Arduino Yun*
* Added support for *Adafruit* boards to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform: *Adafruit Flora and Adafruit Trinkets*
  (`issue #65 <https://github.com/platformio/platformio/issues/65>`_)
* Added support for *Digispark* boards to
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#boards>`__
  platform: *Digispark USB Development Board and Digispark Pro*
  (`issue #47 <https://github.com/platformio/platformio/issues/47>`_)
* Covered code with tests (`issue #2 <https://github.com/platformio/platformio/issues/2>`_)
* Refactored *Library Dependency Finder* (issues
  `#48 <https://github.com/platformio/platformio/issues/48>`_,
  `#50 <https://github.com/platformio/platformio/issues/50>`_,
  `#55 <https://github.com/platformio/platformio/pull/55>`_)
* Added `src_dir <http://docs.platformio.org/en/latest/projectconf.html#src-dir>`__
  option to ``[platformio]`` section of
  `platformio.ini <http://docs.platformio.org/en/latest/projectconf.html>`__
  which allows to redefine location to project's source directory
  (`issue #83 <https://github.com/platformio/platformio/issues/83>`_)
* Added ``--json-output`` option to
  `platformio boards <http://docs.platformio.org/en/latest/userguide/cmd_boards.html>`__
  and `platformio search <http://docs.platformio.org/en/latest/userguide/cmd_search.html>`__
  commands which allows to return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format
  (`issue #42 <https://github.com/platformio/platformio/issues/42>`_)
* Allowed to ignore some libs from *Library Dependency Finder* via
  `lib_ignore <http://docs.platformio.org/en/latest/projectconf.html#lib-ignore>`_ option
* Improved `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  command: asynchronous output for build process, timing and detailed
  information about environment configuration
  (`issue #74 <https://github.com/platformio/platformio/issues/74>`_)
* Output compiled size and static memory usage with
  `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  command (`issue #59 <https://github.com/platformio/platformio/issues/59>`_)
* Updated `framework-arduino` AVR & SAM to 1.6 stable version
* Fixed an issue with the libraries that are git repositories
  (`issue #49 <https://github.com/platformio/platformio/issues/49>`_)
* Fixed handling of assembly files
  (`issue #58 <https://github.com/platformio/platformio/issues/58>`_)
* Fixed compiling error if space is in user's folder
  (`issue #56 <https://github.com/platformio/platformio/issues/56>`_)
* Fixed `AttributeError: 'module' object has no attribute 'disable_warnings'`
  when a version of `requests` package is less then 2.4.0
* Fixed bug with invalid process's "return code" when PlatformIO has internal
  error (`issue #81 <https://github.com/platformio/platformio/issues/81>`_)
* Several bug fixes, increased stability and performance improvements

PlatformIO 0.0
--------------

0.10.2 (2015-01-06)
~~~~~~~~~~~~~~~~~~~

* Fixed an issue with ``--json-output``
  (`issue #42 <https://github.com/platformio/platformio/issues/42>`_)
* Fixed an exception during
  `platformio upgrade <http://docs.platformio.org/en/latest/userguide/cmd_upgrade.html>`__
  under Windows OS (`issue #45 <https://github.com/platformio/platformio/issues/45>`_)

0.10.1 (2015-01-02)
~~~~~~~~~~~~~~~~~~~

* Added ``--json-output`` option to
  `platformio list <http://docs.platformio.org/en/latest/userguide/cmd_list.html>`__,
  `platformio serialports list <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html>`__ and
  `platformio lib list <http://docs.platformio.org/en/latest/userguide/lib/cmd_list.html>`__
  commands which allows to return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format
  (`issue #42 <https://github.com/platformio/platformio/issues/42>`_)
* Fixed missing auto-uploading by default after `platformio init <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`__
  command

0.10.0 (2015-01-01)
~~~~~~~~~~~~~~~~~~~

**Happy New Year!**

* Implemented `platformio boards <http://docs.platformio.org/en/latest/userguide/cmd_boards.html>`_
  command (`issue #11 <https://github.com/platformio/platformio/issues/11>`_)
* Added support of *Engduino* boards for
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html#engduino>`__
  platform (`issue #38 <https://github.com/platformio/platformio/issues/38>`_)
* Added ``--board`` option to `platformio init <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`__
  command which allows to initialise project with the specified embedded boards
  (`issue #21 <https://github.com/platformio/platformio/issues/21>`_)
* Added `example with uploading firmware <http://docs.platformio.org/en/latest/projectconf.html#examples>`_
  via USB programmer (USBasp) for
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html>`_
  *MCUs* (`issue #35 <https://github.com/platformio/platformio/issues/35>`_)
* Automatic detection of port on `platformio serialports monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_
  (`issue #37 <https://github.com/platformio/platformio/issues/37>`_)
* Allowed auto-installation of platforms when prompts are disabled (`issue #43 <https://github.com/platformio/platformio/issues/43>`_)
* Fixed urllib3's *SSL* warning under Python <= 2.7.2 (`issue #39 <https://github.com/platformio/platformio/issues/39>`_)
* Fixed bug with *Arduino USB* boards (`issue #40 <https://github.com/platformio/platformio/issues/40>`_)

0.9.2 (2014-12-10)
~~~~~~~~~~~~~~~~~~

* Replaced "dark blue" by "cyan" colour for the texts (`issue #33 <https://github.com/platformio/platformio/issues/33>`_)
* Added new setting `enable_prompts <http://docs.platformio.org/en/latest/userguide/cmd_settings.html>`_
  and allowed to disable all *PlatformIO* prompts (useful for cloud compilers)
  (`issue #34 <https://github.com/platformio/platformio/issues/34>`_)
* Fixed compilation bug on *Windows* with installed *MSVC* (`issue #18 <https://github.com/platformio/platformio/issues/18>`_)

0.9.1 (2014-12-05)
~~~~~~~~~~~~~~~~~~

* Ask user to install platform (when it hasn't been installed yet) within
  `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  and `platformio show <http://docs.platformio.org/en/latest/userguide/cmd_show.html>`_ commands
* Improved main `documentation <http://docs.platformio.org>`_
* Fixed "*OSError: [Errno 2] No such file or directory*" within
  `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`__
  command when PlatformIO isn't installed properly
* Fixed example for `Eclipse IDE with Tiva board <https://github.com/platformio/platformio/tree/develop/examples/ide/eclipse>`_
  (`issue #32 <https://github.com/platformio/platformio/pull/32>`_)
* Upgraded `Eclipse Project Examples <https://github.com/platformio/platformio/tree/develop/examples/ide/eclipse>`_
  to latest *Luna* and *PlatformIO* releases

0.9.0 (2014-12-01)
~~~~~~~~~~~~~~~~~~

* Implemented `platformio settings <http://docs.platformio.org/en/latest/userguide/cmd_settings.html>`_ command
* Improved `platformio init <http://docs.platformio.org/en/latest/userguide/cmd_init.html>`_ command.
  Added new option ``--project-dir`` where you can specify another path to
  directory where new project will be initialized (`issue #31 <https://github.com/platformio/platformio/issues/31>`_)
* Added *Migration Manager* which simplifies process with upgrading to a
  major release
* Added *Telemetry Service* which should help us make *PlatformIO* better
* Implemented *PlatformIO AppState Manager* which allow to have multiple
  ``.platformio`` states.
* Refactored *Package Manager*
* Download Manager: fixed SHA1 verification within *Cygwin Environment*
  (`issue #26 <https://github.com/platformio/platformio/issues/26>`_)
* Fixed bug with code builder and built-in Arduino libraries
  (`issue #28 <https://github.com/platformio/platformio/issues/28>`_)

0.8.0 (2014-10-19)
~~~~~~~~~~~~~~~~~~

* Avoided trademark issues in `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`_
  with the new fields: `frameworks <http://docs.platformio.org/en/latest/librarymanager/config.html#frameworks>`_,
  `platforms <http://docs.platformio.org/en/latest/librarymanager/config.html#platforms>`_
  and `dependencies <http://docs.platformio.org/en/latest/librarymanager/config.html#dependencies>`_
  (`issue #17 <https://github.com/platformio/platformio/issues/17>`_)
* Switched logic from "Library Name" to "Library Registry ID" for all
  `platformio lib <http://docs.platformio.org/en/latest/userguide/lib/index.html>`_
  commands (install, uninstall, update and etc.)
* Renamed ``author`` field to `authors <http://docs.platformio.org/en/latest/librarymanager/config.html#authors>`_
  and allowed to setup multiple authors per library in `library.json <http://docs.platformio.org/en/latest/librarymanager/config.html>`_
* Added option to specify "maintainer" status in `authors <http://docs.platformio.org/en/latest/librarymanager/config.html#authors>`_ field
* New filters/options for `platformio lib search <http://docs.platformio.org/en/latest/userguide/lib/cmd_search.html>`_
  command: ``--framework`` and ``--platform``

0.7.1 (2014-10-06)
~~~~~~~~~~~~~~~~~~

* Fixed bug with order for includes in conversation from INO/PDE to CPP
* Automatic detection of port on upload (`issue #15 <https://github.com/platformio/platformio/issues/15>`_)
* Fixed lib update crashing when no libs are installed (`issue #19 <https://github.com/platformio/platformio/issues/19>`_)


0.7.0 (2014-09-24)
~~~~~~~~~~~~~~~~~~

* Implemented new `[platformio] <http://docs.platformio.org/en/latest/projectconf.html#platformio>`_
  section for Configuration File with `home_dir <http://docs.platformio.org/en/latest/projectconf.html#home-dir>`_
  option (`issue #14 <https://github.com/platformio/platformio/issues/14>`_)
* Implemented *Library Manager* (`issue #6 <https://github.com/platformio/platformio/issues/6>`_)

0.6.0 (2014-08-09)
~~~~~~~~~~~~~~~~~~

* Implemented `platformio serialports monitor <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html#platformio-serialports-monitor>`_ (`issue #10 <https://github.com/platformio/platformio/issues/10>`_)
* Fixed an issue ``ImportError: No module named platformio.util`` (`issue #9 <https://github.com/platformio/platformio/issues/9>`_)
* Fixed bug with auto-conversation from Arduino \*.ino to \*.cpp

0.5.0 (2014-08-04)
~~~~~~~~~~~~~~~~~~

* Improved nested lookups for libraries
* Disabled default warning flag "-Wall"
* Added auto-conversation from \*.ino to valid \*.cpp for Arduino/Energia
  frameworks (`issue #7 <https://github.com/platformio/platformio/issues/7>`_)
* Added `Arduino example <https://github.com/platformio/platformio/tree/develop/examples/>`_
  with external library (*Adafruit CC3000*)
* Implemented `platformio upgrade <http://docs.platformio.org/en/latest/userguide/cmd_upgrade.html>`_
  command and "auto-check" for the latest
  version (`issue #8 <https://github.com/platformio/platformio/issues/8>`_)
* Fixed an issue with "auto-reset" for *Raspduino* board
* Fixed a bug with nested libs building

0.4.0 (2014-07-31)
~~~~~~~~~~~~~~~~~~

* Implemented `platformio serialports <http://docs.platformio.org/en/latest/userguide/cmd_serialports.html>`_ command
* Allowed to put special build flags only for ``src`` files via
  `src_build_flags <http://docs.platformio.org/en/latest/projectconf.html#src_build-flags>`_
  environment option
* Allowed to override some of settings via system environment variables
  such as: ``PLATFORMIO_SRC_BUILD_FLAGS`` and ``PLATFORMIO_ENVS_DIR``
* Added ``--upload-port`` option for `platformio run <http://docs.platformio.org/en/latest/userguide/cmd_run.html#cmdoption--upload-port>`__ command
* Implemented (especially for `SmartAnthill <http://docs.smartanthill.ikravets.com/>`_)
  `platformio run -t uploadlazy <http://docs.platformio.org/en/latest/userguide/cmd_run.html>`_
  target (no dependencies to framework libs, ELF and etc.)
* Allowed to skip default packages via `platformio install --skip-default-package <http://docs.platformio.org/en/latest/userguide/cmd_install.html#cmdoption--skip-default>`_
  option
* Added tools for *Raspberry Pi* platform
* Added support for *Microduino* and *Raspduino* boards in
  `atmelavr <http://docs.platformio.org/en/latest/platforms/atmelavr.html>`_ platform


0.3.1 (2014-06-21)
~~~~~~~~~~~~~~~~~~

* Fixed auto-installer for Windows OS (bug with %PATH% customisations)


0.3.0 (2014-06-21)
~~~~~~~~~~~~~~~~~~

* Allowed to pass multiple "SomePlatform" to install/uninstall commands
* Added "IDE Integration" section to README with Eclipse project examples
* Created auto installer script for *PlatformIO* (`issue #3 <https://github.com/platformio/platformio/issues/3>`_)
* Added "Super-Quick" way to Installation section (README)
* Implemented "build_flags" option for environments (`issue #4 <https://github.com/platformio/platformio/issues/4>`_)


0.2.0 (2014-06-15)
~~~~~~~~~~~~~~~~~~

* Resolved `issue #1 "Build referred libraries" <https://github.com/platformio/platformio/issues/1>`_
* Renamed project's "libs" directory to "lib"
* Added `arduino-internal-library <https://github.com/platformio/platformio/tree/develop/examples/>`_ example
* Changed to beta status


0.1.0 (2014-06-13)
~~~~~~~~~~~~~~~~~~

* Birth! First alpha release
