#include "pico/x/dory/dds.h"

#include "hardware/spi.h"
#include "pico/common/spi.h"

// DDS SPI communication configuration.
static const spi_comms_config_t g_dds_spi_comms_config = (spi_comms_config_t){
    .baudrate = 1000000,
    .data_bits = 8,
    .cpol = SPI_CPOL_1,
    .cpha = SPI_CPHA_1,
    .order = SPI_MSB_FIRST,
};

// DDS configuration.
static dds_config_t g_dds_config;

void dds_init(const dds_config_t* config) {
  g_dds_config = *config;
  spi_inst_init(&g_dds_config.spi_io_config, &g_dds_spi_comms_config);
}
