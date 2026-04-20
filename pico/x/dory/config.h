// Configurations for Dory.

#ifndef PICO_X_DORY_CONFIG_H_
#define PICO_X_DORY_CONFIG_H_

#include "pico/x/dory/dds.h"
#include "pico/x/dory/mixer.h"
#include "pico/x/dory/vco.h"
#include "pico/x/dory/vga.h"

// GPIO enumeration.
enum {
  GPIO_INVALID = 0,
  GPIO_VCO_EN = 1,
  GPIO_VCO_RF_EN = 2,
  GPIO_VCO_CLK = 4,
  GPIO_VCO_DATA = 5,
  GPIO_VCO_MUXOUT = 6,
  GPIO_VCO_LE = 7,
  GPIO_VCO_LD = 9,
  GPIO_DDS_RST = 10,
  GPIO_DDS_IO_UPDATE = 11,
  GPIO_DDS_CS = 12,
  GPIO_DDS_SCLK = 14,
  GPIO_DDS_SDIO = 15,
  GPIO_DDS_SDO = 16,
  GPIO_DDS_PS0 = 17,
  GPIO_DDS_PS1 = 19,
  GPIO_DDS_PS2 = 20,
  GPIO_MIXER_EN = 21,
  GPIO_DDS_DRCTL = 22,
  GPIO_DDS_DRHOLD = 24,
  GPIO_DDS_DROVER = 25,
  GPIO_DDS_OSK = 26,
  GPIO_VGA_PS = 27,
  GPIO_VGA_CLK = 29,
  GPIO_MCU_RESET = 30,
  GPIO_VGA_LE = 31,
  GPIO_VGA_SERIN = 32,
  GPIO_VGA_SEROUT = 34,
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
