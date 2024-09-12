"""This module defines the OpenCV modules and libraries."""

load("@//third_party/opencv:workspace.bzl", "OPENCV_VERSION")

OPENCV_MODULES = [
    "core",
    "highgui",
    "imgproc",
    "viz",
]

def opencv_shared_libs_osx():
    """Lists the OpenCV shared libraries on OSX.

    Returns:
        The list of OpenCV shared libraries.
    """
    shared_libs = []
    for module in OPENCV_MODULES:
        module_libs = [
            "libopencv_{}.dylib".format(module),
            "libopencv_{}.{}.dylib".format(module, "".join(OPENCV_VERSION.split(".")[:2])),
            "libopencv_{}.{}.dylib".format(module, OPENCV_VERSION),
        ]
        shared_libs.extend(module_libs)
    return shared_libs

def opencv_shared_libs_unix():
    """Lists the OpenCV shared libraries on Unix.

    Returns:
        The list of OpenCV shared libraries.
    """
    shared_libs = []
    for module in OPENCV_MODULES:
        module_libs = [
            "libopencv_{}.so".format(module),
            "libopencv_{}.so.{}".format(module, "".join(OPENCV_VERSION.split(".")[:2])),
            "libopencv_{}.so.{}".format(module, OPENCV_VERSION),
        ]
        shared_libs.extend(module_libs)
    return shared_libs

OPENCV_SHARED_LIBS = select({
    "@platforms//os:osx": opencv_shared_libs_osx(),
    "@platforms//os:linux": opencv_shared_libs_unix(),
    "//conditions:default": [],
})
