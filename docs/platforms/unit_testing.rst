..  Copyright 2014-present PlatformIO <contact@platformio.org>
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

.. _unit_testing:

Unit Testing
============

.. versionadded:: 3.0

`Unit Testing (wiki) <https://en.wikipedia.org/wiki/Unit_testing>`_
is a software testing method by which individual units of source code, sets
of one or more MCU program modules together with associated control data,
usage procedures, and operating procedures, are tested to determine whether
they are fit for use. Unit testing finds problems early in the development cycle.

PlatformIO Test System is very interesting for embedded development.
It allows you to write tests locally and run them directly on the target
device (hardware unit testing). Also, you will be able to run the same tests
on the different target devices (:ref:`embedded_boards`).

PlatformIO Test System consists of:

* Project builder
* Test builder
* Firmware uploader
* Test processor

There is special command :ref:`cmd_test` to run tests from PlatformIO Project.

.. contents::

.. _unit_testing_design:

Design
------

PlatformIO Test System design is based on a few isolated components:

1. **Main program**. Contains the independent modules, procedures,
   functions or methods that will be the target candidates (TC) for testing.
2. **Unit test**. This a small independent program that is intended to
   re-use TC from the main program and apply tests for them.
3. **Test processor**. The set of approaches and tools that will be used
   to apply test for the environments from :ref:`projectconf`.

Workflow
--------

1. Create PlatformIO project using :ref:`cmd_init` command.
2. Place source code of main program to ``src`` directory.
3. Wrap ``main()`` or ``setup()/loop()`` methods of main program in ``UNIT_TEST``
   guard:

   .. code-block:: c

       /**
        * Arduino Wiring-based Framework
        */
       #ifndef UNIT_TEST
       void setup () {
          // some code...
       }

       void loop () {
          // some code...
       }
       #endif

       /**
        * Generic C/C++
        */
       #ifndef UNIT_TEST
       int main() {
          // setup code...

          while (1) {
              // loop code...
          }
       }
       #endif

4. Create ``test`` directory in the root of project. See :ref:`projectconf_pio_test_dir`.
5. Write test using :ref:`unit_testing_api`. The each test is a small
   independent program with own ``main()`` or ``setup()/loop()`` methods. Also,
   test should start from ``UNITY_BEGIN()`` and finish with ``UNITY_END()``.
