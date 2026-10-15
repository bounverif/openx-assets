"""Render vehicles at night with one light function switched on at a time.

For each .blend file this renders one image per scenario (low beam, high
beam, daytime running lights, fog lights, left indicators, tail lights,
brake lights, reverse lights, licence plate lights) from the front-left and/or rear-left,
and writes an index.html grid (vehicles x scenarios) for a visual check.

Each emitter of a lit Grp_Light_* group gets its own emissive copy of its
material, coloured by function, so lamps that share a material (Lamp_Red on
tail and brake lamps) light up separately. Headlamps, fog and reverse lamps
also get a spot light along the group's X axis, so a wrong local frame shows
as a beam pointing the wrong way; licence plate lamps get a small point light. Never saves the files.

Usage: python scripts/render_lights.py [src/vehicles/<name>/<name>.blend ...]
       [--outdir build/light-renders] [--only low_beam,brake] [--samples 32]
"""

import argparse
import glob
import html
import math
import re
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

WHITE = (1.0, 0.95, 0.85)
RED = (1.0, 0.0, 0.0)
AMBER = (1.0, 0.35, 0.0)

# scenario: (light types switched on, camera views, emission strength)
# A type "Fog" matches Grp_Light_Fog_*; front/rear filtering happens per view.
SCENARIOS = {
    "low_beam": (["Low_Beam"], ["front"], 20.0),
    "high_beam": (["High_Beam"], ["front"], 20.0),
    "day": (["Day"], ["front"], 20.0),
    "fog": (["Fog"], ["front", "rear"], 20.0),
    "indicator_left": (["Indicator_Left"], ["front", "rear"], 30.0),
    "tail": (["Tail", "Position"], ["rear"], 8.0),
    "brake": (["Brake"], ["rear"], 30.0),
    "reverse": (["Reverse"], ["rear"], 20.0),
    "license_plate": (["License_Plate"], ["rear"], 20.0),
}
# Lights for lamps that light the road or the plate:
# (energy W, spot angle deg or None for a point light, pitch down deg so the beam reaches the road)
BEAMS = {
    "Low_Beam": (1500, 50, 10),
    "High_Beam": (3000, 25, 5),
    "Fog": (1000, 80, 0),
    "Reverse": (500, 80, 10),
    "License_Plate": (2, None, 0),
}
VIEWS = {"front": Vector((1.0, 0.8, 0.4)), "rear": Vector((-1.0, 0.8, 0.4))}


def setup_device(scene, samples):
    """Cycles on the first OptiX/CUDA GPU, as in `openx-assets render`."""
    scene.render.engine = "CYCLES"
    cprefs = bpy.context.preferences.addons["cycles"].preferences
    scene.cycles.device = "CPU"
    for device_type in ("OPTIX", "CUDA"):
        try:
            cprefs.compute_device_type = device_type
        except TypeError:
            continue
        cprefs.get_devices()
        if any(d.type == device_type for d in cprefs.devices):
            for d in cprefs.devices:
                d.use = d.type == device_type
            scene.cycles.device = "GPU"
            break
    scene.cycles.samples = samples
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.use_denoising = True


def setup_night(scene):
    """Dim blue sky and a dark grey ground so emitters and beams stand out."""
    scene.world = bpy.data.worlds.new("Night")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes["Background"]
    background.inputs["Color"].default_value = (0.25, 0.3, 0.5, 1.0)
    background.inputs["Strength"].default_value = 0.15
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"

    mesh = bpy.data.meshes.new("Ground")
    mesh.from_pydata(
        [(-250, -250, 0), (250, -250, 0), (250, 250, 0), (-250, 250, 0)],
        [],
        [(0, 1, 2, 3)],
    )
    ground = bpy.data.objects.new("Ground", mesh)
    mat = bpy.data.materials.new("Ground")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.08, 0.08, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.9
    mesh.materials.append(mat)
    scene.collection.objects.link(ground)


def light_type(group):
    """'Low_Beam' for Grp_Light_Low_Beam_Left_0, 'License_Plate' for Grp_Light_License_Plate_0."""
    m = re.match(r"^Grp_Light_(.+?)(?:_(Left|Right))?_\d+$", group.name)
    return (m[1], m[2]) if m else (None, None)


def emission_colour(kind, group):
    rear = group.matrix_world.translation.x < 0
    if kind == "Indicator":
        return AMBER
    if kind in ("Tail", "Brake", "Brake_Center") or (
        rear and kind in ("Fog", "Position")
    ):
        return RED
    return WHITE


def prepare_lamps(scene):
    """Give every emitter its own materials and every road lamp a spot light, all off.

    Returns [(group, kind, side, [emissive Principled BSDF nodes], spot or None)].
    """
    lamps = []
    for group in sorted(
        (o for o in scene.objects if o.name.startswith("Grp_Light_")),
        key=lambda o: o.name,
    ):
        kind, side = light_type(group)
        if not kind:
            continue
        colour = emission_colour(kind, group)
        nodes = []
        for obj in group.children_recursive:
            if obj.type != "MESH":
                continue
            obj.data = obj.data.copy()  # mirrored lamps may share mesh data
            for slot in obj.material_slots:
                if not slot.material:
                    continue
                slot.material = slot.material.copy()
                bsdf = slot.material.node_tree.nodes.get("Principled BSDF")
                if bsdf:
                    bsdf.inputs["Emission Color"].default_value = (*colour, 1.0)
                    bsdf.inputs["Emission Strength"].default_value = 0.0
                    nodes.append(bsdf)
        spot = None
        if kind in BEAMS and colour == WHITE:
            energy, angle, pitch = BEAMS[kind]
            data = bpy.data.lights.new(
                f"Beam_{group.name}", "SPOT" if angle else "POINT"
            )
            data.energy = 0.0
            data.color = colour
            data.shadow_soft_size = 0.02
            data["energy_on"] = energy
            if angle:
                data.spot_size = math.radians(angle)
                data.spot_blend = 0.6
            spot = bpy.data.objects.new(data.name, data)
            frame = group.matrix_world
            x_axis = frame.col[0].xyz.normalized()
            aim = x_axis - Vector((0, 0, math.tan(math.radians(pitch))))
            # A spot shines along its -Z: aim it along the group's X axis, just past the lens.
            spot.matrix_world = Matrix.LocRotScale(
                frame.translation + x_axis * 0.05, aim.to_track_quat("-Z", "Y"), None
            )
            scene.collection.objects.link(spot)
        lamps.append((group, kind, side, nodes, spot))
    return lamps


