"""This module contains rules for the Matplot++ library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

MATPLOT_VERSION = "1.2.1"

def matplot_workspace():
    http_archive(
        name = "matplot",
        build_file = "//third_party/matplot:matplot.BUILD",
        sha256 = "9dd7cc92b2425148f50329f5a3bf95f9774ac807657838972d35334b5ff7cb87",
        strip_prefix = "matplotplusplus-{}".format(MATPLOT_VERSION),
        url = "https://github.com/alandefreitas/matplotplusplus/archive/refs/tags/v{}.tar.gz".format(MATPLOT_VERSION),
    )
