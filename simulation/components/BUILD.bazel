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
    name = "azimuth_elevation_map",
    srcs = ["azimuth_elevation_map.py"],
    deps = [
        ":radar",
        ":range_doppler_map",
        ":samples",
        ":target",
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
        ":target",
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
