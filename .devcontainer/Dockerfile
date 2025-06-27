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

# Container user
ARG USER=nonroot
ARG USERGROUP=${USER}
ARG UID=1000
ARG GID=${UID}
RUN groupadd ${USERGROUP} -g ${GID}; \
    useradd -ms /bin/bash ${USER} -g ${USERGROUP} -u ${UID} -G sudo; \
    printf "${USER} ALL= NOPASSWD: ALL\\n" >> /etc/sudoers

USER ${USER}
WORKDIR /home/${USER}
