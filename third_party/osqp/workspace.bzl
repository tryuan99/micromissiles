"""This module contains rules for the OSQP library."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

OSQP_COMMIT_HASH = "4532d356f08789461bc041531f22a1001144c40a"

def osqp_workspace():
    http_archive(
        name = "osqp",
        build_file = "//third_party/osqp:osqp.BUILD",
        sha256 = "99f46241bbf047f9e26dbe63eb4ca78cf48ba6a123b26df38d4196c2324b36e7",
        strip_prefix = "osqp-{}".format(OSQP_COMMIT_HASH),
        url = "https://github.com/osqp/osqp/archive/{}.tar.gz".format(OSQP_COMMIT_HASH),
    )
