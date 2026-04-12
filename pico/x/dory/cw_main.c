#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "pico/stdlib.h"
#include "pico/x/dory/config.h"

int main(int argc, char** argv) {
  stdio_init_all();

  while (true) {
    // Print hello world.
    printf("Hello, world!\n");
  }
  return EXIT_SUCCESS;
}
