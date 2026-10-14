FROM ghcr.io/vevalabs/openx-assets:latest-builder
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

# Download and install Autodesk FBX SDK dependencies seperately
# as its propietary license does not allow us to distribute.
RUN export FBXSDK_INSTALL_PREFIX="/tmp/install" &&\
    mkdir -p ${FBXSDK_INSTALL_PREFIX} &&\
    sh /usr/local/bin/fbxsdk-install.sh &&\
    mv ${FBXSDK_INSTALL_PREFIX}/lib/release/* /usr/local/lib &&\
    rm -rf ${FBXSDK_INSTALL_PREFIX} &&\
    ldconfig

# Non-root user for Docker; VS Code remaps its UID/GID to the host user
ARG USER=nonroot
ARG UID=1000
ARG GID=${UID}
RUN groupadd ${USER} -g ${GID} && \
    useradd -ms /bin/bash ${USER} -g ${USER} -u ${UID} -G sudo && \
    printf "${USER} ALL= NOPASSWD: ALL\\n" >> /etc/sudoers
