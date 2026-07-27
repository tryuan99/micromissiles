// Configurations for Bailey.

#ifndef PICO_X_BAILEY_CONFIG_H_
#define PICO_X_BAILEY_CONFIG_H_

#include "pico/x/bailey/adc.h"
#include "pico/x/bailey/beamformer.h"
#include "pico/x/bailey/mixer.h"

// GPIO enumeration.
enum {
  GPIO_INVALID = -1,
  GPIO_BEAMFORMER_TX_LOAD = 0,
  GPIO_BEAMFORMER_SPI_CS = 1,
  GPIO_ADC_CONV_START_N = 2,
  GPIO_ADC_DATA_READY = 3,
  GPIO_SPI_MISO = 4,
  GPIO_MIXER_CS = 5,
  GPIO_SPI_CLK = 6,
  GPIO_SPI_MOSI = 7,
  GPIO_MIXER_EN = 8,
  GPIO_BEAMFORMER_TR = 9,
  GPIO_MIXER_MUXOUT = 16,
  GPIO_ADC_SPI_CS = 17,
  GPIO_ADC_RESET_N = 18,
  GPIO_ADC_FAULT_N = 19,
};

// Beamformer configuration.
extern beamformer_config_t g_beamformer_config;

// Mixer configuration.
extern mixer_config_t g_mixer_config;

// ADC configuration.
extern adc_config_t g_adc_config;

#endif  // PICO_X_BAILEY_CONFIG_H_
