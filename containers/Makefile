IMAGE_NAME ?= localhost/openx-assets
VERSION ?= latest
CONTAINER_BUILD_CONTEXT ?= .

builder:
	buildah build \
		-f openx-assets-devel/Dockerfile \
		--build-arg IMAGE_NAME=${IMAGE_NAME} \
		--build-arg VERSION=${VERSION} \
		--format oci \
		--layers=true \
		--target openx-assets-builder \
		--tag ${IMAGE_NAME}:${VERSION}-builder \
	${CONTAINER_BUILD_CONTEXT}

devel:
	buildah build \
		-f openx-assets-devel/Dockerfile \
		--build-arg IMAGE_NAME=${IMAGE_NAME} \
		--build-arg VERSION=${VERSION} \
		--format oci \
		--layers=true \
		--target openx-assets-devel \
		--tag ${IMAGE_NAME}:${VERSION}-devel \
	${CONTAINER_BUILD_CONTEXT}
