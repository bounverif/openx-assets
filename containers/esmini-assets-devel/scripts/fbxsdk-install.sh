#!/bin/sh
set -e

# Set default values if not already set
FBXSDK_VERSION_MAJOR="${FBXSDK_VERSION_MAJOR:-2020}"
FBXSDK_VERSION_MINOR="${FBXSDK_VERSION_MINOR:-3}"
FBXSDK_VERSION_PATCH="${FBXSDK_VERSION_PATCH:-7}"
FBXSDK_VERSION="${FBXSDK_VERSION_MAJOR}${FBXSDK_VERSION_MINOR}${FBXSDK_VERSION_PATCH}"
FBXSDK_VERSION_DASHED="${FBXSDK_VERSION_MAJOR}-${FBXSDK_VERSION_MINOR}-${FBXSDK_VERSION_PATCH}"
FBXSDK_DOWNLOAD_URL="https://damassets.autodesk.net/content/dam/autodesk/www/files/fbx${FBXSDK_VERSION}_fbxsdk_gcc_linux.tar.gz"
FBXSDK_INSTALL_PREFIX="${FBXSDK_INSTALL_PREFIX:-/usr/local}"

# Create necessary directories
mkdir -p /tmp/fbxsdk
mkdir -p ${FBXSDK_INSTALL_PREFIX}

# Download and extract FBX SDK
curl -kL --user-agent "Mozilla/5.0" "$FBXSDK_DOWNLOAD_URL" | tar xzv -C /tmp/fbxsdk

# Install FBX SDK
yes yes | /tmp/fbxsdk/fbx${FBXSDK_VERSION}_fbxsdk_linux ${FBXSDK_INSTALL_PREFIX}
