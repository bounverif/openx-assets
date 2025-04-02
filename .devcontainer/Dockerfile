FROM ghcr.io/bounverif/esmini-assets:latest-devel
ARG TARGETARCH TARGETOS TARGETPLATFORM TARGETVARIANT

# Download and install Autodesk FBX SDK dependencies seperately
# as its propietary license does not allow us to distribute.
RUN sudo sh /usr/local/bin/fbxsdk-install.sh
