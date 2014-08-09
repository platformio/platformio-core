.. _cmd_install:

platformio install
==================

.. contents::

Usage
-----

.. code-block:: bash

    platformio install [OPTIONS] [PLATFORMS]


Description
-----------

Install pre-built development :ref:`Platforms <platforms>` with related
packages.

There are several predefined aliases for packages, such as:

* ``toolchain``
* ``uploader``


Options
-------

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

1. Install :ref:`platform_timsp430` with default packages

.. code-block:: bash

    $ platformio install timsp430
    Installing toolchain-timsp430 package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing tool-mspdebug package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    Installing framework-energiamsp430 package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The platform 'timsp430' has been successfully installed!


2. Install :ref:`platform_timsp430` with ``uploader`` utility only and skip
   default packages

.. code-block:: bash

    $ platformio install timsp430 --skip-default-package --with-package=uploader
    Installing tool-mspdebug package:
    Downloading  [####################################]  100%
    Unpacking  [####################################]  100%
    The platform 'timsp430' has been successfully installed!
