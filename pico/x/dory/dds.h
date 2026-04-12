// The AD9914 chip is a 3.5 GSPS direct digital synthesizer with a 12-bit DAC.

#ifndef PICO_X_DORY_DDS_H_
#define PICO_X_DORY_DDS_H_

#include <stdint.h>

#include "pico/common/spi.h"

// DDS mode enumeration.
typedef enum {
  DDS_MODE_INVALID = -1,
  DDS_MODE_CW,
  DDS_MODE_FMCW,
  DDS_MODE_MAX,
} dds_mode_e;

// DDS configuration struct.
typedef struct {
  // SPI I/O configuration.
  spi_io_config_t spi_io_config;

  // DDS reset GPIO.
  uint8_t gpio_rst;

  // IO update GPIO.
  uint8_t gpio_io_update;

  // Profile select 0 GPIO.
  uint8_t gpio_ps0;

  // Profile select 1 GPIO.
  uint8_t gpio_ps1;

  // Profile select 2 GPIO.
  uint8_t gpio_ps2;

  // Ramp control GPIO.
  uint8_t gpio_drctl;

  // Ramp hold GPIO.
  uint8_t gpio_drhold;

  // Ramp over GPIO.
  uint8_t gpio_drover;

  // Output shift keying GPIO.
  uint8_t gpio_osk;

  // DDS mode.
  dds_mode_e mode;
} dds_config_t;

// Initialize the DDS chip.
void dds_init(const dds_config_t* config);

#endif  // PICO_X_DORY_DDS_H_
