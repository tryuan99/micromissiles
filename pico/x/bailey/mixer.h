// The LMX8410L chip is a 5 GHz to 10 GHz downconverter with a fully integrated
// synthesizer.

#ifndef PICO_X_BAILEY_MIXER_H_
#define PICO_X_BAILEY_MIXER_H_

#include <stdint.h>

#include "pico/common/spi.h"

// Mixer configuration struct.
typedef struct {
  // SPI I/O configuration.
  spi_io_config_t spi_io_config;

  // Enable GPIO.
  uint8_t gpio_enable;

  // Multiplexer output GPIO.
  uint8_t gpio_muxout;
} mixer_config_t;

// Initialize the mixer.
void mixer_init(const mixer_config_t* config);

// Enable the mixer.
void mixer_enable(void);

// Disable the mixer.
void mixer_disable(void);

#endif  // PICO_X_BAILEY_MIXER_H_
