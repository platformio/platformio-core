/**
 * Copyright (C) Ivan Kravets <me@ikravets.com>
 * See LICENSE for details.
 */

/**
  Turns ON and OFF the Wiring compatible board LED,
  with intervals of 1 second (1000 milliseconds)
*/

#ifdef ENERGIA

#include "Energia.h"
#define WLED  RED_LED

#else

#include "Arduino.h"
#define WLED	13  // Most Arduino boards already have an LED attached to pin 13 on the board itself

#endif

void setup()
{
  pinMode(WLED, OUTPUT);  // set pin as output
}

void loop()
{
  digitalWrite(WLED, HIGH);  // set the LED on
  delay(1000);               // wait for a second
  digitalWrite(WLED, LOW);   // set the LED off
  delay(1000);               // wait for a second
}