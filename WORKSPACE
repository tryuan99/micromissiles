workspace(name = "scum")

# Load third-party workspaces.
load("//third_party:workspace.bzl", "load_third_party_workspaces")
load_third_party_workspaces()

# Register the Python toolchain.
load("//tools:python.bzl", "register_python_toolchain")
register_python_toolchain()

# Parse pip requirements.
load("//deps:pip_requirements.bzl", "parse_pip_requirements")
parse_pip_requirements()

# Load pip dependencies.
load("//deps:pip_deps.bzl", "load_pip_dependencies")
load_pip_dependencies()
