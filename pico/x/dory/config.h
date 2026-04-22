// Configurations for Dory.

#ifndef PICO_X_DORY_CONFIG_H_
#define PICO_X_DORY_CONFIG_H_

#include "pico/x/dory/dds.h"
#include "pico/x/dory/mixer.h"
#include "pico/x/dory/vco.h"
#include "pico/x/dory/vga.h"

// GPIO enumeration.
enum {
  GPIO_INVALID = -1,
  GPIO_VCO_EN = 0,
  GPIO_VCO_RF_EN = 1,
  GPIO_VCO_CLK = 2,
  GPIO_VCO_DATA = 3,
  GPIO_VCO_MUXOUT = 4,
  GPIO_VCO_LE = 5,
  GPIO_VCO_LD = 6,
  GPIO_DDS_RST = 7,
  GPIO_DDS_IO_UPDATE = 8,
  GPIO_DDS_CS = 9,
  GPIO_DDS_SCLK = 10,
  GPIO_DDS_SDIO = 11,
  GPIO_DDS_SDO = 12,
  GPIO_DDS_PS0 = 13,
  GPIO_DDS_PS1 = 14,
  GPIO_DDS_PS2 = 15,
  GPIO_MIXER_EN = 16,
  GPIO_DDS_DRCTL = 17,
  GPIO_DDS_DRHOLD = 18,
  GPIO_DDS_DROVER = 19,
  GPIO_DDS_OSK = 20,
  GPIO_VGA_PS = 21,
  GPIO_VGA_CLK = 22,
  GPIO_VGA_LE = 26,
  GPIO_VGA_SERIN = 27,
  GPIO_VGA_SEROUT = 28,
};

// VCO configuration.
extern vco_config_t g_vco_config;

// DDS configuration.
extern dds_config_t g_dds_config;

// Mixer configuration.
extern mixer_config_t g_mixer_config;

// VGA configuration.
extern vga_config_t g_vga_config;

#endif  // PICO_X_DORY_CONFIG_H_
