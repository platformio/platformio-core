.. _platform_atmelavr:

Platform ``atmelavr``
=====================

`Atmel AVR® 8- and 32-bit MCUs <http://www.atmel.com/products/microcontrollers/avr/default.aspx>`_
deliver a unique combination of performance, power efficiency and design
flexibility. Optimized to speed time to market—and easily adapt to new
ones—they are based on the industry's most code-efficient architecture for
C and assembly programming.

.. contents::

Packages
--------

.. list-table::
    :header-rows:  1

    * - Name
      - Alias
      - Contents
    * - ``toolchain-atmelavr``
      - toolchain
      - `avr-gcc <https://gcc.gnu.org/wiki/avr-gcc>`_,
        `GDB <http://www.gnu.org/software/gdb/>`_,
        `AVaRICE <http://avarice.sourceforge.net>`_,
        `SimulAVR <http://www.nongnu.org/simulavr/>`_
    * - ``tool-avrdude``
      - uploader
      - `AVRDUDE <http://www.nongnu.org/avrdude/>`_
    * - ``framework-arduinoavr``
      - framework
      - See below in :ref:`atmelavr_frameworks`


.. note::
    You can install ``atmelavr`` platform with these packages
    via :ref:`cmd_install` command.


.. _atmelavr_frameworks:

Frameworks
----------

.. list-table::
    :header-rows:  1

    * - Type ``framework``
      - Name
      - Reference
    * - ``arduino``
      - Arduino Wiring-based Framework (AVR Core, 1.5.x branch)
      - `Documentation <http://arduino.cc/en/Reference/HomePage>`_


Boards
------

.. note::
   For more detailed ``board`` information please scroll tables below by
   horizontal.

Arduino
~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller ``board_mcu``
      - Frequency ``board_f_cpu``
      - Flash
      - RAM
    * - ``diecimilaatmega168``
      - `Arduino Diecimila or Duemilanove (ATmega168)
        <http://arduino.cc/en/Main/ArduinoBoardDiecimila>`_
      - ATmega168 ``atmega168``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 1 Kb
    * - ``diecimilaatmega328``
      - `Arduino Diecimila or Duemilanove (ATmega328)
        <http://arduino.cc/en/Main/ArduinoBoardDiecimila>`_
      - ATmega328 ``atmega328``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb
    * - ``fio``
      - `Arduino Fio
        <http://arduino.cc/en/Main/ArduinoBoardFio>`_
      - ATmega328P ``atmega328p``
      - 8 MHz ``8000000L``
      - 32 Kb
      - 2 Kb
    * - ``leonardo``
      - `Arduino Leonardo <http://arduino.cc/en/Main/arduinoBoardLeonardo>`_
      - ATmega32u4 ``atmega32u4``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2.5 Kb
    * - ``LilyPadUSB``
      - `Arduino LilyPad USB
        <http://arduino.cc/en/Main/ArduinoBoardLilyPadUSB>`_
      - ATmega32u4 ``atmega32u4``
      - 8 MHz ``8000000L``
      - 32 Kb
      - 2.5 Kb
    * - ``lilypadatmega168``
      - `Arduino LilyPad (ATmega168)
        <http://arduino.cc/en/Main/ArduinoBoardLilyPad>`_
      - ATmega168 ``atmega168``
      - 8 MHz ``8000000L``
      - 16 Kb
      - 1 Kb
    * - ``lilypadatmega328``
      - `Arduino LilyPad (ATmega328)
        <http://arduino.cc/en/Main/ArduinoBoardLilyPad>`_
      - ATmega328P ``atmega328p``
      - 8 MHz ``8000000L``
      - 32 Kb
      - 2 Kb
    * - ``megaatmega1280``
      - `Arduino Mega (ATmega1280)
        <http://arduino.cc/en/Main/arduinoBoardMega>`_
      - ATmega1280 ``atmega1280``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 8 Kb
    * - ``megaatmega2560``
      - `Arduino Mega (ATmega2560)
        <http://arduino.cc/en/Main/arduinoBoardMega2560>`_
      - ATmega2560 ``atmega2560``
      - 16 MHz ``16000000L``
      - 256 Kb
      - 8 Kb
    * - ``megaADK``
      - `Arduino Mega ADK
        <http://arduino.cc/en/Main/ArduinoBoardMegaADK>`_
      - ATmega2560 ``atmega2560``
      - 16 MHz ``16000000L``
      - 256 Kb
      - 8 Kb
    * - ``micro``
      - `Arduino Micro
        <http://arduino.cc/en/Main/ArduinoBoardMicro>`_
      - ATmega32u4 ``atmega32u4``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2.5 Kb
    * - ``miniatmega168``
      - `Arduino Mini (ATmega168)
        <http://arduino.cc/en/Main/ArduinoBoardMini>`_
      - ATmega168 ``atmega168``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 1 Kb
    * - ``miniatmega328``
      - `Arduino Mini (ATmega328P)
        <http://arduino.cc/en/Main/ArduinoBoardMini>`_
      - ATmega328P ``atmega328p``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb
    * - ``nanoatmega168``
      - `Arduino Nano (ATmega168)
        <http://arduino.cc/en/Main/ArduinoBoardNano>`_
      - ATmega168 ``atmega168``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 1 Kb
    * - ``nanoatmega328``
      - `Arduino Nano (ATmega328P)
        <http://arduino.cc/en/Main/ArduinoBoardNano>`_
      - ATmega328P ``atmega328p``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb
    * - ``pro8MHzatmega168``
      - `Arduino Pro or Pro Mini (ATmega168, 3.3V)
        <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATmega168 ``atmega168``
      - 8 MHz ``8000000L``
      - 16 Kb
      - 1 Kb
    * - ``pro16MHzatmega168``
      - `Arduino Pro or Pro Mini (ATmega168, 5V)
        <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATmega168 ``atmega168``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 1 Kb
    * - ``pro8MHzatmega328``
      - `Arduino Pro or Pro Mini (ATmega328P, 3.3V)
        <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATmega328P ``atmega328p``
      - 8 MHz ``8000000L``
      - 32 Kb
      - 2 Kb
    * - ``pro16MHzatmega328``
      - `Arduino Pro or Pro Mini (ATmega328P, 5V)
        <http://arduino.cc/en/Main/ArduinoBoardProMini>`_
      - ATmega328P ``atmega328p``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb
    * - ``uno``
      - `Arduino Uno
        <http://arduino.cc/en/Main/ArduinoBoardUno>`_
      - ATmega328P ``atmega328p``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb

