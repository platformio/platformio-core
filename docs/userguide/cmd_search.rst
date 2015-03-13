.. _cmd_search:

platformio search
=================

.. contents::

Usage
-----

.. code-block:: bash

    platformio search QUERY [OPTIONS]


Description
-----------

Search for development :ref:`Platforms <platforms>`

Options
~~~~~~~

.. option::
    --json-output

Return the output in `JSON <http://en.wikipedia.org/wiki/JSON>`_ format


Examples
--------

1. Print all available development platforms

.. code-block:: bash

    $ platformio search
    atmelavr (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    --------
    Atmel AVR 8- and 32-bit MCUs deliver a unique combination of performance...

    atmelsam (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    --------
    Atmel | SMART offers Flash- based ARM products based on the ...

    freescalekinetis (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ----------------
    Freescale Kinetis Microcontrollers is family of multiple hardware- and ...

    nordicnrf51 (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    -----------
    The Nordic nRF51 Series is a family of highly flexible, multi-protocol ...

    nxplpc (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ------
    The NXP LPC is a family of 32-bit microcontroller integrated circuits ...

    ststm32 (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    -------
    The STM32 family of 32-bit Flash MCUs based on the ARM Cortex-M ...

    teensy (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ------
    Teensy is a complete USB-based microcontroller development syste ...

    timsp430 (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    --------
    MSP430 microcontrollers (MCUs) from Texas Instruments (TI) are ...

    titiva (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ------
    Texas Instruments TM4C12x MCUs offer the industrys most popular ...

2. Search for TI development platforms

.. code-block:: bash

    $ platformio search ti
    timsp430 (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    --------
    MSP430 microcontrollers (MCUs) from Texas Instruments (TI) are ...

    titiva (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ------
    Texas Instruments TM4C12x MCUs offer the industrys most popular ...

3. Search for development platforms which support "mbed Framework"

.. code-block:: bash

    $ platformio search mbed
    freescalekinetis (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ----------------
    Freescale Kinetis Microcontrollers is family of multiple hardware- and ...

    nordicnrf51 (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    -----------
    The Nordic nRF51 Series is a family of highly flexible, multi-protocol ...

    nxplpc (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    ------
    The NXP LPC is a family of 32-bit microcontroller integrated circuits ...

    ststm32 (available packages: ldscripts, toolchain-gccarmnoneeabi, tool-lm4flash, framework-opencm3, framework-energiativa)
    -------
    The STM32 family of 32-bit Flash MCUs based on the ARM Cortex-M ...
