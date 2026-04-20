set script_dir [file dirname [file normalize [info script]]]

# Source files.
set srcs_files [list \
    [file normalize [file join $script_dir ../src/dory.v]] \
    [file normalize [file join $script_dir ../src/button_debouncer.v]] \
    [file normalize [file join $script_dir ../src/switch_debouncer.v]] \
    [file normalize [file join $script_dir ../src/synchronizer.v]] \
]

# Constraint files.
set constrs_files [list \
    [file normalize [file join $script_dir ../src/dory.xdc]] \
]
