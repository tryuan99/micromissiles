load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all",
    srcs = glob(["**"]),
)

cmake(
    name = "libmpc",
    lib_source = "@libmpc//:all",
    out_headers_only = True,
    tags = ["requires-network"],
    deps = [
        "@eigen",
        "@nlopt",
        "@osqp",
    ],
)
