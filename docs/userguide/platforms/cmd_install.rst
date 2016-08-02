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

    platformio platform install [OPTIONS] [PLATFORM...]

    # [PLATFORM...] forms
    platformio platform install <name>
    platformio platform install <name>@<version>
    platformio platform install <name>@<version range>
    platformio platform install <zip or tarball url>
    platformio platform install file://<zip or tarball file>
    platformio platform install file://<folder>
    platformio platform install <repository>
    platformio platform install <name=repository> (name it should have locally)
    platformio platform install <repository#tag> ("tag" can be commit, branch or tag)


Description
-----------

Install :ref:`platforms` and dependent packages.

The ``version`` supports `Semantic Versioning <http://semver.org>`_ (
``<major>.<minor>.<patch>``) and can take any of the following forms:

* ``0.1.2`` - an exact version number. Use only this exact version
* ``^0.1.2`` - any compatible version (exact version for ``0.x.x`` versions
* ``~0.1.2`` - any version with the same major and minor versions, and an
  equal or greater patch version
* ``>0.1.2`` - any version greater than ``0.1.2``. ``>=``, ``<``, and ``<=``
  are also possible
* ``>0.1.0,!=0.2.0,<0.3.0`` - any version greater than ``0.1.0``, not equal to
  ``0.2.0`` and less than ``0.3.0``

Also, PlatformIO supports installing from local directory or archive. Need to
use ``file://`` prefix before local path. Also, directory or archive should
contain ``platform.json`` manifest.

* ``file:///local/path/to/the/platform/dir``
* ``file:///local/path/to/the/platform.zip``
* ``file:///local/path/to/the/platform.tar.gz``

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

Version control
---------------

PlatformIO supports installing from Git, Mercurial and Subversion, and detects
the type of VCS using url prefixes: "git+", "hg+", or "svn+".

.. note::
    PlatformIO requires a working VCS command on your path: ``git``, ``hg``
    or ``svn``.

Git
^^^

The supported schemes are: ``git``, ``git+https`` and ``git+ssh``. Here are
the supported forms:

* platformio/platform-NAME (short version for GitHub repository)
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

Examples
--------

1. Install :ref:`platform_atmelavr` with default packages

.. code::

    > platformio platform install atmelavr

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

.. code::

    > platformio platform install atmelavr --skip-default-package --with-package=uploader

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

.. code::

    > platformio platform install https://github.com/platformio/platform-atmelavr.git

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
