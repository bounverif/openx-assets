import bpy
import math

from mathutils import Vector
from bpy.props import FloatProperty, PointerProperty


class MinMaxInfo(bpy.types.PropertyGroup):
    min: FloatProperty(name="Min")
    max: FloatProperty(name="Max")

class BoundingBoxInfo(bpy.types.PropertyGroup):
    x: PointerProperty(type=MinMaxInfo)
    y: PointerProperty(type=MinMaxInfo)
    z: PointerProperty(type=MinMaxInfo)

class WheelAxleInfo(bpy.types.PropertyGroup):
    wheelDiameter: FloatProperty(name="Wheel Diameter")
    trackWidth: FloatProperty(name="Track Width")
    positionX: FloatProperty(name="Position X")
    positionZ: FloatProperty(name="Position Z")

class OpenMaterialAssetInfo(bpy.types.PropertyGroup):
    """Property group to hold bounding box information for OpenMATERIAL 3D assets."""
    boundingBox: PointerProperty(type=BoundingBoxInfo)
    frontAxle: PointerProperty(type=WheelAxleInfo)
    rearAxle: PointerProperty(type=WheelAxleInfo)


def get_bounding_box():

    if not any(obj.type == 'MESH' for obj in bpy.data.objects):
        return {
            "x": {"min": 0.0, "max": 0.0},
            "y": {"min": 0.0, "max": 0.0},
            "z": {"min": 0.0, "max": 0.0},
        }

    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            matrix = obj.matrix_world
            m = [[matrix[i][j] for j in range(4)] for i in range(4)]

            for corner in obj.bound_box:
                x, y, z = obj.matrix_world @ Vector(corner)
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                min_z = min(min_z, z)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                max_z = max(max_z, z)

    return {
        "x": {"min": min_x, "max": max_x},
        "y": {"min": min_y, "max": max_y},
        "z": {"min": min_z, "max": max_z},
    }

def get_axle_info(axle=0):

    wheel_right = bpy.data.objects.get('Grp_Wheel_{}_0'.format(axle))
    wheel_left = bpy.data.objects.get('Grp_Wheel_{}_1'.format(axle))

    return {
        "wheelDiameter": wheel_right.location.z * 2,
        "trackWidth": wheel_left.location.y - wheel_right.location.y,
        "positionX": wheel_right.location.x,
        "positionZ": wheel_right.location.z,
    }

def get_mesh_count():
    mesh_count = sum(1 for obj in bpy.data.objects if obj.type == 'MESH')
    return mesh_count

def get_triangle_count():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total_triangles = 0

    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()
            mesh.calc_loop_triangles()
            total_triangles += len(mesh.loop_triangles)
            obj_eval.to_mesh_clear()

    return total_triangles

