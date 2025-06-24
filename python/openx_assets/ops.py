import bpy

from bpy.props import BoolProperty

from jsonschema import validate
from . import xom3d_utils


# Define the operator
class XOM3D_MoveAssetToOrigin(bpy.types.Operator):
    bl_idname = "xom3d.move_asset_to_origin"
    bl_label = "Move Asset to Origin"
    bl_description = "Moves asset so its bounding box is centered at origin"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        xom3d_utils.move_asset_to_origin()
        self.report({"INFO"}, "Asset moved to origin")
        return {"FINISHED"}


class XOM3D_ValidateAssetFile(bpy.types.Operator):
    bl_idname = "xom3d.validate_asset_file"
    bl_label = "Validate Asset File"
    bl_description = "Validates the asset file for partial OpenMATERIAL 3D compliance"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene

        asset_data = getattr(scene, "xom3d", None)

        # Placeholder for validation logic
        self.report({"INFO"}, "Asset file validation is not implemented yet")
        return {"FINISHED"}


def register():
    """Register the module."""
    bpy.utils.register_class(XOM3D_MoveAssetToOrigin)


def unregister():
    """Unregister the module."""
    bpy.utils.unregister_class(XOM3D_MoveAssetToOrigin)
