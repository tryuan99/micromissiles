load("@pip_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "if_signal",
    srcs = ["if_signal.py"],
    deps = [
        ":radar",
        ":target",
        "//utils:constants",
        requirement("numpy"),
    ],
)

py_library(
    name = "noise",
    srcs = ["noise.py"],
    deps = [requirement("numpy")],
)

py_library(
    name = "radar",
    srcs = ["radar.py"],
    deps = [requirement("numpy")],
)

py_library(
    name = "target",
    srcs = ["target.py"],
    deps = [requirement("numpy")],
)

py_binary(
    name = "if_amplitude_vs_range_main",
    srcs = ["if_amplitude_vs_range_main.py"],
    deps = [
        ":radar",
        ":target",
        ":if_signal",
        "//utils:constants",
        requirement("absl-py"),
        requirement("matplotlib"),
        requirement("numpy"),
        requirement("scipy"),
    ],
)

py_binary(
    name = "range_doppler_main",
    srcs = ["range_doppler_main.py"],
    deps = [
        ":noise",
        ":radar",
        ":target",
        ":if_signal",
        "//utils:constants",
        "//utils/visualization:color_maps",
        requirement("absl-py"),
        requirement("matplotlib"),
        requirement("numpy"),
        requirement("scipy"),
    ],
)
