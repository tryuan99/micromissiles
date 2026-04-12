// SPI interface.

#ifndef PICO_COMMON_SPI_H_
#define PICO_COMMON_SPI_H_

#include <stddef.h>
#include <stdint.h>

#include "hardware/spi.h"

// SPI I/O configuration struct.
typedef struct {
  // SPI instance (spi0 or spi1).
  spi_inst_t* inst;

  // GPIO pins.
  uint8_t gpio_sclk;
  uint8_t gpio_mosi;
  uint8_t gpio_miso;
  uint8_t gpio_cs;
} spi_io_config_t;

// SPI communication configuration struct.
typedef struct {
  // Baudrate.
  uint32_t baudrate;

  // Number of data bits.
  uint8_t data_bits;

  // Clock polarity.
  spi_cpol_t cpol;

  // Clock phase.
  spi_cpha_t cpha;

  // Bit order.
  spi_order_t order;
} spi_comms_config_t;

// Initialize the SPI instance.
void spi_inst_init(const spi_io_config_t* io_config,
                   const spi_comms_config_t* comms_config);

// Transmit data over SPI. This function blocks on the SPI write. Return the
// number of bytes transmitted or -1 on failure.
int spi_transmit(const spi_io_config_t* config, const void* data,
                 size_t length);

// Transmit and receive data over SPI. This function blocks on the SPI read.
// Return the number of bytes received or -1 on failure.
int spi_transmit_receive(const spi_io_config_t* config, const void* data,
                         void* buffer, size_t length);

// Receive data over SPI. This function blocks on the SPI read. Return the
// number of bytes received or -1 on failure.
int spi_receive(const spi_io_config_t* config, void* buffer, size_t length);

#endif  // PICO_COMMON_SPI_H_
