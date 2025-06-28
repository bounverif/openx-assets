# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
#
# SPDX-License-Identifier: GPL-3.0-or-later


def reload_package(module_dict_main):
    import importlib
    from pathlib import Path

    def reload_package_recursive(current_dir, module_dict):
        for path in current_dir.iterdir():
            if "__init__" in str(path) or path.stem not in module_dict:
                continue

            if path.is_file() and path.suffix == ".py":
                importlib.reload(module_dict[path.stem])
            elif path.is_dir():
                reload_package_recursive(path, module_dict[path.stem].__dict__)

    reload_package_recursive(Path(__file__).parent, module_dict_main)


if "bpy" in locals():
    reload_package(locals())

from . import ops
from . import ui_preferences
from . import ui_vehicle_menu
from . import ui_vehicle_info_panel

import bpy

from dataclasses import dataclass
from typing import Optional, Dict, Tuple

from . import xom3d_utils


@dataclass
class XOM3D_Context:
    asset_schema: Optional[Dict] = None
    asset: Optional[Dict] = None
    material_schema: Optional[Dict] = None
    materials: Optional[Dict] = None


def register():

    if not hasattr(bpy.types.Scene, "xom3d_context"):
        bpy.types.Scene.xom3d_context = XOM3D_Context()

    ops.register()
    ui_preferences.register()
    ui_vehicle_menu.register()
    ui_vehicle_info_panel.register()


def unregister():
    ui_vehicle_info_panel.unregister()
    ui_vehicle_menu.unregister()
    ui_preferences.unregister()
    ops.unregister()

    if hasattr(bpy.types.Scene, "xom3d_context"):
        del bpy.types.Scene.xom3d_context


if __name__ == "__main__":
    register()
