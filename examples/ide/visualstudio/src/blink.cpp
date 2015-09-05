#include "Arduino.h"

// Most Arduino boards already have a LED attached to pin 13 on the board itself
#define LED_PIN 13

void setup() {
  pinMode(LED_PIN, OUTPUT);     // set pin as output
}

void loop() {
  digitalWrite(LED_PIN, HIGH);  // set the LED on
  delay(1000);                  // wait for a second
  digitalWrite(LED_PIN, LOW);   // set the LED off
  delay(1000);                  // wait for a second
}
