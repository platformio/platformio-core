..  Copyright 2014-present Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _cmd_platform_install:

platformio platform install
===========================

.. contents::

Usage
-----

.. code-block:: bash

    # install platform by name
    platformio platform install [OPTIONS] [PLATFORM...]

    # install specific platform version using Semantic Versioning
    platformio platform install [OPTIONS] PLATFORM@X.Y.Z

    # install platform using URL
    platformio platform install [OPTIONS] URL


Description
-----------

Install :ref:`platforms` and dependent packages.

There are several predefined aliases for packages, such as:

* ``framework``
* ``toolchain``
* ``uploader``

Local
~~~~~

PlatformIO supports installing development platform from local directory or
archive. Need to use ``file://`` prefix before local path. Also, platform
directory or archive should contain ``platform.json`` manifest.

* ``file:///local/path/to/the/platform/dir``
* ``file:///local/path/to/the/platform.zip``
* ``file:///local/path/to/the/platform.tar.gz``

Remote
~~~~~~

VCS
~~~

PlatformIO supports installing from Git, Mercurial and Subversion, and detects
the type of VCS using url prefixes: "git+", "hg+", or "svn+".

PlatformIO requires a working VCS command on your path: git, hg or svn.

Git
^^^

The supported schemes are: ``git``, ``git+https`` and ``git+ssh``. Here are
the supported forms:

* https://github.com/platformio/platform-NAME.git
* git+git://git.server.org/my-platform
* git+https://git.server.org/my-platform
* git+ssh://git.server.org/my-platform

Passing branch names, a commit hash or a tag name is possible like so:

* https://github.com/platformio/platform-name.git#master
* git+git://git.server.org/my-platform#master
* git+https://git.server.org/my-platform#v1.0
* git+ssh://git.server.org/my-platform#7846d8ad52f983f2f2887bdc0f073fe9755a806d

Mercurial
^^^^^^^^^

The supported schemes are: ``hg+http``, ``hg+https`` and ``hg+ssh``. Here are
the supported forms:

* hg+hg://hg.server.org/my-platform
* hg+https://hg.server.org/my-platform
* hg+ssh://hg.server.org/my-platform

Passing branch names, a commit hash or a tag name is possible like so:

* hg+hg://hg.server.org/my-platform#master
* hg+https://hg.server.org/my-platform#v1.0
* hg+ssh://hg.server.org/my-platform#4cfe2fa00668

Subversion
^^^^^^^^^^

The supported schemes are: ``svn``, ``svn+svn``, ``svn+http``, ``svn+https``
and ``svn+ssh``. Here are the supported forms:

* svn+svn://svn.server.org/my-platform
* svn+https://svn.server.org/my-platform
* svn+ssh://svn.server.org/my-platform

You can also give specific revisions to an SVN URL, like so:

* svn+svn://svn.server.org/my-platform#13

Options
-------

.. program:: platformio platform install

.. option::
    --with-package

Install specified package (or alias)


.. option::
    --without-package

Do not install specified package (or alias)

.. option::
    --skip-default

Skip default packages

Examples
--------

1. Install :ref:`platform_atmelavr` with default packages

.. code-block:: bash

    $ platformio platform install atmelavr
    PlatformManager: Installing atmelavr
    Downloading...
    Unpacking  [####################################]  100%
    atmelavr @ 0.0.0 has been successfully installed!
    PackageManager: Installing tool-scons @ >=2.3.0,<2.6.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    tool-scons @ 2.4.1 has been successfully installed!
    PackageManager: Installing toolchain-atmelavr @ ~1.40801.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    toolchain-atmelavr @ 1.40801.0 has been successfully installed!
    The platform 'atmelavr' has been successfully installed!
    The rest of packages will be installed automatically depending on your build environment.

2. Install :ref:`platform_atmelavr` with ``uploader`` utility only and skip
   default packages

.. code-block:: bash

    PlatformManager: Installing atmelavr
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    atmelavr @ 0.0.0 has been successfully installed!
    PackageManager: Installing tool-micronucleus @ ~1.200.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    tool-micronucleus @ 1.200.0 has been successfully installed!
    PackageManager: Installing tool-avrdude @ ~1.60001.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    tool-avrdude @ 1.60001.1 has been successfully installed!
    The platform 'atmelavr' has been successfully installed!
    The rest of packages will be installed automatically depending on your build environment.

3. Install the latest development :ref:`platform_atmelavr` from Git repository

.. code-block:: bash

    $ platformio platform install https://github.com/platformio/platform-atmelavr.git

    PlatformManager: Installing platform-atmelavr
    git version 2.7.4 (Apple Git-66)
    Cloning into '/Volumes/MEDIA/tmp/pio3_test_projects/arduino-digihead-master/home_dir/platforms/installing-U3ucN0-package'...
    remote: Counting objects: 176, done.
    remote: Compressing objects: 100% (55/55), done.
    remote: Total 176 (delta 114), reused 164 (delta 109), pack-reused 0
    Receiving objects: 100% (176/176), 38.86 KiB | 0 bytes/s, done.
    Resolving deltas: 100% (114/114), done.
    Checking connectivity... done.
    Submodule 'examples/arduino-external-libs/lib/OneWire' (https://github.com/PaulStoffregen/OneWire.git) registered for path 'examples/arduino-external-libs/lib/OneWire'
    Cloning into 'examples/arduino-external-libs/lib/OneWire'...
    remote: Counting objects: 91, done.
    remote: Total 91 (delta 0), reused 0 (delta 0), pack-reused 91
    Unpacking objects: 100% (91/91), done.
    Checking connectivity... done.
    Submodule path 'examples/arduino-external-libs/lib/OneWire': checked out '57c18c6de80c13429275f70875c7c341f1719201'
    atmelavr @ 0.0.0 has been successfully installed!
    PackageManager: Installing tool-scons @ >=2.3.0,<2.6.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    tool-scons @ 2.4.1 has been successfully installed!
    PackageManager: Installing toolchain-atmelavr @ ~1.40801.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    toolchain-atmelavr @ 1.40801.0 has been successfully installed!
    The platform 'https://github.com/platformio/platform-atmelavr.git' has been successfully installed!
    The rest of packages will be installed automatically depending on your build environment.
