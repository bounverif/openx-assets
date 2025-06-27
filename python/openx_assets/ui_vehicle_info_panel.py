import bpy
import math
import json
import os
import pathlib

from . import xom3d
from . import xom3d_utils


class XOM3D_AssetBoundingBox(bpy.types.PropertyGroup):
    min: bpy.props.FloatVectorProperty(
        name="Minimum",
        description="Minimum coordinates of the bounding box",
        size=3,
        default=(0.0, 0.0, 0.0),
        unit="LENGTH",
    )
    max: bpy.props.FloatVectorProperty(
        name="Maximum",
        description="Maximum coordinates of the bounding box",
        size=3,
        default=(0.0, 0.0, 0.0),
        unit="LENGTH",
    )


class XOM3D_VehicleWheelAxle(bpy.types.PropertyGroup):
    max_steering: bpy.props.FloatProperty(
        name="Max Steering Angle",
        description="Maximum steering angle of the axle in degrees",
        default=0.0,
        unit="ROTATION",
    )
    wheel_diameter: bpy.props.FloatProperty(
        name="Wheel Diameter",
        description="Diameter of the wheel in meters",
        default=0.0,
        unit="LENGTH",
    )
    track_width: bpy.props.FloatProperty(
        name="Track Width",
        description="Distance between the wheels on the same axle in meters",
        default=0.0,
        unit="LENGTH",
    )
    position_x: bpy.props.FloatProperty(
        name="Position X",
        description="X position of the axle in meters",
        default=0.0,
        unit="LENGTH",
    )
    position_z: bpy.props.FloatProperty(
        name="Position Z",
        description="Z position of the axle in meters",
        default=0.0,
        unit="LENGTH",
    )


class XOM3D_AssetPanelData(bpy.types.PropertyGroup):

    asset_name: bpy.props.StringProperty(
        name="Asset Name",
        default="Unnamed Asset",
    )

    description: bpy.props.StringProperty(
        name="Description",
        default="No description provided",
    )

    license: bpy.props.StringProperty(
        name="License",
        default="No license information provided",
    )

    asset_type: bpy.props.EnumProperty(
        name="Asset Type",
        description="Type of the asset",
        items=[
            ("vehicle", "Vehicle", "Vehicle asset"),
            ("human", "Human", "Human asset"),
            ("environment", "Environment", "Environment asset"),
            ("scene", "Scene", "Other type of asset"),
            ("other", "Other", "Other type of asset"),
        ],
        default="other",
    )

    bounding_box_x: bpy.props.FloatVectorProperty(
        name="Bounding Box X",
        description="Bounding box of the asset in X direction",
        size=2,
    )

    bounding_box_y: bpy.props.FloatVectorProperty(
        name="Bounding Box Y",
        description="Bounding box of the asset in Y direction",
        size=2,
    )

    bounding_box_z: bpy.props.FloatVectorProperty(
        name="Bounding Box Z",
        description="Bounding box of the asset in Z direction",
        size=2,
    )

    bounding_box: bpy.props.PointerProperty(
        type=XOM3D_AssetBoundingBox,
        name="Bounding Box",
        description="Bounding box of the asset",
    )

    axles: bpy.props.CollectionProperty(
        type=XOM3D_VehicleWheelAxle,
        name="Wheel Axles",
        description="Wheel axles for the vehicle asset",
    )

    mesh_count: bpy.props.IntProperty(
        name="Mesh Count",
        description="Number of meshes in the asset",
        default=0,
    )

    triangle_count: bpy.props.IntProperty(
        name="Triangle Count",
        description="Number of triangles in the asset",
        default=0,
    )

    # Export options
    export_glb: bpy.props.BoolProperty(
        name="GLTF (Binary)",
        default=True,
        description="Export asset as GLB with default settings",
    )
    export_gltf: bpy.props.BoolProperty(
        name="GLTF (Separate)",
        default=False,
        description="Export asset as GLTF with default settings",
    )
    export_fbx: bpy.props.BoolProperty(
        name="FBX",
        default=False,
        description="Export asset as FBX with default settings",
    )


