/**
 * Copyright (C) Ivan Kravets <me@ikravets.com>
 * See LICENSE for details.
 */

#include "Energia.h"

void setup()
{
  pinMode(GREEN_LED, OUTPUT);     // set pin as output
}

void loop()
{
  digitalWrite(GREEN_LED, HIGH);  // set the LED on
  delay(1000);                  // wait for a second
  digitalWrite(GREEN_LED, LOW);   // set the LED off
  delay(1000);                  // wait for a second
}
