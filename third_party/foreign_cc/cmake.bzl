"""This module defines a CMake rule that compiles C++ with g++ on Linux."""

load("@rules_foreign_cc//foreign_cc:defs.bzl", _cmake = "cmake")

def cmake(name, env = None, **kwargs):
    """Builds a CMake project with g++ as the C++ compiler on Linux.

    Args:
        name: Name of the target.
        env: Environment variables to set during the build.
        **kwargs: Additional arguments to pass to the cmake rule.
    """
    _cmake(
        name = name,
        env = (env or {}) | select({
            "@platforms//os:linux": {"CXX": "g++"},
            "//conditions:default": {},
        }),
        **kwargs
    )
