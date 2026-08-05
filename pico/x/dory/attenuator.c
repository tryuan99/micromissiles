#include "pico/x/dory/attenuator.h"

#include <stddef.h>
#include <stdint.h>

#include "hardware/gpio.h"

// Number of attenuator bits.
#define ATTENUATOR_NUM_BITS 4

// Attenuator gain attenuation mask enumeration.
typedef enum {
  ATTENUATOR_GAIN_ATTENUATION_MASK_ZERO = 0b1111,
  ATTENUATOR_GAIN_ATTENUATION_MASK_ONE = 0b1110,
  ATTENUATOR_GAIN_ATTENUATION_MASK_TWO = 0b1101,
  ATTENUATOR_GAIN_ATTENUATION_MASK_FOUR = 0b1011,
  ATTENUATOR_GAIN_ATTENUATION_MASK_EIGHT = 0b0111,
} attenuator_gain_attenuation_mask_e;

// Attenuator configuration.
static attenuator_config_t g_attenuator_config;

static inline uint8_t attenuator_get_attenuation_control(
    const uint8_t gain_attenuation) {
  if (gain_attenuation >= (1 << ATTENUATOR_NUM_BITS)) {
    return 0;
  }
  return (~gain_attenuation) & ((1 << ATTENUATOR_NUM_BITS) - 1);
}

void attenuator_init(const attenuator_config_t* config) {
  g_attenuator_config = *config;

  // Initialize the control voltage pins.
  gpio_init(g_attenuator_config.gpio_v1);
  gpio_set_dir(g_attenuator_config.gpio_v1, GPIO_OUT);
  gpio_init(g_attenuator_config.gpio_v2);
  gpio_set_dir(g_attenuator_config.gpio_v2, GPIO_OUT);
  gpio_init(g_attenuator_config.gpio_v3);
  gpio_set_dir(g_attenuator_config.gpio_v3, GPIO_OUT);
  gpio_init(g_attenuator_config.gpio_v4);
  gpio_set_dir(g_attenuator_config.gpio_v4, GPIO_OUT);
}

void attenuator_set_gain_attenuation(const uint8_t gain_attenuation) {
  const uint8_t gain_attenuation_control =
      attenuator_get_attenuation_control(gain_attenuation);
  gpio_put(g_attenuator_config.gpio_v1, gain_attenuation_control & 0x1);
  gpio_put(g_attenuator_config.gpio_v2, (gain_attenuation_control >> 1) & 0x1);
  gpio_put(g_attenuator_config.gpio_v3, (gain_attenuation_control >> 2) & 0x1);
  gpio_put(g_attenuator_config.gpio_v4, (gain_attenuation_control >> 3) & 0x1);
}
