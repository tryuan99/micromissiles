#!/bin/bash

CREATE_PROJECT=false
BUILD_ONLY=false
SKIP_BUILD=false
FLASH=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"

show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Options:
  --create-project Create a new Vivado project (runs create_project.tcl)
  --build-only     Run build only and exit (no programming or flashing)
  --skip-build     Skip the build step
  --flash          Flash the design to hardware (runs flash.tcl instead of program.tcl)
  -h, --help       Show this help message
EOF
}

# Parse command-line arguments.
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --create-project) CREATE_PROJECT=true ;;
        --build-only) BUILD_ONLY=true ;;
        --skip-build) SKIP_BUILD=true ;;
        --flash) FLASH=true ;;
        -h|--help) show_help; exit 0 ;;
        *) echo "Unknown option: $1"; show_help; exit 1 ;;
    esac
    shift
done

# Check if Vivado is installed.
if ! command -v vivado &> /dev/null; then
    echo "Error: Vivado is not found in your PATH. Please install or add Vivado to PATH before running this script."
    exit 1
fi

# Function to run a TCL script with Vivado.
run_tcl() {
    local script="$1"
    if [[ ! -f "$script" ]]; then
        echo "Error: '$script' does not exist."
        exit 1
    fi

    local cmd=(vivado -mode batch -source "$script")
    echo "Executing: ${cmd[*]}"
    if ! "${cmd[@]}"; then
        echo "Error: $script failed."
        exit 1
    fi
}

if [[ "$CREATE_PROJECT" = true ]]; then
    run_tcl "$SCRIPT_DIR/create_project.tcl"
    exit 0
fi

if [[ "$SKIP_BUILD" = false ]]; then
    run_tcl "$SCRIPT_DIR/dory.tcl"
fi

if [[ "$BUILD_ONLY" = true ]]; then
    echo "Exiting without programming or flashing."
    exit 0
fi

if [[ "$FLASH" = true ]]; then
    run_tcl "$SCRIPT_DIR/flash.tcl"
else
    run_tcl "$SCRIPT_DIR/program.tcl"
fi
