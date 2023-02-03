load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_PROTO_VERSION = "5.3.0-21.7"

def rules_proto_workspace():
    http_archive(
        name = "rules_proto",
        sha256 = "dc3fb206a2cb3441b485eb1e423165b231235a1ea9b031b4433cf7bc1fa460dd",
        strip_prefix = "rules_proto-{}".format(RULES_PROTO_VERSION),
        url = "https://github.com/bazelbuild/rules_proto/archive/refs/tags/{}.tar.gz".format(RULES_PROTO_VERSION),
    )
