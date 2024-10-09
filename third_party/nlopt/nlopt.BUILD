load("@//third_party/nlopt:workspace.bzl", "NLOPT_ABI_VERSION")
load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all",
    srcs = glob(["**"]),
)

cmake(
    name = "nlopt",
    cache_entries = {
        "BUILD_SHARED_LIBS": "ON",
        "NLOPT_PYTHON": "OFF",
        "NLOPT_OCTAVE": "OFF",
        "NLOPT_MATLAB": "OFF",
        "NLOPT_GUILE": "OFF",
        "NLOPT_SWIG": "OFF",
    },
    lib_source = "@nlopt//:all",
    out_shared_libs = select({
        "@platforms//os:osx": [
            "libnlopt.dylib",
            "libnlopt.{}.dylib".format(NLOPT_ABI_VERSION.split(".", 1)[0]),
            "libnlopt.{}.dylib".format(NLOPT_ABI_VERSION),
        ],
        "@platforms//os:linux": [
            "libnlopt.so",
            "libnlopt.so.{}".format(NLOPT_ABI_VERSION.split(".", 1)[0]),
            "libnlopt.so.{}".format(NLOPT_ABI_VERSION),
        ],
        "//conditions:default": [],
    }),
)
