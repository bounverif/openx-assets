import bpy

from . import xom3d_utils


# Define the operator
class OBJECT_OT_MoveAssetToOrigin(bpy.types.Operator):
    bl_idname = "object.move_asset_to_origin"
    bl_label = "Move Asset to Origin"
    bl_description = "Moves asset so its bounding box is centered at origin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        xom3d_utils.move_asset_to_origin()
        self.report({"INFO"}, "Asset moved to origin")
        return {"FINISHED"}


def register():
    """Register the module."""
    bpy.utils.register_class(OBJECT_OT_MoveAssetToOrigin)


def unregister():
    """Unregister the module."""
    bpy.utils.unregister_class(OBJECT_OT_MoveAssetToOrigin)
