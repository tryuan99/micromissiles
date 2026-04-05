#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/stdlib.h"

// LED delay in milliseconds.
#define LED_DELAY_MS 250  // milliseconds

// Initialize the LED.
static inline void led_init() {
  gpio_init(PICO_DEFAULT_LED_PIN);
  gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
}

int main(int argc, char** argv) {
  stdio_init_all();
  led_init();

  while (true) {
    // Print hello world.
    printf("Hello, world!\n");

    // Toggle the LED.
    gpio_put(PICO_DEFAULT_LED_PIN, true);
    sleep_ms(LED_DELAY_MS);
    gpio_put(PICO_DEFAULT_LED_PIN, false);
    sleep_ms(LED_DELAY_MS);
  }
  return EXIT_SUCCESS;
}
