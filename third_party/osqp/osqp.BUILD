load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all",
    srcs = glob(["**"]),
)

cmake(
    name = "osqp",
    cache_entries = {
        "OSQP_BUILD_SHARED_LIB": "ON",
        "OSQP_BUILD_STATIC_LIB": "OFF",
        "OSQP_ENABLE_PRINTING": "OFF",
        "OSQP_ENABLE_PROFILING": "OFF",
    },
    lib_source = "@osqp//:all",
    out_shared_libs = select({
        "@platforms//os:osx": ["libosqp.dylib"],
        "@platforms//os:linux": ["libosqp.so"],
        "//conditions:default": [],
    }),
    tags = ["requires-network"],
)
