/*
IMPORTANT: THIS SOFTWARE CURRENTLY DOES NOT WORK, and future
status is uncertain.  Twitter has changed their API to require
SSL (Secure Sockets Layer) on -all- connections, a complex
operation beyond the Arduino's ability to handle.  The code is
being kept around on the chance that a suitable proxy service
becomes available...but at present we have no such service, no
code for such, nor a schedule or even a firm commitment to
pursue it.  For projects requiring Twitter we now recommend
using an SSL-capable system such as Raspberry Pi.
*/


/*
Send tweets wirelessly from Arduino using the new Twitter 1.1 API.
Self-contained, operates directly -- no proxy server required!

Designed for IoTA -- Internet of Things by Adafruit -- a series of Arduino-
compatible WiFi products based on the TI CC3000 module, to be available in
shield, breakout and standalone development board form-factors.

Written by Adafruit Industries, distributed under BSD License.

MUST BE CONFIGURED FOR TWITTER 1.1 API BEFORE USE.  See notes below.

REQUIRES ARDUINO IDE 1.0 OR LATER -- Back-porting is not likely to occur,
as the code is deeply dependent on the Stream class, etc.

Requires Adafruit fork of Peter Knight's Cryptosuite library for Arduino:
https://github.com/adafruit/Cryptosuite

Required hardware includes an 802.11 wireless access point, any of the
Adafruit IoTa WiFi devices, a compatible Arduino board (for shield and
breakout form-factors) and, optionally, sensors to be read and reported
via Twitter.

Resources:
http://www.adafruit.com/products/1469 IoTa breakout board
http://www.adafruit.com/products/201  Arduino Uno
[ additional links will go here ]

Uses Twitter 1.1 API.  This REQUIRES a Twitter account and some account
configuration.  Start at dev.twitter.com, sign in with your Twitter
credentials, select "My Applications" from the avatar drop-down menu at the
top right, then "Create a new application."  Provide a name, description,
placeholder URL and complete the captcha, after which you'll be provided a
"consumer key" and "consumer secret" for your app.  Select "Create access
token" to also generate an "access token" and "access token secret."
ALL FOUR STRINGS must be copied to the correct positions in the globals below,
and configure the search string to your liking.  DO NOT SHARE your keys or
secrets!  If you put code on Github or other public repository, replace them
with dummy strings.  Next, from the Twitter "Settings" tab, change the
Application Type to "Read and Write" -- MANDATORY or the sketch won't work!


Copyright (c) 2013 Adafruit Industries.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
*/

#include <Adafruit_CC3000.h>
#include <ccspi.h>
#include <SPI.h>
#include <sha1.h>

// --------------------------------------------------------------------------
// This is a relatively complex sketch, not recommended as a first
// introduction to IoTa.  Try running some of the other, simpler sketches
// first before attempting to adapt this code.  Additionally, some of the
// CC3000 helper and status functions have been pared back in this code.
// See other example sketches for more complete and verbose debugging info
// during your initial IoTa experiments.

// Configurable globals and defines.  Edit to your needs. -------------------

// CC3000 interrupt and control pins
#define ADAFRUIT_CC3000_IRQ   3 // MUST be an interrupt pin!
#define ADAFRUIT_CC3000_VBAT  5 // These can be
#define ADAFRUIT_CC3000_CS   10 // any two pins
// Hardware SPI required for remaining pins.
// On an UNO, SCK = 13, MISO = 12, and MOSI = 11
Adafruit_CC3000 cc3000 = Adafruit_CC3000(
  ADAFRUIT_CC3000_CS, ADAFRUIT_CC3000_IRQ, ADAFRUIT_CC3000_VBAT,
  SPI_CLOCK_DIVIDER);

// WiFi access point credentials
#define WLAN_SSID     "myNetwork"  // 32 characters max
#define WLAN_PASS     "myPassword"
#define WLAN_SECURITY WLAN_SEC_WPA2 // WLAN_SEC_UNSEC/WLAN_SEC_WEP/WLAN_SEC_WPA/WLAN_SEC_WPA2

const char PROGMEM
  // Twitter application credentials -- see notes above -- DO NOT SHARE.
  consumer_key[]  = "PUT_YOUR_CONSUMER_KEY_HERE",
  access_token[]  = "PUT_YOUR_ACCESS_TOKEN_HERE",
  signingKey[]    = "PUT_YOUR_CONSUMER_SECRET_HERE"      // Consumer secret
    "&"             "PUT_YOUR_ACCESS_TOKEN_SECRET_HERE", // Access token secret
  // The ampersand is intentional -- do not delete!

  // Other globals.  You probably won't need to change these. ---------------
  endpoint[]      = "/1.1/statuses/update.json",
  agent[]         = "Arduino-Tweet-Test v1.0";
