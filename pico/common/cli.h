// CLI interface.

#ifndef PICO_COMMON_CLI_H_
#define PICO_COMMON_CLI_H_

// Callback function type for each input.
typedef void (*cli_callback_t)(const char* command);

// Register the input callback function.
void cli_register_callback(cli_callback_t callback);

// Wait and receive for one complete input.
void cli_read_input(void);

#endif  // PICO_COMMON_CLI_H_
