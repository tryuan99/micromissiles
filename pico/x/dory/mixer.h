// The LTC5576 chip is a 3 GHz to 8 GHz active upconverting mixer.

#ifndef PICO_X_DORY_MIXER_H_
#define PICO_X_DORY_MIXER_H_

#include <stdint.h>

// Mixer configuration struct.
typedef struct {
  // Mixer enable GPIO.
  uint8_t gpio_enable;
} mixer_config_t;

// Initialize the mixer.
void mixer_init(const mixer_config_t* config);

// Enable the mixer.
void mixer_enable(void);

// Disable the mixer.
void mixer_disable(void);

#endif  // PICO_X_DORY_MIXER_H_
