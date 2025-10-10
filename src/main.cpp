#include <Arduino.h>

void setup() {
    // Initialize serial communication
    Serial.begin(9600);
    // Initialize LED pin
    pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    // Toggle LED
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
}