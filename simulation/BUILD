load("@pip_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_library(
    name = "adc_data",
    srcs = ["adc_data.py"],
    deps = [
        ":radar",
        ":samples",
        ":target",
        "//utils:constants",
        requirement("numpy"),
    ],
)

py_library(
    name = "noise",
    srcs = ["noise.py"],
    deps = [
        ":samples",
        requirement("numpy"),
    ],
)

py_library(
    name = "radar",
    srcs = ["radar.py"],
    deps = [
        ":noise",
        requirement("numpy"),
        requirement("scipy"),
    ],
)

py_library(
    name = "range_doppler_map",
    srcs = ["range_doppler_map.py"],
    deps = [
        ":radar",
        ":samples",
        requirement("numpy"),
    ],
)

py_library(
    name = "samples",
    srcs = ["samples.py"],
    deps = [requirement("numpy")],
)

py_library(
    name = "target",
    srcs = ["target.py"],
    deps = [requirement("numpy")],
)

py_binary(
    name = "snr_vs_range_main",
    srcs = ["snr_vs_range_main.py"],
    deps = [
        ":radar",
        ":target",
        ":adc_data",
        "//utils:constants",
        requirement("absl-py"),
        requirement("matplotlib"),
        requirement("numpy"),
    ],
)

py_binary(
    name = "range_doppler_main",
    srcs = ["range_doppler_main.py"],
    deps = [
        ":radar",
        ":range_doppler_map",
        ":samples",
        ":target",
        ":adc_data",
        "//utils:constants",
        "//utils/visualization:color_maps",
        requirement("absl-py"),
        requirement("matplotlib"),
        requirement("numpy"),
    ],
)
