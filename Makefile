# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

PROJECT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

all: generic-package

generic-package:
	@mkdir -p /tmp/esmini-assets/models
	@mkdir -p /tmp/esmini-assets/vehicles
	@mkdir -p /tmp/esmini-assets/models/generic
	#
	$(MAKE) -C src generic-vans 
	@cp -r ${PROJECT_DIR}/src/generic-vans/osgb/* /tmp/esmini-assets/models/generic/
	# 
	@cp -r vehicles/generic.xosc /tmp/esmini-assets/vehicles/
	@cd /tmp/esmini-assets && zip -r $(PROJECT_DIR)/esmini-assets.zip .
	@rm -rf /tmp/esmini-assets

.PHONY: all generic-package