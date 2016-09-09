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

.. |PIOAPICR| replace:: *PlatformIO Library Registry Crawler*
.. _library_config:

library.json
============

``library.json`` is a manifest file of development library. It allows developers
to keep project in own structure and define:

* location of source code
* examples list
* compatible frameworks and platforms
* library dependencies
* advanced build settings

PlatformIO Library Crawler uses ``library.json`` manifest to extract
source code from developer's location and keeps a cleaned library in own
Library Registry.

A data in ``library.json`` should be represented
in `JSON-style <http://en.wikipedia.org/wiki/JSON>`_ via
`associative array <http://en.wikipedia.org/wiki/Associative_array>`_
(name/value pairs). An order doesn't matter. The allowable fields
(names from pairs) are described below.

.. contents::

.. _libjson_name:

``name``
--------

**Required** | Type: ``String`` | Max. Length: 50

A name of the library.

* Must be unique.
* Should be slug style for simplicity, consistency and compatibility.
  Example: *Arduino-SPI*
* Title Case, Aa-z, can contain digits and dashes (but not start/end
  with them).
* Consecutive dashes are not allowed.


.. _libjson_description:

``description``
---------------

**Required** | Type: ``String`` | Max. Length: 255

The field helps users to identify and search for your library with a brief
description. Describe the hardware devices (sensors, boards and etc.) which
are suitable with it.


.. _libjson_keywords:

``keywords``
------------

**Required** | Type: ``String`` | Max. Length: 255

Used for search by keyword. Helps to make your library easier to discover
without people needing to know its name.

The keyword should be lowercased, can contain a-z, digits and dash (but not
start/end with them). A list from the keywords can be specified with
separator ``,``


.. _libjson_authors:

``authors``
-----------

*Required* if :ref:`libjson_repository` field is not defined | Type: ``Object``
or ``Array``

An author contact information

* ``name`` Full name (**Required**)
* ``email``
* ``url`` An author's contact page
* ``maintainer`` Specify "maintainer" status

Examples:

.. code-block:: javascript

    "authors":
    {
        "name": "John Smith",
        "email": "me@john-smith.com",
        "url": "http://www.john-smith/contact"
    }

    ...

    "authors":
    [
        {
            "name": "John Smith",
            "email": "me@john-smith.com",
            "url": "http://www.john-smith/contact"
        },
        {
            "name": "Andrew Smith",
            "email": "me@andrew-smith.com",
            "url": "http://www.andrew-smith/contact",
            "maintainer": true
        }
    ]


.. note::
    You can omit :ref:`libjson_authors` field and define
    :ref:`libjson_repository` field. Only *GitHub-based* repository is
    supported now. In this case
    |PIOAPICR| will use information from
    `GitHub API Users <https://developer.github.com/v3/users/>`_.


.. _libjson_repository:

``repository``
--------------

*Required* if :ref:`libjson_downloadurl` field is not defined | Type: ``Object``

The repository in which the source code can be found. The field consists of the
next items:

* ``type`` the only "git", "hg" or "svn" are supported
* ``url``
* ``branch`` if is not specified, default branch will be used. This field will
  be ignored if tag/release exists with the value of :ref:`libjson_version`.

Example:

.. code-block:: javascript

    "repository":
    {
        "type": "git",
        "url": "https://github.com/foo/bar.git"
    }

.. _libjson_version:

``version``
-----------

*Required* if :ref:`libjson_repository` field is not defined | Type: ``String``
| Max. Length: 20

A version of the current library source code. Can contain a-z, digits, dots or
dash. `Semantic Versioning <http://semver.org>`_ IS RECOMMENDED.

:Case 1:

    :ref:`libjson_version` and :ref:`libjson_repository` fields are defined.
    The :ref:`libjson_repository` is hosted on GitHub or Bitbucket.

    |PIOAPICR| will lookup for release tag named as value of :ref:`libjson_version`
    or with ``v`` prefix (you do not need to pass this ``v`` prefix to the
    :ref:`libjson_version` field).

:Case 2:

    :ref:`libjson_version` and :ref:`libjson_repository` fields are defined
    and :ref:`libjson_repository` does not contain tag/release with value of
    :ref:`libjson_version`.

    |PIOAPICR| will use the latest source code from :ref:`libjson_repository`
    and link it with specified :ref:`libjson_version`. If :ref:`libjson_repository`
    ``branch`` is not specified, then default branch will be used.
    Also, if you push new commits to :ref:`libjson_repository`
    and do not update :ref:`libjson_version` field, the library will not be
    updated until you change the :ref:`libjson_version`.

