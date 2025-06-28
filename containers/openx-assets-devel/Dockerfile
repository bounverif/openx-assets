ARG IMAGE_NAME=localhost/openx-assets
ARG VERSION=latest

FROM docker.io/library/debian:12 AS openx-openscenegraph-builder
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

COPY openx-assets-devel/scripts/* /usr/local/bin/
RUN export FBXSDK_INSTALL_PREFIX=/opt/fbxsdk &&\
    sh /usr/local/bin/fbxsdk-install.sh &&\
    sh /usr/local/bin/openscenegraph-install.sh

FROM docker.io/library/debian:12 AS openx-assets-builder
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

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
      git-lfs \
      gnupg2 \
      zlib1g \
      tar zip unzip xz-utils \
      make \
      build-essential \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

COPY --from=openx-openscenegraph-builder /usr/local/ /usr/local/

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      python3 \
      python3-dev \
      python3-pip \
      python3-numpy \
      pipx \
      libxml2 \
      libx11-6 \
      \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

RUN pipx ensurepath && \
    pipx install --pip-args="--no-cache-dir" reuse

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=${TARGETPLATFORM}/var/cache/apt \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && \
    apt-get install -qy --no-install-recommends \
      libxrender1 \
      libxxf86vm1 \
      libxfixes3 \
      libxi6 \
      libxkbcommon0 \
      libsm6 \
      libgl1 \
      libfontconfig1 \
      && \
    apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

ENV PIP_BREAK_SYSTEM_PACKAGES=1

FROM openx-assets-builder AS openx-assets-devel
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

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
