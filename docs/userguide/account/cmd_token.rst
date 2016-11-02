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

.. _cmd_account_token:

platformio account token
===========================

.. contents::

Usage
-----

.. code-block:: bash

    platformio account token


Description
-----------

Get or regenerate Personal Authentication Token. It is very useful for :ref:`ci`
systems, :ref:`pio_remote` operations where you are not able manually authorize.

PlatformIO handles Personal Authentication Token from environment variable
:envvar:`PLATFORMIO_AUTH_TOKEN`.

Options
~~~~~~~

.. program:: platformio account token

.. option::
    --regenerate

    If this option is specified a new authentication token will be generated.
