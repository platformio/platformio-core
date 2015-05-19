.. _cmd_ci:

platformio ci
=============

.. contents::

Usage
-----

.. code-block:: bash

    platformio ci [OPTIONS] [SRC]


Description
-----------

`Continuous integration (CI, wiki) <http://en.wikipedia.org/wiki/Continuous_integration>`_
is the practice, in software engineering, of merging all developer working
copies with a shared mainline several times a day.

:ref:`cmd_ci` command is conceived of as "hot key" for building project with
arbitrary source code structure. In a nutshell, using ``SRC`` and
:option:`platformio ci --lib` contents PlatformIO initialises via
:ref:`cmd_init` new project in :option:`platformio ci --build-dir`
with the build environments (using :option:`platformio ci --board` or
:option:`platformio ci --project-conf`) and processes them via :ref:`cmd_run`
command.

:ref:`cmd_ci` command is intended to be used in combination with the build
servers and the popular
`Continuous Integration Software <http://en.wikipedia.org/wiki/Comparison_of_continuous_integration_software>`_.

By integrating regularly, you can detect errors quickly, and locate them more
easily.

.. note::
    :ref:`cmd_ci` command accepts **multiple** ``SRC`` arguments,
    :option:`platformio ci --lib` and :option:`platformio ci --exclude` options
    which can be a path to directory, file or
    `Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_.

.. note::
    You can omit ``SRC`` argument and set path (multiple paths are allowed
    denoting with ``:``) to
    ``PLATFORMIO_CI_SRC`` `Environment variable <http://en.wikipedia.org/wiki/Environment_variable>`_

Options
-------

.. program:: platformio ci

.. option::
    -l, --lib

Source code which will be copied to ``%build_dir%/lib`` directly.

If :option:`platformio ci --lib` is a path to file (not to directory), then
PlatformIO will create temporary directory within ``%build_dir%/lib`` and copy
the rest files into it.


.. option::
    --exclude

Exclude directories and/-or files from :option:`platformio ci --build-dir`. The
path must be relative to PlatformIO project within
:option:`platformio ci --build-dir`.

For example, exclude from project ``src`` directory:

* ``examples`` folder
* ``*.h`` files from ``foo`` folder

