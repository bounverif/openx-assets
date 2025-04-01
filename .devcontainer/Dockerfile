FROM docker.io/library/debian:trixie AS esmini-openscenegraph-builder
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      sudo \
      curl \
      git \
      jq \
      gnupg2 \
      ca-certificates \
      build-essential \
      cmake \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      libgl1-mesa-dev \
      libxml2-dev \
      libjpeg-dev \
      libpng-dev \
      libtiff-dev \
      libfontconfig-dev \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN export FBXSDK_VERSION_MAJOR="${FBXSDK_VERSION_MAJOR:-2020}" &&\
    export FBXSDK_VERSION_MINOR="${FBXSDK_VERSION_MINOR:-3}" &&\
    export FBXSDK_VERSION_PATCH="${FBXSDK_VERSION_PATCH:-7}" &&\
    export FBXSDK_VERSION="${FBXSDK_VERSION_MAJOR}${FBXSDK_VERSION_MINOR}${FBXSDK_VERSION_PATCH}" &&\
    export FBXSDK_VERSION_DASHED="${FBXSDK_VERSION_MAJOR}-${FBXSDK_VERSION_MINOR}-${FBXSDK_VERSION_PATCH}" &&\
    export FBXSDK_DOWNLOAD_URL="https://damassets.autodesk.net/content/dam/autodesk/www/files/fbx${FBXSDK_VERSION}_fbxsdk_gcc_linux.tar.gz" &&\
    mkdir -p /tmp/fbxsdk &&\
    mkdir -p /tmp/fbxsdk/install &&\
    curl -kL --user-agent "Mozilla/5.0" ${FBXSDK_DOWNLOAD_URL} | tar xzv -C /tmp/fbxsdk &&\
    yes yes | /tmp/fbxsdk/fbx${FBXSDK_VERSION}_fbxsdk_linux /tmp/fbxsdk/install

RUN git clone --single-branch --depth 1 --branch OpenSceneGraph-${OSG_VERSION:-3.6.5} https://github.com/OpenSceneGraph/OpenSceneGraph /tmp/osg && \
    cd /tmp/osg && \
    cmake . \
        -DFBX_INCLUDE_DIR="/tmp/fbxsdk/install/include" \
        -DFBX_LIBRARY="/tmp/fbxsdk/install/lib/release/libfbxsdk.a" \
        -DFBX_LIBRARY_DEBUG="/tmp/fbxsdk/install/lib/debug/libfbxsdk.a" \
        -DCMAKE_INSTALL_PREFIX="/usr/local" \
        && \
    cmake --build . --config Release --target install

FROM docker.io/library/debian:trixie AS esmini-assets-devel
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

# Install dependencies
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      sudo \
      curl \
      wget \
      ca-certificates \
      git \
      gnupg2 \
      tar zip unzip xz-utils \
      make \
      python3 python3-pip pipx \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY --from=esmini-openscenegraph-builder /usr/local/ /usr/local/

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      blender \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Container user
ARG USER=bounverif
ARG USERGROUP=${USER}
ARG UID=1000
ARG GID=${UID}
RUN groupadd ${USERGROUP} -g ${GID}; \
    useradd -ms /bin/bash ${USER} -g ${USERGROUP} -u ${UID} -G sudo; \
    printf "${USER} ALL= NOPASSWD: ALL\\n" >> /etc/sudoers

USER ${USER}
WORKDIR /home/${USER}

RUN export PIP_BREAK_SYSTEM_PACKAGES=1 &&\
    pip install --upgrade pip &&\
    pip install \
      reuse
