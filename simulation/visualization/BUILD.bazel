load("@pip_deps//:requirements.bzl", "requirement")

package(default_visibility = ["//visibility:public"])

py_binary(
    name = "direction_of_arrival_main",
    srcs = ["direction_of_arrival_main.py"],
    deps = [
        "//simulation/components:azimuth_elevation_map",
        "//simulation/components:radar",
        "//simulation/components:range_doppler_map",
        "//simulation/components:samples",
        "//simulation/components:target",
        "//simulation/components:adc_data",
        "//utils:constants",
        "//utils/visualization:color_maps",
        requirement("absl-py"),
        requirement("matplotlib"),
        requirement("numpy"),
    ],
)

py_binary(
    name = "snr_vs_range_main",
    srcs = ["snr_vs_range_main.py"],
    deps = [
        "//simulation/components:radar",
        "//simulation/components:target",
        "//simulation/components:adc_data",
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
        "//simulation/components:radar",
        "//simulation/components:range_doppler_map",
        "//simulation/components:samples",
        "//simulation/components:target",
        "//simulation/components:adc_data",
        "//utils:constants",
        "//utils/visualization:color_maps",
        requirement("absl-py"),
        requirement("matplotlib"),
        requirement("numpy"),
    ],
)
