"""This module contains rules for the OpenCV library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

OPENCV_VERSION = "4.10.0"

def opencv_workspace():
    http_archive(
        name = "opencv",
        build_file = "//third_party/opencv:opencv.BUILD",
        sha256 = "b2171af5be6b26f7a06b1229948bbb2bdaa74fcf5cd097e0af6378fce50a6eb9",
        strip_prefix = "opencv-{}".format(OPENCV_VERSION),
        url = "https://github.com/opencv/opencv/archive/refs/tags/{}.tar.gz".format(OPENCV_VERSION),
    )