More detailed information you can find here
`Arduino boards <http://arduino.cc/en/Main/Products>`_.


Microduino
~~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller ``board_mcu``
      - Frequency ``board_f_cpu``
      - Flash
      - RAM
    * - ``168pa8m``
      - `Microduino Core (ATmega168P, 3.3V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATmega168P ``atmega168p``
      - 8 MHz ``8000000L``
      - 16 Kb
      - 1 Kb
    * - ``168pa16m``
      - `Microduino Core (ATmega168P, 5V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATmega168P ``atmega168p``
      - 16 MHz ``16000000L``
      - 16 Kb
      - 1 Kb
    * - ``328p8m``
      - `Microduino Core (ATmega328P, 3.3V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATmega328P ``atmega328p``
      - 8 MHz ``8000000L``
      - 32 Kb
      - 2 Kb
    * - ``328p16m``
      - `Microduino Core (ATmega328P, 5V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core>`_
      - ATmega328P ``atmega328p``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb
    * - ``644pa8m``
      - `Microduino Core+ (ATmega644PA, 3.3V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - ATmega644PA ``atmega644p``
      - 8 MHz ``8000000L``
      - 64 Kb
      - 4 Kb
    * - ``644pa16m``
      - `Microduino Core+ (ATmega644PA, 5V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - ATmega644PA ``atmega644p``
      - 16 MHz ``16000000L``
      - 64 Kb
      - 4 Kb
    * - ``1284p8m``
      - `Microduino Core+ (Atmega1284P, 3.3V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - Atmega1284P ``atmega1284p``
      - 8 MHz ``8000000L``
      - 128 Kb
      - 16 Kb
    * - ``1284p16m``
      - `Microduino Core+ (Atmega1284P, 5V)
        <http://www.microduino.cc/wiki/index.php?title=Microduino-Core%2B>`_
      - Atmega1284P ``atmega1284p``
      - 16 MHz ``16000000L``
      - 128 Kb
      - 16 Kb
    * - ``32u416m``
      - `Microduino-Core USB
        <http://www.microduino.cc/wiki/index.php?title=Microduino-CoreUSB>`_
      - ATmega32u4 ``atmega32u4``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2.5 Kb


More detailed information you can find here
`Microduino boards <http://www.microduino.cc/wiki/index.php?title=Main_Page>`_.


Raspduino
~~~~~~~~~

.. list-table::
    :header-rows:  1

    * - Type ``board``
      - Name
      - Microcontroller ``board_mcu``
      - Frequency ``board_f_cpu``
      - Flash
      - RAM
    * - ``raspduino``
      - `Raspduino
        <http://www.bitwizard.nl/wiki/index.php/Raspduino>`_
      - ATmega328P ``atmega328p``
      - 16 MHz ``16000000L``
      - 32 Kb
      - 2 Kb

More detailed information you can find in
`Wiki <http://www.bitwizard.nl/wiki/index.php/Raspduino>`_.
