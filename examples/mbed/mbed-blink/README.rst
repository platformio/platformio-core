How to build PlatformIO based project
=====================================

1. `Install PlatformIO <http://docs.platformio.org/en/latest/installation.html>`_
2. Download `source code with examples <https://github.com/platformio/platformio/archive/develop.zip>`_
3. Extract ZIP archive
4. Run these commands:

.. code-block:: bash

    # Change directory to example
    > cd platformio-develop/examples/mbed/mbed-blink

    # Process example project
    > platformio run

    # Upload firmware
    > platformio run --target upload

    # Clean build files
    > platformio run --target clean