6. Place test to ``test`` directory. If you have more than one test, split them
   into sub-folders. For example, ``test/test_1/*.[c,cpp,h]``,
   ``test_N/*.[c,cpp,h]``, etc. If no such directory in ``test`` folder, then
   PlatformIO Test System will treat the source code of ``test`` folder
   as SINGLE test.
7. Run tests using :ref:`cmd_test` command.

.. _unit_testing_api:

Test API
--------

The summary of `Unity Test API <https://github.com/ThrowTheSwitch/Unity#unity-test-api>`_:

* `Running Tests <https://github.com/ThrowTheSwitch/Unity#running-tests>`_

  - ``RUN_TEST(func, linenum)``

* `Ignoring Tests <https://github.com/ThrowTheSwitch/Unity#ignoring-tests>`_

  - ``TEST_IGNORE()``
  - ``TEST_IGNORE_MESSAGE (message)``

* `Aborting Tests <https://github.com/ThrowTheSwitch/Unity#aborting-tests>`_

  - ``TEST_PROTECT()``
  - ``TEST_ABORT()``

* `Basic Validity Tests <https://github.com/ThrowTheSwitch/Unity#basic-validity-tests>`_

  - ``TEST_ASSERT_TRUE(condition)``
  - ``TEST_ASSERT_FALSE(condition)``
  - ``TEST_ASSERT(condition)``
  - ``TEST_ASSERT_UNLESS(condition)``
  - ``TEST_FAIL()``
  - ``TEST_FAIL_MESSAGE(message)``

* `Numerical Assertions: Integers <https://github.com/ThrowTheSwitch/Unity#numerical-assertions-integers>`_

  - ``TEST_ASSERT_EQUAL_INT(expected, actual)``
  - ``TEST_ASSERT_EQUAL_INT8(expected, actual)``
  - ``TEST_ASSERT_EQUAL_INT16(expected, actual)``
  - ``TEST_ASSERT_EQUAL_INT32(expected, actual)``
  - ``TEST_ASSERT_EQUAL_INT64(expected, actual)``

  - ``TEST_ASSERT_EQUAL_UINT(expected, actual)``
  - ``TEST_ASSERT_EQUAL_UINT8(expected, actual)``
  - ``TEST_ASSERT_EQUAL_UINT16(expected, actual)``
  - ``TEST_ASSERT_EQUAL_UINT32(expected, actual)``
  - ``TEST_ASSERT_EQUAL_UINT64(expected, actual)``

  - ``TEST_ASSERT_EQUAL_HEX(expected, actual)``
  - ``TEST_ASSERT_EQUAL_HEX8(expected, actual)``
  - ``TEST_ASSERT_EQUAL_HEX16(expected, actual)``
  - ``TEST_ASSERT_EQUAL_HEX32(expected, actual)``
  - ``TEST_ASSERT_EQUAL_HEX64(expected, actual)``
  - ``TEST_ASSERT_EQUAL_HEX8_ARRAY(expected, actual, elements)``

  - ``TEST_ASSERT_EQUAL(expected, actual)``
  - ``TEST_ASSERT_INT_WITHIN(delta, expected, actual)``

* `Numerical Assertions: Bitwise <https://github.com/ThrowTheSwitch/Unity#numerical-assertions-bitwise>`_

  - ``TEST_ASSERT_BITS(mask, expected, actual)``
  - ``TEST_ASSERT_BITS_HIGH(mask, actual)``
  - ``TEST_ASSERT_BITS_LOW(mask, actual)``
  - ``TEST_ASSERT_BIT_HIGH(mask, actual)``
  - ``TEST_ASSERT_BIT_LOW(mask, actual)``

* `Numerical Assertions: Floats <https://github.com/ThrowTheSwitch/Unity#numerical-assertions-floats>`_

  - ``TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual)``
  - ``TEST_ASSERT_EQUAL_FLOAT(expected, actual)``
  - ``TEST_ASSERT_EQUAL_DOUBLE(expected, actual)``

* `String Assertions <https://github.com/ThrowTheSwitch/Unity#string-assertions>`_

  - ``TEST_ASSERT_EQUAL_STRING(expected, actual)``
  - ``TEST_ASSERT_EQUAL_STRING_LEN(expected, actual, len)``
  - ``TEST_ASSERT_EQUAL_STRING_MESSAGE(expected, actual, message)``
  - ``TEST_ASSERT_EQUAL_STRING_LEN_MESSAGE(expected, actual, len, message)``

* `Pointer Assertions <https://github.com/ThrowTheSwitch/Unity#pointer-assertions>`_

  - ``TEST_ASSERT_NULL(pointer)``
  - ``TEST_ASSERT_NOT_NULL(pointer)``

* `Memory Assertions <https://github.com/ThrowTheSwitch/Unity#pointer-assertions>`_

  - ``TEST_ASSERT_EQUAL_MEMORY(expected, actual, len)``

Example
-------

1. Please follow to :ref:`quickstart` and create "Blink Project". According
   to the Unit Testing :ref:`unit_testing_design` it is the **Main program**.
2. Create ``test`` directory in that project (on the same level as ``src``)
   and place ``test_main.cpp`` file to it (the source code is located below).
3. Wrap ``setup()`` and ``loop()`` methods of main program in ``UNIT_TEST``
   guard.
4. Run tests using :ref:`cmd_test` command.

Project structure
~~~~~~~~~~~~~~~~~

.. code-block:: bash

    project_dir
    ├── lib
    │   └── readme.txt
    ├── platformio.ini
    ├── src
    │   └── main.cpp
    └── test
        └── test_main.cpp

Source files
~~~~~~~~~~~~

* ``platformio.ini``

  .. code-block:: ini

      ; Project Configuration File
      ; Docs: http://docs.platformio.org/en/latest/projectconf.html

      [env:uno]
      platform = atmelavr
      framework = arduino
      board = uno

      [env:nodemcu]
      platform = espressif
      framework = arduino
      board = nodemcu

      [env:teensy31]
      platform = teensy
      framework = arduino
      board = teensy31

* ``src/main.cpp``

  .. code-block:: cpp

      /*
       * Blink
       * Turns on an LED on for one second,
       * then off for one second, repeatedly.
       */

      #include "Arduino.h"

      #ifndef UNIT_TEST  // IMPORTANT LINE!

      void setup()
      {
        // initialize LED digital pin as an output.
        pinMode(LED_BUILTIN, OUTPUT);
      }

      void loop()
      {
        // turn the LED on (HIGH is the voltage level)
        digitalWrite(LED_BUILTIN, HIGH);
        // wait for a second
        delay(1000);
        // turn the LED off by making the voltage LOW
        digitalWrite(LED_BUILTIN, LOW);
         // wait for a second
        delay(1000);
      }

      #endif    // IMPORTANT LINE!

* ``test/test_main.cpp``

  .. code-block:: cpp

      #include <Arduino.h>
      #include <unity.h>

      #ifdef UNIT_TEST

      // void setUp(void) {
      // // set stuff up here
      // }

      // void tearDown(void) {
      // // clean stuff up here
      // }

      void test_led_builtin_pin_number(void) {
          TEST_ASSERT_EQUAL(LED_BUILTIN, 13);
      }

      void test_led_state_high(void) {
          digitalWrite(LED_BUILTIN, HIGH);
          TEST_ASSERT_EQUAL(digitalRead(LED_BUILTIN), HIGH);
      }

      void test_led_state_low(void) {
          digitalWrite(LED_BUILTIN, LOW);
          TEST_ASSERT_EQUAL(digitalRead(LED_BUILTIN), LOW);
      }

      void setup() {
          UNITY_BEGIN();    // IMPORTANT LINE!
          RUN_TEST(test_led_builtin_pin_number);

          pinMode(LED_BUILTIN, OUTPUT);
      }

      uint8_t i = 0;
      uint8_t max_blinks = 5;

      void loop() {
          if (i < max_blinks)
          {
              RUN_TEST(test_led_state_high);
              delay(500);
              RUN_TEST(test_led_state_low);
              delay(500);
              i++;
          }
          else if (i == max_blinks) {
            UNITY_END(); // stop unit testing
          }
      }

      #endif