.. code-block:: bash

    platformio ci --exclude=src/examples --exclude=src/foo/*.h [SRC]

.. option::
    -b, --board

Build project with automatically pre-generated environments based on board
settings.

For more details please look into :option:`platformio init --board`.

.. option::
    --build-dir

Path to directory where PlatformIO will initialise new project. By default it's
temporary directory within your operation system.

.. note::

    This directory will be removed at the end of build process. If you want to
    keep it, please use :option:`platformio ci --keep-build-dir`.

.. option::
    --keep-build-dir

Don't remove :option:`platformio ci --build-dir` after build process.

.. option::
    --project-conf

Buid project using pre-configured :ref:`projectconf`.

.. option::
    -v, --verbose

Shows details about the results of processing environments. More details
:option:`platformio run --verbose`

By default, verbosity level is set to 1 (only errors will be printed).

Examples
--------

1. Integration `Travis.CI <http://travis-ci.org/>`_, `Shippable <http://shippable.com/>`_ for GitHub
   `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``.travis.yml`` configuration file:

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    env:
        - PLATFORMIO_CI_SRC=examples/Bluetooth/PS3SPP/PS3SPP.ino
        - PLATFORMIO_CI_SRC=examples/pl2303/pl2303_gps/pl2303_gps.ino

    install:
        - python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"
        - pip install --egg http://sourceforge.net/projects/scons/files/latest/download
        - wget https://github.com/xxxajk/spi4teensy3/archive/master.zip -O /tmp/spi4teensy3.zip
        - unzip /tmp/spi4teensy3.zip -d /tmp

    script:
        - platformio ci --lib="." --lib="/tmp/spi4teensy3-master" --board=uno --board=teensy31 --board=due

2. Integration `CircleCI <http://circleci.com/>`_ for GitHub
   `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``circle.yml`` configuration file:

.. code-block:: yaml

    machine:

      environment:
        PLATFORMIO_CI_SRC: examples/Bluetooth/PS3SPP/PS3SPP.ino
        PLATFORMIO_CI_SRC: examples/pl2303/pl2303_gps/pl2303_gps.ino

    dependencies:
      pre:
        - sudo apt-get install python2.7-dev
        - sudo python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"
        - sudo pip install --egg http://sourceforge.net/projects/scons/files/latest/download
        - wget https://github.com/xxxajk/spi4teensy3/archive/master.zip -O /tmp/spi4teensy3.zip
        - unzip /tmp/spi4teensy3.zip -d /tmp
    test:
      override:
        - platformio ci --lib="." --lib="/tmp/spi4teensy3-master" --board=uno --board=teensy31 --board=due

3. Integration `AppVeyor CI <http://appveyor.com/>`_ for GitHub
   `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``appveyor.yml`` configuration file:

.. code-block:: yaml

    build: off
    environment:
      global:
        WITH_COMPILER: "cmd /E:ON /V:ON /C .\\scripts\\appveyor\\run_with_compiler.cmd"
      matrix:
        - PLATFORMIO_CI_SRC: "examples\\Bluetooth\\PS3SPP\\PS3SPP.ino"
          PLATFORMIO_CI_SRC: "examples\\pl2303\\pl2303_gps\\pl2303_gps.ino"
          WINDOWS_SDK_VERSION: "v7.0"
          PYTHON_HOME: "C:\\Python27-x64"
          PYTHON_VERSION: "2.7"
          PYTHON_ARCH: "64"
    init:
      - ps: "ls C:\\Python*"
    install:
      - "git submodule update --init --recursive"
      - "powershell scripts\\appveyor\\install.ps1"
    before_test:
      - cmd: SET PATH=%PATH%;%PYTHON_HOME%;%PYTHON_HOME%\Scripts
      - cmd: git clone https://github.com/xxxajk/spi4teensy3.git c:\spi4teensy
    test_script:
      - "%PYTHON_HOME%\\Scripts\\pip --version"
      - '%WITH_COMPILER% %PYTHON_HOME%\\Scripts\\platformio ci --lib="." --lib="c:\spi4teensy" --board=uno --board=teensy31 --board=due'

The ``run_with_compiler.cmd`` script file:

.. code-block:: none

    @ECHO OFF

    SET COMMAND_TO_RUN=%*
    SET WIN_SDK_ROOT=C:\Program Files\Microsoft SDKs\Windows

    SET MAJOR_PYTHON_VERSION="%PYTHON_VERSION:~0,1%"
    IF %MAJOR_PYTHON_VERSION% == "2" (
        SET WINDOWS_SDK_VERSION="v7.0"
    ) ELSE IF %MAJOR_PYTHON_VERSION% == "3" (
        SET WINDOWS_SDK_VERSION="v7.1"
    ) ELSE (
        ECHO Unsupported Python version: "%MAJOR_PYTHON_VERSION%"
        EXIT 1
    )

    IF "%PYTHON_ARCH%"=="64" (
        ECHO Configuring Windows SDK %WINDOWS_SDK_VERSION% for Python %MAJOR_PYTHON_VERSION% on a 64 bit architecture
        SET DISTUTILS_USE_SDK=1
        SET MSSdk=1
        "%WIN_SDK_ROOT%\%WINDOWS_SDK_VERSION%\Setup\WindowsSdkVer.exe" -q -version:%WINDOWS_SDK_VERSION%
        "%WIN_SDK_ROOT%\%WINDOWS_SDK_VERSION%\Bin\SetEnv.cmd" /x64 /release
        ECHO Executing: %COMMAND_TO_RUN%
        call %COMMAND_TO_RUN% || EXIT 1
    ) ELSE (
        ECHO Using default MSVC build environment for 32 bit architecture
        ECHO Executing: %COMMAND_TO_RUN%
        call %COMMAND_TO_RUN% || EXIT 1
    )


The ``install.ps1`` script file:

.. code-block:: none

    $BASE_URL = "https://www.python.org/ftp/python/"
    $GET_PIP_URL = "https://bootstrap.pypa.io/get-pip.py"
    $GET_PIP_PATH = "C:\get-pip.py"


    function DownloadPython ($python_version, $platform_suffix) {
        $webclient = New-Object System.Net.WebClient
        $filename = "python-" + $python_version + $platform_suffix + ".msi"
        $url = $BASE_URL + $python_version + "/" + $filename

        $basedir = $pwd.Path + "\"
        $filepath = $basedir + $filename
        if (Test-Path $filename) {
            Write-Host "Reusing" $filepath
            return $filepath
        }

        # Download and retry up to 5 times in case of network transient errors.
        Write-Host "Downloading" $filename "from" $url
        $retry_attempts = 3
        for($i=0; $i -lt $retry_attempts; $i++){
            try {
                $webclient.DownloadFile($url, $filepath)
                break
            }
            Catch [Exception]{
                Start-Sleep 1
            }
       }
       Write-Host "File saved at" $filepath
       return $filepath
    }


    function InstallPython ($python_version, $architecture, $python_home) {
        Write-Host "Installing Python" $python_version "for" $architecture "bit architecture to" $python_home
        if (Test-Path $python_home) {
            Write-Host $python_home "already exists, skipping."
            return $false
        }
        if ($architecture -eq "32") {
            $platform_suffix = ""
        } else {
            $platform_suffix = ".amd64"
        }
        $filepath = DownloadPython $python_version $platform_suffix
        Write-Host "Installing" $filepath "to" $python_home
        $args = "/qn /i $filepath TARGETDIR=$python_home"
        Write-Host "msiexec.exe" $args
        Start-Process -FilePath "msiexec.exe" -ArgumentList $args -Wait -Passthru
        Write-Host "Python $python_version ($architecture) installation complete"
        return $true
    }


    function InstallPip ($python_home) {
        $pip_path = $python_home + "/Scripts/pip.exe"
        $python_path = $python_home + "/python.exe"
        if (-not(Test-Path $pip_path)) {
            Write-Host "Installing pip..."
            $webclient = New-Object System.Net.WebClient
            $webclient.DownloadFile($GET_PIP_URL, $GET_PIP_PATH)
            Write-Host "Executing:" $python_path $GET_PIP_PATH
            Start-Process -FilePath "$python_path" -ArgumentList "$GET_PIP_PATH" -Wait -Passthru
        } else {
            Write-Host "pip already installed."
        }
    }

    function InstallPackage ($python_home, $pkg) {
        $pip_path = $python_home + "/Scripts/pip.exe"
        & $pip_path install $pkg
    }

    function InstallScons ($python_home) {
        Write-Host "Start installing Scons"
        $pip_path = $python_home + "/Scripts/pip.exe"
        & $pip_path install --egg "http://sourceforge.net/projects/scons/files/latest/download"
        Write-Host "Scons installed"
    }

    function main () {
        InstallPython $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON_HOME
        InstallPip $env:PYTHON_HOME
        InstallPackage $env:PYTHON_HOME setuptools
        InstallScons $env:PYTHON_HOME
        InstallPackage $env:PYTHON_HOME "https://github.com/platformio/platformio/archive/develop.zip"
    }

    main

3. Integration `Drone CI <http://drone.io/>`_ for GitHub
   `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The project settings:

`Environment Variables`:

.. code-block:: none

    PLATFORMIO_CI_SRC=examples/Bluetooth/PS3SPP/PS3SPP.ino
    PLATFORMIO_CI_SRC=examples/pl2303/pl2303_gps/pl2303_gps.ino

`Commands`:

.. code-block:: none

    pip install --egg http://sourceforge.net/projects/scons/files/latest/download
    python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"
    wget https://github.com/xxxajk/spi4teensy3/archive/master.zip -O /tmp/spi4teensy3.zip
    unzip /tmp/spi4teensy3.zip -d /tmp
    platformio ci --lib="." --lib="/tmp/spi4teensy3-master" --board=uno --board=teensy31 --board=due


