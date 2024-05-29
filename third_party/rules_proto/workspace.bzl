"""This module contains Bazel rules for Protobuf."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_PROTO_VERSION = "6.0.0"

def rules_proto_workspace():
    http_archive(
        name = "rules_proto",
        sha256 = "303e86e722a520f6f326a50b41cfc16b98fe6d1955ce46642a5b7a67c11c0f5d",
        strip_prefix = "rules_proto-{}".format(RULES_PROTO_VERSION),
        url = "https://github.com/bazelbuild/rules_proto/archive/refs/tags/{}.tar.gz".format(RULES_PROTO_VERSION),
    )