:Case 3:

    :ref:`libjson_version` field is not defined and :ref:`libjson_repository`
    field is defined.

    |PIOAPICR| will use the
    `VCS <http://en.wikipedia.org/wiki/Concurrent_Versions_System>`_ revision from
    the latest commit as "current version". For example, ``13`` (*SVN*) or first
    10 chars of *SHA* digest ``e4564b7da4`` (*Git*). If :ref:`libjson_repository`
    ``branch`` is not specified, then default branch will be used.

    We recommend to use :ref:`libjson_version` field and specify the real release
    version and make appropriate tag in the :ref:`libjson_repository`. In other
    case, users will receive updates for library with each new commit to
    :ref:`libjson_repository`.

.. note::
    |PIOAPICR| updates library only if:
        - the :ref:`libjson_version` is changed
        - ``library.json`` is modified

Example:

.. code-block:: javascript

    "repository":
    {
        "type": "git",
        "url": "https://github.com/foo/bar.git"
    },
    "version": "1.0.0"


``license``
-----------

*Optional* | Type: ``String``

A license of the library. You can check
`the full list of SPDX license IDs <https://spdx.org/licenses/>`_. Ideally you
should pick one that is `OSI <https://opensource.org/licenses/alphabetical>`_
approved.

.. code-block:: javascript

    "license": "Apache-2.0"

.. _libjson_downloadurl:

``downloadUrl``
---------------

*Required* if :ref:`libjson_repository` field is not defined | Type: ``String``

It is the *HTTP URL* to the archived source code of library. It should end
with the type of archive (``.zip`` or ``.tar.gz``).

.. note::

    :ref:`libjson_downloadurl` has higher priority than
    :ref:`libjson_repository`.

Example with fixed release/tag on GitHub:

.. code-block:: javascript

    "version": "1.0.0",
    "downloadUrl": "https://github.com/foo/bar/archive/v1.0.0.tar.gz",
    "include": "bar-1.0.0"

See more ``library.json`` :ref:`library_creating_examples`.

``homepage``
------------

*Optional* | Type: ``String`` | Max. Length: 255

Home page of library (if is different from :ref:`libjson_repository` url).


.. _libjson_export:

``export``
----------

*Optional* | Type: ``Object``

Explain PlatformIO Library Crawler which content from the repository/archive
should be exported as "source code" of the library. This option is useful if
need to exclude extra data (test code, docs, images, PDFs, etc). It allows to
reduce size of the final archive.

Possible options:

.. contents::
    :local:

``include``
~~~~~~~~~~~

*Optional* | Type: ``String`` or ``Array`` |
`Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_

If ``include`` field is a type of ``String``, then |PIOAPICR| will recognize
it like a "relative path inside repository/archive to library source code".
See example below where the only
source code from the relative directory ``LibrarySourceCodeHere`` will be
included.

.. code-block:: javascript

    "include": "some/child/dir/LibrarySourceCodeHere"

If ``include`` field is a type of ``Array``, then |PIOAPICR| firstly will
apply ``exclude`` filter and then include only directories/files
which match with ``include`` patterns.

Example:

.. code-block:: javascript

    "export": {
        "include":
        [
            "dir/*.[ch]pp",
            "dir/examples/*",
            "*/*/*.h"
        ]
    }


Pattern	Meaning

.. list-table::
    :header-rows:  1

    * - Pattern
      - Meaning
    * - ``*``
      - matches everything
    * - ``?``
      - matches any single character
    * - ``[seq]``
      - matches any character in seq
    * - ``[!seq]``
      - matches any character not in seq

See more ``library.json`` :ref:`library_creating_examples`.


``exclude``
~~~~~~~~~~~

*Optional* | Type: ``String`` or ``Array`` |
`Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_

Exclude the directories and files which match with ``exclude`` patterns.

.. _libjson_frameworks:

``frameworks``
--------------

*Optional* | Type: ``String`` or ``Array``

A list with compatible frameworks. The available framework types are defined in
the :ref:`platforms` section.

If the library is compatible with the all frameworks, then you can use ``*``
symbol:

.. code-block:: javascript

    "frameworks": "*"

.. _libjson_platforms:

``platforms``
-------------

*Optional* | Type: ``String`` or ``Array``

A list with compatible platforms. The available platform types are
defined in :ref:`platforms` section.

If the library is compatible with the all platforms, then you can use ``*``
symbol:

.. code-block:: javascript

    "platforms": "*"


.. _libjson_dependencies:

``dependencies``
----------------

