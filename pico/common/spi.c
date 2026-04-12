#include "pico/common/spi.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "hardware/gpio.h"
#include "hardware/spi.h"

void spi_inst_init(const spi_io_config_t* io_config,
                   const spi_comms_config_t* comms_config) {
  // Initialize the SPI instance.
  spi_init(io_config->inst, comms_config->baudrate);
  spi_set_format(io_config->inst, comms_config->data_bits, comms_config->cpol,
                 comms_config->cpha, comms_config->order);

  // Initialize the GPIO pins.
  gpio_set_function(io_config->gpio_sclk, GPIO_FUNC_SPI);
  gpio_set_function(io_config->gpio_mosi, GPIO_FUNC_SPI);
  gpio_set_function(io_config->gpio_miso, GPIO_FUNC_SPI);

  // Initialize the chip select pin.
  gpio_init(io_config->gpio_cs);
  gpio_set_dir(io_config->gpio_cs, GPIO_OUT);
  gpio_put(io_config->gpio_cs, true);
}

int spi_transmit(const spi_io_config_t* config, const void* data,
                 const size_t length) {
  if (config == NULL || data == NULL) {
    return -1;
  }
  if (length == 0) {
    return 0;
  }

  gpio_put(config->gpio_cs, false);
  const int num_bytes =
      spi_write_blocking(config->inst, (const uint8_t*)data, length);
  gpio_put(config->gpio_cs, true);
  return num_bytes;
}

int spi_transmit_receive(const spi_io_config_t* config, const void* data,
                         void* buffer, const size_t length) {
  if (config == NULL || data == NULL || buffer == NULL) {
    return -1;
  }
  if (length == 0) {
    return 0;
  }

  gpio_put(config->gpio_cs, false);
  const int num_bytes = spi_write_read_blocking(
      config->inst, (const uint8_t*)data, (uint8_t*)buffer, length);
  gpio_put(config->gpio_cs, true);
  return num_bytes;
}

int spi_receive(const spi_io_config_t* config, void* buffer,
                const size_t length) {
  if (config == NULL || buffer == NULL) {
    return -1;
  }
  if (length == 0) {
    return 0;
  }

  gpio_put(config->gpio_cs, false);
  const int num_bytes = spi_read_blocking(config->inst, /*repeated_tx_data=*/0,
                                          (uint8_t*)buffer, length);
  gpio_put(config->gpio_cs, true);
  return num_bytes;
}
