# SPDX-FileCopyrightText: 2025 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
#
# SPDX-License-Identifier: GPL-3.0-or-later

if "bpy" in locals():
    import importlib
    importlib.reload(xom3d_vehicle)
else:
    from . import xom3d_vehicle

import bpy



class OBJECT_OT_xom3d_add_empty_vehicle_structure(bpy.types.Operator):
    bl_idname = "xom3d_vehicle.add_empty_vehicle_structure"
    bl_label = "Add Empty Vehicle Structure"
    bl_description = "Add an empty ASAM OpenMATERIAL 3D vehicle structure"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        xom3d_vehicle.add_empty_vehicle_structure()
        return {'FINISHED'}
    
class OBJECT_OT_xom3d_trim_vehicle_structure(bpy.types.Operator):
    bl_idname = "xom3d_vehicle.trim_vehicle_structure"
    bl_label = "Trim Vehicle Structure"
    bl_description = "Trim ASAM OpenMATERIAL 3D vehicle structure"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        xom3d_vehicle.trim_vehicle_structure()
        return {'FINISHED'}

# Define the dropdown submenu
class VIEW3D_MT_object_openx_submenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_object_openx_submenu"
    bl_label = "OpenX Assets"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_xom3d_add_empty_vehicle_structure.bl_idname, icon='EMPTY_AXIS')
        layout.operator(OBJECT_OT_xom3d_trim_vehicle_structure.bl_idname, icon='EMPTY_AXIS')
        # Add more operators here if needed

# Add the dropdown menu to the Object menu
def draw_object_menu_openx(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(VIEW3D_MT_object_openx_submenu.bl_idname, icon='AUTO')

# Registration
classes = (
    OBJECT_OT_xom3d_add_empty_vehicle_structure,
    OBJECT_OT_xom3d_trim_vehicle_structure,
    VIEW3D_MT_object_openx_submenu,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(draw_object_menu_openx)

def unregister():
    bpy.types.VIEW3D_MT_object.remove(draw_object_menu_openx)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()