class XOM3D_OT_ExportAsset(bpy.types.Operator):
    bl_idname = "xom3d.panel_export_asset"
    bl_label = "Export Scene"
    bl_description = "Export the current scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        panel_data = context.scene.xom3d_asset_panel_data

        filepaths = []

        if panel_data.export_glb:
            filepath = xom3d_utils.export_scene_gltf(export_format="GLB")
            filepaths.append(filepath)

        if panel_data.export_gltf:
            filepath = xom3d_utils.export_scene_gltf(export_format="GLTF_SEPARATE")
            filepaths.append(filepath)

        if panel_data.export_fbx:
            filepath = xom3d_utils.export_scene_fbx()
            filepaths.append(filepath)

        if not filepaths:
            self.report({"WARNING"}, "No export format selected")
            return

        xom3d_utils.export_asset_file(asset_data=context.scene.xom3d_context.asset)

        self.report({"INFO"}, f"Exported assets")

        return {"FINISHED"}


class XOM3D_OT_ReloadAssetFile(bpy.types.Operator):
    bl_idname = "xom3d.reload_asset_file"
    bl_label = "Reload Asset File"
    bl_description = "Reload the OpenMATERIAL 3D asset file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        filepath = bpy.data.filepath
        if not filepath:
            self.report({"WARNING"}, "No .blend file is currently open")
            return {"CANCELLED"}
        xomapath = str(pathlib.Path(filepath).with_suffix(".xoma").resolve())
        if not os.path.exists(xomapath):
            self.report({"WARNING"}, f"No OpenMATERIAL 3D file found at {xomapath}")
            return {"CANCELLED"}

        return {"FINISHED"}


class XOM3D_PT_AssetPanel(bpy.types.Panel):
    bl_label = "OpenMaterial 3D Asset Info"
    bl_idname = "XOM3D_PT_AssetPanel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Asset Info"
    # bl_icon = 'AUTO'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        self.draw_asset_metadata(context)
        self.draw_bounding_box_info(context)
        self.draw_vehicle_info(context)
        self.draw_mesh_stats_info(context)
        self.draw_export_box(context)

        col = layout.column(align=True)
        col.label(text="OpenX Assets © 2025 Dogan Ulus")
        col.enabled = False
        col.alignment = "CENTER"
        col.scale_y = 0.5

    def draw_asset_metadata(self, context):
        layout = self.layout
        panel_data = context.scene.xom3d_asset_panel_data

        box = layout.box()
        col = box.column(align=True)
        col.prop(panel_data, "asset_name", text="Name", emboss=False)
        col.prop(panel_data, "description", text="Description", emboss=False)
        col.prop(panel_data, "license", text="License", emboss=False)
        col.enabled = False
        box.operator("xom3d.reload_asset_file", text="Reload Asset File")

    def draw_bounding_box_info(self, context):
        layout = self.layout
        bbox = context.scene.xom3d_asset_panel_data.bounding_box

        box = layout.box()
        row = box.row(align=True)
        split = row.split(factor=0.1, align=True)
        col0 = split.column(align=True)
        col0.alignment = "RIGHT"
        col0.label(text="X")
        col0.label(text="Y")
        col0.label(text="Z")

        sub = split.split(factor=0.5, align=True)
        # X bounds
        col_x = sub.column(align=True)
        col_x.prop(bbox, "min", index=0, text="")
        col_x.prop(bbox, "min", index=1, text="")
        col_x.prop(bbox, "min", index=2, text="")
        col_x.enabled = False

        # Y bounds
        col_y = sub.column(align=True)
        col_y.prop(bbox, "max", index=0, text="")
        col_y.prop(bbox, "max", index=1, text="")
        col_y.prop(bbox, "max", index=2, text="")
        col_y.enabled = False

        if not xom3d_utils.is_asset_centered():
            row = box.row(align=True)
            split = row.split(factor=0.1, align=True)
            split.label(text="")
            sub = split.split(factor=1, align=True)
            sub.operator("xom3d.move_asset_to_origin", text="Move Asset to Origin")

    def draw_vehicle_info(self, context):
        layout = self.layout
        panel_data = context.scene.xom3d_asset_panel_data

        if panel_data.asset_type != "vehicle":
            return

        box = layout.box()
        row = box.row(align=True)
        split = row.split(factor=0.4, align=True)
        col0 = split.column(align=True)
        col0.alignment = "RIGHT"
        col0.label(text="")
        col0.label(text="Max Steering")
        col0.label(text="Wheel Diameter")
        col0.label(text="Track Width")
        col0.label(text="Position X")
        col0.label(text="Position Z")
        col0.enabled = False

        sub = split.split(factor=0.5, align=True)
        for i, axle in enumerate(panel_data.axles):
            col = sub.column(align=True)
            col.label(
                text=(
                    "Front Axle"
                    if i == 0
                    else "Rear Axle" if i == 1 else "Additional Axle {}".format(i - 1)
                )
            )
            col.prop(axle, "max_steering", text="", emboss=False)
            col.prop(axle, "wheel_diameter", text="", emboss=False)
            col.prop(axle, "track_width", text="", emboss=False)
            col.prop(axle, "position_x", text="", emboss=False)
            col.prop(axle, "position_z", text="", emboss=False)
            col.enabled = False

    def draw_mesh_stats_info(self, context):
        layout = self.layout
        panel_data = context.scene.xom3d_asset_panel_data

        box = layout.box()
        col = box.column(align=True)
        col.prop(panel_data, "mesh_count", text="Mesh Count", emboss=False)
        col.prop(panel_data, "triangle_count", text="Triangle Count", emboss=False)
        col.enabled = False

    def draw_export_box(self, context):
        layout = self.layout
        panel_data = context.scene.xom3d_asset_panel_data

        box = layout.box()
        col = box.column(align=True, heading="Export Format")
        col.prop(panel_data, "export_glb", text="GLTF (Binary)")
        col.prop(panel_data, "export_gltf", text="GLTF (Separate)")
        col.prop(panel_data, "export_fbx", text="FBX")
        box.operator("xom3d.panel_export_asset", text="Export Asset")


