# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTIONS ?= bogazici generic

OPENX_ASSETS_COLLECTIONS := bogazici
OPENX_ASSETS_VANILLA_COLLECTIONS := audi fiat ford tesla toyota volkswagen volvo

BLENDER_USER_RESOURCES := $(shell blender --background --factory-startup --python-expr "import bpy; print(bpy.utils.resource_path('USER'))" | head -n 1)

esmini-assets:
	rm -rf /tmp/esmini-assets
	@mkdir -p /tmp/esmini-assets/models
	@mkdir -p /tmp/esmini-assets/vehicles
	@for collection in $(COLLECTIONS); do \
		echo "Processing $$collection"; \
		$(MAKE) $$collection; \
	done
	@cd /tmp/esmini-assets && zip -r $(PROJECT_DIR)/esmini-assets.zip .

bogazici:
	@mkdir -p /tmp/esmini-assets/models/bogazici/
	@mkdir -p ${PROJECT_DIR}/assets/models/bogazici/
	#
	$(MAKE) -C src bogazici
	@cp -r ${PROJECT_DIR}/src/bogazici/osgb/* ${PROJECT_DIR}/assets/models/bogazici/
	@cp -r ${PROJECT_DIR}/assets/models/bogazici/* /tmp/esmini-assets/models/bogazici/
	@cp -r ${PROJECT_DIR}/assets/vehicles/bogazici.xosc /tmp/esmini-assets/vehicles/
	rm -rf ${PROJECT_DIR}/src/bogazici/fbx
	rm -rf ${PROJECT_DIR}/src/bogazici/osgb

generic:
	@mkdir -p /tmp/esmini-assets/models/generic
	@mkdir -p ${PROJECT_DIR}/assets/models/generic/
	#
	$(MAKE) -C src generic
	@cp -r ${PROJECT_DIR}/src/generic/osgb/* ${PROJECT_DIR}/assets/models/generic/
	@cp -r ${PROJECT_DIR}/assets/models/generic/* /tmp/esmini-assets/models/generic/
	@cp -r ${PROJECT_DIR}/assets/vehicles/generic.xosc /tmp/esmini-assets/vehicles/
	rm -rf ${PROJECT_DIR}/src/generic/fbx
	rm -rf ${PROJECT_DIR}/src/generic/osgb

openx-assets:
	rm -rf /tmp/openx-assets
	mkdir -p /tmp/openx-assets/vanilla
	@for collection in $(OPENX_ASSETS_VANILLA_COLLECTIONS); do \
		echo "Processing $$collection"; \
		cp -r ${PROJECT_DIR}/collections/$$collection/*.xoma /tmp/openx-assets/vanilla/ || true; \
	done
	@for collection in $(OPENX_ASSETS_COLLECTIONS); do \
		echo "Processing $$collection"; \
		mkdir -p /tmp/openx-assets/$$collection; \
		$(MAKE) xom-$$collection; \
		cp -r ${PROJECT_DIR}/collections/$$collection/*/*.xoma /tmp/openx-assets/$$collection/ || true; \
		cp -r ${PROJECT_DIR}/collections/$$collection/*/*.glb /tmp/openx-assets/$$collection/ || true; \
		# cp -r ${PROJECT_DIR}/collections/$$collection/*/*.gltf /tmp/openx-assets/$$collection/ || true; \
		# cp -r ${PROJECT_DIR}/collections/$$collection/*/*.bin /tmp/openx-assets/$$collection/ || true; \
		cp -r ${PROJECT_DIR}/collections/$$collection/*/*.fbx /tmp/openx-assets/$$collection/ || true; \
		cp -r ${PROJECT_DIR}/collections/$$collection/*/*.osgb /tmp/openx-assets/$$collection/ || true; \
	done
	@cd /tmp/openx-assets && zip -r "$(PROJECT_DIR)/openx-assets.zip" .

xom-bogazici:
	@for asset in m1_mini_countryman_2016 m1_audi_q7_2015; do \
		echo "Processing $$asset"; \
		blender --background \
			collections/bogazici/$$asset/$$asset.blend \
			--python scripts/blender-export-xom.py \
			-- \
			--xoma-template collections/bogazici/collection.xoma.json \
			--export-fbx \
			--export-gltf \
			--export-glb;\
		osgconv -o 90-1,0,0 \
			collections/bogazici/$$asset/$$asset.fbx \
			collections/bogazici/$$asset/$$asset.osgb; \
		osgconv -o -90-0,0,1 \
			collections/bogazici/$$asset/$$asset.osgb \
			collections/bogazici/$$asset/$$asset.osgb; \
	done


xom-generic:
	@echo "Processing generic"

blender:
	mkdir -p ${BLENDER_USER_RESOURCES}/extensions/user_default
	ln -s ${PROJECT_DIR}/python/openx_assets ${BLENDER_USER_RESOURCES}/extensions/user_default/

.PHONY: all generic-package
