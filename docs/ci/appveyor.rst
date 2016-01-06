..  Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _ci_appveyor:

AppVeyor
========

`AppVeyor <http://www.appveyor.com/about>`_ is an open-source hosted,
distributed continuous integration service used to build and test projects
hosted at `GitHub <http://en.wikipedia.org/wiki/GitHub>`_ on Windows family
systems.

AppVeyor is configured by adding a file named ``appveyor.yml``, which is a
`YAML <http://en.wikipedia.org/wiki/YAML>`_ format text file, to the root
directory of the GitHub repository.

AppVeyor automatically detects when a commit has been made and pushed to a
GitHub repository that is using AppVeyor, and each time this happens, it will
try to build the project using :ref:`cmd_ci` command. This includes commits to
all branches, not just to the master branch. AppVeyor will also build and run
pull requests. When that process has completed, it will notify a developer in
the way it has been configured to do so — for example, by sending an email
containing the build results (showing success or failure), or by posting a
message on an IRC channel. It can be configured to build project on a range of
different :ref:`platforms`.

.. contents::

Integration
-----------

Put ``appveyor.yml`` to the root directory of the GitHub repository.

.. code-block:: yaml

    build: off
    environment:
        global:
            WITH_COMPILER: "cmd /E:ON /V:ON /C .\\scripts\\appveyor\\run_with_compiler.cmd"
        matrix:
            - PLATFORMIO_CI_SRC: "path\\to\\source\\file.c"
              PLATFORMIO_CI_SRC: "path\\to\\source\\file.ino"
              PLATFORMIO_CI_SRC: "path\\to\\source\\directory"
              WINDOWS_SDK_VERSION: "v7.0"
              PYTHON_HOME: "C:\\Python27-x64"
              PYTHON_VERSION: "2.7"
              PYTHON_ARCH: "64"
        install:
          - "git submodule update --init --recursive"
          - "powershell scripts\\appveyor\\install.ps1"
        before_test:
          - cmd: SET PATH=%PATH%;%PYTHON_HOME%;%PYTHON_HOME%\Scripts
        test_script:
          - '%WITH_COMPILER% %PYTHON_HOME%\\Scripts\\platformio ci --board=TYPE_1 --board=TYPE_2 --board=TYPE_N'


Then create ``scripts/appveyor`` folder and put these 2 scripts (they are the
same for the all projects, don't need to modify them):

1. ``scripts/appveyor/install.ps1``:

.. code-block:: PowerShell

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
        $python_path = $python_home + "/python.exe"
        Write-Host "Installing pip..."
        $webclient = New-Object System.Net.WebClient
        $webclient.DownloadFile($GET_PIP_URL, $GET_PIP_PATH)
        Write-Host "Executing:" $python_path $GET_PIP_PATH
        Start-Process -FilePath "$python_path" -ArgumentList "$GET_PIP_PATH" -Wait -Passthru
    }

    function InstallPackage ($python_home, $pkg) {
        $pip_path = $python_home + "/Scripts/pip.exe"
        & $pip_path install -U $pkg
    }

    function main () {
        InstallPython $env:PYTHON_VERSION $env:PYTHON_ARCH $env:PYTHON_HOME
        InstallPip $env:PYTHON_HOME
        InstallPackage $env:PYTHON_HOME setuptools
        InstallPackage $env:PYTHON_HOME platformio
    }

    main

2. ``scripts/appveyor/run_with_compiler.cmd``:

.. code-block:: guess

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

For more details as for PlatformIO build process please look into :ref:`cmd_ci`
command.

Examples
--------

1. Integration for `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
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
        install:
          - "git submodule update --init --recursive"
          - "powershell scripts\\appveyor\\install.ps1"
        before_test:
          - cmd: SET PATH=%PATH%;%PYTHON_HOME%;%PYTHON_HOME%\Scripts
          - cmd: git clone https://github.com/xxxajk/spi4teensy3.git c:\spi4teensy
        test_script:
          - '%WITH_COMPILER% %PYTHON_HOME%\\Scripts\\platformio ci --lib="." --lib="c:\spi4teensy" --board=uno --board=teensy31 --board=due'
