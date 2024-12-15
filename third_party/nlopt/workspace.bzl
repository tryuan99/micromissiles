"""This module contains rules for the NLopt library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

NLOPT_VERSION = "2.9.1"
NLOPT_ABI_VERSION = "0.13.0"

def nlopt_workspace():
    http_archive(
        name = "nlopt",
        build_file = "//third_party/nlopt:nlopt.BUILD",
        sha256 = "1e6c33f8cbdc4138d525f3326c231f14ed50d99345561e85285638c49b64ee93",
        strip_prefix = "nlopt-{}".format(NLOPT_VERSION),
        url = "https://github.com/stevengj/nlopt/archive/refs/tags/v{}.tar.gz".format(NLOPT_VERSION),
    )
