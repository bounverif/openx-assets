#!/bin/sh
set -e

# Set OpenSceneGraph version
OPENSCENEGRAPH_VERSION="${OPENSCENEGRAPH_VERSION:-3.6.5}"
FBXSDK_INSTALL_PREFIX="${FBXSDK_INSTALL_PREFIX:-/usr/local}"

# Clone OpenSceneGraph repository
git clone --single-branch --depth 1 --branch "OpenSceneGraph-${OPENSCENEGRAPH_VERSION}" https://github.com/OpenSceneGraph/OpenSceneGraph /tmp/osg

# Build and install OpenSceneGraph
cd /tmp/osg || exit 1
cmake . \
  -DFBX_INCLUDE_DIR="${FBXSDK_INSTALL_PREFIX}/include" \
  -DFBX_LIBRARY="${FBXSDK_INSTALL_PREFIX}/lib/release/libfbxsdk.so" \
  -DFBX_LIBRARY_DEBUG="${FBXSDK_INSTALL_PREFIX}/lib/debug/libfbxsdk.so" \
  -DFBX_XML2_LIBRARY="xml2" \
  -DFBX_XML2_LIBRARY_DEBUG="xml2" \
  -DFBX_ZLIB_LIBRARY="z" \
  -DFBX_ZLIB_LIBRARY_DEBUG="z" \
  -DCMAKE_INSTALL_PREFIX="/usr/local"

cmake --build . --config Release --target install
