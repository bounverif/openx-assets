import bpy

from .xom3d_vehicle_structure import add_empty_vehicle_structure, trim_vehicle_structure


class OBJECT_OT_xom3d_add_empty_vehicle_structure(bpy.types.Operator):
    bl_idname = "xom3d_vehicle.add_empty_vehicle_structure"
    bl_label = "Add Empty Vehicle Structure"
    bl_description = "Add an empty ASAM OpenMATERIAL 3D vehicle structure"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        add_empty_vehicle_structure()
        return {"FINISHED"}


class OBJECT_OT_xom3d_trim_vehicle_structure(bpy.types.Operator):
    bl_idname = "xom3d_vehicle.trim_vehicle_structure"
    bl_label = "Trim Vehicle Structure"
    bl_description = "Trim ASAM OpenMATERIAL 3D vehicle structure"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        trim_vehicle_structure()
        return {"FINISHED"}


# Define the dropdown submenu
class VIEW3D_MT_object_openx_submenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_object_openx_submenu"
    bl_label = "OpenX Assets"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            OBJECT_OT_xom3d_add_empty_vehicle_structure.bl_idname, icon="EMPTY_AXIS"
        )
        layout.operator(
            OBJECT_OT_xom3d_trim_vehicle_structure.bl_idname, icon="EMPTY_AXIS"
        )
        # Add more operators here if needed


# Add the dropdown menu to the Object menu
def draw_object_menu_openx(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(VIEW3D_MT_object_openx_submenu.bl_idname, icon="AUTO")


def register():
    """Register the module."""

    bpy.utils.register_class(OBJECT_OT_xom3d_add_empty_vehicle_structure)
    bpy.utils.register_class(OBJECT_OT_xom3d_trim_vehicle_structure)
    bpy.utils.register_class(VIEW3D_MT_object_openx_submenu)

    bpy.types.VIEW3D_MT_object.append(draw_object_menu_openx)


def unregister():
    """Unregister the module."""
    bpy.types.VIEW3D_MT_object.remove(draw_object_menu_openx)

    bpy.utils.unregister_class(VIEW3D_MT_object_openx_submenu)
    bpy.utils.unregister_class(OBJECT_OT_xom3d_trim_vehicle_structure)
    bpy.utils.unregister_class(OBJECT_OT_xom3d_add_empty_vehicle_structure)