*Optional* | Type: ``Array`` or ``Object``

A list of dependent libraries. They will be installed automatically with
:ref:`cmd_lib_install` command.

Allowed requirements for dependent library:

* ``name`` | Type: ``String``
* ``version`` | Type: ``String``
* ``authors`` | Type: ``String`` or ``Array``
* ``frameworks`` | Type: ``String`` or ``Array``
* ``platforms`` | Type: ``String`` or ``Array``

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

The rest possible values including VCS repository URLs are documented in
:ref:`cmd_lib_install` command.

Example:

.. code-block:: javascript

    "dependencies":
    [
        {
            "name": "Library-Foo",
            "authors":
            [
                "Jhon Smith",
                "Andrew Smith"
            ]
        },
        {
            "name": "Library-Bar",
            "version": "~1.2.3"
        },
        {
            "name": "lib-from-repo",
            "version": "https://github.com/user/package.git#1.2.3"
        }
    ]

A short definition of dependencies is allowed:

.. code-block:: javascript

    "dependencies": {
        "mylib": "1.2.3",
        "lib-from-repo": "githubuser/package"
    }


See more ``library.json`` :ref:`library_creating_examples`.

.. _libjson_examples:

``examples``
------------

*Optional* | Type: ``String`` or ``Array`` |
`Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_

A list of example patterns. This field is predefined with default value:

.. code-block:: javascript

    "examples": [
        "[Ee]xamples/*.c",
        "[Ee]xamples/*.cpp",
        "[Ee]xamples/*.ino",
        "[Ee]xamples/*.pde",
        "[Ee]xamples/*/*.c",
        "[Ee]xamples/*/*.cpp",
        "[Ee]xamples/*/*.ino",
        "[Ee]xamples/*/*.pde",
        "[Ee]xamples/*/*/*.c",
        "[Ee]xamples/*/*/*.cpp",
        "[Ee]xamples/*/*/*.ino",
        "[Ee]xamples/*/*/*.pde"
    ]


.. _libjson_build:

``build``
---------

*Optional* | Type: ``Object``

Specify advanced settings, options and flags for the build system. Possible
options:

.. contents::
    :local:

``flags``
~~~~~~~~~

*Optional* | Type: ``String`` or ``Array``

Extra flags to control preprocessing, compilation, assembly and linking
processes. More details :ref:`projectconf_build_flags`.

``unflags``
~~~~~~~~~~~

*Optional* | Type: ``String`` or ``Array``

Remove base/initial flags which were set by development platform. More
details :ref:`projectconf_build_unflags`.

``srcFilter``
~~~~~~~~~~~~~

*Optional* | Type: ``String`` or ``Array``

Specify which source files should be included/excluded from build process.
More details :ref:`projectconf_src_filter`.

``extraScript``
~~~~~~~~~~~~~~~

*Optional* | Type: ``String``

Launch extra script before build process.
More details :ref:`projectconf_extra_script`.

``libArchive``
~~~~~~~~~~~~~~

*Optional* | Type: ``Boolean``

Archive object files to Static Library. This is default behavior of PlatformIO
Build System (``"libArchive": true``).

``libLDFMode``
~~~~~~~~~~~~~~

*Optional* | Type: ``Integer``

Specify Library Dependency Finder Mode. See :ref:`ldf_mode` for details.

**Examples**

1. Custom macros/defines

.. code-block:: javascript

    "build": {
        "flags": "-D MYLIB_REV=0.1.2 -DRELEASE"
    }

2. Extra includes for C preprocessor

.. code-block:: javascript

    "build": {
        "flags": [
            "-I inc",
            "-I inc/target_x13"
        ]
    }

3. Force to use ``C99`` standard instead of ``C11``

.. code-block:: javascript

    "build": {
        "unflags": "-std=gnu++11",
        "flags": "-std=c99"
    }

4. Build source files (``c, cpp, h``) at the top level of the library

.. code-block:: javascript

    "build": {
        "srcFilter": [
            "+<*.c>",
            "+<*.cpp>",
            "+<*.h>"
        ]
    }


5. Extend PlatformIO Build System with own extra script

.. code-block:: javascript

    "build": {
        "extraScript": "generate_headers.py"
    }

``generate_headers.py``

.. code-block:: python

    Import('env')
    # print env.Dump()
    env.Append(
        CPPDEFINES=["HELLO=WORLD", "TAG=1.2.3", "DEBUG"],
        CPPPATH=["inc", "inc/devices"]
    )

    # some python code that generates header files "on-the-fly"
