IMAGE_NAME ?= localhost/openx-assets
OPENX_ASSETS_VERSION ?= latest
OPENX_ASSETS_CURRENT_VERSION = $(if $(filter latest,$(OPENX_ASSETS_VERSION)),$(shell curl -s https://api.github.com/repos/vevalabs/openx-assets/releases/latest | jq -r .tag_name),$(OPENX_ASSETS_VERSION))
CONTAINER_BUILD_CONTEXT ?= .

builder:
	buildah build \
		-f openx-assets-devel/Dockerfile \
		--build-arg IMAGE_NAME=${IMAGE_NAME} \
		--build-arg VERSION=${OPENX_ASSETS_VERSION} \
		--format oci \
		--layers=true \
		--target openx-assets-builder \
		--tag ${IMAGE_NAME}:${OPENX_ASSETS_VERSION}-builder \
	${CONTAINER_BUILD_CONTEXT}

devel:
	buildah build \
		-f openx-assets-devel/Dockerfile \
		--build-arg IMAGE_NAME=${IMAGE_NAME} \
		--build-arg VERSION=${OPENX_ASSETS_VERSION} \
		--format oci \
		--layers=true \
		--target openx-assets-devel \
		--tag ${IMAGE_NAME}:${OPENX_ASSETS_VERSION}-devel \
	${CONTAINER_BUILD_CONTEXT}

esmini:
	buildah build \
		-f openx-assets/Dockerfile \
		--build-arg IMAGE_NAME=${IMAGE_NAME} \
		--build-arg VERSION=${OPENX_ASSETS_VERSION} \
		--format oci \
		--layers=true \
		--target openx-assets-esmini \
		--tag ${IMAGE_NAME}:${OPENX_ASSETS_VERSION}-esmini \
		--tag ${IMAGE_NAME}:${OPENX_ASSETS_CURRENT_VERSION}-esmini \
	${CONTAINER_BUILD_CONTEXT}
