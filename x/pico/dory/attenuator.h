// The HMC540S chip is a 1 dB LSB 4-bit digital positive control attenuator.

#ifndef X_PICO_DORY_ATTENUATOR_H_
#define X_PICO_DORY_ATTENUATOR_H_

#include <stdint.h>

// Attenuator configuration struct.
typedef struct {
  // Attenuator control voltage pins.
  uint8_t gpio_v1;
  uint8_t gpio_v2;
  uint8_t gpio_v3;
  uint8_t gpio_v4;
} attenuator_config_t;

// Initialize the attenuator.
void attenuator_init(const attenuator_config_t* config);

// Set the attenuation's gain.
void attenuator_set_gain_attenuation(uint8_t gain_attenuation);

#endif  // X_PICO_DORY_ATTENUATOR_H_
