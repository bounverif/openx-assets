# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTIONS ?= bogazici generic

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
	@for collection in $(COLLECTIONS); do \
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
	blender --background \
		collections/bogazici/m1_mini_countryman_2016/m1_mini_countryman_2016.blend \
		--python scripts/blender-export-xom.py \
		-- \
		--xoma-template collections/bogazici/collection.xoma.json \
		--export-fbx \
		--export-gltf \
		--export-glb
	osgconv -o 90-1,0,0 \
		collections/bogazici/m1_mini_countryman_2016/m1_mini_countryman_2016.fbx \
		collections/bogazici/m1_mini_countryman_2016/m1_mini_countryman_2016.osgb 
	osgconv -o -90-0,0,1 \
		collections/bogazici/m1_mini_countryman_2016/m1_mini_countryman_2016.osgb \
		collections/bogazici/m1_mini_countryman_2016/m1_mini_countryman_2016.osgb 

xom-generic:
	@echo "Processing generic"

.PHONY: all generic-package