#!/usr/bin/env python

import bpy
import sys
import os
import uuid
import datetime
import argparse
import json

def get_bounding_box(normalize=False, collection_name='Grp_Root'):
    def transform_point(matrix, point):
        x, y, z = point
        # Homogeneous coordinates
        px = matrix[0][0]*x + matrix[0][1]*y + matrix[0][2]*z + matrix[0][3]
        py = matrix[1][0]*x + matrix[1][1]*y + matrix[1][2]*z + matrix[1][3]
        pz = matrix[2][0]*x + matrix[2][1]*y + matrix[2][2]*z + matrix[2][3]
        return (px, py, pz)

    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        print(f"Collection '{collection_name}' not found.")
        return None

    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')

    for obj in collection.all_objects:
        if obj.type == 'MESH':
            matrix = obj.matrix_world
            m = [[matrix[i][j] for j in range(4)] for i in range(4)]

            for corner in obj.bound_box:
                x, y, z = transform_point(m, corner)
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                min_z = min(min_z, z)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                max_z = max(max_z, z)

    if normalize:
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        offset_z = min_z

        offset = (-center_x, -center_y, -offset_z)

        # Move all objects in the collection by the offset
        for obj in collection.all_objects:
            obj.location.x += offset[0]
            obj.location.y += offset[1]
            obj.location.z += offset[2]

        min_x += offset[0]
        min_y += offset[1]
        min_z += offset[2]
        max_x += offset[0]
        max_y += offset[1]
        max_z += offset[2]

    return {
        "x": (round(min_x,4), round(max_x,4)),
        "y": (round(min_y,4), round(max_y,4)),
        "z": (round(min_z,4), round(max_z,4)),
    }

def get_collection_triangle_count(collection_name='Grp_Root'):
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        print(f"Collection '{collection_name}' not found.")
        return 0

    depsgraph = bpy.context.evaluated_depsgraph_get()
    total_tris = 0

    for obj in collection.all_objects:
        if obj.type == 'MESH':
            obj_eval = obj.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()
            mesh.calc_loop_triangles()
            total_tris += len(mesh.loop_triangles)
            obj_eval.to_mesh_clear()

    return total_tris

def get_calendar_version():
    today = datetime.date.today()
    calver = today.strftime("%Y.%-m.%-d")
    return calver

def get_mesh_count(collection_name='Grp_Root'):
    collection = bpy.data.collections.get(collection_name)
    mesh_count = sum(1 for obj in collection.all_objects if obj.type == 'MESH')
    return mesh_count

def get_axle_info(axle=0, collection_name='Grp_Exterior_Dynamic'):

    collection = bpy.data.collections.get(collection_name)

    wheel_right = collection.objects.get('Grp_Wheel_{}_0'.format(axle))
    wheel_left = collection.objects.get('Grp_Wheel_{}_1'.format(axle))

    return {
        "wheelDiameter": round(wheel_right.dimensions.z,4),
        "trackWidth": round(wheel_left.location.y,4) - round(wheel_right.location.y,4),
        "positionX": round(wheel_right.location.x,4),
        "positionZ": round(wheel_right.location.z,4),
    }
    
def export_blender_fbx(filepath):
    print(f"Exporting FBX to {filepath}")
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        colors_type='NONE',
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-X', # -X
        axis_up='Z'        #  Z
    )

def export_blender_gltf(filepath):
    print(f"Exporting GLTF to {filepath}")
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_vertex_color='NONE',
        export_hierarchy_full_collections=True,
        export_format='GLTF_SEPARATE',
        export_yup=True,
    )

def export_blender_glb(filepath):
    print(f"Exporting GLTF to {filepath}")
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_vertex_color='NONE',
        export_hierarchy_full_collections=True,
        export_format='GLB',
        export_yup=True,
    )

def main(args):

    blend_file = bpy.data.filepath

    if not blend_file:
        blend_file = args.blend_file
    
    if not blend_file:
        print("No blend file specified.")
        return

    asset_name = os.path.basename(blend_file).split('.')[0]
    asset_dirname = os.path.dirname(blend_file)

    with open(args.xoma_template) as f:
        xoma_data = json.load(f)

    xoma_data['metadata']['name'] = asset_name
    xoma_data['metadata']['assetVersion'] = get_calendar_version()
    xoma_data['metadata']['uuid'] = str(uuid.uuid5(uuid.NAMESPACE_URL, asset_name))
    xoma_data['metadata']['triangleCount'] = get_collection_triangle_count()
    xoma_data['metadata']['meshCount'] = get_mesh_count()
    xoma_data['metadata']['boundingBox'] |= get_bounding_box(normalize=True)
    xoma_data['metadata']['vehicleClassData']['axles']["frontAxle"] |= get_axle_info(0)
    xoma_data['metadata']['vehicleClassData']['axles']["rearAxle"] |= get_axle_info(1)

    output_path = os.path.join(asset_dirname, '{}.xoma'.format(asset_name))
    with open(output_path, 'w') as f:
        json.dump(xoma_data, f, indent=2)

    if args.export_fbx:
        asset_path = os.path.join(asset_dirname, '{}.fbx'.format(asset_name))
        export_blender_fbx(asset_path)

    if args.export_gltf:
        asset_path = os.path.join(asset_dirname, '{}.gltf'.format(asset_name))
        export_blender_gltf(asset_path)

    if args.export_glb:
        asset_path = os.path.join(asset_dirname, '{}.glb'.format(asset_name))
        export_blender_glb(asset_path)

if __name__ == "__main__":
    argv = sys.argv

    # Parse args after `--` if in Blender, else just use sys.argv[1:]
    if "blender" in argv[0].lower():
        if "--" in argv:
            python_argv = argv[argv.index("--") + 1:]
        else:
            python_argv = []  
    else:
        python_argv = argv[1:]

    # Common parser
    parser = argparse.ArgumentParser(prog='blexom')
    parser.add_argument('--blend-file', type=str, required=False, help='Path to the Blender file')
    parser.add_argument('--xoma-template', type=str, required=False, help='Path to the XOMA template file')
    parser.add_argument('--export-fbx', action='store_true', help='Export the scene as FBX')
    parser.add_argument('--export-glb', action='store_true', help='Export the scene as GLB')
    parser.add_argument('--export-gltf', action='store_true', help='Export the scene as GLTF')
    args = parser.parse_args(python_argv)

    main(args)
