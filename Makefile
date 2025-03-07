# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTIONS ?= bogazici generic-vans

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
	@cp -r ${PROJECT_DIR}/assets/models/bogazici/ /tmp/esmini-assets/models/bogazici/
	@cp -r ${PROJECT_DIR}/assets/vehicles/bogazici.xosc /tmp/esmini-assets/vehicles/
	rm -rf ${PROJECT_DIR}/src/bogazici/fbx
	rm -rf ${PROJECT_DIR}/src/bogazici/osgb

generic-vans:
	@mkdir -p /tmp/esmini-assets/models/generic
	@mkdir -p ${PROJECT_DIR}/assets/models/generic/
	#
	$(MAKE) -C src generic-vans 
	@cp -r ${PROJECT_DIR}/src/generic-vans/osgb/* ${PROJECT_DIR}/assets/models/generic/
	@cp -r ${PROJECT_DIR}/assets/models/generic/ /tmp/esmini-assets/models/generic/
	@cp -r ${PROJECT_DIR}/assets/vehicles/generic.xosc /tmp/esmini-assets/vehicles/
	rm -rf ${PROJECT_DIR}/src/generic-vans/fbx
	rm -rf ${PROJECT_DIR}/src/generic-vans/osgb

.PHONY: all generic-package