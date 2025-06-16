import bpy

from mathutils import Vector


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


def get_bounding_box():

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

    return {
        "x": {"min": min_x, "max": max_x},
        "y": {"min": min_y, "max": max_y},
        "z": {"min": min_z, "max": max_z},
    }


def get_axle_info(axle=0):

    wheel_right = bpy.data.objects.get("Grp_Wheel_{}_0".format(axle))
    wheel_left = bpy.data.objects.get("Grp_Wheel_{}_1".format(axle))

    return {
        "wheelDiameter": wheel_right.location.z * 2,
        "trackWidth": wheel_left.location.y - wheel_right.location.y,
        "positionX": wheel_right.location.x,
        "positionZ": wheel_right.location.z,
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


def move_asset_to_origin():
    """Move asset to ensure its bounding box is centered at the origin."""

    bbox = get_bounding_box()
    if not bbox:
        return

    for obj in bpy.data.objects:
        if obj.type == "MESH":
            obj.location.x -= (bbox["x"]["min"] + bbox["x"]["max"]) / 2
            obj.location.y -= (bbox["y"]["min"] + bbox["y"]["max"]) / 2
            obj.location.z -= bbox["z"]["min"]


def is_vehicle_asset():
    """Check if the current asset is a vehicle asset."""
    return any(obj.name.startswith("Grp_Exterior") for obj in bpy.data.objects)
