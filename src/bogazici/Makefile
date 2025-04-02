# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0
#
COLLECTION_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

LICENSE_COPYRIGHT1 := "\# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>"
LICENSE_COPYRIGHT2 := "\# SPDX-FileCopyrightText: 2019 razor24 <https://sketchfab.com/razor24>"
LICENSE_IDENTIFIER := "\# SPDX-License-""Identifier: MPL-2.0 "

license:
	@echo "Adding license files for osgb models"
	@for osgb_model in ${COLLECTION_DIR}/osgb/*.osgb; do \
		license_file="$${osgb_model}.license"; \
		echo $(LICENSE_COPYRIGHT1) >  "$$license_file"; \
		echo $(LICENSE_COPYRIGHT2) >> "$$license_file"; \
		echo "#" >> "$$license_file"; \
		echo $(LICENSE_IDENTIFIER) >> "$$license_file"; \
	done
