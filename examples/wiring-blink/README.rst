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
    $ platformio install atmelavr --with-package=framework-arduinoavr

    # Install TI MSP430 development platform with Energia Framework
    $ platformio install timsp430 --with-package=framework-energiamsp430

    # Install TI TIVA development platform with Energia Framework
    $ platformio install titiva --with-package=framework-energiativa

    # Process example project
    $ platformio run

.. image:: console-result.png