class VIEW3D_PT_OpenXAssetsPanel(bpy.types.Panel):
    bl_label = "Open MATERIAL 3D Info"
    bl_idname = "VIEW3D_PT_info_box_tool"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "OpenX Assets"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        xoma_info = getattr(context.scene, "xoma_info", None)
        if not xoma_info:
            layout.label(text="DEBUG: xoma_info not set")
            return
        
        bb = xoma_info.boundingBox
        box = layout.box()
        box.label(text="Bounding Box:")

        for axis_name in ['x', 'y', 'z']:
            axis = getattr(bb, axis_name)
            
            row = box.row(align=True)

            split = row.split(factor=0.1, align=True)
            split.label(text=f"{axis_name.upper()}:")

            sub = split.split(factor=0.5, align=True)
            sub.prop(axis, "min", text="")
            sub.prop(axis, "max", text="")

        if (not math.isclose(bb.x.max + bb.x.min, 0.0, abs_tol=0.0001)) or \
           (not math.isclose(bb.y.max + bb.y.min, 0.0, abs_tol=0.0001)) or \
           (not math.isclose(bb.z.min, 0.0, abs_tol=0.0001)) or \
           (bb.z.min < 0.0):

            row = box.row(align=True)
            row.scale_y = 0.8
            split = row.split(factor=0.1, align=True)
            split.label(text="")
            sub = split.split(factor=1, align=True)
            sub.label(text="Asset is NOT centered at origin", icon='ERROR')

        box = layout.box()

        front_axle = xoma_info.frontAxle 
        rear_axle = xoma_info.rearAxle

        row = box.row(align=True)
        row.enabled = False
        split = row.split(factor=0.4, align=True)
        split.label(text="")
        sub = split.split(factor=0.5, align=True)
        row.alignment = 'CENTER'
        sub.label(text="Front Axle")
        sub.label(text="Rear  Axle")

        for property_name in ['wheelDiameter', 'trackWidth', 'positionX', 'positionZ']:
            row = box.row(align=True)

            # Split row: 40% label, 60% property
            split = row.split(factor=0.4, align=True)
            split.label(text={
                'wheelDiameter': "Diameter:",
                'trackWidth': "Track Width:",
                'positionX': "Position X:",
                'positionZ': "Position Z:"
            }.get(property_name, property_name))

            sub = split.split(factor=0.5, align=True)
            sub.prop(front_axle, property_name, text="", emboss=False)
            sub.prop(rear_axle, property_name, text="", emboss=False)

        box = layout.box()
        box.scale_y = 0.8

        row = box.row(align=True)
        row.label(text="Mesh Count:")
        row.label(text=str(get_mesh_count()))

        row = box.row(align=True)
        row.label(text="Triangle Count:")
        row.label(text=str(get_triangle_count()))


def update_xoma_info_handler(scene):
    """Update the OpenMATERIAL 3D info in the scene."""

    xoma = scene.xoma_info
    bb_data = get_bounding_box()
    front_axle = get_axle_info(0)
    rear_axle = get_axle_info(1)

    # Assign bounding box values
    xoma.boundingBox.x.min = bb_data["x"]["min"]
    xoma.boundingBox.x.max = bb_data["x"]["max"]
    xoma.boundingBox.y.min = bb_data["y"]["min"]
    xoma.boundingBox.y.max = bb_data["y"]["max"]
    xoma.boundingBox.z.min = bb_data["z"]["min"]
    xoma.boundingBox.z.max = bb_data["z"]["max"]

    # Assign wheel axle values
    xoma.frontAxle.wheelDiameter = front_axle["wheelDiameter"]
    xoma.frontAxle.trackWidth = front_axle["trackWidth"]
    xoma.frontAxle.positionX = front_axle["positionX"]
    xoma.frontAxle.positionZ = front_axle["positionZ"]
    xoma.rearAxle.wheelDiameter = rear_axle["wheelDiameter"]
    xoma.rearAxle.trackWidth = rear_axle["trackWidth"]
    xoma.rearAxle.positionX = rear_axle["positionX"]
    xoma.rearAxle.positionZ = rear_axle["positionZ"]

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
    
def register():

    bpy.utils.register_class(MinMaxInfo)
    bpy.utils.register_class(BoundingBoxInfo)
    bpy.utils.register_class(WheelAxleInfo)
    bpy.utils.register_class(OpenMaterialAssetInfo)
    bpy.utils.register_class(VIEW3D_PT_OpenXAssetsPanel)

    if not hasattr(bpy.types.Scene, "xoma_info"):
        bpy.types.Scene.xoma_info = PointerProperty(type=OpenMaterialAssetInfo)

    if update_xoma_info_handler not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(update_xoma_info_handler)

def unregister():
    if update_xoma_info_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(update_xoma_info_handler)

    if hasattr(bpy.types.Scene, "xoma_info"):
        del bpy.types.Scene.xoma_info

    bpy.utils.unregister_class(VIEW3D_PT_OpenXAssetsPanel)
    bpy.utils.unregister_class(OpenMaterialAssetInfo)
    bpy.utils.unregister_class(WheelAxleInfo)
    bpy.utils.unregister_class(BoundingBoxInfo)
    bpy.utils.unregister_class(MinMaxInfo)
