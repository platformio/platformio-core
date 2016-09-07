..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _cmd_lib_install:

platformio lib install
======================

.. contents::

Usage
-----

.. code-block:: bash

    platformio lib [STORAGE_OPTIONS] install [OPTIONS] [LIBRARY...]

    # install project dependent library
    # (run it from a project root where is located "platformio.ini")
    platformio lib install [OPTIONS] [LIBRARY...]

    # install to global storage
    platformio lib --global install [OPTIONS] [LIBRARY...]
    platformio lib -g install [OPTIONS] [LIBRARY...]

    # install to custom storage
    platformio lib --storage-dir /path/to/dir install [OPTIONS] [LIBRARY...]
    platformio lib -d /path/to/dir install [OPTIONS] [LIBRARY...]

    # [LIBRARY...] forms
    platformio lib [STORAGE_OPTIONS] install (with no args, project dependencies)
    platformio lib [STORAGE_OPTIONS] install <id>
    platformio lib [STORAGE_OPTIONS] install id=<id>
    platformio lib [STORAGE_OPTIONS] install <id>@<version>
    platformio lib [STORAGE_OPTIONS] install <id>@<version range>
    platformio lib [STORAGE_OPTIONS] install <name>
    platformio lib [STORAGE_OPTIONS] install <name>@<version>
    platformio lib [STORAGE_OPTIONS] install <name>@<version range>
    platformio lib [STORAGE_OPTIONS] install <zip or tarball url>
    platformio lib [STORAGE_OPTIONS] install file://<zip or tarball file>
    platformio lib [STORAGE_OPTIONS] install file://<folder>
    platformio lib [STORAGE_OPTIONS] install <repository>
    platformio lib [STORAGE_OPTIONS] install <name>=<repository> (name it should have locally)
    platformio lib [STORAGE_OPTIONS] install <repository#tag> ("tag" can be commit, branch or tag)

.. warning::
  If some libraries are not visible in :ref:`ide_atom` and Code Completion or
  Code Linting does not work properly, please perform  ``Menu: PlatformIO >
  Rebuild C/C++ Project Index (Autocomplete, Linter)``

Description
-----------

Install a library, and any libraries that it depends on using:

1. Library ``id`` or ``name`` from `PlatformIO Library Registry <http://platformio.org/lib>`_
2. Custom folder, repository or archive.

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

PlatformIO supports installing from local directory or archive. Need
to use ``file://`` prefix before local path. Also, directory or
archive should contain ``.library.json`` manifest (see :ref:`library_config`).

* ``file:///local/path/to/the/platform/dir``
* ``file:///local/path/to/the/platform.zip``
* ``file:///local/path/to/the/platform.tar.gz``

Storage Options
---------------

See base options for :ref:`userguide_lib`.

Options
-------

.. program:: platformio lib install

.. option::
    -s, --silent

Suppress progress reporting

.. option::
    --interactive

Allow to make a choice for all prompts

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

* user/library (short version for GitHub repository)
* https://github.com/user/library.git
* git+git://git.server.org/my-library
* git+https://git.server.org/my-library
* git+ssh://git.server.org/my-library

Passing branch names, a commit hash or a tag name is possible like so:

* https://github.com/user/library.git#master
* git+git://git.server.org/my-library#master
* git+https://git.server.org/my-library#v1.0
* git+ssh://git.server.org/my-library#7846d8ad52f983f2f2887bdc0f073fe9755a806d

Mercurial
^^^^^^^^^

The supported schemes are: ``hg+http``, ``hg+https`` and ``hg+ssh``. Here are
the supported forms:

* https://developer.mbed.org/users/user/code/library/ (install ARM mbed library)
* hg+hg://hg.server.org/my-library
* hg+https://hg.server.org/my-library
* hg+ssh://hg.server.org/my-library

Passing branch names, a commit hash or a tag name is possible like so:

* hg+hg://hg.server.org/my-library#master
* hg+https://hg.server.org/my-library#v1.0
* hg+ssh://hg.server.org/my-library#4cfe2fa00668

Subversion
^^^^^^^^^^

The supported schemes are: ``svn``, ``svn+svn``, ``svn+http``, ``svn+https``
and ``svn+ssh``. Here are the supported forms:

* svn+svn://svn.server.org/my-library
* svn+https://svn.server.org/my-library
* svn+ssh://svn.server.org/my-library

You can also give specific revisions to an SVN URL, like so:

* svn+svn://svn.server.org/my-library#13


Examples
--------

1. Install the latest version of library to a global storage using ID or NAME

.. code::

    > platformio lib -g install 4

    Library Storage: /storage/dir/...
    LibraryManager: Installing id=4
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    IRremote @ 2.2.1 has been successfully installed!

    # repeat command with name
    > platformio lib -g install IRRemote

    Library Storage: /storage/dir/...
    Looking for IRRemote library in registry
    Found: http://platformio.org/lib/show/4/IRremote
    LibraryManager: Installing id=4
    IRremote @ 2.2.1 is already installed


2. Install specified version of a library to a global storage

.. code::

    > platformio lib -g install Json@5.4.0

    Library Storage: /storage/dir/...
    Looking for Json library in registry
    Found: http://platformio.org/lib/show/64/Json
    LibraryManager: Installing id=64 @ 5.4.0
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Json @ 5.4.0 has been successfully installed!


3. Install library with dependencies to custom storage

.. code::

    > platformio lib --storage-dir /my/storage/dir install DallasTemperature

    Library Storage: /my/storage/dir
    Looking for DallasTemperature library in registry
    Found: http://platformio.org/lib/show/54/DallasTemperature
    LibraryManager: Installing id=54
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    DallasTemperature @ 3.7.7 has been successfully installed!
    Installing dependencies
    Looking for OneWire library in registry
    Found: http://platformio.org/lib/show/1/OneWire
    LibraryManager: Installing id=1
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    OneWire @ 8fd2ebfec7 has been successfully installed!

4. Install ARM mbed library to the global storage

.. code::

    > platformio lib -g install https://developer.mbed.org/users/simon/code/TextLCD/

    Library Storage: /storage/dir/...
    LibraryManager: Installing TextLCD
    Mercurial Distributed SCM (version 3.8.4)
    (see https://mercurial-scm.org for more information)

    Copyright (C) 2005-2016 Matt Mackall and others
    This is free software; see the source for copying conditions. There is NO
    warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    requesting all changes
    adding changesets
    adding manifests
    adding file changes
    added 9 changesets with 18 changes to 6 files
    updating to branch default
    2 files updated, 0 files merged, 0 files removed, 0 files unresolved
    TextLCD @ 308d188a2d3a has been successfully installed!

5. Install from archive using URL

.. code::

    > platformio lib -g install  https://github.com/adafruit/DHT-sensor-library/archive/master.zip

    Library Storage: /storage/dir/...
    LibraryManager: Installing master
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    DHT sensor library @ 1.2.3 has been successfully installed!
