/**
 * Copyright (C) Ivan Kravets <me@ikravets.com>
 * See LICENSE for details.
 */

/**
  Turns ON and OFF the Wiring compatible board LED,
  with intervals of 1 second (1000 milliseconds)
*/

#include "Arduino.h"

#ifndef LED_PIN
#define LED_PIN 13  // Most Arduino boards already have an LED attached to pin 13 on the board itself
#endif


void setup()
{
  pinMode(LED_PIN, OUTPUT);     // set pin as output
}

void loop()
{
  digitalWrite(LED_PIN, HIGH);  // set the LED on
  delay(1000);                  // wait for a second
  digitalWrite(LED_PIN, LOW);   // set the LED off
  delay(1000);                  // wait for a second
}
