ARG VERSION=latest

ARG OPENX_ASSETS_RELEASE_URL=https://github.com/vevalabs/openx-assets/releases
ARG OPENX_ASSETS_RELEASE_FILENAME=openx-assets-esmini.zip
ARG OPENX_ASSETS_RELEASE_TAG=${VERSION}

FROM docker.io/library/debian:12 AS release-downloader
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT
ARG OPENX_ASSETS_RELEASE_URL OPENX_ASSETS_RELEASE_FILENAME OPENX_ASSETS_RELEASE_TAG

RUN apt-get update -qq && apt-get install -qy --no-install-recommends \
      curl \
      ca-certificates \
      unzip \
      && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# GitHub serves the latest release under /latest/download instead of /download/<tag>
RUN if [ "${OPENX_ASSETS_RELEASE_TAG}" = "latest" ]; then \
      url="${OPENX_ASSETS_RELEASE_URL}/latest/download/${OPENX_ASSETS_RELEASE_FILENAME}"; \
    else \
      url="${OPENX_ASSETS_RELEASE_URL}/download/${OPENX_ASSETS_RELEASE_TAG}/${OPENX_ASSETS_RELEASE_FILENAME}"; \
    fi && \
    echo "Downloading ${url}" && \
    curl -fsSL -o /tmp/openx-assets.zip "${url}" && \
    unzip -q /tmp/openx-assets.zip -d /opt/openx-assets && \
    rm /tmp/openx-assets.zip

FROM docker.io/library/debian:12 AS openx-assets-esmini
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

COPY --from=release-downloader /opt/openx-assets /opt/openx-assets
