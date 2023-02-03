load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_PYTHON_VERSION = "0.17.3"

def rules_python_workspace():
    http_archive(
        name = "rules_python",
        sha256 = "8c15896f6686beb5c631a4459a3aa8392daccaab805ea899c9d14215074b60ef",
        strip_prefix = "rules_python-{}".format(RULES_PYTHON_VERSION),
        url = "https://github.com/bazelbuild/rules_python/archive/refs/tags/{}.tar.gz".format(RULES_PYTHON_VERSION),
    )
