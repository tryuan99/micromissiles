set script_dir [file dirname [file normalize [info script]]]

# Source files.
set srcs_files [list \
    [file normalize [file join $script_dir ../src/bailey.v]] \
    [file normalize [file join $script_dir ../src/debouncer.v]] \
    [file normalize [file join $script_dir ../src/fifo.v]] \
    [file normalize [file join $script_dir ../src/synchronizer.v]] \
]

# Constraint files.
set constrs_files [list \
    [file normalize [file join $script_dir ../src/bailey.xdc]] \
]
