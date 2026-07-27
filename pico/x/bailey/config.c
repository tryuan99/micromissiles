#include "pico/x/bailey/config.h"

#include "hardware/spi.h"
#include "pico/x/bailey/adc.h"
#include "pico/x/bailey/beamformer.h"
#include "pico/x/bailey/mixer.h"

adc_config_t g_adc_config = (adc_config_t){
    .spi_io_config =
        (spi_io_config_t){
            .inst = spi0,
            .gpio_sclk = GPIO_SPI_CLK,
            .gpio_mosi = GPIO_SPI_MOSI,
            .gpio_miso = GPIO_SPI_MISO,
            .gpio_cs = GPIO_ADC_SPI_CS,
        },
    .gpio_conversion_start = GPIO_ADC_CONV_START_N,
    .gpio_data_ready = GPIO_ADC_DATA_READY,
    .gpio_reset = GPIO_ADC_RESET_N,
    .gpio_fault = GPIO_ADC_FAULT_N,
};

beamformer_config_t g_beamformer_config = (beamformer_config_t){
    .spi_io_config =
        (spi_io_config_t){
            .inst = spi0,
            .gpio_sclk = GPIO_SPI_CLK,
            .gpio_mosi = GPIO_SPI_MOSI,
            .gpio_miso = GPIO_SPI_MISO,
            .gpio_cs = GPIO_BEAMFORMER_SPI_CS,
        },
    .gpio_tx_load = GPIO_BEAMFORMER_TX_LOAD,
    .gpio_transmit_receive = GPIO_BEAMFORMER_TR,
};

mixer_config_t g_mixer_config = (mixer_config_t){
    .spi_io_config =
        (spi_io_config_t){
            .inst = spi0,
            .gpio_sclk = GPIO_SPI_CLK,
            .gpio_mosi = GPIO_SPI_MOSI,
            .gpio_miso = GPIO_MIXER_MUXOUT,
            .gpio_cs = GPIO_MIXER_CS,
        },
    .gpio_enable = GPIO_MIXER_EN,
    .gpio_muxout = GPIO_MIXER_MUXOUT,
};
