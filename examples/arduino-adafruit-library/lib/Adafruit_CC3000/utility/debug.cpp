/**************************************************************************/
/*!
  @file     Adafruit_CC3000.cpp
  @author   KTOWN (Kevin Townsend Adafruit Industries)
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

#include "debug.h"

/**************************************************************************/
/*!
    @brief  This function will display the number of bytes currently free
            in RAM ... useful for debugging!
*/
/**************************************************************************/

#if defined (__arm__) && defined (__SAM3X8E__) // Arduino Due
// should use uinstd.h to define sbrk but on Arduino Due this causes a conflict
extern "C" char* sbrk(int incr);
int getFreeRam(void) {
  char top;
  return &top - reinterpret_cast<char*>(sbrk(0));
}
#else // AVR 
int getFreeRam(void)
{
  extern int  __bss_end;
  extern int  *__brkval;
  int free_memory;
  if((int)__brkval == 0) {
    free_memory = ((int)&free_memory) - ((int)&__bss_end);
  }
  else {
    free_memory = ((int)&free_memory) - ((int)__brkval);
  }

  return free_memory;
} 
#endif

void displayFreeRam(void)
{
  if (CC3KPrinter == 0) {
    return;
  }
  CC3KPrinter->print(F("Free RAM: "));
  CC3KPrinter->print(getFreeRam());
  CC3KPrinter->println(F(" bytes"));
}

void uart_putchar(char c) {
  if (CC3KPrinter != 0) {
    CC3KPrinter->write(c);
  }
}

void printDec(uint8_t h) {
  uart_putchar((h / 100) + '0');
  h %= 100;
  uart_putchar((h / 10) + '0');
  h %= 10;
  uart_putchar(h + '0');
}


void printHex(uint8_t h) {
  uint8_t d = h >> 4;
  if (d >= 10) {
    uart_putchar(d - 10 + 'A');
  } else {
    uart_putchar(d + '0');
  }
  h &= 0xF;
  if (h >= 10) {
    uart_putchar(h - 10 + 'A');
  } else {
    uart_putchar(h + '0');
  }
}

void printHex16(uint16_t h) {
  uart_putchar('0');
  uart_putchar('x');
  DEBUGPRINT_HEX(h >> 8);
  DEBUGPRINT_HEX(h);
}


void printDec16(uint16_t h) {
  uart_putchar((h / 10000) + '0');
  h %= 10000;
  uart_putchar((h / 1000) + '0');
  h %= 1000;
  uart_putchar((h / 100) + '0');
  h %= 100;
  uart_putchar((h / 10) + '0');
  h %= 10;
  uart_putchar(h + '0');
}


void DEBUGPRINT(const prog_char *fstr)
{
  char c;
  if(!fstr) return;
  while((c = pgm_read_byte(fstr++)))
    uart_putchar(c);
}
