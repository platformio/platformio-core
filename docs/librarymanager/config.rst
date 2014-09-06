.. _library_config:

library.json
============

Libraries are defined by a manifest file ``library.json``. This is a
`JSON-style <http://en.wikipedia.org/wiki/JSON>`_ file. Any data in
``library.json`` should be represented via
`associative array <http://en.wikipedia.org/wiki/Associative_array>`_
(name/value pairs). An order doesn't make a sense.

The allowable fields (names from pairs) are described below. The fields
(:ref:`libjson_name`, :ref:`libjson_description` and :ref:`libjson_keywords`)
will be displayed in search/lookup results on the :ref:`cmd_lib_search`
(*CLI*) and the *WebSite* that can be used to search for libraries.

.. contents::

.. _libjson_name:

``name``
--------

**Required** | Type: ``String`` | Max. Length: 50

The name of the library.

* Must be unique.
* Should be slug style for simplicity, consistency and compatibility.
  Example: Arduino-SPI
* Title Case, Aa-z, can contain digits, can contain dash (but not start/end
  with them).
* Consecutive dashes are not allowed.


.. _libjson_description:

``description``
---------------

**Required** | Type: ``String`` | Max. Length: 255

Help users identify and search for your library with a brief description.
Describe the hardware devices (sensors, boards and etc.) which are suitable
with it.


.. _libjson_keywords:

``keywords``
------------

**Required** | Type: ``String`` | Max. Length: 255

The keyword should be lowercased, can contain a-z, digits and dash (but not
start/end with them). A list from keywords can be specified with
separator ``,``.

Used for search by keyword. Helps make your library easier to discover without
people needing to know its name.


.. _libjson_version:

``version``
-----------

*Required* if :ref:`libjson_repository` field is not defined | Type: ``String``
| Max. Length: 20

The version of the current library source code.

* Can contain a-z, digits, dots and dash.
* `Semantic Versioning <http://semver.org>`_ is recommended.
* A `CVS <http://en.wikipedia.org/wiki/Concurrent_Versions_System>`_
  revision from the latest commit. Example: ``13`` (*SVN*) or first 10
  chars of *SHA* digest ``e4564b7da4`` (*Git*).

.. note::
    You can omit :ref:`libjson_version` field and define
    :ref:`libjson_repository` field.  In this situation
    *PlatformIO-API Crawler* will use the CVS-revision from the latest commit.


.. _libjson_author:

``author``
----------

*Required* if :ref:`libjson_repository` field is not defined | Type: ``Object``

An author's contact information

* ``name`` Full name (**Required**)
* ``email``
* ``url`` An author's contact page

Example:

.. code-block:: javascript

    "author":
    {
        "name": "John Smith",
        "email": "me@john-smith.com",
        "url": "http://www.john-smith/contact"
    }

.. note::
    You can omit :ref:`libjson_author` field and define
    :ref:`libjson_repository` field. Only *GitHub-based* repository is
    supported now. In this situation
    *PlatformIO-API Crawler* will use information from
    `GitHub API Users <https://developer.github.com/v3/users/>`_.


.. _libjson_repository:

``repository``
--------------

*Required* if :ref:`libjson_downloadurl` field is not defined | Type: ``Object``

The repository in which the source code can be found.

Example:

.. code-block:: javascript

    "repository":
    {
        "name": "git",
        "url": "https://github.com/foo/bar.git"
    }


.. _libjson_downloadurl:

``downloadUrl``
---------------

*Required* if :ref:`libjson_repository` field is not defined | Type: ``String``

The *HTTP URL* to archived source code of library. It should end with the type
of archive (``.zip`` or ``.tar.gz``).


.. _libjson_include:

``include``
-----------

*Optional* | Type: ``String`` or ``Array`` |
`Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_

If :ref:`libjson_include` field is a type of ``String``, then
*PlatformIO-API Crawler* will recognize it like a "relative path inside
repository/archive to library source code". See example below where only
source code from the relative directory ``LibrarySourceCodeHere`` will be
included.

.. code-block:: javascript

    "include": "some/child/dir/LibrarySourceCodeHere"

If :ref:`libjson_include` field is a type of ``Array``, then
*PlatformIO-API Crawler* firstly will apply :ref:`libjson_exclude` filter and
then include only directories/files which match with :ref:`libjson_include`
patterns.

Example:

.. code-block:: javascript

    "include":
    [
        "dir/*.[ch]pp",
        "dir/examples/*",
        "*/*/*.h"
    ]

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

.. _libjson_exclude:

``exclude``
-----------

*Optional* | Type: ``String`` or ``Array`` |
`Glob Pattern <http://en.wikipedia.org/wiki/Glob_(programming)>`_

Exclude the directories and files which will match with :ref:`libjson_exclude`
patterns.
