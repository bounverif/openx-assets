import bpy
import os
import json
import pathlib

from bpy.props import EnumProperty


# Called when the version changes
def xom3d_version_update(self, context):
    version = self.xom3d_version
    print("Reloading JSON schema for version:", version)

    # Construct path to JSON schema inside the add-on package
    addon_dir = pathlib.Path(__file__).parent
    schema_path = addon_dir / "schemas" / "xom3d" / f"{version}" / "asset_schema.json"

    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            bpy.context.scene.xom3d_context.asset_schema = json.load(f)
            print("Schema loaded successfully")
            # Store or process schema here (e.g., caching, validation, etc.)
    except FileNotFoundError:
        print(f"[OpenXAssets] Schema file not found: {schema_path}")
    except json.JSONDecodeError as e:
        print(f"[OpenXAssets] Failed to parse JSON: {e}")


class OpenXAssetsPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    supported_xom3d_versions = [
        ("1.0.0", "Version 1.0", "ASAM OpenMATERIAL 3D Version 1.0"),
    ]

    xom3d_version: EnumProperty(
        name="Version",
        description="ASAM OpenMATERIAL 3D Version",
        items=supported_xom3d_versions,
        default="1.0.0",
        update=xom3d_version_update,
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = row.column(align=True, heading="ASAM OpenMATERIAL 3D")
        col.prop(self, "xom3d_version")


class OpenXAssetsPreferencesOperator(bpy.types.Operator):
    """Display example preferences"""

    bl_idname = "object.addon_prefs_example"
    bl_label = "Add-on Preferences Example"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences

        info = f"Current ASAM OpenMATERIAL 3D Version: {addon_prefs.xom3d_version}\n"
        self.report({"INFO"}, info)

        return {"FINISHED"}


def register():
    """Register the module."""
    bpy.utils.register_class(OpenXAssetsPreferences)


def unregister():
    """Unregister the module."""
    bpy.utils.unregister_class(OpenXAssetsPreferences)
