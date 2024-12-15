"""This module contains rules for the Boost library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

BOOST_VERSION = "1.87.0"

def boost_workspace():
    http_archive(
        name = "boost",
        build_file = "//third_party/boost:boost.BUILD",
        sha256 = "f55c340aa49763b1925ccf02b2e83f35fdcf634c9d5164a2acb87540173c741d",
        strip_prefix = "boost_{}".format(BOOST_VERSION.replace(".", "_")),
        url = "https://archives.boost.io/release/{}/source/boost_{}.tar.gz".format(BOOST_VERSION, BOOST_VERSION.replace(".", "_")),
    )
