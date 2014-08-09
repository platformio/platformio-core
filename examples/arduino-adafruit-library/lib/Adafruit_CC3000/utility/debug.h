/**************************************************************************/
/*!
  @file     Adafruit_CC3000.cpp
  @author   KTOWN (Kevin Townsend for Adafruit Industries)
	@license  BSD (see license.txt)

	This is a library for the Adafruit CC3000 WiFi breakout board
	This library works with the Adafruit CC3000 breakout
	----> https://www.adafruit.com/products/1469

	Check out the links above for our tutorials and wiring diagrams
	These chips use SPI to communicate.

	Adafruit invests time and resources providing this open source code,
	please support Adafruit and open-source hardware by purchasing
	products from Adafruit!

	@section  HISTORY

	v1.0    - Initial release
*/
/**************************************************************************/

#include <Arduino.h>

#define GCC_VERSION (__GNUC__ * 10000 + __GNUC_MINOR__ * 100 + __GNUC_PATCHLEVEL__)
#if (GCC_VERSION >= 40702) || !defined(prog_char)
typedef char PROGMEM prog_char;
#endif

#ifndef _CC3000_DEBUG
#define _CC3000_DEBUG

#define DEBUG_MODE                      (0)

int getFreeRam(void);
void displayFreeRam(void);
void uart_putchar(char c);
void printHex(uint8_t h);
void printHex16(uint16_t h);
void DEBUGPRINT(const prog_char *fstr);
void printDec(uint8_t h);
void printDec16(uint16_t h);

#ifndef FLASHIFY
#define FLASHIFY(s) ({static const char c[] __attribute__ ((progmem)) = s;c;})
#endif

#define PRINT_F(__s)         DEBUGPRINT(FLASHIFY(__s))

#if (DEBUG_MODE != 0)
#define DEBUGPRINT_F(__s)         DEBUGPRINT(FLASHIFY(__s))
#define DEBUGPRINT_DEC(x)  printDec(x)
#define DEBUGPRINT_DEC16(x)  printDec16(x)
#define DEBUGPRINT_HEX(x)  printHex(x)
#define DEBUGPRINT_HEX16(x)  printHex16(x)
#else
#define DEBUGPRINT_F(__s)         /* do nothing! */
#define DEBUGPRINT_DEC(x)
#define DEBUGPRINT_DEC16(x)
#define DEBUGPRINT_HEX(x)
#define DEBUGPRINT_HEX16(x)
#endif

extern Print* CC3KPrinter;

#endif
