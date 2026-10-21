load("@//third_party/foreign_cc:cmake.bzl", "cmake")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all",
    srcs = glob(["**"]),
)

cmake(
    name = "libmpc",
    cache_entries = {
        "EIGEN3_INCLUDE_DIRS": "$$EXT_BUILD_DEPS/include",
    },
    lib_source = "@libmpc//:all",
    out_headers_only = True,
    tags = ["requires-network"],
    deps = [
        "@eigen",
        "@nlopt",
        "@osqp",
    ],
)
