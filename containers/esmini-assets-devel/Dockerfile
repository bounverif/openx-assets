ARG IMAGE_NAME=localhost/esmini-assets
ARG VERSION=latest

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
      zlib1g-dev \
      libpng-dev \
      libtiff-dev \
      libfontconfig-dev \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY esmini-assets-devel/scripts/* /usr/local/bin/
RUN export FBXSDK_INSTALL_PREFIX=/opt/fbxsdk &&\
    sh /usr/local/bin/fbxsdk-install.sh &&\
    sh /usr/local/bin/openscenegraph-install.sh

FROM docker.io/library/debian:trixie AS esmini-assets-devel
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

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
      python3-numpy \
      reuse \
      libxml2 \
      zlib1g \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Container user
# ARG USER=nonroot
# ARG USERGROUP=${USER}
# ARG UID=1000
# ARG GID=${UID}
# RUN groupadd ${USERGROUP} -g ${GID}; \
#     useradd -ms /bin/bash ${USER} -g ${USERGROUP} -u ${UID} -G sudo; \
#     printf "${USER} ALL= NOPASSWD: ALL\\n" >> /etc/sudoers

# USER ${USER}
# WORKDIR /home/${USER}


