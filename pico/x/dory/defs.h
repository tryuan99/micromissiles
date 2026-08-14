// Global definitions for Dory.

#ifndef PICO_X_DORY_DEFS_H_
#define PICO_X_DORY_DEFS_H_

#include <stdbool.h>

// Define the controlling device.
#define CONTROLLER_PICO
// #define CONTROLLER_FPGA

// Dory hardware revision. Revision 1 uses the HMC625B VGA, and revision 2
// uses the HMC540S attenuator.
#define DORY_REV 1

#if DORY_REV != 1 && DORY_REV != 2
#error "DORY_REV must be 1 or 2."
#endif  // DORY_REV != 1 && DORY_REV != 2

#endif  // PICO_X_DORY_DEFS_H_
