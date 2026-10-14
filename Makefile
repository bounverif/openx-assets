# SPDX-FileCopyrightText: 2024 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTION ?= src/vehicles
BUILDDIR ?= $(PROJECT_DIR)/build
OPENX_ASSETS_VERSION ?= $(shell date +'%Y.%-m.%-d')

# Every collection exports once into STAGEDIR; each bundle picks its files from there.
STAGEDIR := $(BUILDDIR)/stage
BUNDLES := glb fbx esmini usdz catalog
ZIPS := $(foreach b,$(BUNDLES),openx-assets-$(b).zip)

# Formats to export; a single bundle needs fewer (e.g. EXPORT_FLAGS="--glb --xoma").
EXPORT_FLAGS ?= --glb --fbx --usdz --xoma


all: bundle

install:
	@echo "Installing OpenX Assets Python Package"
	pip install -e .

# Export EXPORT_FLAGS formats for every .blend in the collection.
assets:
	@echo "Exporting OpenX assets..."
	@mkdir -p $(STAGEDIR)/vehicles
	openx-assets export $(COLLECTION) \
		--destdir $(STAGEDIR)/vehicles \
		--no-glb \
		$(EXPORT_FLAGS) \
		--asset-version $(OPENX_ASSETS_VERSION)

# Convert the exported FBX files to OSGB (FBX is Y-up, OpenX assets are Z-up).
assets-osgb: assets
	@echo "Converting OpenX FBX assets to OSGB format..."
	@find "$(STAGEDIR)/vehicles" -type f -name "*.fbx" | while IFS= read -r fbx_path; do \
		osgb_path="$${fbx_path%.fbx}.osgb"; \
		echo "Converting '$${fbx_path}' to '$${osgb_path}'"; \
		osgconv "$${fbx_path}" "$${osgb_path}" -o 120-0.5773503,-0.5773503,-0.5773503 --use-world-frame \
			|| echo "Error converting '$${fbx_path}'. Skipping..."; \
	done

# Copy files matching $(2) from $(STAGEDIR)/vehicles into the $(1) bundle's vehicles, one directory per model.
define copy-models
	@mkdir -p $(BUILDDIR)/$(1)/vehicles
	cd $(STAGEDIR)/vehicles && find . -type f $(2) -exec cp --parents {} $(BUILDDIR)/$(1)/vehicles \;
	cp $(PROJECT_DIR)/src/REUSE.toml $(BUILDDIR)/$(1)/REUSE.toml
endef

# REUSE annotation for the generated catalogs and the vehicle specifications.
define CATALOG_REUSE

[[annotations]]
path = ["catalogs/**", "xom3d/**"]
SPDX-FileCopyrightText = ["2024 Dogan Ulus <dogan.ulus@bogazici.edu.tr>"]
SPDX-License-Identifier = "MPL-2.0"
endef
export CATALOG_REUSE

# glTF models with their OpenMATERIAL 3D metadata.
bundle-glb: assets
	@echo "Bundling GLB assets..."
	@rm -rf $(BUILDDIR)/glb
	$(call copy-models,glb,\( -name "*.glb" -o -name "*.xoma" \))

# OpenSceneGraph models for esmini, all in one directory, with a catalog that references them.
bundle-esmini: assets-osgb
	@echo "Bundling esmini assets..."
	@rm -rf $(BUILDDIR)/esmini
	@mkdir -p $(BUILDDIR)/esmini/vehicles
	find $(STAGEDIR)/vehicles -type f -name "*.osgb" -exec cp {} $(BUILDDIR)/esmini/vehicles \;
	openx-assets catalog $(STAGEDIR)/vehicles \
		--name "vehicles" \
		--model3d-ext "osgb" \
		--model3d-flat \
		--destdir $(BUILDDIR)/esmini/catalogs \
		--asset-version $(OPENX_ASSETS_VERSION)
	sed -E 's|"vehicles/([^"/]+)/\*\*"|"vehicles/\1.osgb"|g' $(PROJECT_DIR)/src/REUSE.toml > $(BUILDDIR)/esmini/REUSE.toml
	echo "$$CATALOG_REUSE" >> $(BUILDDIR)/esmini/REUSE.toml

# FBX models with their OpenMATERIAL 3D metadata.
bundle-fbx: assets
	@echo "Bundling FBX assets..."
	@rm -rf $(BUILDDIR)/fbx
	$(call copy-models,fbx,\( -name "*.fbx" -o -name "*.xoma" \))

# OpenUSD models with their OpenMATERIAL 3D metadata.
bundle-usdz: assets
	@echo "Bundling USDZ assets..."
	@rm -rf $(BUILDDIR)/usdz
	$(call copy-models,usdz,\( -name "*.usdz" -o -name "*.xoma" \))

# Real-world vehicle specifications and their OpenSCENARIO catalogs.
bundle-catalog:
	@echo "Bundling XOM3D vehicle specifications..."
	@rm -rf $(BUILDDIR)/catalog
	@mkdir -p $(BUILDDIR)/catalog/xom3d $(BUILDDIR)/catalog/catalogs
	cp -r $(PROJECT_DIR)/xom3d/vehicles $(BUILDDIR)/catalog/xom3d/
	for dir in $(wildcard $(PROJECT_DIR)/xom3d/vehicles/*); do \
		openx-assets catalog $$dir \
			--name "$$(basename $$dir)" \
			--destdir $(BUILDDIR)/catalog/catalogs \
			--asset-version $(OPENX_ASSETS_VERSION) || exit 1; \
	done
	echo "version = 1$$CATALOG_REUSE" > $(BUILDDIR)/catalog/REUSE.toml

$(ZIPS): openx-assets-%.zip: bundle-%
	@echo "Zipping $* bundle..."
	cp $(PROJECT_DIR)/src/README.md $(BUILDDIR)/$*/README.md
	@mkdir -p $(BUILDDIR)/$*/LICENSES
	for f in $(PROJECT_DIR)/LICENSES/*.txt; do \
		grep -q "$$(basename $$f .txt)" $(BUILDDIR)/$*/REUSE.toml && cp $$f $(BUILDDIR)/$*/LICENSES/ || true; \
	done
	@rm -f $(PROJECT_DIR)/$@
	cd $(BUILDDIR)/$* && zip -qr $(PROJECT_DIR)/$@ .

bundle: $(ZIPS)

clean:
	@echo "Cleaning OpenX assets..."
	rm -rf $(BUILDDIR)

purge: clean
	rm -f $(PROJECT_DIR)/openx-assets*.zip

.PHONY: all install assets assets-osgb $(addprefix bundle-,$(BUNDLES)) bundle clean purge $(ZIPS)
