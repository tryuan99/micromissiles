#include "pico/common/cli.h"

#include <stdbool.h>
#include <stddef.h>

// Maximum input length in bytes.
#define CLI_INPUT_MAX_LENGTH 256

// Input callback function.
static cli_callback_t g_cli_callback;

// Input buffer.
static char g_cli_buffer[CLI_INPUT_MAX_LENGTH];

void cli_register_callback(const cli_callback_t callback) {
  g_cli_callback = callback;
}

void cli_read_input(void) {
  size_t length = 0;
  while (true) {
    const int c = getchar();
    if (c == '\n') {
      break;
    }
    if (c != '\r' && length < CLI_INPUT_MAX_LENGTH - 1) {
      g_cli_buffer[length] = (char)c;
      ++length;
    }
  }
  g_cli_buffer[length] = '\0';

  if (g_cli_callback != NULL) {
    g_cli_callback(g_cli_buffer);
  }
}
