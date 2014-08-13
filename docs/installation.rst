.. _installation:

Installation
============

*PlatformIO* is written in `Python <https://www.python.org>`_ and works with
versions 2.6 and 2.7 on Unix/Linux, OS X, Windows and Credit-card ARM-based
computers (Raspberry Pi).

All commands below should be executed in
`Command-line <http://en.wikipedia.org/wiki/Command-line_interface>`_
application in your *OS*:

* *Unix/Linux/OS X* this is *Terminal* application.
* *Windows* this is
  `Command Prompt <http://en.wikipedia.org/wiki/Command_Prompt>`_ (``cmd.exe``)
  application.


Super-Quick
-----------

To install or upgrade *PlatformIO*, download
`get-platformio.py <https://raw.githubusercontent.com/ivankravets/platformio/develop/scripts/get-platformio.py>`_ script.

Then run the following (which may require administrator access):

.. code-block:: bash

    $ python get-platformio.py

An alternative short version for *Mac/Linux* users:

.. code-block:: bash

    $ curl -L https://raw.githubusercontent.com/ivankravets/platformio/develop/scripts/get-platformio.py | python


On *Windows OS* it may look like:

.. code-block:: bash

    C:\Python27\python.exe get-platformio.py

.. warning::
    If you have an error ``pkg_resources.DistributionNotFound`` try to
    uninstall *PlatformIO* ``$ pip uninstall platformio``, then install it via
    ``$ easy_install platformio``.


Full Guide
----------

1. Check a ``python`` version (only 2.6-2.7 is supported):

.. code-block:: bash

    $ python --version

*Windows OS* Users only:

    * `Download Python 2.7 <https://www.python.org/downloads/>`_ and install it.
    * Add to PATH system variable ``;C:\Python27;C:\Python27\Scripts;`` and
       reopen *Command Prompt* (``cmd.exe``) application. Please read this
       article `How to set the path and environment variables in Windows
       <http://www.computerhope.com/issues/ch000549.htm>`_.


2. Check a ``pip`` tool for installing and managing *Python* packages:

.. code-block:: bash

    $ pip search platformio

You should see short information about ``platformio`` package.

If your computer does not recognize ``pip`` command, try to install it first
using `these instructions <https://pip.pypa.io/en/latest/installing.html>`_.

3. Install a ``platformio`` and related packages:

.. code-block:: bash

    $ pip install platformio && pip install --egg scons

For upgrading the ``platformio`` to new version please use this command:

.. code-block:: bash

    $ pip install -U platformio


