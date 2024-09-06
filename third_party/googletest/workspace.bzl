"""This module contains rules for the Eigen library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

GOOGLETEST_VERSION = "1.15.2"

def googletest_workspace():
    http_archive(
        name = "googletest",
        sha256 = "7b42b4d6ed48810c5362c265a17faebe90dc2373c885e5216439d37927f02926",
        strip_prefix = "googletest-{}".format(GOOGLETEST_VERSION),
        url = "https://github.com/google/googletest/archive/refs/tags/v{}.tar.gz".format(GOOGLETEST_VERSION),
    )
