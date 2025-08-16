# SPDX-FileCopyrightText: 2024 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTION ?= src/vehicles/main
DESTDIR ?= /tmp/openx-assets
OPENX_ASSETS_VERSION ?= $(shell date +'%Y.%-m.%-d')


all: purge assets osgb catalogs

install:
	@echo "Installing OpenX Assets Python Package"
	pip install -e .

assets:
	@echo "Bundling OpenX assets..."
	@mkdir -p $(DESTDIR)/model3d
	openx-assets export $(COLLECTION) \
		--destdir $(DESTDIR)/model3d \
		--glb \
		--fbx \
		--asset-version $(OPENX_ASSETS_VERSION)

assets-catalog:
	@echo "Bundling OpenX asset catalogs..."
	@mkdir -p $(DESTDIR)/catalogs
	openx-assets catalog $(COLLECTION) \
		--name "openx_assets_3d" \
		--model3d-ext "osgb" \
		--destdir $(DESTDIR)/catalogs \
		--asset-version $(OPENX_ASSETS_VERSION)

osgb:
	@echo "Converting OpenX FBX assets to OSGB format..."
	@find "$(DESTDIR)" -type f -name "*.fbx" | while IFS= read -r fbx_path; do \
		rel_path="$${fbx_path#$(DESTDIR)/}"; \
		output_path="$(DESTDIR)/$${rel_path%.fbx}.osgb"; \
		mkdir -p "$$(dirname "$${output_path}")"; \
		echo "Converting '$${fbx_path}' to '$${output_path}'"; \
		osgconv "$${fbx_path}" "$${output_path}" -o 90-1,0,0; \
		osgconv "$${output_path}" "$${output_path}" -o -90-0,0,1; \
		if [ $$? -ne 0 ]; then \
			echo "Error converting '$${fbx_path}'. Skipping..."; \
		fi; \
	done

db-catalog:
	@echo "Generating OpenX asset catalogs..."
	@mkdir -p "$(DESTDIR)/catalogs"
	for dir in $(wildcard $(PROJECT_DIR)/xom3d/vehicles/*); do \
		name=$$(basename $$dir); \
		openx-assets catalog $$dir \
			--name "$$name" \
			--destdir $(DESTDIR)/catalogs \
			--asset-version $(OPENX_ASSETS_VERSION); \
	done
	@mkdir -p "$(DESTDIR)/xom3d/vehicles"
	cp -r $(PROJECT_DIR)/xom3d/vehicles/* "$(DESTDIR)/xom3d/vehicles"


bundle: purge assets osgb assets-catalog db-catalog clean
	@echo "Bundling OpenX assets into a single archive..."
	@cd $(DESTDIR) && zip -r $(PROJECT_DIR)/openx-assets.zip .

clean:
	@echo "Cleaning OpenX assets..."
	rm -rf $(DESTDIR)
	find src -type f -name "*.fbx" -delete
	find src -type f -name "*.glb" -delete
	find src -type f -name "*.bin" -delete
	find src -type f -name "*.gltf" -delete
	find src -type f -name "*.osgb" -delete
	find src -type f -name "*.osgt" -delete
	find src -type f -name "*.png" -delete
	find src -type f -name "*.jpg" -delete
	find src -type f -name "*.jpeg" -delete

purge: clean
	find $(PROJECT_DIR) -maxdepth 1 -name "openx-assets.zip" -delete

.PHONY: install assets catalogs osgb bundle all
