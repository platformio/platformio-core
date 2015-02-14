#ifdef STM32L1
#include <stm32l1xx_gpio.h>
#include <stm32l1xx_rcc.h>
#include <misc.h>
#else
#ifdef STM32F3
#include <stm32f30x_gpio.h>
#include <stm32f30x_rcc.h>
#else
#include <stm32f4xx_gpio.h>
#include <stm32f4xx_rcc.h>
#include <misc.h>
#endif
#endif

/* timing is not guaranteed :) */
void simple_delay(uint32_t us)
{
	/* simple delay loop */
	while (us--) {
		asm volatile ("nop");
	}
}

/* system entry point */
int main(void)
{
	/* gpio init struct */
	GPIO_InitTypeDef gpio;

	/* reset rcc */
	RCC_DeInit();

	/* enable clock to GPIOB */
	RCC_AHBPeriphClockCmd(RCC_AHBPeriph_GPIOB, ENABLE);

	/* use pin 7 */
	gpio.GPIO_Pin = GPIO_Pin_7;
	/* mode: output */
	gpio.GPIO_Mode = GPIO_Mode_OUT;
	/* output type: push-pull */
	gpio.GPIO_OType = GPIO_OType_PP;
	/* apply configuration */
	GPIO_Init(GPIOB, &gpio);

	/* main program loop */
	for (;;) {
		/* set led on */
		GPIO_SetBits(GPIOB, GPIO_Pin_7);
		/* delay */
		simple_delay(100000);
		/* clear led */
		GPIO_ResetBits(GPIOB, GPIO_Pin_7);
		/* delay */
		simple_delay(100000);
	}

	/* never reached */
	return 0;
}