@bpy.app.handlers.persistent
def update_xom3d_asset_panel(scene):
    """Update the OpenMATERIAL 3D info in the scene."""

    panel_data = bpy.context.scene.xom3d_asset_panel_data
    asset_metadata = bpy.context.scene.xom3d_context.asset["metadata"]

    # Assign metadata to panel data
    panel_data.asset_name = asset_metadata.get("name", "Unnamed Asset")
    panel_data.description = asset_metadata.get(
        "description", "No description provided."
    )

    # Assign bounding box values
    bb_data = xom3d_utils.get_bounding_box()

    panel_data.bounding_box.min[0] = bb_data["x"][0]
    panel_data.bounding_box.max[0] = bb_data["x"][1]
    panel_data.bounding_box.min[1] = bb_data["y"][0]
    panel_data.bounding_box.max[1] = bb_data["y"][1]
    panel_data.bounding_box.min[2] = bb_data["z"][0]
    panel_data.bounding_box.max[2] = bb_data["z"][1]

    if "vehicle" == panel_data.asset_type:
        front_axle_data = xom3d_utils.get_axle_info(0)
        rear_axle_data = xom3d_utils.get_axle_info(1)

        panel_data.axles[0].wheel_diameter = front_axle_data.get("wheelDiameter", 0.0)
        panel_data.axles[0].track_width = front_axle_data.get("trackWidth", 0.0)
        panel_data.axles[0].position_x = front_axle_data.get("positionX", 0.0)
        panel_data.axles[0].position_z = front_axle_data.get("positionZ", 0.0)
        panel_data.axles[1].wheel_diameter = rear_axle_data.get("wheelDiameter", 0.0)
        panel_data.axles[1].track_width = rear_axle_data.get("trackWidth", 0.0)
        panel_data.axles[1].position_x = rear_axle_data.get("positionX", 0.0)
        panel_data.axles[1].position_z = rear_axle_data.get("positionZ", 0.0)

    # Assign mesh and triangle counts
    panel_data.mesh_count = xom3d_utils.get_mesh_count()
    panel_data.triangle_count = xom3d_utils.get_triangle_count()


