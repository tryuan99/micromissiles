load("@rules_python//python:repositories.bzl", "python_register_toolchains")

def register_python_toolchain():
    python_register_toolchains(
        name = "python3_10",
        python_version = "3.10",
    )
