#include "pico/common/led.h"

#include <stdbool.h>

#include "hardware/gpio.h"
#include "pico/stdlib.h"

void led_init(void) {
  gpio_init(PICO_DEFAULT_LED_PIN);
  gpio_set_dir(PICO_DEFAULT_LED_PIN, GPIO_OUT);
}

void led_on(void) { gpio_put(PICO_DEFAULT_LED_PIN, true); }

void led_off(void) { gpio_put(PICO_DEFAULT_LED_PIN, true); }
