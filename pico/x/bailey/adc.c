#include "pico/x/bailey/adc.h"

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "hardware/gpio.h"
#include "pico/common/spi.h"

// ADC SPI baudrate.
#define ADC_SPI_BAUDRATE 1000000

typedef enum {
  ADC_REGISTER_INVALID = -1,
  ADC_REGISTER_CLK_CTRL = 0x000,
  ADC_REGISTER_PLL_DEN = 0x001,
  ADC_REGISTER_PLL_NUM = 0x002,
  ADC_REGISTER_PLL_CTRL = 0x003,
  ADC_REGISTER_PLL_LOCK = 0x005,
  ADC_REGISTER_MASTER_ENABLE = 0x040,
  ADC_REGISTER_ADC_ENABLE = 0x041,
  ADC_REGISTER_POWER_ENABLE = 0x042,
  ADC_REGISTER_ASIL_CLEAR = 0x080,
  ADC_REGISTER_ASIL_MASK = 0x081,
  ADC_REGISTER_ASIL_FLAG = 0x082,
  ADC_REGISTER_ASIL_ERROR = 0x083,
  ADC_REGISTER_CRC_VALUE_L = 0x084,
  ADC_REGISTER_CRC_VALUE_H = 0x085,
  ADC_REGISTER_RM_CRC_ENABLE = 0x086,
  ADC_REGISTER_RM_CRC_DONE = 0x087,
  ADC_REGISTER_RM_CRC_VALUE_L = 0x088,
  ADC_REGISTER_RM_CRC_VALUE_H = 0x089,
  ADC_REGISTER_LNA_GAIN = 0x100,
  ADC_REGISTER_PGA_GAIN = 0x101,
  ADC_REGISTER_ADC_ROUTING1_4 = 0x102,
  ADC_REGISTER_DECIM_RATE = 0x140,
  ADC_REGISTER_HIGH_PASS = 0x141,
  ADC_REGISTER_ACK_MODE = 0x143,
  ADC_REGISTER_TRUNCATE_MODE = 0x144,
  ADC_REGISTER_SERIAL_MODE = 0x1C0,
  ADC_REGISTER_PARALLEL_MODE = 0x1C1,
  ADC_REGISTER_OUTPUT_MODE = 0x1C2,
  ADC_REGISTER_ADC_READ0 = 0x200,
  ADC_REGISTER_ADC_READ1 = 0x201,
  ADC_REGISTER_ADC_SPEED = 0x210,
  ADC_REGISTER_ADC_MODE = 0x211,
  ADC_REGISTER_MP0_MODE = 0x250,
  ADC_REGISTER_MP1_MODE = 0x251,
  ADC_REGISTER_MP0_WRITE = 0x260,
  ADC_REGISTER_MP1_WRITE = 0x261,
  ADC_REGISTER_MP0_READ = 0x270,
  ADC_REGISTER_MP1_READ = 0x271,
  ADC_REGISTER_SPI_CLK_PIN = 0x280,
  ADC_REGISTER_MISO_PIN = 0x281,
  ADC_REGISTER_SS_PIN = 0x282,
  ADC_REGISTER_MOSI_PIN = 0x283,
  ADC_REGISTER_ADDR15_PIN = 0x284,
  ADC_REGISTER_FAULT_PIN = 0x285,
  ADC_REGISTER_FS_ADC_PIN = 0x286,
  ADC_REGISTER_CS_PIN = 0x287,
  ADC_REGISTER_SCLK_ADC_PIN = 0x288,
  ADC_REGISTER_ADC_DOUT0_PIN = 0x289,
  ADC_REGISTER_ADC_DOUT1_PIN = 0x28A,
  ADC_REGISTER_ADC_DOUT2_PIN = 0x28B,
  ADC_REGISTER_ADC_DOUT3_PIN = 0x28C,
  ADC_REGISTER_ADC_DOUT4_PIN = 0x28D,
  ADC_REGISTER_ADC_DOUT5_PIN = 0x28E,
  ADC_REGISTER_DATA_READY_PIN = 0x291,
  ADC_REGISTER_XTAL_CTRL = 0x292,
  ADC_REGISTER_ADC_SETTING1 = 0x301,
  ADC_REGISTER_ADC_SETTING2 = 0x308,
  ADC_REGISTER_ADC_SETTING3 = 0x30A,
  ADC_REGISTER_DEJITTER_WINDOW = 0x30E,
  ADC_REGISTER_CRC_EN = 0xFD00,
} adc_register_e;

// ADC SPI communication configuration.
static const spi_comms_config_t g_adc_spi_comms_config = (spi_comms_config_t){
    .baudrate = ADC_SPI_BAUDRATE,
    .data_bits = 8,
    .cpol = SPI_CPOL_0,
    .cpha = SPI_CPHA_0,
    .order = SPI_MSB_FIRST,
};

// ADC configuration.
static adc_config_t g_adc_config;

void adc_init(const adc_config_t* config) {
  g_adc_config = *config;
  spi_inst_init(&g_adc_config.spi_io_config, &g_adc_spi_comms_config);

  // Initialize the conversion start pin.
  gpio_init(g_adc_config.gpio_conversion_start);

  // Initialize the data ready pin.
  gpio_init(g_adc_config.gpio_data_ready);

  // Initialize the reset pin.
  gpio_init(g_adc_config.gpio_reset);
  gpio_set_dir(g_adc_config.gpio_reset, GPIO_OUT);

  // Initialize the fault pin.
  gpio_init(g_adc_config.gpio_fault);
  gpio_set_dir(g_adc_config.gpio_fault, GPIO_IN);
  // TODO(titan): Add an interrupt listener for the fault pin.
}
