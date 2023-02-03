load("//third_party/rules_proto:workspace.bzl", "rules_proto_workspace")
load("//third_party/rules_python:workspace.bzl", "rules_python_workspace")

def load_third_party_workspaces():
    rules_proto_workspace()
    rules_python_workspace()
