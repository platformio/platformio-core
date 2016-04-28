..  Copyright 2014-2016 Ivan Kravets <me@ikravets.com>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

How to build PlatformIO based project
=====================================

1. `Install PlatformIO <http://docs.platformio.org/en/latest/installation.html>`_
2. Download `source code with examples <https://github.com/platformio/platformio-examples/archive/develop.zip>`_
3. Extract ZIP archive
4. Run these commands:

.. code-block:: bash

    # Change directory to example
    > cd platformio-examples/lattice_ice40/lattice_ice40-counter

    # Generate the bitstream
    > platformio run

    # Upload the bitstream into the FPGA
    > platformio run --target upload
