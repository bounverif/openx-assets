#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
# SPDX-License-Identifier: MPL-2.0

import bpy
import sys
import os

EXPORT_PATH = os.path.join(sys.argv[-1], "")

bpy.ops.export_scene.fbx(
    filepath=EXPORT_PATH,
    batch_mode="COLLECTION",
    use_batch_own_dir=False,
    apply_scale_options="FBX_SCALE_ALL",
    axis_forward="-X",  # -X
    axis_up="Z",  #  Z
)
