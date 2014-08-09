/***************************************************
  This is an example for the Adafruit CC3000 Wifi Breakout & Shield

  Designed specifically to work with the Adafruit WiFi products:
  ----> https://www.adafruit.com/products/1469

  Adafruit invests time and resources providing this open source code,
  please support Adafruit and open-source hardware by purchasing
  products from Adafruit!

  Written by Limor Fried, Kevin Townsend and Phil Burgess for
  Adafruit Industries.  BSD license, all text above must be included
  in any redistribution
 ****************************************************/
 
/*
This example queries the freegeoip.net service to get the local
approximate geographic location based on IP address.  Combined with
code in the InternetTime sketch, this can give absolute position and
time, extremely useful for seasonal calculations like sun position,
insolation, day length, etc.  Sure, could always add a GPS module or
just plug in values from one's GPS or phone, but this has the dual
luxuries of coming 'free' with the existing WiFi hardware, and being
automatic (albeit a bit less accurate...but totally sufficient for
the applications mentioned).

Positional accuracy depends on the freegeoip.net database, in turn
based on data collected by maxmind.com.  No guarantees this will work
for every location.

Position should be polled only once, at startup, or very infrequently
if making a mobile network-hopping thing, so as not to overwhelm the
kindly-provided free geolocation service.
*/

#include <Adafruit_CC3000.h>
#include <ccspi.h>
#include <SPI.h>
#include <string.h>
#include "utility/debug.h"

// These are the interrupt and control pins
#define ADAFRUIT_CC3000_IRQ   3  // MUST be an interrupt pin!
// These can be any two pins
#define ADAFRUIT_CC3000_VBAT  5
#define ADAFRUIT_CC3000_CS    10
// Use hardware SPI for the remaining pins
// On an UNO, SCK = 13, MISO = 12, and MOSI = 11
Adafruit_CC3000 cc3000 = Adafruit_CC3000(ADAFRUIT_CC3000_CS,
  ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT,
  SPI_CLOCK_DIVIDER); // you can change this clock speed

#define WLAN_SSID       "myNetwork"   // cannot be longer than 32 characters!
#define WLAN_PASS       "myPassword"
// Security can be WLAN_SEC_UNSEC, WLAN_SEC_WEP, WLAN_SEC_WPA or WLAN_SEC_WPA2
#define WLAN_SECURITY   WLAN_SEC_WPA2

Adafruit_CC3000_Client client;

const unsigned long
  dhcpTimeout     = 60L * 1000L, // Max time to wait for address from DHCP
  connectTimeout  = 15L * 1000L, // Max time to wait for server connection
  responseTimeout = 15L * 1000L; // Max time to wait for data from server

// This program prints a few tidbits of information about the current location
// (Country, region (state), city, longitude and latitude).  Additional info is
// available but just isn't recorded by this code -- can look at jsonParse()
// function to see how it's done and add what you need (or remove what you don't).
// The total list of available attributes includes: ip, country_code,
// country_name, region_code, region_name, city, zipcode, latitude, longitude,
// metro_code and areacode.
char
  country[20],
  region[20],
  city[20],
  name[13],  // Temp space for name:value parsing
  value[64]; // Temp space for name:value parsing
float
  longitude, latitude;

void setup(void) {
  uint32_t ip = 0L, t;

  Serial.begin(115200);
  Serial.println(F("Hello, CC3000!"));

  Serial.print("Free RAM: "); Serial.println(getFreeRam(), DEC);

  Serial.print(F("Initializing..."));
  if(!cc3000.begin()) {
    Serial.println(F("failed. Check your wiring?"));
    return;
  }

  Serial.print(F("OK.\r\nConnecting to network..."));
  if(!cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY)) {
    Serial.println(F("Failed!"));
    return;
  }
  Serial.println(F("connected!"));

  Serial.print(F("Requesting address from DHCP server..."));
  for(t=millis(); !cc3000.checkDHCP() && ((millis() - t) < dhcpTimeout); delay(1000));
  if(cc3000.checkDHCP()) {
    Serial.println(F("OK"));
  } else {
    Serial.println(F("failed"));
    return;
  }

  while(!displayConnectionDetails()) delay(1000);

  // Look up server's IP address
  Serial.print(F("\r\nGetting server IP address..."));
  t = millis();
  while((0L == ip) && ((millis() - t) < connectTimeout)) {
    if(cc3000.getHostByName("freegeoip.net", &ip)) break;
    delay(1000);
  }
  if(0L == ip) {
    Serial.println(F("failed"));
    return;
  }
  cc3000.printIPdotsRev(ip);
  Serial.println();

  // Request JSON-formatted data from server (port 80)
  Serial.print(F("Connecting to geo server..."));
  client = cc3000.connectTCP(ip, 80);
  if(client.connected()) {
    Serial.print(F("connected.\r\nRequesting data..."));
    client.print(F("GET /json/ HTTP/1.0\r\nConnection: close\r\n\r\n"));
  } else {
    Serial.println(F("failed"));
    return;
  }

  Serial.print("\r\nReading response...");
  country[0] = region[0] = city[0] = 0; // Clear data
  jsonParse(0, 0);
  client.close();
  Serial.println(F("OK"));

  /* You need to make sure to clean up after yourself or the CC3000 can freak out */
  /* the next time your try to connect ... */
  Serial.println(F("\nDisconnecting"));
  cc3000.disconnect();

  Serial.print(F("\r\nRESULTS:\r\n  Country: "));
  Serial.println(country);
  Serial.print(F("  Region: "));
  Serial.println(region);
  Serial.print(F("  City: "));
  Serial.println(city);
  Serial.print(F("  Longitude: "));
  Serial.println(longitude);
  Serial.print(F("  Latitude: "));
  Serial.println(latitude);
}