const char
  host[]          = "api.twitter.com";
const unsigned long
  dhcpTimeout     = 60L * 1000L, // Max time to wait for address from DHCP
  connectTimeout  = 15L * 1000L, // Max time to wait for server connection
  responseTimeout = 15L * 1000L; // Max time to wait for data from server
unsigned long
  currentTime = 0L;
Adafruit_CC3000_Client
  client;        // For WiFi connections

// Similar to F(), but for PROGMEM string pointers rather than literals
#define F2(progmem_ptr) (const __FlashStringHelper *)progmem_ptr

// --------------------------------------------------------------------------

void setup(void) {

  uint32_t ip = 0L, t;

  Serial.begin(115200);

  Serial.print(F("Hello! Initializing CC3000..."));
  if(!cc3000.begin()) hang(F("failed. Check your wiring?"));

  uint16_t firmware = checkFirmwareVersion();
  if ((firmware != 0x113) && (firmware != 0x118)) {
    hang(F("Wrong firmware version!"));
  }

  Serial.print(F("OK\r\nDeleting old connection profiles..."));
  if(!cc3000.deleteProfiles()) hang(F("failed."));

  Serial.print(F("OK\r\nConnecting to network..."));
  /* NOTE: Secure connections are not available in 'Tiny' mode! */
  if(!cc3000.connectToAP(WLAN_SSID, WLAN_PASS, WLAN_SECURITY)) hang(F("Failed!"));

  Serial.print(F("OK\r\nRequesting address from DHCP server..."));
  for(t=millis(); !cc3000.checkDHCP() && ((millis() - t) < dhcpTimeout); delay(100));
  if(!cc3000.checkDHCP()) hang(F("failed"));
  Serial.println(F("OK"));

  while(!displayConnectionDetails());

  // Get initial time from time server (make a few tries if needed)
  for(uint8_t i=0; (i<5) && !(currentTime = getTime()); delay(5000L), i++);

  // Initialize crypto library
  Sha1.initHmac_P((uint8_t *)signingKey, sizeof(signingKey) - 1);
}

// On error, print PROGMEM string to serial monitor and stop
void hang(const __FlashStringHelper *str) {
  Serial.println(str);
  for(;;);
}

uint8_t countdown = 23; // Countdown to next time server query (once per ~24hr)

void loop() {

  unsigned long t = millis();

  // For now this just issues a fixed tweet.  In reality, you might want to
  // read from some sensors or that sort of thing, then nicely format the
  // results into a buffer to be passed to the sendTweet() function.
  sendTweet("Adafruit IoTa test. Tweet directly from Arduino...no proxy, no wires! http://www.adafruit.com/products/1469");

  // Delay remainder of 1 hour (takes tweeting time into account)
  Serial.println("Waiting ~1 hour...");
  delay((60L * 60L * 1000L) - (millis() - t));
  currentTime += 60L * 60L * 1000L;

  if(!countdown) {        // 24 hours elapsed?
    if((t = getTime())) { // Synchronize time if server contacted
      currentTime = t;
      countdown   = 23;   // and reset counter
    }
  } else countdown--;
}

