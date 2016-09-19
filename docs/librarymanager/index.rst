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

.. _librarymanager:

Library Manager
===============

*PlatformIO Library Manager* is a tool for managing libraries of
`PlatformIO Registry <http://platformio.org/lib>`__ and VCS repositories (Git,
Hg, SVN). It makes it exceedingly simple to find, install and keep libraries
up-to-date. PlatformIO Library Manager supports
`Semantic Versioning <http://semver.org>`_ and its rules.

There are 2 options how to find library:

* `Web Library Search <http://platformio.org/lib>`__
* :ref:`Command Line Interface <cmd_lib_search>`

You can manage different library storages using
:option:`platformio lib --global` or  :option:`platformio lib --storage-dir`
options. If you change current working directory in terminal to project folder,
then :ref:`platformio lib <cmd_lib>` command will manage automatically dependency
storage in :ref:`projectconf_pio_libdeps_dir`.

Project dependencies
--------------------

*PlatformIO Library Manager* allows to specify project dependencies
(:ref:`projectconf_lib_deps`) that will be installed automatically per project
before environment processing. You do not need to install libraries manually.
The only one simple step is to define dependencies in :ref:`projectconf`.
You can use library ID, Name or even repository URL. For example,

.. code-block:: ini

  [env:myenv]
  platform = ...
  framework = ...
  board = ...
  lib_deps =
    13
    PubSubClient
    Json@~5.6,!=5.4
    https://github.com/gioblu/PJON.git@v2.0
    https://github.com/me-no-dev/ESPAsyncTCP.git
    https://github.com/adafruit/DHT-sensor-library/archive/master.zip

Please follow to :ref:`cmd_lib_install` for detailed documentation about
possible values.

.. warning::
  If some libraries are not visible in :ref:`ide_atom` and Code Completion or
  Code Linting does not work properly, please perform  ``Menu: PlatformIO >
  Rebuild C/C++ Project Index (Autocomplete, Linter)``

.. image:: ../_static/platformio-demo-lib.gif
