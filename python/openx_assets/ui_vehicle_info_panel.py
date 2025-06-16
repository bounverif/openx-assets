import bpy
import math

from .xom3d_utils import (
    get_bounding_box,
    get_axle_info,
    get_mesh_count,
    get_triangle_count,
)


class VIEW3D_PT_OpenXAssetsPanel(bpy.types.Panel):
    bl_label = "Open MATERIAL 3D Info"
    bl_idname = "VIEW3D_PT_info_box_tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "OpenX Assets"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        self.draw_bounding_box_info(context)
        # self.draw_wheel_axles_info(context)
        self.draw_mesh_stats_info(context)

    def draw_bounding_box_info(self, context):
        layout = self.layout
        asset_data = getattr(context.scene, "xom3d_vehicle_asset", None)
        bb = asset_data.boundingBox
        box = layout.box()
        box.label(text="Bounding Box:")

        for axis_name in ["x", "y", "z"]:
            axis = getattr(bb, axis_name)

            row = box.row(align=True)

            split = row.split(factor=0.1, align=True)
            split.label(text=f"{axis_name.upper()}:")

            sub = split.split(factor=0.5, align=True)
            sub.prop(axis, "min", text="")
            sub.prop(axis, "max", text="")
            # sub.enabled = False

        if (
            (not math.isclose(bb.x.max + bb.x.min, 0.0, abs_tol=0.0001))
            or (not math.isclose(bb.y.max + bb.y.min, 0.0, abs_tol=0.0001))
            or (not math.isclose(bb.z.min, 0.0, abs_tol=0.0001))
            or (bb.z.min < 0.0)
        ):
            # row = box.row(align=True)
            # row.scale_y = 0.8
            # split = row.split(factor=0.1, align=True)
            # split.label(text="")
            # sub = split.split(factor=1, align=True)
            # sub.label(text="Asset is NOT centered at origin", icon="ERROR")

            row = box.row(align=True)
            split = row.split(factor=0.1, align=True)
            split.label(text="")
            sub = split.split(factor=1, align=True)
            sub.operator("object.move_asset_to_origin", text="Move Asset to Origin")

    def draw_wheel_axles_info(self, context):
        layout = self.layout
        asset_data = getattr(context.scene, "xom3d_vehicle_asset", None)
        box = layout.box()
        front_axle = asset_data.frontAxle
        rear_axle = asset_data.rearAxle

        row = box.row(align=True)
        row.enabled = False
        split = row.split(factor=0.4, align=True)
        split.label(text="")
        sub = split.split(factor=0.5, align=True)
        row.alignment = "CENTER"
        sub.label(text="Front Axle")
        sub.label(text="Rear  Axle")

        for property_name in ["wheelDiameter", "trackWidth", "positionX", "positionZ"]:
            row = box.row(align=True)

            # Split row: 40% label, 60% property
            split = row.split(factor=0.4, align=True)
            split.label(
                text={
                    "wheelDiameter": "Diameter:",
                    "trackWidth": "Track Width:",
                    "positionX": "Position X:",
                    "positionZ": "Position Z:",
                }.get(property_name, property_name)
            )

            sub = split.split(factor=0.5, align=True)
            sub.prop(front_axle, property_name, text="", emboss=False)
            sub.prop(rear_axle, property_name, text="", emboss=False)

    def draw_mesh_stats_info(self, context):
        layout = self.layout
        box = layout.box()
        box.scale_y = 0.8

        row = box.row(align=True)
        row.label(text="Mesh Count:")
        row.label(text=str(get_mesh_count()))

        row = box.row(align=True)
        row.label(text="Triangle Count:")
        row.label(text=str(get_triangle_count()))


@bpy.app.handlers.persistent
def update_xom3d_vehicle_asset_handler(scene):
    """Update the OpenMATERIAL 3D info in the scene."""

    xoma = scene.xom3d_vehicle_asset
    bb_data = get_bounding_box()
    # front_axle = get_axle_info(0)
    # rear_axle = get_axle_info(1)

    # Assign bounding box values
    xoma.boundingBox.x.min = bb_data["x"]["min"]
    xoma.boundingBox.x.max = bb_data["x"]["max"]
    xoma.boundingBox.y.min = bb_data["y"]["min"]
    xoma.boundingBox.y.max = bb_data["y"]["max"]
    xoma.boundingBox.z.min = bb_data["z"]["min"]
    xoma.boundingBox.z.max = bb_data["z"]["max"]

    # # Assign wheel axle values
    # xoma.frontAxle.wheelDiameter = front_axle["wheelDiameter"]
    # xoma.frontAxle.trackWidth = front_axle["trackWidth"]
    # xoma.frontAxle.positionX = front_axle["positionX"]
    # xoma.frontAxle.positionZ = front_axle["positionZ"]
    # xoma.rearAxle.wheelDiameter = rear_axle["wheelDiameter"]
    # xoma.rearAxle.trackWidth = rear_axle["trackWidth"]
    # xoma.rearAxle.positionX = rear_axle["positionX"]
    # xoma.rearAxle.positionZ = rear_axle["positionZ"]


@bpy.app.handlers.persistent
def update_xom3d_vehicle_asset_on_load(dummy=None):
    """Run the vehicle asset update handler once after loading a .blend file."""

    scene = bpy.context.scene
    if scene:
        print("[OpenX] Running update_xom3d_vehicle_asset_handler on file load...")
        update_xom3d_vehicle_asset_handler(scene)
    else:
        print("[OpenX] Scene not ready yet — skipping update on load.")


def register():

    bpy.utils.register_class(VIEW3D_PT_OpenXAssetsPanel)

    if update_xom3d_vehicle_asset_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(
            update_xom3d_vehicle_asset_handler
        )

    if update_xom3d_vehicle_asset_on_load not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(update_xom3d_vehicle_asset_on_load)


def unregister():
    if update_xom3d_vehicle_asset_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(update_xom3d_vehicle_asset_on_load)

    if update_xom3d_vehicle_asset_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(
            update_xom3d_vehicle_asset_handler
        )

    bpy.utils.unregister_class(VIEW3D_PT_OpenXAssetsPanel)
