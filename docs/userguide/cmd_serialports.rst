.. _cmd_serialports:

platformio serialports
======================

.. contents::

Usage
-----

.. code-block:: bash

    platformio serialports


Description
-----------

List available `Serial Ports <http://en.wikipedia.org/wiki/Serial_port>`_


Examples
--------

1. Unix OS

.. code-block:: bash

    $ platformio serialports
    /dev/cu.SLAB_USBtoUART
    ----------
    Hardware ID: USB VID:PID=10c4:ea60 SNR=0001
    Description: CP2102 USB to UART Bridge Controller

    /dev/cu.uart-1CFF4676258F4543
    ----------
    Hardware ID: USB VID:PID=451:f432 SNR=1CFF4676258F4543
    Description: Texas Instruments MSP-FET430UIF


2. Windows OS

.. code-block:: bash

    $ platformio serialports
    COM4
    ----------
    Hardware ID: USB VID:PID=0451:F432
    Description: MSP430 Application UART (COM4)

    COM3
    ----------
    Hardware ID: USB VID:PID=10C4:EA60 SNR=0001
    Description: Silicon Labs CP210x USB to UART Bridge (COM3)
