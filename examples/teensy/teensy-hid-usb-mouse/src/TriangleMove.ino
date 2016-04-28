/* Simple USB Mouse Example
   Teensy becomes a USB mouse and moves the cursor in a triangle

   You must select Mouse from the "Tools > USB Type" menu

   This example code is in the public domain.
*/

#include <Arduino.h>

void setup() { } // no setup needed
void loop() {
  int i;
  for (i=0; i<40; i++) {
    Mouse.move(2, -1);
    delay(25);
  }
  for (i=0; i<40; i++) {
    Mouse.move(2, 2);
    delay(25);
  }
  for (i=0; i<40; i++) {
    Mouse.move(-4, -1);
    delay(25);
  }
}