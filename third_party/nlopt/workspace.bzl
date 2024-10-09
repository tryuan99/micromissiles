"""This module contains rules for the NLopt library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

NLOPT_VERSION = "2.8.0"
NLOPT_ABI_VERSION = "0.12.0"

def nlopt_workspace():
    http_archive(
        name = "nlopt",
        build_file = "//third_party/nlopt:nlopt.BUILD",
        sha256 = "e02a4956a69d323775d79fdaec7ba7a23ed912c7d45e439bc933d991ea3193fd",
        strip_prefix = "nlopt-{}".format(NLOPT_VERSION),
        url = "https://github.com/stevengj/nlopt/archive/refs/tags/v{}.tar.gz".format(NLOPT_VERSION),
    )