Test results
~~~~~~~~~~~~

.. code-block:: bash

    > platformio test --environment uno
    Collected 1 items

    ========================= [test::*] Building... (1/3) ==============================

    [Wed Jun 15 00:27:42 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    avr-g++ -o .pioenvs/uno/test/test_main.o -c -fno-exceptions -fno-threadsafe-statics -std=gnu++11 -g -Os -Wall -ffunction-sections -fdata-sections -mmcu=atmega328p -DF_CPU=16000000L -DPLATFORMIO=030000 -DARDUINO_ARCH_AVR -DARDUINO_AVR_UNO -DARDUINO=10608 -DUNIT_TEST -DUNITY_INCLUDE_CONFIG_H -I.pioenvs/uno/FrameworkArduino -I.pioenvs/uno/FrameworkArduinoVariant -Isrc -I.pioenvs/uno/UnityTestLib test/test_main.cpp
    avr-g++ -o .pioenvs/uno/firmware.elf -Os -mmcu=atmega328p -Wl,--gc-sections,--relax .pioenvs/uno/src/main.o .pioenvs/uno/test/output_export.o .pioenvs/uno/test/test_main.o -L.pioenvs/uno -Wl,--start-group .pioenvs/uno/libUnityTestLib.a .pioenvs/uno/libFrameworkArduinoVariant.a .pioenvs/uno/libFrameworkArduino.a -lm -Wl,--end-group
    avr-objcopy -O ihex -R .eeprom .pioenvs/uno/firmware.elf .pioenvs/uno/firmware.hex
    avr-size --mcu=atmega328p -C -d .pioenvs/uno/firmware.elf
    AVR Memory Usage
    ----------------
    Device: atmega328p

    Program:    4702 bytes (14.3% Full)
    (.text + .data + .bootloader)

    Data:        460 bytes (22.5% Full)
    (.data + .bss + .noinit)


    ========================= [test::*] Uploading... (2/3)  ==============================

    [Wed Jun 15 00:27:43 2016] Processing uno (platform: atmelavr, board: uno, framework: arduino)
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------
    avr-g++ -o .pioenvs/uno/firmware.elf -Os -mmcu=atmega328p -Wl,--gc-sections,--relax .pioenvs/uno/src/main.o .pioenvs/uno/test/output_export.o .pioenvs/uno/test/test_main.o -L.pioenvs/uno -Wl,--start-group .pioenvs/uno/libUnityTestLib.a .pioenvs/uno/libFrameworkArduinoVariant.a .pioenvs/uno/libFrameworkArduino.a -lm -Wl,--end-group
    MethodWrapper([".pioenvs/uno/firmware.elf"], [".pioenvs/uno/src/main.o", ".pioenvs/uno/test/output_export.o", ".pioenvs/uno/test/test_main.o"])
    Check program size...
    text     data     bss     dec     hex filename
    4464      238     222    4924    133c .pioenvs/uno/firmware.elf
    BeforeUpload(["upload"], [".pioenvs/uno/firmware.hex"])
    Looking for upload port/disk...
    avr-size --mcu=atmega328p -C -d .pioenvs/uno/firmware.elf

    Auto-detected: /dev/cu.usbmodemFD131
    avrdude -v -p atmega328p -C "/Users/ikravets/.platformio/packages/tool-avrdude/avrdude.conf" -c arduino -b 115200 -P "/dev/cu.usbmodemFD131" -D -U flash:w:.pioenvs/uno/firmware.hex:i

    [...]

    avrdude done.  Thank you.

    ========================= [test::*] Testing... (3/3) =========================

    If you do not see any output for the first 10 secs, please reset board (press reset button)

    test/test_main.cpp:30:test_led_builtin_pin_number PASSED
    test/test_main.cpp:41:test_led_state_high PASSED
    test/test_main.cpp:43:test_led_state_low  PASSED
    test/test_main.cpp:41:test_led_state_high PASSED
    test/test_main.cpp:43:test_led_state_low  PASSED
    test/test_main.cpp:41:test_led_state_high PASSED
    test/test_main.cpp:43:test_led_state_low  PASSED
    test/test_main.cpp:41:test_led_state_high PASSED
    test/test_main.cpp:43:test_led_state_low  PASSED
    test/test_main.cpp:41:test_led_state_high PASSED
    test/test_main.cpp:43:test_led_state_low  PASSED
    -----------------------
    11 Tests 0 Failures 0 Ignored

    ========================= [TEST SUMMARY] =====================================
    test:*/env:uno  PASSED
    ========================= [PASSED] Took 13.35 seconds ========================

-------

For the other examples and source code please follow to
`PlatformIO Unit Testing Examples <https://github.com/platformio/platformio-examples/tree/feature/platformio-30/unit-testing>`_ repository.