// Returns true on success, false on error
boolean sendTweet(char *msg) { // 140 chars max! No checks made here.
  uint8_t                  *in, out, i;
  char                      nonce[9],       // 8 random digits + NUL
                            searchTime[11], // 32-bit int + NUL
                            b64[29];
  unsigned long             startTime, t, ip;
  static const char PROGMEM b64chars[] =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

  startTime = millis();

  sprintf(nonce, "%04x%04x", random() ^ currentTime, startTime ^ currentTime);
  sprintf(searchTime, "%ld", currentTime);

  // A dirty hack makes the Oauth song and dance MUCH simpler within the
  // Arduino's limited RAM and CPU.  A proper general-purpose implementation
  // would be expected to URL-encode keys and values (from the complete list
  // of POST parameters and authentication values), sort by encoded key,
  // concatenate and URL-encode the combined result.  Sorting is avoided
  // because every POST this program performs has exactly the same set of
  // parameters, so we've pre-sorted the list as it appears here.  Keys
  // (and many values) are pre-encoded because they never change; many are
  // passed through verbatim because the format is known to not require
  // encoding.  Most reside in PROGMEM, not RAM.  This is bending a LOT of
  // rules of Good and Proper Authentication and would land you an 'F' in
  // Comp Sci class, but it handles the required task and is VERY compact.
  Sha1.print(F("POST&http%3A%2F%2F"));
  Sha1.print(host);
  urlEncode(Sha1, endpoint, true, false);
  Sha1.print(F("&oauth_consumer_key%3D"));
  Sha1.print(F2(consumer_key));
  Sha1.print(F("%26oauth_nonce%3D"));
  Sha1.print(nonce);
  Sha1.print(F("%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D"));
  Sha1.print(searchTime);
  Sha1.print(F("%26oauth_token%3D"));
  Sha1.print(F2(access_token));
  Sha1.print(F("%26oauth_version%3D1.0%26status%3D"));
  urlEncode(Sha1, msg, false, true);

  // base64-encode SHA-1 hash output.  This is NOT a general-purpose base64
  // encoder!  It's stripped down for the fixed-length hash -- always 20
  // bytes input, always 27 chars output + '='.
  for(in = Sha1.resultHmac(), out=0; ; in += 3) { // octets to sextets
    b64[out++] =   in[0] >> 2;
    b64[out++] = ((in[0] & 0x03) << 4) | (in[1] >> 4);
    if(out >= 26) break;
    b64[out++] = ((in[1] & 0x0f) << 2) | (in[2] >> 6);
    b64[out++] =   in[2] & 0x3f;
  }
  b64[out] = (in[1] & 0x0f) << 2;
  // Remap sextets to base64 ASCII chars
  for(i=0; i<=out; i++) b64[i] = pgm_read_byte(&b64chars[b64[i]]);
  b64[i++] = '=';
  b64[i++] = 0;

  // Hostname lookup
  Serial.print(F("Locating Twitter server..."));
  cc3000.getHostByName((char *)host, &ip);

  // Connect to numeric IP
  Serial.print(F("OK\r\nConnecting to server..."));
  t = millis();
  do {
    client = cc3000.connectTCP(ip, 80);
  } while((!client.connected()) &&
          ((millis() - t) < connectTimeout));

  if(client.connected()) { // Success!
    Serial.print(F("OK\r\nIssuing HTTP request..."));

    // Unlike the hash prep, parameters in the HTTP request don't require sorting.
    client.fastrprint(F("POST "));
    client.fastrprint(F2(endpoint));
    client.fastrprint(F(" HTTP/1.1\r\nHost: "));
    client.fastrprint(host);
    client.fastrprint(F("\r\nUser-Agent: "));
    client.fastrprint(F2(agent));
    client.fastrprint(F("\r\nConnection: close\r\n"
                       "Content-Type: application/x-www-form-urlencoded;charset=UTF-8\r\n"
                       "Content-Length: "));
    client.print(7 + encodedLength(msg));
    client.fastrprint(F("\r\nAuthorization: Oauth oauth_consumer_key=\""));
    client.fastrprint(F2(consumer_key));
    client.fastrprint(F("\", oauth_nonce=\""));
    client.fastrprint(nonce);
    client.fastrprint(F("\", oauth_signature=\""));
    urlEncode(client, b64, false, false);
    client.fastrprint(F("\", oauth_signature_method=\"HMAC-SHA1\", oauth_timestamp=\""));
    client.fastrprint(searchTime);
    client.fastrprint(F("\", oauth_token=\""));
    client.fastrprint(F2(access_token));
    client.fastrprint(F("\", oauth_version=\"1.0\"\r\n\r\nstatus="));
    urlEncode(client, msg, false, false);

    Serial.print(F("OK\r\nAwaiting response..."));
    int c = 0;
    // Dirty trick: instead of parsing results, just look for opening
    // curly brace indicating the start of a successful JSON response.
    while(((c = timedRead()) > 0) && (c != '{'));
    if(c == '{')   Serial.println(F("success!"));
    else if(c < 0) Serial.println(F("timeout"));
    else           Serial.println(F("error (invalid Twitter credentials?)"));
    client.close();
    return (c == '{');
  } else { // Couldn't contact server
    Serial.println(F("failed"));
    return false;
  }
}

// Helper functions. --------------------------------------------------------

uint16_t checkFirmwareVersion(void) {
  uint8_t  major, minor;
  uint16_t version = 0;
  
#ifndef CC3000_TINY_DRIVER
  if(!cc3000.getFirmwareVersion(&major, &minor)) {
    Serial.println(F("Unable to retrieve the firmware version!\r\n"));
  } else {
    Serial.print(F("Firmware V. : "));
    Serial.print(major); Serial.print(F(".")); Serial.println(minor);
    version = ((uint16_t)major << 8) | minor;
  }
#endif
  return version;
}

