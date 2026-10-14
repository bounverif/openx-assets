# SPDX-FileCopyrightText: 2024 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTION ?= src/vehicles
DESTDIR ?= /tmp/openx-assets
OPENX_ASSETS_VERSION ?= $(shell date +'%Y.%-m.%-d')

# Every collection exports once into STAGEDIR; each bundle picks its files from there.
STAGEDIR := $(BUILDDIR)/stage
BUNDLES := glb fbx esmini usdz catalog
ZIPS := $(foreach b,$(BUNDLES),openx-assets-$(b).zip)

all: purge assets assets-osgb model3d-catalog xosc-catalog xom3d-catalog

install:
	@echo "Installing OpenX Assets Python Package"
	pip install -e .

# Export EXPORT_FLAGS formats for every .blend in the collection.
assets:
	@echo "Exporting OpenX assets..."
	@mkdir -p $(STAGEDIR)/vehicles
	openx-assets export $(COLLECTION) \
		--destdir $(DESTDIR)/model3d \
		--glb \
		--fbx \
		--asset-version $(OPENX_ASSETS_VERSION)

assets-fbx-only:
	@echo "Bundling OpenX assets..."
	@mkdir -p $(DESTDIR)/model3d
	openx-assets export $(COLLECTION) \
		--destdir $(DESTDIR)/model3d \
		--fbx \
		--no-glb \
		--no-xoma \
		--asset-version $(OPENX_ASSETS_VERSION)

assets-osgb:
	@echo "Converting OpenX FBX assets to OSGB format..."
	@find "$(STAGEDIR)/vehicles" -type f -name "*.fbx" | while IFS= read -r fbx_path; do \
		osgb_path="$${fbx_path%.fbx}.osgb"; \
		echo "Converting '$${fbx_path}' to '$${osgb_path}'"; \
		osgconv "$${fbx_path}" "$${osgb_path}" -o 120-0.5773503,-0.5773503,-0.5773503 --use-world-frame \
			|| echo "Error converting '$${fbx_path}'. Skipping..."; \
	done

model3d-catalog:
	@echo "Bundling OpenX asset catalogs..."
	@mkdir -p $(DESTDIR)/catalogs
	openx-assets catalog $(COLLECTION) \
		--name "model3d" \
		--model3d-ext "osgb" \
		--destdir $(DESTDIR)/catalogs \
		--asset-version $(OPENX_ASSETS_VERSION)

xosc-catalog:
	@echo "Generating OpenX asset catalogs..."
	@mkdir -p "$(DESTDIR)/catalogs"
	for dir in $(wildcard $(PROJECT_DIR)/xom3d/vehicles/*); do \
		openx-assets catalog $$dir \
			--name "$$name" \
			--destdir $(DESTDIR)/catalogs \
			--asset-version $(OPENX_ASSETS_VERSION); \
	done;

xom3d-catalog:
	@mkdir -p "$(DESTDIR)/xom3d/vehicles"
	@ cp -r $(PROJECT_DIR)/xom3d/vehicles/* "$(DESTDIR)/xom3d/vehicles"

bundle: purge assets assets-osgb model3d-catalog xosc-catalog xom3d-catalog clean
	@echo "Bundling OpenX assets into a single archive..."
	@cd $(DESTDIR) && zip -r $(PROJECT_DIR)/openx-assets.zip .

esmini: purge assets-fbx-only assets-osgb model3d-catalog xosc-catalog
	@echo "Bundling OpenX assets for esmini..."
	@find $(DESTDIR) -type f -name "*.fbx" -delete
	@cd $(DESTDIR) && zip -r $(PROJECT_DIR)/openx-assets-esmini.zip .

clean:
	@echo "Cleaning OpenX assets..."
	rm -rf $(BUILDDIR)

purge: clean
	find $(PROJECT_DIR) -maxdepth 1 -name "openx-assets.zip" -delete
	find $(PROJECT_DIR) -maxdepth 1 -name "openx-assets-esmini.zip" -delete
	find $(PROJECT_DIR) -maxdepth 1 -name "openx-assets-gltf.zip" -delete
	find $(PROJECT_DIR) -maxdepth 1 -name "openx-assets-openusd.zip" -delete

.PHONY: all install assets assets-fbx-only assets-osgb model3d-catalog xosc-catalog xom3d-catalog bundle esmini clean purge
