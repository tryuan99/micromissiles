// The ADF4350 chip is a wideband synthesizer up to 4.4 GHz with an integrated
// VCO.

#ifndef PICO_X_DORY_VCO_H_
#define PICO_X_DORY_VCO_H_

#include <stdbool.h>
#include <stdint.h>

#include "pico/common/spi.h"
#include "pico/x/dory/config.h"

// VCO PFD frequency enumeration.
typedef enum {
  VCO_PFD_FREQUENCY_INVALID = -1,
  VCO_PFD_FREQUENCY_25_MHZ,
  VCO_PFD_FREQUENCY_MAX,
} vco_pfd_frequency_e;

// VCO output power enumeration.
typedef enum {
  VCO_OUTPUT_POWER_INVALID = -1,
  VCO_OUTPUT_POWER_MINUS_FOUR_DBM = 0,
  VCO_OUTPUT_POWER_MINUS_ONE_DBM = 1,
  VCO_OUTPUT_POWER_TWO_DBM = 2,
  VCO_OUTPUT_POWER_FIVE_DBM = 3,
} vco_output_power_e;

// VCO configuration struct.
typedef struct {
  // SPI I/O configuration.
  spi_io_config_t spi_io_config;

  // VCO enable GPIO.
  uint8_t gpio_enable;

  // VCO RF enable GPIO.
  uint8_t gpio_rf_enable;

  // Multiplexer output GPIO.
  uint8_t gpio_muxout;

  // Lock detect GPIO.
  uint8_t gpio_ld;
} vco_config_t;

// Initialize the VCO.
void vco_init(const vco_config_t* config);

// Set the VCO PFD and RF output frequencies.
void vco_set_frequencies(vco_pfd_frequency_e pfd_frequency,
                         double rf_frequency);

// Set the VCO output power.
void vco_set_output_power(vco_output_power_e output_power,
                          vco_output_power_e aux_output_power);

// Configure the VCO.
void vco_configure(void);

// Enable the VCO.
void vco_enable(void);

// Disable the VCO.
void vco_disable(void);

// Enable the VCO RF output.
void vco_rf_enable(void);

// Disable the VCO RF output.
void vco_rf_disable(void);

// Return whether the VCO is locked.
bool vco_locked(void);

#endif  // PICO_X_DORY_VCO_H_
