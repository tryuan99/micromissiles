load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

RULES_PYTHON_VERSION = "0.22.1"

def rules_python_workspace():
    http_archive(
        name = "rules_python",
        sha256 = "a5640fddd4beb03e8c1fde5ed7160c0ba6bd477e7d048661c30c06936a26fd63",
        strip_prefix = "rules_python-{}".format(RULES_PYTHON_VERSION),
        url = "https://github.com/bazelbuild/rules_python/archive/refs/tags/{}.tar.gz".format(RULES_PYTHON_VERSION),
    )