bool displayConnectionDetails(void) {
  uint32_t addr, netmask, gateway, dhcpserv, dnsserv;

  if(!cc3000.getIPAddress(&addr, &netmask, &gateway, &dhcpserv, &dnsserv))
    return false;

  Serial.print(F("IP Addr: ")); cc3000.printIPdotsRev(addr);
  Serial.print(F("\r\nNetmask: ")); cc3000.printIPdotsRev(netmask);
  Serial.print(F("\r\nGateway: ")); cc3000.printIPdotsRev(gateway);
  Serial.print(F("\r\nDHCPsrv: ")); cc3000.printIPdotsRev(dhcpserv);
  Serial.print(F("\r\nDNSserv: ")); cc3000.printIPdotsRev(dnsserv);
  Serial.println();
  return true;
}

// Read from client stream with a 5 second timeout.  Although an
// essentially identical method already exists in the Stream() class,
// it's declared private there...so this is a local copy.
int timedRead(void) {
  unsigned long start = millis();
  while((!client.available()) && ((millis() - start) < responseTimeout));
  return client.read();  // -1 on timeout
}

// For URL-encoding functions below
static const char PROGMEM hexChar[] = "0123456789ABCDEF";

// URL-encoding output function for Print class.
// Input from RAM or PROGMEM (flash).  Double-encoding is a weird special
// case for Oauth (encoded strings get encoded a second time).
void urlEncode(
  Print      &p,       // EthernetClient, Sha1, etc.
  const char *src,     // String to be encoded
  boolean     progmem, // If true, string is in PROGMEM (else RAM)
  boolean     x2)      // If true, "double encode" parenthesis
{
  uint8_t c;

  while((c = (progmem ? pgm_read_byte(src) : *src))) {
    if(((c >= 'a') && (c <= 'z')) || ((c >= 'A') && (c <= 'Z')) ||
       ((c >= '0') && (c <= '9')) || strchr_P(PSTR("-_.~"), c)) {
      p.write(c);
    } else {
      if(x2) p.print("%25");
      else   p.write('%');
      p.write(pgm_read_byte(&hexChar[c >> 4]));
      p.write(pgm_read_byte(&hexChar[c & 15]));
    }
    src++;
  }
}

// Returns would-be length of encoded string, without actually encoding
int encodedLength(char *src) {
  uint8_t c;
  int     len = 0;

  while((c = *src++)) {
    len += (((c >= 'a') && (c <= 'z')) || ((c >= 'A') && (c <= 'Z')) ||
            ((c >= '0') && (c <= '9')) || strchr_P(PSTR("-_.~"), c)) ? 1 : 3;
  }

  return len;
}

// Minimalist time server query; adapted from Adafruit Gutenbird sketch,
// which in turn has roots in Arduino UdpNTPClient tutorial.
unsigned long getTime(void) {

  uint8_t       buf[48];
  unsigned long ip, startTime, t = 0L;

  Serial.print(F("Locating time server..."));

  // Hostname to IP lookup; use NTP pool (rotates through servers)
  if(cc3000.getHostByName("pool.ntp.org", &ip)) {
    static const char PROGMEM
      timeReqA[] = { 227,  0,  6, 236 },
      timeReqB[] = {  49, 78, 49,  52 };

    Serial.println(F("found\r\nConnecting to time server..."));
    startTime = millis();
    do {
      client = cc3000.connectUDP(ip, 123);
    } while((!client.connected()) &&
            ((millis() - startTime) < connectTimeout));

    if(client.connected()) {
      Serial.print(F("connected!\r\nIssuing request..."));

      // Assemble and issue request packet
      memset(buf, 0, sizeof(buf));
      memcpy_P( buf    , timeReqA, sizeof(timeReqA));
      memcpy_P(&buf[12], timeReqB, sizeof(timeReqB));
      client.write(buf, sizeof(buf));

      Serial.print(F("OK\r\nAwaiting response..."));
      memset(buf, 0, sizeof(buf));
      startTime = millis();
      while((!client.available()) &&
            ((millis() - startTime) < responseTimeout));
      if(client.available()) {
        client.read(buf, sizeof(buf));
        t = (((unsigned long)buf[40] << 24) |
             ((unsigned long)buf[41] << 16) |
             ((unsigned long)buf[42] <<  8) |
              (unsigned long)buf[43]) - 2208988800UL;
        Serial.println(F("success!"));
      }
      client.close();
    }
  }
  if(!t) Serial.println(F("error"));
  return t;
}
