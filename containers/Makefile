IMAGE_NAME ?= localhost/esmini-assets
VERSION ?= latest
CONTAINER_BUILD_CONTEXT ?= .

devel:
	buildah build \
		-f esmini-assets-devel/Dockerfile \
		--build-arg IMAGE_NAME=${IMAGE_NAME} \
		--build-arg VERSION=${VERSION} \
		--format oci \
		--layers=true \
		--target esmini-assets-devel \
		--tag ${IMAGE_NAME}:${VERSION}-devel \
	${CONTAINER_BUILD_CONTEXT}