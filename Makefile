# SPDX-FileCopyrightText: 2024 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTION ?= collections/main
DESTDIR ?= /tmp/openx-assets
OPENX_ASSETS_VERSION ?= $(shell date +'%Y.%-m.%-d')


all: purge assets osgb catalogs

install:
	@echo "Installing OpenX Assets Python Package"
	pip install .

assets:
	@echo "Bundling OpenX assets..."
	@mkdir -p $(DESTDIR)/assets
	openx-assets export $(COLLECTION) \
		--destdir $(DESTDIR)/assets \
		--glb \
		--gltf \
		--fbx \
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

catalogs:
	@echo "Generating OpenX asset catalogs..."
	@mkdir -p "$(DESTDIR)/catalogs"
	cp -r $(PROJECT_DIR)/catalogs/* "$(DESTDIR)/catalogs/"

bundle: purge assets osgb catalogs clean
	@echo "Bundling OpenX assets into a single archive..."
	@cd $(DESTDIR) && zip -r $(PROJECT_DIR)/openx-assets.zip .

clean:
	@echo "Cleaning OpenX assets..."
	rm -rf /tmp/openx-assets
	find collections -type f -name "*.fbx" -delete
	find collections -type f -name "*.glb" -delete
	find collections -type f -name "*.bin" -delete
	find collections -type f -name "*.gltf" -delete
	find collections -type f -name "*.osgb" -delete
	find collections -type f -name "*.osgt" -delete

purge: clean
	find $(PROJECT_DIR) -maxdepth 1 -name "openx-assets.zip" -delete

.PHONY: install assets catalogs osgb bundle all
