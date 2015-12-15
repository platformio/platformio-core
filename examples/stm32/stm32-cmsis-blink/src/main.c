#ifdef STM32L1
	#include "stm32l1xx.h"
	#define LEDPORT (GPIOB)
	#define LED1 (6)
	#define LED2 (7)
	#define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOBEN)
	#define GPIOMODER ((GPIO_MODER_MODER7_0|GPIO_MODER_MODER6_0))
#elif STM32F3
	#include "stm32f3xx.h"
	#define LEDPORT (GPIOE)
	#define LED1 (8)
	#define LED2 (9)
	#define ENABLE_GPIO_CLOCK (RCC->AHBENR |= RCC_AHBENR_GPIOEEN)
	#define GPIOMODER ((GPIO_MODER_MODER9_0|GPIO_MODER_MODER8_0))
#elif STM32F4
	#include "stm32f4xx.h"
	#define LEDPORT (GPIOD)
	#define LED1 (12)
	#define LED2 (13)
	#define ENABLE_GPIO_CLOCK (RCC->AHB1ENR |= RCC_AHB1ENR_GPIODEN)
	#define GPIOMODER ((GPIO_MODER_MODER13_0|GPIO_MODER_MODER12_0))
#endif


void ms_delay(int ms)
{
   while (ms-- > 0) {
      volatile int x=500;
      while (x-- > 0)
         __asm("nop");
   }
}

//Alternates blue and green LEDs quickly
int main(void)
{
	ENABLE_GPIO_CLOCK; 		 					// enable the clock to GPIO
	LEDPORT->MODER |= GPIOMODER;				// set pins to be general purpose output
	for (;;) {
		ms_delay(500);
		LEDPORT->ODR ^= (1<<LED1|1<<LED2); 		// toggle diodes
	}
	
	return 0;
}