def switch(lamps, types, view, strength):
    """Turn on the lamps whose type matches `types` and that face the camera's end of the car."""
    count = 0
    for group, kind, side, nodes, spot in lamps:
        # "Brake" also matches Brake_Center; "Indicator_Left" only the left indicators.
        on = any(
            t in (kind, f"{kind}_{side}") or kind.startswith(t + "_") for t in types
        )
        if on and types == ["Fog"]:
            on = (group.matrix_world.translation.x > 0) == (view == "front")
        for bsdf in nodes:
            bsdf.inputs["Emission Strength"].default_value = strength if on else 0.0
        if spot:
            spot.data.energy = spot.data["energy_on"] if on else 0.0
        count += on
    return count


def place_camera(scene, view):
    meshes = [o for o in scene.objects if o.type == "MESH" and o.name != "Ground"]
    corners = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
    lo = Vector([min(c[i] for c in corners) for i in range(3)])
    hi = Vector([max(c[i] for c in corners) for i in range(3)])
    # Aim low and past the lit end of the car so the beam on the road is in the frame.
    centre = Vector(
        (
            (lo.x + hi.x) / 2 + VIEWS[view].x * (hi.x - lo.x) * 0.3,
            (lo.y + hi.y) / 2,
            lo.z + (hi.z - lo.z) * 0.25,
        )
    )
    cam = scene.camera
    if cam is None:
        cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
        scene.collection.objects.link(cam)
        scene.camera = cam
    cam.data.lens = 35
    cam.location = centre + VIEWS[view].normalized() * (hi - lo).length * 1.5
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()


def render_file(path, outdir, scenarios, args):
    """Render one .blend file and return {(scenario, view): (image path, lit group count)}."""
    bpy.ops.wm.open_mainfile(filepath=str(path))
    scene = bpy.context.scene
    for obj in scene.objects:
        obj.hide_render = False
        if obj.type == "LIGHT":  # drop lights saved in the file
            bpy.data.objects.remove(obj)
    setup_device(scene, args.samples)
    setup_night(scene)
    scene.render.resolution_x, scene.render.resolution_y = args.resolution
    scene.render.image_settings.file_format = "WEBP"
    lamps = prepare_lamps(scene)

    results = {}
    for scenario in scenarios:
        types, views, strength = SCENARIOS[scenario]
        for view in views:
            count = switch(lamps, types, view, strength)
            image = outdir / path.stem / f"{scenario}_{view}.webp"
            results[scenario, view] = (image, count)
            if count == 0:
                continue  # nothing to see; the index marks it as missing
            place_camera(scene, view)
            scene.render.filepath = str(image)
            bpy.ops.render.render(write_still=True)
    return results


def write_index(outdir, all_results, scenarios):
    columns = [(s, v) for s in scenarios for v in SCENARIOS[s][1]]
    rows = []
    for stem, results in all_results.items():
        cells = [f"<th>{html.escape(stem)}</th>"]
        for key in columns:
            image, count = results[key]
            if count:
                rel = image.relative_to(outdir).as_posix()
                cells.append(
                    f'<td><a href="{rel}"><img src="{rel}" loading="lazy"></a><br>{count} groups</td>'
                )
            else:
                cells.append('<td class="none">none</td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")
    header = "".join(f"<th>{s}<br>{v}</th>" for s, v in columns)
    (outdir / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Vehicle lights</title>"
        "<style>body{background:#111;color:#ddd;font:13px sans-serif}"
        "table{border-collapse:collapse}th,td{border:1px solid #333;padding:4px;text-align:center}"
        "th{position:sticky;top:0;background:#222}tbody th{left:0;position:sticky;background:#222}"
        "img{width:240px;display:block}.none{color:#a55}</style>"
        f"<table><thead><tr><th></th>{header}</tr></thead><tbody>{''.join(rows)}</tbody></table>\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "blends", nargs="*", type=Path, help="default: src/vehicles/*/*.blend"
    )
    parser.add_argument("--outdir", type=Path, default=Path("build/light-renders"))
    parser.add_argument(
        "--only", help=f"comma-separated scenarios out of {','.join(SCENARIOS)}"
    )
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument(
        "--resolution", type=int, nargs=2, default=(640, 400), metavar=("X", "Y")
    )
    args = parser.parse_args()

    blends = args.blends or sorted(Path(p) for p in glob.glob("src/vehicles/*/*.blend"))
    scenarios = args.only.split(",") if args.only else list(SCENARIOS)
    unknown = set(scenarios) - set(SCENARIOS)
    if unknown:
        parser.error(f"unknown scenarios: {', '.join(sorted(unknown))}")
    outdir = args.outdir.resolve()
    all_results = {}
    for path in blends:
        print(f"Rendering lights of {path}")
        all_results[path.stem] = render_file(path.resolve(), outdir, scenarios, args)
        write_index(outdir, all_results, scenarios)  # usable while the rest renders
    print(f"Wrote {outdir / 'index.html'}")


if __name__ == "__main__":
    main()
