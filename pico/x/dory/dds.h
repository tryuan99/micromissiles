// The AD9914 chip is a 3.5 GSPS direct digital synthesizer with a 12-bit DAC.

#ifndef PICO_X_DORY_DDS_H_
#define PICO_X_DORY_DDS_H_

#include "pico/common/spi.h"
#include "pico/x/dory/config.h"

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

  // DDS mode.
  dds_mode_e mode;
} dds_config_t;

// Initialize the DDS chip.
void dds_init(const dds_config_t* config);

#endif  // PICO_X_DORY_DDS_H_
