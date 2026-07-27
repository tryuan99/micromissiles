// The ADAR7251 chip is a 4-channel, 16-bit continuous time acquisition ADC.

#ifndef PICO_X_BAILEY_ADC_H_
#define PICO_X_BAILEY_ADC_H_

#include <stdint.h>

#include "pico/common/spi.h"

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

// Initialize the ADC.
void adc_init(const adc_config_t* config);

#endif  // PICO_X_BAILEY_ADC_H_
