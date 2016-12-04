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

.. _setting_enable_ssl:

``enable_ssl``
^^^^^^^^^^^^^^

:Default:   No
:Values:    Yes/No

Enable SSL for PlatformIO Services

.. _setting_force_verbose:

``force_verbose``
^^^^^^^^^^^^^^^^^

:Default:   No
:Values:    Yes/No

Force verbose output when processing environments. This setting overrides

* :option:`platformio run --verbose`
* :option:`platformio ci --verbose`
* :option:`platformio test --verbose`

.. _setting_enable_telemetry:

``enable_telemetry``
^^^^^^^^^^^^^^^^^^^^

:Default:   Yes
:Values:    Yes/No

Share diagnostics and usage information to help us make PlatformIO better:

* PlatformIO errors/exceptions
* The name of used platforms, boards, frameworks (for example, "espressif", "arduino", "uno", etc.)
* The name of commands (for example, "run", "lib list", etc.)
* The type of IDE (for example, "atom", "eclipse", etc.)

This gives us a sense of what parts of the PlatformIO is most important.

The source code of telemetry service is `open source <https://github.com/platformio/platformio-core/blob/develop/platformio/telemetry.py>`_. You can make sure that we DO NOT share PRIVATE information or
source code of your project. All information shares anonymously.

Thanks a lot that keep this setting enabled.


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
    enable_telemetry                Yes               Telemetry service (Yes/No)


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
