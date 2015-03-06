.. _cmd_settings:

platformio settings
===================

Manage PlatformIO settings

.. contents::

platformio settings get
-----------------------

Usage
~~~~~

.. code-block:: bash

    platformio settings get [NAME]


Description
~~~~~~~~~~~

Get/List existing settings

Settings
~~~~~~~~

.. _setting_auto_update_libraries:

``auto_update_libraries``
^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   Yes
:Values:    Yes/No

Automatically update libraries.

.. _setting_auto_update_platforms:

``auto_update_platforms``
^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   Yes
:Values:    Yes/No

Automatically update platforms.

.. _setting_check_libraries_interval:

``check_libraries_interval``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   7
:Values:    Days (Number)

Check for the library updates interval.

.. _setting_check_platformio_interval:

``check_platformio_interval``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   3
:Values:    Days (Number)

Check for the new PlatformIO interval.

.. _setting_check_platforms_interval:

``check_platforms_interval``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:Default:   7
:Values:    Days (Number)

Check for the platform updates interval.

.. _setting_enable_prompts:

``enable_prompts``
^^^^^^^^^^^^^^^^^^

:Default:   Yes
:Values:    Yes/No

Can PlatformIO communicate with you via prompts?

* propose to install platforms which aren't installed yet
* paginate over library search results
* and etc.

.. warning::
    If you are going to run *PlatformIO* from **subprocess**, you **MUST
    DISABLE** all prompts. It will allow you to avoid blocking.

.. _setting_enable_telemetry:

``enable_telemetry``
^^^^^^^^^^^^^^^^^^^^

:Default:   Yes
:Values:    Yes/No

Shares commands, platforms and libraries usage to help us make PlatformIO
better.


.. note::
    * The ``Yes`` value is equl to: ``True``, ``Y``, ``1``.
      The value is not case sensetive.
    * You can override these settings using :ref:`envvars`.

Examples
~~~~~~~~

1. List all settings and theirs current values

.. code-block:: bash

    $ platformio settings get
    Name                            Value [Default]   Description
    ------------------------------------------------------------------------------------------
    auto_update_libraries           Yes               Automatically update libraries (Yes/No)
    auto_update_platforms           Yes               Automatically update platforms (Yes/No)
    check_libraries_interval        7                 Check for the library updates interval (days)
    check_platformio_interval       3                 Check for the new PlatformIO interval (days)
    check_platforms_interval        7                 Check for the platform updates interval (days)
    enable_prompts                  Yes               Can PlatformIO communicate with you via prompts: propose to install platforms which aren't installed yet, paginate over library search results and etc.)? ATTENTION!!! If you call PlatformIO like subprocess, please disable prompts to avoid blocking (Yes/No)
    enable_telemetry                Yes               Shares commands, platforms and libraries usage to help us make PlatformIO better (Yes/No)


2. Show specified setting

.. code-block:: bash

    $ platformio settings get auto_update_platforms
    Name                            Value [Default]   Description
    ------------------------------------------------------------------------------------------
    auto_update_platforms           Yes               Automatically update platforms (Yes/No)


platformio settings set
-----------------------

Usage
~~~~~

.. code-block:: bash

    platformio settings set NAME VALUE


Description
~~~~~~~~~~~

Set new value for the setting

Examples
~~~~~~~~

Change to check for the new PlatformIO each day

.. code-block:: bash

    $ platformio settings set check_platformio_interval 1
    The new value for the setting has been set!
    Name                            Value [Default]   Description
    ------------------------------------------------------------------------------------------
    check_platformio_interval       1 [3]             Check for the new PlatformIO interval (days)


platformio settings reset
-------------------------

Usage
~~~~~

.. code-block:: bash

    platformio settings reset


Description
~~~~~~~~~~~

Reset settings to default

Examples
~~~~~~~~

.. code-block:: bash

    $ platformio settings reset
    The settings have been reseted!

    Name                            Value [Default]   Description
    ------------------------------------------------------------------------------------------
    auto_update_libraries           Yes               Automatically update libraries (Yes/No)
    auto_update_platforms           Yes               Automatically update platforms (Yes/No)
    check_libraries_interval        7                 Check for the library updates interval (days)
    check_platformio_interval       3                 Check for the new PlatformIO interval (days)
    check_platforms_interval        7                 Check for the platform updates interval (days)
