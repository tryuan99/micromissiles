#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "hardware/spi.h"
#include "pico/stdlib.h"
#include "pico/x/dory/config.h"
#include "pico/x/dory/dds.h"
#include "pico/x/dory/vco.h"
#include "pico/x/dory/vga.h"

// VCO configuration.
static vco_config_t g_vco_config = (vco_config_t){
    .spi_config =
        (spi_io_config_t){
            .inst = spi0,
            .gpio_sclk = GPIO_VCO_CLK,
            .gpio_mosi = GPIO_VCO_DATA,
            .gpio_miso = GPIO_VCO_MUXOUT,
            .gpio_cs = GPIO_VCO_LE,
        },
    .gpio_enable = GPIO_VCO_EN,
    .gpio_rf_enable = GPIO_VCO_RF_EN,
    .gpio_muxout = GPIO_VCO_MUXOUT,
    .gpio_ld = GPIO_VCO_LD,
};

// DDS configuration.
static dds_config_t g_dds_config = (dds_config_t){
    .spi_config =
        (spi_io_config_t){
            .inst = spi1,
            .gpio_sclk = GPIO_DDS_SCLK,
            .gpio_mosi = GPIO_DDS_SDIO,
            .gpio_miso = GPIO_DDS_SDO,
            .gpio_cs = GPIO_DDS_CS,
        },
    .gpio_rst = GPIO_DDS_RST,
    .gpio_io_update = GPIO_DDS_IO_UPDATE,
    .gpio_ps0 = GPIO_DDS_PS0,
    .gpio_ps1 = GPIO_DDS_PS1,
    .gpio_ps2 = GPIO_DDS_PS2,
    .gpio_drctl = GPIO_DDS_DRCTL,
    .gpio_drhold = GPIO_DDS_DRHOLD,
    .gpio_drover = GPIO_DDS_DROVER,
    .gpio_osk = GPIO_DDS_OSK,
    .mode = DDS_MODE_CW,
};

// Mixer configuration.
static mixer_config_t g_mixer_config = (mixer_config_t){
    .gpio_enable = GPIO_MIXER_EN,
};

// VGA configuration.
static vga_config_t g_vga_config = (vga_config_t){
    .spi_config =
        (spi_io_config_t){
            .inst = spi0,
            .gpio_sclk = GPIO_VGA_CLK,
            .gpio_mosi = GPIO_VGA_SERIN,
            .gpio_miso = GPIO_VGA_SEROUT,
            .gpio_cs = GPIO_VGA_LE,
        },
};

int main(int argc, char** argv) {
  stdio_init_all();

  while (true) {
    // Print hello world.
    printf("Hello, world!\n");
  }
  return EXIT_SUCCESS;
}
