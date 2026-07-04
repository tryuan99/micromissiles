#include "pico/x/dory/mixer.h"

#include <stdbool.h>

#include "hardware/gpio.h"
#include "pico/x/dory/defs.h"

// Mixer configuration.
static mixer_config_t g_mixer_config;

void mixer_init(const mixer_config_t* config) {
  g_mixer_config = *config;

  // Initialize the enable pin.
  gpio_init(g_mixer_config.gpio_enable);
#ifdef CONTROLLER_PICO
  gpio_set_dir(g_mixer_config.gpio_enable, GPIO_OUT);
#endif  // CONTROLLER_PICO
}

void mixer_enable(void) { gpio_put(g_mixer_config.gpio_enable, true); }

void mixer_disable(void) { gpio_put(g_mixer_config.gpio_enable, false); }
