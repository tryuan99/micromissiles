load("@//third_party/opencv:opencv.bzl", "OPENCV_MODULES", "OPENCV_SHARED_LIBS")
load("@rules_foreign_cc//foreign_cc:defs.bzl", "cmake")

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "all",
    srcs = glob(["**"]),
)

cmake(
    name = "opencv",
    build_data = ["@opencv_contrib//:modules"],
    cache_entries = {
        "BUILD_SHARED_LIBS": "ON",
        "BUILD_LIST": ",".join(OPENCV_MODULES),
        "OPENCV_EXTRA_MODULES_PATH": "$EXT_BUILD_ROOT/external/opencv_contrib/modules",
        "WITH_EIGEN": "ON",
        "WITH_VTK": "ON",
        "BUILD_ZLIB": "OFF",
    },
    lib_source = "@opencv//:all",
    out_include_dir = "include/opencv4",
    out_shared_libs = OPENCV_SHARED_LIBS,
    tags = ["requires-network"],
)
