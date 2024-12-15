"""This module contains rules for the OSQP library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

OSQP_COMMIT_HASH = "e303d106e33c4aefce6964e668b443c99d9da86e"

def osqp_workspace():
    http_archive(
        name = "osqp",
        build_file = "//third_party/osqp:osqp.BUILD",
        sha256 = "3d7b0d48f0f2460d57f41130f117b8ccb40cc1b4d39f0536c5fed83470d5d11d",
        strip_prefix = "osqp-{}".format(OSQP_COMMIT_HASH),
        url = "https://github.com/osqp/osqp/archive/{}.tar.gz".format(OSQP_COMMIT_HASH),
    )
