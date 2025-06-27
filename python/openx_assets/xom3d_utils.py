import bpy
import math
import json
import uuid
import pathlib

from mathutils import Vector
from jsonschema import validate


def add_empty_node(name, parent_name=None, dtype="PLAIN_AXES"):
    if name in bpy.data.objects:
        return bpy.data.objects[name]
    empty_node = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(empty_node)
    empty_node.empty_display_type = dtype
    if parent_name and parent_name in bpy.data.objects:
        empty_node.parent = bpy.data.objects[parent_name]
        empty_node.matrix_parent_inverse = empty_node.parent.matrix_world.inverted()
        bpy.context.evaluated_depsgraph_get().update()
    return empty_node


def update_depsgraph():
    """Force an update of the dependency graph."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    depsgraph.update()


def get_bounding_box(rounded=0):

    if not any(obj.type == "MESH" for obj in bpy.data.objects):
        return {
            "x": {"min": 0.0, "max": 0.0},
            "y": {"min": 0.0, "max": 0.0},
            "z": {"min": 0.0, "max": 0.0},
        }

    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")

    for obj in bpy.data.objects:
        if obj.type == "MESH":
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

    if rounded > 0:
        min_x = round(min_x, rounded)
        max_x = round(max_x, rounded)
        min_y = round(min_y, rounded)
        max_y = round(max_y, rounded)
        min_z = round(min_z, rounded)
        max_z = round(max_z, rounded)

    return {
        "x": [min_x, max_x],
        "y": [min_y, max_y],
        "z": [min_z, max_z],
    }


def get_axle_info(axle=0, rounded=0):

    wheel_right = bpy.data.objects.get("Grp_Wheel_{}_0".format(axle))
    wheel_left = bpy.data.objects.get("Grp_Wheel_{}_1".format(axle))

    wheel_diameter = wheel_right.location.z * 2
    track_width = wheel_left.location.y - wheel_right.location.y
    position_x = wheel_right.location.x
    position_z = wheel_right.location.z

    if rounded > 0:
        wheel_diameter = round(wheel_diameter, rounded)
        track_width = round(track_width, rounded)
        position_x = round(position_x, rounded)
        position_z = round(position_z, rounded)

    return {
        "wheelDiameter": wheel_diameter,
        "trackWidth": track_width,
        "positionX": position_x,
        "positionZ": position_z,
    }


def get_mesh_count():
    mesh_count = sum(1 for obj in bpy.data.objects if obj.type == "MESH")
    return mesh_count


def get_triangle_count():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total_triangles = 0

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()
            mesh.calc_loop_triangles()
            total_triangles += len(mesh.loop_triangles)
            obj_eval.to_mesh_clear()

    return total_triangles


def get_uuid():
    """Generate a UUID for the current Blender file."""
    return str(uuid.uuid4())


def move_asset_to_origin():
    """Move asset to ensure its bounding box is centered at the origin."""

    bbox = get_bounding_box()
    if not bbox:
        return

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.location.x -= (bbox["x"][0] + bbox["x"][1]) / 2
            obj.location.y -= (bbox["y"][0] + bbox["y"][1]) / 2
            obj.location.z -= bbox["z"][0]


def is_vehicle_asset():
    """Check if the current asset is a vehicle asset."""
    return any(obj.name.startswith("Grp_Exterior") for obj in bpy.data.objects)


def is_asset_centered(rel_tol=0, abs_tol=1e-6):
    """Check if the asset is centered at the origin."""
    bbox = get_bounding_box()
    if not bbox:
        return False

    x_centered = math.isclose(bbox["x"][0] + bbox["x"][1], rel_tol, abs_tol=abs_tol)
    y_centered = math.isclose(bbox["y"][0] + bbox["y"][1], rel_tol, abs_tol=abs_tol)
    z_centered = (
        math.isclose(bbox["z"][0], rel_tol, abs_tol=abs_tol) and bbox["z"][0] >= 0
    )

    return x_centered and y_centered and z_centered


def set_active_and_select(active_obj, select_objs):
    """Helper to clear selection, select specified objects and set active object."""
    bpy.ops.object.select_all(action="DESELECT")
    for obj in select_objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = active_obj


def move_empty_parent_to_child():
    child = bpy.context.active_object
    if not child:
        print("No active object selected.")
        return

    parent = child.parent
    if not parent:
        print(f"[Skipped] '{child.name}' has no parent.")
        return

    if parent.type != "EMPTY":
        print(
            f"[Skipped] Parent '{parent.name}' is not an Empty object. Its type is '{parent.type}'."
        )
        return

    # Ensure Object mode
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")

    # Save child's world matrix before parenting changes
    child_world_matrix = child.matrix_world.copy()

    # Clear parenting but keep child's world transform
    set_active_and_select(child, [child])
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")

    # Move parent to child's former world matrix
    parent.matrix_world = child_world_matrix

    # Reparent child to parent with keep transform
    set_active_and_select(parent, [parent, child])
    bpy.ops.object.parent_set(type="OBJECT", keep_transform=True)

    # Apply Parent Inverse to the child (bakes inverse matrix)
    set_active_and_select(child, [child])
    bpy.ops.object.parent_inverse_apply()
    print(f"[Done] Applied Parent Inverse to '{child.name}'.")

    # Apply all transforms to the parent (location, rotation, scale)
    set_active_and_select(child, [child])
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    print(
        f"[Done] Applied all transforms (location, rotation, scale) to '{parent.name}'."
    )


def export_scene_gltf(destdir="", export_format="GLB"):
    """Export the current scene to a GLTF file."""
    # get current scene filepath

    extension = ".glb" if export_format == "GLB" else ".gltf"

    blendpath = bpy.data.filepath
    asset_path = pathlib.Path(blendpath).with_suffix(extension).resolve()

    if destdir:
        asset_path = pathlib.Path(destdir) / pathlib.Path(asset_path.name)

    bpy.ops.export_scene.gltf(
        filepath=str(asset_path),
        export_format=export_format,
        export_vertex_color="NONE",
        export_yup=True,
        export_animations=False,
        # export_draco_mesh_compression_enable=True,
        # export_materials='PLACEHOLDER',
        export_extras=True,
    )

    return str(asset_path)


def export_scene_fbx(destdir=""):
    """Export the current scene to an FBX file."""

    blendpath = bpy.data.filepath
    asset_path = pathlib.Path(blendpath).with_suffix(".fbx").resolve()

    if destdir:
        asset_path = pathlib.Path(destdir) / pathlib.Path(asset_path.name)

    bpy.ops.export_scene.fbx(
        filepath=str(asset_path),
        colors_type="NONE",
        apply_scale_options="FBX_SCALE_ALL",
        axis_forward="-X",  # -X
        axis_up="Z",  #  Z
    )

    return str(asset_path)


def deep_merge(d1, d2):
    merged = dict(d1)
    for k, v in d2.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def export_asset_file(asset_data, user_data=dict(), destdir="", rounded=4):
    """Export asset data to a .xoma file."""

    filepath = bpy.data.filepath
    xomapath = pathlib.Path(filepath).with_suffix(".xoma").resolve()

    if destdir:
        xomapath = pathlib.Path(destdir) / pathlib.Path(xomapath.name)

    if not asset_data.get("metadata", {}).get("uuid"):
        asset_data["metadata"]["uuid"] = get_uuid()

    calculated_data = {
        "metadata": {
            "boundingBox": get_bounding_box(rounded=rounded),
            "vehicleClassData": {
                "axles": {
                    "frontAxle": get_axle_info(0, rounded=rounded),
                    "rearAxle": get_axle_info(1, rounded=rounded),
                }
            },
            "meshCount": get_mesh_count(),
            "triangleCount": get_triangle_count(),
        }
    }

    updated_data = deep_merge(user_data, calculated_data)
    current_data = deep_merge(asset_data, updated_data)

    # Dump asset data to JSON
    with open(xomapath, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2)
        f.write("\n")

    return xomapath
