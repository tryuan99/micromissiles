#include "pico/x/dory/vga.h"

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "hardware/spi.h"
#include "pico/common/spi.h"

// VGA SPI baudrate.
#define VGA_SPI_BAUDRATE 1000000

// Number of VGA data bits.
#define VGA_NUM_DATA_BITS 6

// VCO gain attenuation mask enumeration.
typedef enum {
  VGA_GAIN_ATTENUATION_MASK_ZERO = 0b111111,
  VGA_GAIN_ATTENUATION_MASK_HALF = 0b111110,
  VGA_GAIN_ATTENUATION_MASK_ONE = 0b111101,
  VGA_GAIN_ATTENUATION_MASK_TWO = 0b111011,
  VGA_GAIN_ATTENUATION_MASK_FOUR = 0b110111,
  VGA_GAIN_ATTENUATION_MASK_EIGHT = 0b101111,
  VGA_GAIN_ATTENUATION_MASK_SIXTEEN = 0b011111,
} vga_gain_attenuation_mask_e;

// VGA SPI communication configuration.
static const spi_comms_config_t g_vga_spi_comms_config = (spi_comms_config_t){
    .baudrate = VGA_SPI_BAUDRATE,
    .data_bits = VGA_NUM_DATA_BITS,
    .cpol = SPI_CPOL_1,
    .cpha = SPI_CPHA_1,
    .order = SPI_MSB_FIRST,
};

// VGA configuration.
static vga_config_t g_vga_config;

static inline uint8_t vga_get_attenuation_control(
    const double gain_attenuation) {
  if (gain_attenuation < 0 || gain_attenuation > 31.5) {
    return VGA_GAIN_ATTENUATION_MASK_ZERO;
  }

  // Convert to half-step units (0.5 dB resolution).
  size_t steps = (size_t)(gain_attenuation * 2 + 0.5);
  uint8_t gain_attenuation_control = VGA_GAIN_ATTENUATION_MASK_ZERO;
  for (size_t i = 0; i < VGA_NUM_DATA_BITS; ++i) {
    if (steps & (1 << i)) {
      gain_attenuation_control &= ~(1 << i);
    }
  }
  return gain_attenuation_control;
}

void vga_init(const vga_config_t* config) { g_vga_config = *config; }

void vga_set_gain_attenuation(const double gain_attenuation) {
  const uint8_t gain_attenuation_control =
      vga_get_attenuation_control(gain_attenuation);

  // Transmit the VGA gain attenuation control.
  spi_inst_init(&g_vga_config.spi_io_config, &g_vga_spi_comms_config);
  const int num_tx_bytes = spi_transmit(
      &g_vga_config.spi_io_config, &gain_attenuation_control, /*length=*/1);
  if (num_tx_bytes != 1) {
    printf("Failed to transmit VGA gain attenuation control.\n");
    return;
  }

  // Receive the transmitted VGA gain attenuation control.
  uint8_t rx_gain_attenuation_control = 0;
  const int num_rx_bytes = spi_receive(
      &g_vga_config.spi_io_config, &rx_gain_attenuation_control, /*length=*/1);
  if (num_rx_bytes != 1) {
    printf("Failed to receive VGA gain attenuation control.\n");
    return;
  }

  // Compare the transmitted and received VGA gain attenuation control.
  const uint8_t mask = (1 << VGA_NUM_DATA_BITS) - 1;
  const uint8_t masked_gain_attenuation_control =
      gain_attenuation_control & mask;
  const uint8_t masked_rx_gain_attenuation_control =
      rx_gain_attenuation_control & mask;
  if (masked_rx_gain_attenuation_control != masked_gain_attenuation_control) {
    printf(
        "Received VGA gain attenuation control does not match transmitted VGA "
        "gain attenuation control: %u vs. %u.",
        masked_gain_attenuation_control, masked_rx_gain_attenuation_control);
  }
}
