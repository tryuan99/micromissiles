#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/common/led.h"
#include "pico/stdlib.h"

// LED delay in milliseconds.
#define LED_DELAY_MS 250  // milliseconds

int main(int argc, char** argv) {
  stdio_init_all();
  led_init();

  while (true) {
    // Print hello world.
    printf("Hello, world!\n");

    // Toggle the LED.
    led_on();
    sleep_ms(LED_DELAY_MS);
    led_off();
    sleep_ms(LED_DELAY_MS);
  }
  return EXIT_SUCCESS;
}
