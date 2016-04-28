/**
 * @file main.c
 * @version 1.0
 *
 * @section License
 * Copyright (C) 2015-2016, Erik Moqvist
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * This file is part of the Simba project.
 */

#include "simba.h"

int main()
{
    struct pin_driver_t led;

    /* Start the kernel. */
    sys_start();

    /* Initialize the LED pin as output. */
    pin_init(&led, &pin_led_dev, PIN_OUTPUT);
    
    while (1) {
        /* Wait for a seconds. */
        thrd_usleep(1000000);
        
        /* Toggle the LED on/off. */
        pin_toggle(&led);
    }

    return (0);
}
