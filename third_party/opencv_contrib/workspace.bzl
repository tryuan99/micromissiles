"""This module contains rules for OpenCV's extra modules."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

OPENCV_CONTRIB_VERSION = "4.10.0"

def opencv_contrib_workspace():
    http_archive(
        name = "opencv_contrib",
        build_file = "//third_party/opencv_contrib:opencv_contrib.BUILD",
        sha256 = "65597f8fb8dc2b876c1b45b928bbcc5f772ddbaf97539bf1b737623d0604cba1",
        strip_prefix = "opencv_contrib-{}".format(OPENCV_CONTRIB_VERSION),
        url = "https://github.com/opencv/opencv_contrib/archive/refs/tags/{}.tar.gz".format(OPENCV_CONTRIB_VERSION),
    )