@bpy.app.handlers.persistent
def update_xom3d_on_load(dummy=None):
    """Load up OpenMMATERIAL files once after loading a .blend file."""

    def delayed_load():
        filepath = bpy.data.filepath
        if not filepath:
            print("Still no filepath, try again later.")
            return 0.1  # Try again in 0.1 seconds

        xomapath = str(pathlib.Path(filepath).with_suffix(".xoma").resolve())
        if os.path.exists(xomapath):
            with open(xomapath, "r", encoding="utf-8") as f:
                bpy.context.scene.xom3d_context.asset = json.load(f)

        asset_metadata = bpy.context.scene.xom3d_context.asset["metadata"]

        panel_data = bpy.context.scene.xom3d_asset_panel_data
        panel_data.asset_name = asset_metadata.get("name", "Unnamed Asset")
        panel_data.description = asset_metadata.get(
            "description", "No description provided."
        )
        panel_data.license = asset_metadata.get(
            "license", "No license information provided."
        )

        if "object" == asset_metadata.get("assetType"):
            panel_data.asset_type = asset_metadata.get("objectClass")
        elif "scene" == asset_metadata.get("assetType"):
            panel_data.asset_type = "scene"

        panel_data.axles.clear()
        if panel_data.asset_type == "vehicle":
            vehicle_data = asset_metadata.get("vehicleClassData", {})
            axles_data = vehicle_data.get("axles", {})
            front_axle = panel_data.axles.add()
            front_axle.max_steering = axles_data.get("frontAxle", {}).get(
                "maxSteering", 0.0
            )
            front_axle.wheel_diameter = axles_data.get("frontAxle", {}).get(
                "wheelDiameter", 0.0
            )
            front_axle.track_width = axles_data.get("frontAxle", {}).get(
                "trackWidth", 0.0
            )
            front_axle.position_x = axles_data.get("frontAxle", {}).get(
                "positionX", 0.0
            )
            front_axle.position_z = axles_data.get("frontAxle", {}).get(
                "positionZ", 0.0
            )
            rear_axle = panel_data.axles.add()
            rear_axle.max_steering = axles_data.get("rearAxle", {}).get(
                "maxSteering", 0.0
            )
            rear_axle.wheel_diameter = axles_data.get("rearAxle", {}).get(
                "wheelDiameter", 0.0
            )
            rear_axle.track_width = axles_data.get("rearAxle", {}).get(
                "trackWidth", 0.0
            )
            rear_axle.position_x = axles_data.get("rearAxle", {}).get("positionX", 0.0)
            rear_axle.position_z = axles_data.get("rearAxle", {}).get("positionZ", 0.0)

            for axle_data in axles_data.get("additionalAxles", []):
                axle = panel_data.axles.add()
                axle.max_steering = axle_data.get("maxSteering", 0.0)
                axle.wheel_diameter = axle_data.get("wheelDiameter", 0.0)
                axle.track_width = axle_data.get("trackWidth", 0.0)
                axle.position_x = axle_data.get("positionX", 0.0)
                axle.position_z = axle_data.get("positionZ", 0.0)

        update_xom3d_asset_panel(bpy.context.scene)

        return None

    # Register the delayed load function to run after a short delay
    bpy.app.timers.register(delayed_load, first_interval=0.1)


def register():
    bpy.utils.register_class(XOM3D_AssetBoundingBox)
    bpy.utils.register_class(XOM3D_VehicleWheelAxle)
    bpy.utils.register_class(XOM3D_AssetPanelData)
    bpy.utils.register_class(XOM3D_OT_ExportAsset)
    bpy.utils.register_class(XOM3D_OT_ReloadAssetFile)
    bpy.utils.register_class(XOM3D_PT_AssetPanel)
    bpy.types.Scene.xom3d_asset_panel_data = bpy.props.PointerProperty(
        type=XOM3D_AssetPanelData
    )

    if update_xom3d_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(update_xom3d_on_load)

    if update_xom3d_asset_panel not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(update_xom3d_asset_panel)


def unregister():
    if update_xom3d_asset_panel in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_xom3d_asset_panel)

    if update_xom3d_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_xom3d_on_load)

    del bpy.types.Scene.xom3d_asset_panel_data
    bpy.utils.unregister_class(XOM3D_PT_AssetPanel)
    bpy.utils.unregister_class(XOM3D_OT_ReloadAssetFile)
    bpy.utils.unregister_class(XOM3D_OT_ExportAsset)
    bpy.utils.unregister_class(XOM3D_AssetPanelData)
    bpy.utils.unregister_class(XOM3D_VehicleWheelAxle)
    bpy.utils.unregister_class(XOM3D_AssetBoundingBox)
