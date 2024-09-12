load("@//third_party/matplot:workspace.bzl", "MATPLOT_VERSION")
load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all",
    srcs = glob(["**"]),
)

cmake(
    name = "matplot",
    cache_entries = {
        "BUILD_SHARED_LIBS": "ON",
        "MATPLOTPP_BUILD_EXAMPLES": "OFF",
        "MATPLOTPP_BUILD_TESTS": "OFF",
    },
    lib_source = "@matplot//:all",
    out_shared_libs = select({
        "@platforms//os:osx": [
            "libmatplot.dylib",
            "libmatplot.{}.0.dylib".format(".".join(MATPLOT_VERSION.split(".")[:2])),
        ],
        "@platforms//os:linux": [
            "libmatplot.so",
            "libmatplot.so.{}.0".format(".".join(MATPLOT_VERSION.split(".")[:2])),
        ],
        "//conditions:default": [],
    }),
)
