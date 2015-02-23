#include <EngduinoLEDs.h>
#include <EngduinoAccelerometer.h>
#include <Wire.h>

// Accelerometer demo - level
//
// Show a red LED on one side if we're low on that side
// show nothing if we're high, and show green on both sides
// if it's level(ish)
//
// We delay between readings because it's a bit flashy
// otherwise - too hard to hold steady
//

void setup()
{
  EngduinoLEDs.begin();
  EngduinoAccelerometer.begin();
}

void loop()
{ float xyz[3];

  // Read the acceleration
  //
  EngduinoAccelerometer.xyz(xyz);
  
  // And light the appropriate LEDs depending on whether we're level
  // or not. The LEDs chosen are on opposite sides of the board.
  //
  if ((xyz[0] > 0 && xyz[0] < 0.02) || (xyz[0] < 0 && xyz[0] > -0.02)) {
    EngduinoLEDs.setLED(12, GREEN);
    EngduinoLEDs.setLED( 4, GREEN);
  }
  else if (xyz[0] > 0.02) {
    EngduinoLEDs.setLED(12, RED);
    EngduinoLEDs.setLED( 4, OFF);    
  }
  else {
    EngduinoLEDs.setLED(12, OFF);
    EngduinoLEDs.setLED( 4, RED);
  }
  
  if ((xyz[1] > 0 && xyz[1] < 0.02) || (xyz[1] < 0 && xyz[1] > -0.02)) {
    EngduinoLEDs.setLED( 9, GREEN);
    EngduinoLEDs.setLED(15, GREEN);
  }
  else if (xyz[1] > 0.02) {
    EngduinoLEDs.setLED( 9, RED);
    EngduinoLEDs.setLED(15, OFF);    
  }
  else {
    EngduinoLEDs.setLED( 9, OFF);
    EngduinoLEDs.setLED(15, RED);
  }
  
  // Wait 50ms, then loop
  //
  delay(50);
}