void loop(void) { } // Not used by this code


bool displayConnectionDetails(void) {
  uint32_t ipAddress, netmask, gateway, dhcpserv, dnsserv;

  if(!cc3000.getIPAddress(&ipAddress, &netmask, &gateway, &dhcpserv, &dnsserv)) {
    Serial.println(F("Unable to retrieve the IP Address!\r\n"));
    return false;
  } else {
    Serial.print(F("\nIP Addr: ")); cc3000.printIPdotsRev(ipAddress);
    Serial.print(F("\nNetmask: ")); cc3000.printIPdotsRev(netmask);
    Serial.print(F("\nGateway: ")); cc3000.printIPdotsRev(gateway);
    Serial.print(F("\nDHCPsrv: ")); cc3000.printIPdotsRev(dhcpserv);
    Serial.print(F("\nDNSserv: ")); cc3000.printIPdotsRev(dnsserv);
    Serial.println();
    return true;
  }
}


// Helper functions swiped from Adafruit 'Gutenbird' code (with changes)

boolean jsonParse(int depth, byte endChar) {
  int     c, i;
  boolean readName = true;
  for(;;) {
    while(isspace(c = timedRead())); // Scan past whitespace
    if(c < 0)        return false;   // Timeout
    if(c == endChar) return true;    // EOD

    if(c == '{') { // Object follows
      if(!jsonParse(depth + 1, '}')) return false;
      if(!depth)                     return true; // End of file
    } else if(c == '[') { // Array follows
      if(!jsonParse(depth + 1,']')) return false;
    } else if((c == '"') || (c == '\'')) { // String follows
      if(readName) { // Name-reading mode
        if(!readString(name, sizeof(name)-1, c)) return false;
      } else { // Value-reading mode
        if(!readString(value, sizeof(value)-1, c)) return false;
        // Process name and value strings:
        if       (!strcasecmp(name, "country_name")) {
          strncpy(country, value, sizeof(country)-1);
        } else if(!strcasecmp(name, "region_name")) {
          strncpy(region, value, sizeof(region)-1);
        } else if(!strcasecmp(name, "city")) {
          strncpy(city, value, sizeof(city)-1);
        }
      }
    } else if(c == ':') { // Separator between name:value
      readName = false; // Now in value-reading mode
      value[0] = 0;     // Clear existing value data
    } else if(c == ',') { // Separator between name/value pairs
      readName = true; // Now in name-reading mode
      name[0]  = 0;    // Clear existing name data
    } else {
      // Else true/false/null or a number follows.
      value[0] = c;
      if(!strcasecmp(name, "longitude")) {
        if(!readString(value+1, sizeof(value)-1, ',')) return false;
        longitude = atof(value);
      } else if(!strcasecmp(name, "latitude")) {
        if(!readString(value+1, sizeof(value)-1, ',')) return false;
        latitude = atof(value);
      }
      readName = true; // Now in name-reading mode
      name[0]  = 0;    // Clear existing name data
    }
  }
}

// Read string from client stream into destination buffer, up to a maximum
// requested length.  Buffer should be at least 1 byte larger than this to
// accommodate NUL terminator.  Opening quote is assumed already read,
// closing quote will be discarded, and stream will be positioned
// immediately following the closing quote (regardless whether max length
// is reached -- excess chars are discarded).  Returns true on success
// (including zero-length string), false on timeout/read error.
boolean readString(char *dest, int maxLen, char quote) {
  int c, len = 0;

  while((c = timedRead()) != quote) { // Read until closing quote
    if(c == '\\') {    // Escaped char follows
      c = timedRead(); // Read it
      // Certain escaped values are for cursor control --
      // there might be more suitable printer codes for each.
      if     (c == 'b') c = '\b'; // Backspace
      else if(c == 'f') c = '\f'; // Form feed
      else if(c == 'n') c = '\n'; // Newline
      else if(c == 'r') c = '\r'; // Carriage return
      else if(c == 't') c = '\t'; // Tab
      else if(c == 'u') c = unidecode(4);
      else if(c == 'U') c = unidecode(8);
      // else c is unaltered -- an escaped char such as \ or "
    } // else c is a normal unescaped char

    if(c < 0) return false; // Timeout

    // In order to properly position the client stream at the end of
    // the string, characters are read to the end quote, even if the max
    // string length is reached...the extra chars are simply discarded.
    if(len < maxLen) dest[len++] = c;
  }

  dest[len] = 0;
  return true; // Success (even if empty string)
}

// Read a given number of hexadecimal characters from client stream,
// representing a Unicode symbol.  Return -1 on error, else return nearest
// equivalent glyph in printer's charset.  (See notes below -- for now,
// always returns '-' or -1.)
int unidecode(byte len) {
  int c, v, result = 0;
  while(len--) {
    if((c = timedRead()) < 0) return -1; // Stream timeout
    if     ((c >= '0') && (c <= '9')) v =      c - '0';
    else if((c >= 'A') && (c <= 'F')) v = 10 + c - 'A';
    else if((c >= 'a') && (c <= 'f')) v = 10 + c - 'a';
    else return '-'; // garbage
    result = (result << 4) | v;
  }

  return '?';
}

// Read from client stream with a 5 second timeout.  Although an
// essentially identical method already exists in the Stream() class,
// it's declared private there...so this is a local copy.
int timedRead(void) {
  unsigned long start = millis();
  while((!client.available()) && ((millis() - start) < 5000L));
  return client.read();  // -1 on timeout
}

