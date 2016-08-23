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

There 2 options how to find library:

* :ref:`Command Line Interface <cmd_lib_search>`
* `Web-based Library Search <http://platformio.org/lib>`__

*PlatformIO Library Manager* allows to manage different library storages using
:option:`platformio lib --global` or  :option:`platformio lib --storage-dir`
options.

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

Please follow to :ref:`cmd_lib_install` for detailed documentation about
possible values.

.. image:: ../_static/platformio-demo-lib.gif
