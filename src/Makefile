# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0
#
# This script is used to build the generic model collection from FBX files
#
# Use the following Blender FBX Export settings:
#
# Batch Mode: Collection (unset Batch Own Dir option)
# Transform:
#   Apply Scalings:  FBX All
#   Forward:        -X Forward
#   Up:              Z Up
#
# It is assumed that the FBX files are in the same directory as this script

PROJECT_SOURCE_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COLLECTION_DIR := ${PROJECT_SOURCE_DIR}/${COLLECTION}

# Determine which the Blender executable to use
# Use the flatpak version of Blender if the native executable is not installed
BLENDER_EXE := $(shell \
    if command -v flatpak >/dev/null 2>&1 && flatpak list --app | grep -q org.blender.Blender; then \
        echo "flatpak run org.blender.Blender"; \
    elif command -v blender >/dev/null 2>&1; then \
        echo "blender"; \
    elif command -v blender-headless >/dev/null 2>&1; then \
        echo "blender-headless"; \
    else \
        echo ""; \
    fi)

ifeq ($(BLENDER_EXE),)
    $(error No Blender executable found. Please install Blender, Blender headless, or the Blender Flatpak package.)
endif

all: blender-export-fbx osgconv-build-osgb license

blender-export-fbx:
	@echo "Using ${BLENDER_EXE} executable"
	mkdir -p ${COLLECTION_DIR}/fbx
	${BLENDER_EXE} ${COLLECTION_DIR}/${COLLECTION}.blend --background --python ${PROJECT_SOURCE_DIR}/blender-export-fbx.py -- ${COLLECTION_DIR}/fbx

osgconv-build-osgb:
	@echo "Building osgb files from FBX files"
	mkdir -p ${COLLECTION_DIR}/osgb
	@for fbx_model in ${COLLECTION_DIR}/fbx/*.fbx; do \
		echo "Processing $(shell basename $$fbx_model)"; \
		osgconv "$$fbx_model" "${COLLECTION_DIR}/osgb/$$(basename $${fbx_model%.fbx}.osgb)" -o 90-1,0,0; \
	done

bogazici:
	$(MAKE) COLLECTION=bogazici all

generic:
	$(MAKE) COLLECTION=generic all

license:
	$(MAKE) -C ${COLLECTION_DIR} license

.PHONY: all blender-export-fbx osgconv-build-osgb license bogazici generic
