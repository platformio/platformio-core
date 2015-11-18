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

.. _cmd_boards:

platformio boards
=================

.. contents::

Usage
-----

.. code-block:: bash

    # Print all available pre-configured embedded boards
    platformio boards

    # Filter boards by "Query"
    platformio boards QUERY


Description
-----------

List pre-configured Embedded Boards


Examples
--------

1. Show Arduino-based boards

.. code-block:: bash

    $ platformio boards arduino

    Platform: atmelavr
    ---------------------------------------------------------------------------
    Type                  MCU           Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    btatmega168           atmega168     16Mhz     14Kb    1Kb    Arduino BT ATmega168
    btatmega328           atmega328p    16Mhz     28Kb    2Kb    Arduino BT ATmega328
    diecimilaatmega168    atmega168     16Mhz     14Kb    1Kb    Arduino Duemilanove or Diecimila ATmega168
    diecimilaatmega328    atmega328p    16Mhz     30Kb    2Kb    Arduino Duemilanove or Diecimila ATmega328
    esplora               atmega32u4    16Mhz     28Kb    2Kb    Arduino Esplora
    ethernet              atmega328p    16Mhz     31Kb    2Kb    Arduino Ethernet
    ...


2. Show mbed-enabled boards

.. code-block:: bash

    $ platformio boards mbed

    Platform: freescalekinetis
    ---------------------------------------------------------------------------
    Type                  MCU            Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    frdm_k20d50m          mk20dx128vlh5  48Mhz     128Kb   16Kb   Freescale Kinetis FRDM-K20D50M
    frdm_k22f             mk22fn512vlh12 120Mhz    512Kb   128Kb  Freescale Kinetis FRDM-K22F
    ...

    Platform: nordicnrf51
    ---------------------------------------------------------------------------
    Type                  MCU            Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    wallBotBLE            nrf51822       16Mhz     128Kb   16Kb   JKSoft Wallbot BLE
    nrf51_dk              nrf51822       32Mhz     256Kb   32Kb   Nordic nRF51-DK
    ...

    Platform: nxplpc
    ---------------------------------------------------------------------------
    Type                  MCU            Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    blueboard_lpc11u24    lpc11u24       48Mhz     32Kb    8Kb    BlueBoard-LPC11U24
    dipcortexm0           lpc11u24       50Mhz     32Kb    8Kb    DipCortex M0
    lpc11u35              lpc11u35       48Mhz     64Kb    10Kb   EA LPC11U35 QuickStart Board
    ...

    Platform: ststm32
    ---------------------------------------------------------------------------
    Type                  MCU            Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    disco_f401vc          stm32f401vct6  84Mhz     256Kb   64Kb   32F401CDISCOVERY
    nucleo_f030r8         stm32f030r8t6  48Mhz     64Kb    8Kb    ST Nucleo F030R8
    ...

3. Show boards which are based on ``ATmega168`` MCU

.. code-block:: bash

    $ platformio boards atmega168

    Platform: atmelavr
    ---------------------------------------------------------------------------
    Type                  MCU           Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    btatmega168           atmega168     16Mhz     14Kb    1Kb    Arduino BT ATmega168
    diecimilaatmega168    atmega168     16Mhz     14Kb    1Kb    Arduino Duemilanove or Diecimila ATmega168
    miniatmega168         atmega168     16Mhz     14Kb    1Kb    Arduino Mini ATmega168
    atmegangatmega168     atmega168     16Mhz     14Kb    1Kb    Arduino NG or older ATmega168
    nanoatmega168         atmega168     16Mhz     14Kb    1Kb    Arduino Nano ATmega168
    pro8MHzatmega168      atmega168     8Mhz      14Kb    1Kb    Arduino Pro or Pro Mini ATmega168 (3.3V, 8 MHz)
    pro16MHzatmega168     atmega168     16Mhz     14Kb    1Kb    Arduino Pro or Pro Mini ATmega168 (5V, 16 MHz)
    lilypadatmega168      atmega168     8Mhz      14Kb    1Kb    LilyPad Arduino ATmega168
    168pa16m              atmega168p    16Mhz     15Kb    1Kb    Microduino Core (Atmega168PA@16M,5V)
    168pa8m               atmega168p    8Mhz      15Kb    1Kb    Microduino Core (Atmega168PA@8M,3.3V)

4. Show boards by :ref:`platform_timsp430`

.. code-block:: bash

    $ platformio boards timsp430

    Platform: timsp430
    ---------------------------------------------------------------------------
    Type                  MCU           Frequency  Flash   RAM    Name
    ---------------------------------------------------------------------------
    lpmsp430fr5739        msp430fr5739  16Mhz     15Kb    1Kb    FraunchPad w/ msp430fr5739
    lpmsp430f5529         msp430f5529   16Mhz     128Kb   1Kb    LaunchPad w/ msp430f5529 (16MHz)
    lpmsp430f5529_25      msp430f5529   25Mhz     128Kb   1Kb    LaunchPad w/ msp430f5529 (25MHz)
    lpmsp430fr5969        msp430fr5969  8Mhz      64Kb    1Kb    LaunchPad w/ msp430fr5969
    lpmsp430g2231         msp430g2231   1Mhz      2Kb     128B   LaunchPad w/ msp430g2231 (1MHz)
    lpmsp430g2452         msp430g2452   16Mhz     8Kb     256B   LaunchPad w/ msp430g2452 (16MHz)
    lpmsp430g2553         msp430g2553   16Mhz     16Kb    512B   LaunchPad w/ msp430g2553 (16MHz)

