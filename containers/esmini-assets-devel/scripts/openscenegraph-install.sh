#!/bin/sh
set -e

# Set OpenSceneGraph version
OPENSCENEGRAPH_VERSION="${OPENSCENEGRAPH_VERSION:-3.6.5}"

# Clone OpenSceneGraph repository
git clone --single-branch --depth 1 --branch "OpenSceneGraph-${OPENSCENEGRAPH_VERSION}" https://github.com/OpenSceneGraph/OpenSceneGraph /tmp/osg

# Build and install OpenSceneGraph
cd /tmp/osg || exit 1
cmake . \
  -DFBX_INCLUDE_DIR="/opt/fbxsdk/include" \
  -DFBX_LIBRARY="/opt/fbxsdk/lib/release/libfbxsdk.so" \
  -DFBX_LIBRARY_DEBUG="/opt/fbxsdk/lib/debug/libfbxsdk.so" \
  -DFBX_XML2_LIBRARY="xml2" \
  -DFBX_XML2_LIBRARY_DEBUG="xml2" \
  -DFBX_ZLIB_LIBRARY="z" \
  -DFBX_ZLIB_LIBRARY_DEBUG="z" \
  -DCMAKE_INSTALL_PREFIX="/usr/local"

cmake --build . --config Release --target install
