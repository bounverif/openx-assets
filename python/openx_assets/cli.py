import argparse
import pathlib
import glob
import json
import bpy
import mathutils

from . import xom3d_utils

from .xom3d import FileTemplates


def export_command(args):
    blend_files = glob.glob(args.collection + "/" + args.pattern, recursive=True)
    if not blend_files:
        print(f"No .blend files found with pattern: {args.pattern}")
        return

    if args.destdir:
        destdir = pathlib.Path(args.destdir).resolve()
        destdir.mkdir(parents=True, exist_ok=True)

    for blendpath in blend_files:
        print(f"Exporting file: {blendpath}")
        bpy.ops.wm.open_mainfile(filepath=blendpath)

        relative_dir = pathlib.Path(blendpath).relative_to(args.collection).parent
        assets_dir = (
            destdir / relative_dir if args.destdir else pathlib.Path(blendpath).parent
        )

        if args.export_glb:
            xom3d_utils.export_scene_gltf(destdir=assets_dir, export_format="GLB")
        if args.export_gltf:
            xom3d_utils.export_scene_gltf(
                destdir=assets_dir, export_format="GLTF_SEPARATE"
            )
        if args.export_fbx:
            xom3d_utils.export_scene_fbx(destdir=assets_dir)

        xomapath = str(pathlib.Path(blendpath).with_suffix(".xoma").resolve())
        try:
            with open(xomapath, "r") as file:
                filedata = json.load(file)
        except FileNotFoundError:
            print(f"Warning: {xomapath} not found.")
            filedata = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing {xomapath}: {e}")
            filedata = {}

        template = FileTemplates.xoma_1_0_0
        asset_data = xom3d_utils.deep_merge(template, filedata)
        if args.asset_version:
            asset_data["metadata"]["assetVersion"] = args.asset_version
        xom3d_utils.export_asset_file(asset_data, destdir=assets_dir)


def render_command(args):
    blend_files = glob.glob(args.collection + "/" + args.pattern, recursive=True)
    if not blend_files:
        print(f"No .blend files found with pattern: {args.pattern}")
        return

    for blendpath in blend_files:
        print(f"Rendering file: {blendpath}")
        bpy.ops.wm.open_mainfile(filepath=blendpath)
        scene = bpy.context.scene

        # Use Cycles with GPU if available
        scene.render.engine = "CYCLES"
        prefs = bpy.context.preferences
        cprefs = prefs.addons["cycles"].preferences
        try:
            cprefs.compute_device_type = "CUDA" if "CUDA" in cprefs.devices else "NONE"
        except:
            pass
        scene.cycles.device = "GPU" if cprefs.compute_device_type != "NONE" else "CPU"
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.samples = 64
        scene.cycles.use_denoising = True
        scene.render.film_transparent = False  # Let materials reflect the sky

        for obj in bpy.context.scene.objects:
            obj.hide_render = False
            obj.hide_viewport = False

        # Set up a basic environment lighting
        scene.world.use_nodes = True
        env_nodes = scene.world.node_tree.nodes
        if "Background" in env_nodes:
            env_nodes["Background"].inputs[0].default_value = (
                1.0,
                1.0,
                1.0,
                1.0,
            )  # white light
            env_nodes["Background"].inputs[1].default_value = 1.0  # strength

        # Add Sunlight if not present
        if "Sun" not in bpy.data.objects:
            light_data = bpy.data.lights.new(name="Sun", type="SUN")
            light_data.energy = 5.0
            sun = bpy.data.objects.new("Sun", light_data)
            bpy.context.collection.objects.link(sun)
            sun.location = (10, -10, 10)
            sun.rotation_euler = (0.6, 0.1, 0.8)

        # Compute bounding box of all meshes
        min_corner = mathutils.Vector((float("inf"),) * 3)
        max_corner = mathutils.Vector((float("-inf"),) * 3)
        mesh_objects = [obj for obj in scene.objects if obj.type == "MESH"]
        if not mesh_objects:
            print("No mesh objects found in scene.")
            continue

        for obj in mesh_objects:
            for v in obj.bound_box:
                world_v = obj.matrix_world @ mathutils.Vector(v)
                min_corner = mathutils.Vector(map(min, min_corner, world_v))
                max_corner = mathutils.Vector(map(max, max_corner, world_v))

        center = (min_corner + max_corner) / 2
        size = (max_corner - min_corner).length

        print(f"Bounding Box Center: {center}, Size: {size}")

        # Setup camera at (+X, -Y, +Z) pointing to center
        cam_data = bpy.data.cameras.new("Camera")
        cam = bpy.data.objects.new("Camera", cam_data)
        bpy.context.collection.objects.link(cam)
        scene.camera = cam

        direction = mathutils.Vector((1, -0.8, 0.4)).normalized()
        cam_distance = size * 1.4
        cam.location = center + direction * cam_distance
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()

        # Optional: Ground Plane with Material
        if "Ground" not in bpy.data.objects:
            bpy.ops.mesh.primitive_plane_add(
                size=500, location=(0, 0, min_corner.z - 0.01)
            )
            ground = bpy.context.active_object
            ground.name = "Ground"
            mat = bpy.data.materials.new(name="GroundMaterial")
            mat.use_nodes = True
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (0.0, 0.0, 0.02, 1.0)
                bsdf.inputs["Roughness"].default_value = 1.0
            ground.data.materials.append(mat)

        # Set output render resolution and format
        pngpath = str(pathlib.Path(blendpath).with_suffix(".png").resolve())
        scene.render.filepath = pngpath
        scene.render.image_settings.file_format = "PNG"
        scene.render.resolution_x = 400
        scene.render.resolution_y = 300

        bpy.ops.render.render(write_still=True)


