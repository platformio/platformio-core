..  Copyright 2014-2015 Ivan Kravets <me@ikravets.com>
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

..

    *"The missing library manager for development platforms"* [#]_

*PlatformIO Library Manager* allows you to organize external embedded libraries.
You can search for new libraries via

* :ref:`Command Line interface <cmd_lib_search>`
* `Web 2.0 Library Search <http://platformio.org/#!/lib>`_

You don't need to bother for finding the latest version of library. Due to
:ref:`cmd_lib_update` command you will have up-to-date external libraries.

.. toctree::
    :maxdepth: 2

    config
    creating
    User Guide <../userguide/lib/index.rst>

.. [#] Inspired by `npm <https://www.npmjs.com/>`_ and `bower
    <http://bower.io>`_ package managers for web.
