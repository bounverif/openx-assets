FROM ghcr.io/bounverif/openx-assets:latest-builder
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

# Download and install Autodesk FBX SDK dependencies seperately
# as its propietary license does not allow us to distribute.
RUN export FBXSDK_INSTALL_PREFIX="/tmp/install" &&\
    mkdir -p ${FBXSDK_INSTALL_PREFIX} &&\
    sh /usr/local/bin/fbxsdk-install.sh &&\
    mv ${FBXSDK_INSTALL_PREFIX}/lib/release/* /usr/local/lib &&\
    rm -rf ${FBXSDK_INSTALL_PREFIX} &&\
    ldconfig
