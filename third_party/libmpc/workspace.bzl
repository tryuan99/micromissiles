"""This module contains rules for the libmpc++ library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

LIBMPC_VERSION = "0.6.2"

def libmpc_workspace():
    http_archive(
        name = "libmpc",
        build_file = "//third_party/libmpc:libmpc.BUILD",
        sha256 = "6aab3f029f8fc706987a0b5f34bf0b5f7c0403e1a0961072cd4db47d73ba95e5",
        strip_prefix = "libmpc-{}".format(LIBMPC_VERSION),
        url = "https://github.com/nicolapiccinelli/libmpc/archive/refs/tags/{}.tar.gz".format(LIBMPC_VERSION),
    )
