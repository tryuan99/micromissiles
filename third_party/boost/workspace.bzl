"""This module contains rules for the Boost library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

BOOST_VERSION = "1.86.0"

def boost_workspace():
    http_archive(
        name = "boost",
        build_file = "//third_party/boost:boost.BUILD",
        sha256 = "2575e74ffc3ef1cd0babac2c1ee8bdb5782a0ee672b1912da40e5b4b591ca01f",
        strip_prefix = "boost_{}".format(BOOST_VERSION.replace(".", "_")),
        url = "https://archives.boost.io/release/{}/source/boost_{}.tar.gz".format(BOOST_VERSION, BOOST_VERSION.replace(".", "_")),
    )
