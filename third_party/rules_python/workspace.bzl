load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_PYTHON_VERSION = "0.22.0"

def rules_python_workspace():
    http_archive(
        name = "rules_python",
        sha256 = "863ba0fa944319f7e3d695711427d9ad80ba92c6edd0b7c7443b84e904689539",
        strip_prefix = "rules_python-{}".format(RULES_PYTHON_VERSION),
        url = "https://github.com/bazelbuild/rules_python/archive/refs/tags/{}.tar.gz".format(RULES_PYTHON_VERSION),
    )
