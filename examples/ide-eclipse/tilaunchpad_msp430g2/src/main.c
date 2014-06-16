/**
 * Copyright (C) Ivan Kravets <me@ikravets.com>
 * See LICENSE for details.
 */

#include <msp430g2553.h>

int main(void)
{
    WDTCTL = WDTPW + WDTHOLD;

    // make the LED pin an output for P1.0
    P1DIR |= 0x01;

    volatile int i;

    while (1)
    {
        for (i = 0; i < 10000; i++);

        // toggle the LED
        P1OUT ^= 0x01;
    }

    return 0;
}
