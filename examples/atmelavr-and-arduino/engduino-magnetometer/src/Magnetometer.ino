#include <EngduinoMagnetometer.h>
#include <Wire.h>

// Magnetometer demo
//
// Print the field strength values
//

void setup()
{ 
  EngduinoMagnetometer.begin();
}

void loop()
{ 
  float magneticField[3];

  // Read magnetic field strength. The values range from -20000
  // to +20000 counts and are based on internal calibration
  // values
  //
  EngduinoMagnetometer.xyz(magneticField);
  
  float x = magneticField[0];
  float y = magneticField[1];
  float z = magneticField[2];
  Serial.print("Magnetic field strength: x = ");
  Serial.print(x);
  Serial.print(" counts y = ");
  Serial.print(y);
  Serial.print(" counts z = ");
  Serial.print(z);
  Serial.println(" counts");
  
  // Note that this is an uncalibrated temperature
  // of the die itself. Whilst it should be a value
  // in degrees C, the lack of calibration could mean
  // that it's anything.
  int8_t t = EngduinoMagnetometer.temperature();
  Serial.print("Temperature: ");
  Serial.println(t);
  
  delay(1000);
}