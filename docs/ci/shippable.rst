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

.. _ci_shippable:

Shippable
=========

`Shippable <http://en.wikipedia.org/wiki/Shippable>`_ is a hosted cloud
platform that provides hosted continuous integration, deployment, and testing
to `GitHub <http://en.wikipedia.org/wiki/GitHub>`_ and
`BitBucket <http://en.wikipedia.org/wiki/Bitbucket>`_ repositories.
Shippable's continuous integration service is built using Docker.

Shippable is configured by adding a file named ``shippable.yml``, which is a
`YAML <http://en.wikipedia.org/wiki/YAML>`_ format text file, to the root
directory of the GitHub repository or you can use your Travis CI configuration
file ``.travis.yml``.

Shippable automatically detects when a commit has been made and pushed to a
GitHub repository that is using Shippable, and each time this happens, it will
try to build the project using :ref:`cmd_ci` command. This includes commits to
all branches, not just to the master branch. Shippable will also build and run
pull requests. When that process has completed, it will notify a developer in
the way it has been configured to do so — for example, by sending an email
containing the build results (showing success or failure), or by posting a
message on an IRC channel. It can be configured to build project on a range of
different :ref:`platforms`.

.. contents::

Integration
-----------

Please put ``shippable.yml`` or ``.travis.yml`` to the root directory of the
GitHub repository.

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    env:
        - PLATFORMIO_CI_SRC=path/to/source/file.c
        - PLATFORMIO_CI_SRC=path/to/source/file.ino
        - PLATFORMIO_CI_SRC=path/to/source/directory

    install:
        - python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"

    script:
        - platformio ci --board=TYPE_1 --board=TYPE_2 --board=TYPE_N


For more details as for PlatformIO build process please look into :ref:`cmd_ci`
command.

Examples
--------

1. Integration for `USB_Host_Shield_2.0 <https://github.com/felis/USB_Host_Shield_2.0>`_
   project. The ``shippable.yml`` or ``.travis.yml`` configuration file:

.. code-block:: yaml

    language: python
    python:
        - "2.7"

    env:
        - PLATFORMIO_CI_SRC=examples/Bluetooth/PS3SPP/PS3SPP.ino
        - PLATFORMIO_CI_SRC=examples/pl2303/pl2303_gps/pl2303_gps.ino

    install:
        - python -c "$(curl -fsSL https://raw.githubusercontent.com/platformio/platformio/master/scripts/get-platformio.py)"
        - wget https://github.com/xxxajk/spi4teensy3/archive/master.zip -O /tmp/spi4teensy3.zip
        - unzip /tmp/spi4teensy3.zip -d /tmp

    script:
        - platformio ci --lib="." --lib="/tmp/spi4teensy3-master" --board=uno --board=teensy31 --board=due
