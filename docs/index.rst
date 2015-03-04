PlatformIO: A cross-platform code builder and the missing library manager
=========================================================================

.. image:: _static/platformio-logo.png
    :target: http://platformio.org

`Website + Library Search <http://platformio.org>`_ |
`Project Examples <https://github.com/ivankravets/platformio/tree/develop/examples>`_ |
`Source Code <https://github.com/ivankravets/platformio>`_ |
`Issues <https://github.com/ivankravets/platformio/issues>`_ |
`Blog <http://www.ikravets.com/category/computer-life/platformio>`_ |
`Twitter <https://twitter.com/PlatformIO_Org>`_

You have no need to install any *IDE* or compile any tool chains. *PlatformIO*
has pre-built different development platforms including: compiler, debugger,
uploader (for embedded) and many other useful tools.

**PlatformIO** allows developer to compile the same code with different
platforms using only one command :ref:`cmd_run`. This happens due to
:ref:`projectconf` where you can setup different environments with specific
options: platform type, firmware uploading settings, pre-built framework
and many more.

Embedded Development. *Easier Than Ever.*
-----------------------------------------

* Colourful command-line output
* Built-in :ref:`Serial Port Monitor <cmd_serialports_monitor>`
* Configurable build :ref:`-flags/-options <projectconf_build_flags>`
* Integration with :ref:`development environments (IDE) <ide>`
* Pre-built tool chains, frameworks for the popular Hardware Platforms

Smart Code Builder. *Fast and Reliable.*
----------------------------------------

* Reliable, automatic dependency analysis and detection of build changes
* Improved support for parallel builds
* Ability to share built files in a cache
* Lookup for external libraries which are installed via :ref:`librarymanager`

The Missing Library Manager. *It's here!*
-----------------------------------------

* Friendly Command-Line Interface
* Modern `Web 2.0 Library Search <http://platformio.org/#!/lib>`_
* Library dependency management
* Automatic library updating
* It runs on Windows, Mac OS X, and Linux (+ARM).


Contents
--------

.. toctree::
    :maxdepth: 2

    quickstart
    installation
    projectconf
    envvars
    platforms/index
    librarymanager/index
    userguide/index
    ide
    history
