// The ADAR7251 chip is a 4-channel, 16-bit continuous time acquisition ADC.

#ifndef PICO_X_BAILEY_ADC_H_
#define PICO_X_BAILEY_ADC_H_

#include <stdbool.h>
#include <stdint.h>

#include "pico/common/spi.h"

// Number of ADC channels.
#define ADC_NUM_CHANNELS 4

// ADC source enumeration.
typedef enum {
  ADC_SOURCE_INVALID = -1,
  ADC_SOURCE_DISABLED = 0,
  ADC_SOURCE_LNA_PGA_EQ = 1,
  ADC_SOURCE_LNA_PGA = 2,
  ADC_SOURCE_BYPASS = 3,
  ADC_SOURCE_SWAP_CHANNELS = 4,
  ADC_SOURCE_TEST_PIN = 5,
} adc_source_e;

// ADC LNA gain enumeration.
typedef enum {
  ADC_LNA_GAIN_INVALID = -1,
  ADC_LNA_GAIN_TWO = 0,
  ADC_LNA_GAIN_FOUR = 1,
  ADC_LNA_GAIN_EIGHT = 2,
  ADC_LNA_GAIN_SIXTEEN = 3,
} adc_lna_gain_e;

// ADC equalizer cutoff frequency enumeration.
typedef enum {
  ADC_EQUALIZER_CUTOFF_FREQUENCY_INVALID = -1,
  ADC_EQUALIZER_CUTOFF_FREQUENCY_54_KHZ = 0,
  ADC_EQUALIZER_CUTOFF_FREQUENCY_45_KHZ = 1,
  ADC_EQUALIZER_CUTOFF_FREQUENCY_37_KHZ = 2,
  ADC_EQUALIZER_CUTOFF_FREQUENCY_32_KHZ = 3,
} adc_equalizer_cutoff_frequency_e;

// ADC configuration struct.
typedef struct {
  // SPI I/O configuration.
  spi_io_config_t spi_io_config;

  // Conversion start GPIO.
  uint8_t gpio_conversion_start;

  // Data ready GPIO.
  uint8_t gpio_data_ready;

  // Reset GPIO.
  uint8_t gpio_reset;

  // Fault GPIO.
  uint8_t gpio_fault;
} adc_config_t;

// ADC channel configuration struct.
typedef struct {
  // If true, the ADC channel is enabled.
  bool enabled;

  // ADC source.
  adc_source_e source;

  // LNA gain.
  adc_lna_gain_e lna_gain;
} adc_channel_config_t;

// ADC measurement configuration struct.
typedef struct {
  // ADC channel configurations.
  adc_channel_config_t channel_configs[ADC_NUM_CHANNELS];

  // Equalizer cutoff frequency.
  adc_equalizer_cutoff_frequency_e equalizer_cutoff_frequency;
} adc_measurement_config_t;

// Initialize the ADC.
void adc_init(const adc_config_t* config);

// Configure the ADC.
void adc_configure(const adc_measurement_config_t* config);

// Enable the ADC.
void adc_enable(void);

// Disable the ADC.
void adc_disable(void);

// Return whether the ADC PLL is locked.
bool adc_pll_locked(void);

#endif  // PICO_X_BAILEY_ADC_H_
