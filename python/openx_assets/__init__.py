# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if "bpy" in locals():
    import importlib

    importlib.reload(ops)
    importlib.reload(props)
    importlib.reload(xom3d_utils)
    importlib.reload(xom3d_vehicle_structure)
    importlib.reload(ui_vehicle_menu)
    importlib.reload(ui_vehicle_info_panel)

else:
    from . import ops
    from . import props
    from . import xom3d_utils
    from . import xom3d_vehicle_structure
    from . import ui_vehicle_menu
    from . import ui_vehicle_info_panel

import bpy


def register():
    ops.register()
    props.register()
    ui_vehicle_menu.register()
    ui_vehicle_info_panel.register()


def unregister():
    ui_vehicle_info_panel.unregister()
    ui_vehicle_menu.unregister()
    props.unregister()
    ops.unregister()


if __name__ == "__main__":
    register()
