Wiring Framework (Arduino + Energia) Blink Example
==================================================

1. Download ``platformio``
   `sources <https://github.com/ivankravets/platformio/archive/develop.zip>`_
2. Extract ZIP archive
3. Then run these commands:

.. code-block:: bash

    # Change directory to example
    $ cd platformio-develop/examples/wiring-blink/

    # Install Atmel AVR development platform with Arduino Framework
    # Install TI MSP430 development platform with Energia Framework
    # Install TI TIVA development platform with Energia Framework
    $ platformio install atmelavr timsp430 titiva

    # Process example project
    $ platformio run

.. image:: console-result.png
