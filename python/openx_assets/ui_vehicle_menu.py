import bpy

from .xom3d_vehicle_structure import (
    add_empty_vehicle_structure,
    trim_vehicle_structure,
)

from .xom3d_utils import move_empty_parent_to_child

addon_keymaps = []


class XOM3D_OT_add_empty_vehicle_structure(bpy.types.Operator):
    bl_idname = "xom3d.add_empty_vehicle_structure"
    bl_label = "Add Empty Vehicle Structure"
    bl_description = "Add an empty ASAM OpenMATERIAL 3D vehicle structure"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        add_empty_vehicle_structure()
        return {"FINISHED"}


class XOM3D_OT_trim_vehicle_structure(bpy.types.Operator):
    bl_idname = "xom3d.trim_vehicle_structure"
    bl_label = "Trim Vehicle Structure"
    bl_description = "Trim ASAM OpenMATERIAL 3D vehicle structure"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        trim_vehicle_structure()
        return {"FINISHED"}


class XOM3D_OT_move_empty_parent_to_child(bpy.types.Operator):
    bl_idname = "xom3d.move_empty_parent_to_child"
    bl_label = "Move Empty Parent to Child"
    bl_description = "Move the parent empty to the child object"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        move_empty_parent_to_child()
        return {"FINISHED"}


# Define the dropdown submenu
class XOM3D_MT_object_openx_submenu(bpy.types.Menu):
    bl_idname = "XOM3D_MT_object_openx_submenu"
    bl_label = "OpenX Assets"

    def draw(self, context):
        layout = self.layout
        layout.operator(
            XOM3D_OT_add_empty_vehicle_structure.bl_idname, icon="EMPTY_AXIS"
        )
        layout.operator(
            XOM3D_OT_move_empty_parent_to_child.bl_idname, icon="EMPTY_AXIS"
        )
        layout.operator(XOM3D_OT_trim_vehicle_structure.bl_idname, icon="EMPTY_AXIS")
        # Add more operators here if needed


# Add the dropdown menu to the Object menu
def draw_object_menu_openx(self, context):
    layout = self.layout
    layout.separator()
    layout.menu(XOM3D_MT_object_openx_submenu.bl_idname, icon="AUTO")


def register():
    """Register the module."""

    bpy.utils.register_class(XOM3D_OT_add_empty_vehicle_structure)
    bpy.utils.register_class(XOM3D_OT_trim_vehicle_structure)
    bpy.utils.register_class(XOM3D_OT_move_empty_parent_to_child)
    bpy.utils.register_class(XOM3D_MT_object_openx_submenu)

    bpy.types.VIEW3D_MT_object.append(draw_object_menu_openx)

    # Register the hotkey
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            idname="wm.call_menu", type="X", value="PRESS", alt=True
        )
        kmi.properties.name = XOM3D_MT_object_openx_submenu.bl_idname
        addon_keymaps.append((km, kmi))


def unregister():
    """Unregister the module."""

    # Remove shortcut
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_object.remove(draw_object_menu_openx)

    bpy.utils.unregister_class(XOM3D_MT_object_openx_submenu)
    bpy.utils.unregister_class(XOM3D_OT_move_empty_parent_to_child)
    bpy.utils.unregister_class(XOM3D_OT_trim_vehicle_structure)
    bpy.utils.unregister_class(XOM3D_OT_add_empty_vehicle_structure)
