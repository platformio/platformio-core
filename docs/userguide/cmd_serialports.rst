.. _cmd_serialports:

platformio serialports
======================

.. contents::

platformio serialports list
---------------------------

Usage
~~~~~

.. code-block:: bash

    platformio serialports list


Description
~~~~~~~~~~~

List available `Serial Ports <http://en.wikipedia.org/wiki/Serial_port>`_


Examples
~~~~~~~~

1. Unix OS

.. code-block:: bash

    $ platformio serialports list
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

    $ platformio serialports list
    COM4
    ----------
    Hardware ID: USB VID:PID=0451:F432
    Description: MSP430 Application UART (COM4)

    COM3
    ----------
    Hardware ID: USB VID:PID=10C4:EA60 SNR=0001
    Description: Silicon Labs CP210x USB to UART Bridge (COM3)


platformio serialports monitor
------------------------------

Usage
~~~~~

.. code-block:: bash

    platformio serialports monitor [OPTIONS]


Description
~~~~~~~~~~~

This is a console application that provides a small terminal
application. It is based on `Miniterm <http://pyserial.sourceforge.net/examples.html#miniterm>`_
and itself does not implement any terminal features such
as *VT102* compatibility. However it inherits these features from the terminal
it is run. For example on GNU/Linux running from an *xterm* it will support the
escape sequences of the *xterm*. On *Windows* the typical console window is dumb
and does not support any escapes. When *ANSI.sys* is loaded it supports some
escapes.

To control *monitor* please use these "hot keys":

* ``Ctrl+]`` Quit
* ``Ctrl+T`` Menu
* ``Ctrl+T followed by Ctrl+H`` Help

Options
~~~~~~~

.. option::
    -p, --port

Port, a number or a device name

.. option::
    -b, --baud

Set baud rate, default ``9600``

.. option::
    --parity

Set parity (*None, Even, Odd, Space, Mark*), one of
[``N``, ``E``, ``O``, ``S``, ``M``], default ``N``

.. option::
    --rtscts

Enable ``RTS/CTS`` flow control, default ``Off``

.. option::
    --xonxoff

Enable software flow control, default ``Off``

.. option::
    --rts

Set initial ``RTS`` line state, default ``0``

.. option::
    --dtr

Set initial ``DTR`` line state, default ``0``

.. option::
    --echo

Enable local echo, default ``Off``

.. option::
    --cr

Do not send ``CR+LF``, send ``R`` only, default ``Off``

.. option::
    --lf

Do not send ``CR+LF``, send ``LF`` only, default ``Off``

.. option::
    -d, --debug

Debug received data (escape non-printable chars). ``--debug`` can be given
multiple times:

0. just print what is received
1. escape non-printable characters, do newlines as unusual
2. escape non-printable characters, newlines too
3. hex dump everything

.. option::
    --exit-char

ASCII code of special character that is used to exit the application,
default ``0x1d``

.. option::
    --menu-char

ASCII code of special character that is used to control miniterm (menu),
default ``0x14``

.. option::
    ---quiet

Diagnostics: suppress non-error messages, default ``Off``

Examples
~~~~~~~~

1. Show available option for command

.. code-block:: bash

    $ platformio serialports monitor --help
    Usage: platformio serialports monitor [OPTIONS]

    Options:
      -p, --port TEXT       Port, a number or a device name
      -b, --baud INTEGER    Set baud rate, default=9600
      --parity [N|E|O|S|M]  Set parity, default=N
      --rtscts              Enable RTS/CTS flow control, default=Off
      --xonxoff             Enable software flow control, default=Off
      --rts [0|1]           Set initial RTS line state, default=0
      --dtr [0|1]           Set initial DTR line state, default=0
      --echo                Enable local echo, default=Off
      --cr                  Do not send CR+LF, send CR only, default=Off
      --lf                  Do not send CR+LF, send LF only, default=Off
      -d, --debug           Debug received data (escape non-printable chars)
                            --debug can be given multiple times:
                            0: just print what is received
                            1: escape non-printable characters, do newlines as
                               unusual
                            2: escape non-printable characters, newlines too
                            3: hex dump everything
      --exit-char INTEGER   ASCII code of special character that is used to exit
                            the application, default=0x1d
      --menu-char INTEGER   ASCII code of special character that is used to
                            control miniterm (menu), default=0x14
      --quiet               Diagnostics: suppress non-error messages, default=Off
      --help                Show this message and exit.

2. Communicate with serial device and print help inside terminal

.. code-block:: bash

    $ platformio serialports monitor

    --- Available ports:
    --- /dev/cu.Bluetooth-Incoming-Port n/a
    --- /dev/cu.Bluetooth-Modem n/a
    --- /dev/cu.SLAB_USBtoUART CP2102 USB to UART Bridge Controller
    --- /dev/cu.obd2ecu-SPPDev n/a
    Enter port name:/dev/cu.SLAB_USBtoUART
    --- Miniterm on /dev/cu.SLAB_USBtoUART: 9600,8,N,1 ---
    --- Quit: Ctrl+]  |  Menu: Ctrl+T | Help: Ctrl+T followed by Ctrl+H ---
    Hello PlatformIO!
    --- pySerial (2.7) - miniterm - help
    ---
    --- Ctrl+]   Exit program
    --- Ctrl+T   Menu escape key, followed by:
    --- Menu keys:
    ---    Ctrl+T  Send the menu character itself to remote
    ---    Ctrl+]  Send the exit character itself to remote
    ---    Ctrl+I  Show info
    ---    Ctrl+U  Upload file (prompt will be shown)
    --- Toggles:
    ---    Ctrl+R  RTS          Ctrl+E  local echo
    ---    Ctrl+D  DTR          Ctrl+B  BREAK
    ---    Ctrl+L  line feed    Ctrl+A  Cycle repr mode
    ---
    --- Port settings (Ctrl+T followed by the following):
    ---    p          change port
    ---    7 8        set data bits
    ---    n e o s m  change parity (None, Even, Odd, Space, Mark)
    ---    1 2 3      set stop bits (1, 2, 1.5)
    ---    b          change baud rate
    ---    x X        disable/enable software flow control
    ---    r R        disable/enable hardware flow control
    --- exit ---
