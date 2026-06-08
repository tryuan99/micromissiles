// The HMC625B chip is a 0.5 dB LSB 6-bit digital variable gain amplifier.

#ifndef PICO_X_DORY_VGA_H_
#define PICO_X_DORY_VGA_H_

#include "pico/common/spi.h"

// VGA configuration struct.
typedef struct {
  // SPI I/O configuration.
  spi_io_config_t spi_io_config;
} vga_config_t;

// Initialize the VGA.
void vga_init(const vga_config_t* config);

// Set the VGA gain attenuation.
void vga_set_gain_attenuation(double gain_attenuation);

#endif  // PICO_X_DORY_VGA_H_