def validate_command(args):
    blend_files = glob.glob(args.pattern)
    if not blend_files:
        print(f"No .blend files found with pattern: {args.pattern}")
        return

    for blend_file in blend_files:
        print(f"Validating file: {blend_file}")
        if args.schema:
            print(f"  Using schema: {args.schema}")
        # TODO: Actual validation logic

    print(args)


def main():
    parser = argparse.ArgumentParser(
        description="OpenXAssets Command Line Interface",
    )
    parser.add_argument("--schema", help="Schema version or path", default="1.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define a common parent parser for shared arguments
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "collection",
        nargs="?",
        help="Directory path to look for .blend files",
        default=".",
    )
    common_parser.add_argument(
        "--schema", default="1.0", help="Schema version or path for validation."
    )
    common_parser.add_argument(
        "--pattern",
        default="**/*.blend",
        help="Glob pattern to match .blend files (default: *.blend)",
    )

    # Export subcommand
    export_parser = subparsers.add_parser(
        "export", help="Export OpenX assets", parents=[common_parser]
    )

    export_parser.add_argument(
        "--glb",
        dest="export_glb",
        action="store_true",
        default=True,
        help="Export to GLTF (Binary) format",
    )
    export_parser.add_argument(
        "--no-glb",
        dest="export_glb",
        action="store_false",
        help="Do not export to GLTF (Binary) format",
    )
    export_parser.add_argument(
        "--gltf",
        dest="export_gltf",
        action="store_true",
        default=False,
        help="Export to GLTF (Separate) format",
    )
    export_parser.add_argument(
        "--no-gltf",
        dest="export_gltf",
        action="store_false",
        help="Do not export to GLTF (Separate) format",
    )
    export_parser.add_argument(
        "--fbx",
        dest="export_fbx",
        action="store_true",
        default=False,
        help="Export to FBX format",
    )
    export_parser.add_argument(
        "--no-fbx",
        dest="export_fbx",
        action="store_false",
        help="Do not export to FBX format",
    )
    export_parser.add_argument(
        "--destdir",
        type=pathlib.Path,
        help="Output directory for exported files (default: next to source file)",
    )
    export_parser.add_argument(
        "--asset-version",
        help="Asset version to use in the exported file",
    )

    export_parser.set_defaults(func=export_command)

    # Render subcommand
    render_parser = subparsers.add_parser(
        "render", help="Render OpenX assets", parents=[common_parser]
    )
    render_parser.set_defaults(func=render_command)

    # Validate subcommand
    validate_parser = subparsers.add_parser(
        "validate", help="Validate OpenX assets", parents=[common_parser]
    )
    # validate_parser.add_argument('collection', help='Directory path to look for .blend files', default='.')
    validate_parser.set_defaults(func=validate_command)

    # Parse and dispatch
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
