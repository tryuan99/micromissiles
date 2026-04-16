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

// DDS CW configuration struct.
typedef struct {
  // Frequency in Hz.
  double frequency;

  // 12-bit DAC scale.
  uint16_t amplitude;

  // 16-bit phase offset.
  uint16_t phase;
} dds_cw_config_t;

// DDS FMCW configuration struct.
typedef struct {
  // Start frequency in Hz.
  double start_frequency;

  // End frequency in Hz.
  double end_frequency;

  // Frequency step in Hz.
  double frequency_step;

  // Step time in s.
  double step_time;

  // 12-bit DAC scale.
  uint16_t amplitude;

  // 16-bit phase offset.
  uint16_t phase;
} dds_fmcw_config_t;

// Initialize the DDS chip.
void dds_init(const dds_config_t* config);

// Reset the DDS.
void dds_reset(void);

// Assert the DDS IO update.
void dds_io_update(void);

// Set the DDS profile.
void dds_set_profile(uint8_t profile);

// Configure the DDS CW mode.
void dds_configure_cw(uint8_t profile, const dds_cw_config_t* cfg);

// Confingure the DDS FMCW mode.
void dds_configure_fmcw(uint8_t profile, const dds_fmcw_config_t* cfg);

// Start the DDS FMCW mode.
void dds_start_fmcw(void);

#endif  // PICO_X_DORY_DDS_H_
