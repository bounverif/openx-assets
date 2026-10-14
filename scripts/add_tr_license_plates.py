"""Add Turkish-style license plate decals to vehicle .blend files.

The decal (black border, blue TR band, white field and black lettering) is
modelled as flat geometry and joined into each existing License_Plate_N mesh,
so it survives GLB, FBX and OSGB export without textures.

Usage:
    python scripts/add_tr_license_plates.py src/vehicles/*/*.blend [--text VEVALABS] [--replace]
"""

import argparse

import bpy  # must precede bmesh when using the bpy module
import bmesh
from mathutils import Matrix, Vector

MATERIALS = {
    "License_Plate_White": (0.9, 0.9, 0.9, 1.0),
    "License_Plate_Blue": (0.0, 0.08, 0.6, 1.0),
    "License_Plate_Black": (0.01, 0.01, 0.01, 1.0),
}

# Proportions of a 520 x 110 mm Turkish plate, relative to plate height
BORDER = 0.03
BAND_WIDTH = 0.36
TEXT_HEIGHT = 0.70
BAND_TEXT_HEIGHT = 0.28

# Offsets along the plate normal, in meters. Border, band and field share one
# layer without overlapping; only the lettering overlaps them. The gaps are
# large enough to avoid z-fighting in real-time viewers at a distance.
OFFSET_FIELD = 0.001
OFFSET_TEXT = 0.0025


def get_material(name):
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
        bsdf = material.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = MATERIALS[name]
        bsdf.inputs["Roughness"].default_value = 0.4
        material.diffuse_color = MATERIALS[name]
    return material


def find_plate_face(obj):
    """Return (center, u, v, n, width, height) of the plate's front surface.

    Plate meshes vary (single quads, split ngons, frames, flipped normals), so
    the plane is fitted to all roughly front/back-facing polygons rather than
    taken from a single face.
    """
    world = obj.matrix_world
    normal_matrix = world.to_3x3().inverted_safe().transposed()
    mesh = obj.data
    points = [world @ v.co for v in mesh.vertices]
    center_x = sum(p.x for p in points) / len(points)
    outward = Vector((1.0 if center_x > 0 else -1.0, 0.0, 0.0))

    faces = []
    for poly in mesh.polygons:
        n = (normal_matrix @ poly.normal).normalized()
        if abs(n.dot(outward)) > 0.7:
            area = sum(
                (
                    (points[poly.vertices[0]] - points[a]).cross(
                        points[poly.vertices[0]] - points[b]
                    )
                ).length
                / 2
                for a, b in zip(poly.vertices[1:], poly.vertices[2:])
            )
            faces.append((n if n.dot(outward) > 0 else -n, world @ poly.center, area))
    if not faces:
        raise RuntimeError(f"{obj.name}: no front-facing polygon found")

    n = sum((f[0] * f[2] for f in faces), Vector()).normalized()
    v = (Vector((0, 0, 1)) - n * n.z).normalized()
    u = v.cross(n)

    # The decal covers the whole plate outline, so sit just in front of its
    # outermost point; some plates have raised centers or frames
    plane = max(p.dot(n) for p in points)

    us = [p.dot(u) for p in points]
    vs = [p.dot(v) for p in points]
    width, height = max(us) - min(us), max(vs) - min(vs)
    center = u * (min(us) + max(us)) / 2 + v * (min(vs) + max(vs)) / 2 + n * plane

    # Bring the decal forward if surrounding bodywork would cover part of it
    depsgraph = bpy.context.evaluated_depsgraph_get()
    push = 0.0
    for i in range(11):
        for j in range(5):
            p = (
                center
                + u * width * (i / 10 - 0.5) * 0.98
                + v * height * (j / 4 - 0.5) * 0.98
            )
            hit, location, _, _, hit_obj, _ = bpy.context.scene.ray_cast(
                depsgraph, p + n * 0.5, -n
            )
            if hit and hit_obj.name != obj.name:
                push = max(push, (location - p).dot(n))
    if push > 0.01:
        print(
            f"  {obj.name}: covered by {push * 1000:.0f} mm of other geometry, not adjusting"
        )
    elif push > 0:
        center += n * push
    return center, u, v, n, width, height


def add_quad(bm, x0, y0, x1, y1, z, material_index):
    verts = [
        bm.verts.new((x, y, z)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    ]
    bm.faces.new(verts).material_index = material_index


def add_text(bm, body, height, max_width, cx, cy, z, material_index):
    curve = bpy.data.curves.new("plate_text", "FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.resolution_u = 4
    curve.fill_mode = "BOTH"
    text_obj = bpy.data.objects.new("plate_text", curve)
    bpy.context.scene.collection.objects.link(text_obj)

    # Measure at unit cap height, then fit inside the available width
    curve.size = 1.0
    bpy.context.view_layer.update()
    xs = [c[0] for c in text_obj.bound_box]
    ys = [c[1] for c in text_obj.bound_box]
    scale = min(height / (max(ys) - min(ys)), max_width / (max(xs) - min(xs)))
    dx = cx - scale * (min(xs) + max(xs)) / 2
    dy = cy - scale * (min(ys) + max(ys)) / 2

    mesh = bpy.data.meshes.new_from_object(
        text_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    )
    mesh.transform(Matrix.Translation((dx, dy, z)) @ Matrix.Scale(scale, 4))
    # The decal is untextured; don't add UV layers to plates that have none
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])
    for poly in mesh.polygons:
        poly.material_index = material_index
    bm.from_mesh(mesh)

    bpy.data.objects.remove(text_obj)
    bpy.data.curves.remove(curve)
    bpy.data.meshes.remove(mesh)


def build_decal(text, width, height, slots):
    """Build the decal in plate space: x right, y up, z outward."""
    bm = bmesh.new()
    w2, h2 = width / 2, height / 2
    border = BORDER * height
    band = BAND_WIDTH * height

    # Border as a frame around the band and field, not an underlay
    black = slots["License_Plate_Black"]
    add_quad(bm, -w2, -h2, -w2 + border, h2, OFFSET_FIELD, black)
    add_quad(bm, w2 - border, -h2, w2, h2, OFFSET_FIELD, black)
    add_quad(bm, -w2 + border, -h2, w2 - border, -h2 + border, OFFSET_FIELD, black)
    add_quad(bm, -w2 + border, h2 - border, w2 - border, h2, OFFSET_FIELD, black)

    x0 = -w2 + border
    add_quad(
        bm,
        x0,
        -h2 + border,
        x0 + band,
        h2 - border,
        OFFSET_FIELD,
        slots["License_Plate_Blue"],
    )
    add_quad(
        bm,
        x0 + band,
        -h2 + border,
        w2 - border,
        h2 - border,
        OFFSET_FIELD,
        slots["License_Plate_White"],
    )

    add_text(
        bm,
        "TR",
        BAND_TEXT_HEIGHT * height,
        0.7 * band,
        x0 + band / 2,
        -h2 + border + 0.3 * height,
        OFFSET_TEXT,
        slots["License_Plate_White"],
    )
    field_left, field_right = x0 + band, w2 - border
    add_text(
        bm,
        text,
        TEXT_HEIGHT * height,
        0.9 * (field_right - field_left),
        (field_left + field_right) / 2,
        0.0,
        OFFSET_TEXT,
        slots["License_Plate_Black"],
    )
    return bm


def is_decal_slot(slot):
    return slot.material is not None and slot.material.name in MATERIALS


def remove_plate(obj):
    """Remove a previously added decal, leaving the original plate mesh."""
    indices = [i for i, s in enumerate(obj.material_slots) if is_decal_slot(s)]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    faces = [f for f in bm.faces if f.material_index in indices]
    bmesh.ops.delete(bm, geom=faces, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    for i in reversed(indices):
        obj.data.materials.pop(index=i)

    # Earlier versions added an all-zero UV layer to plates without UVs
    for layer in list(obj.data.uv_layers):
        if all(d.uv.length == 0 for d in layer.data):
            obj.data.uv_layers.remove(layer)


def add_plate(obj, text, replace=False):
    if any(is_decal_slot(s) for s in obj.material_slots):
        if not replace:
            print(f"  {obj.name}: already has a plate decal, skipping")
            return
        remove_plate(obj)

    if obj.data.users > 1:
        obj.data = obj.data.copy()

    center, u, v, n, width, height = find_plate_face(obj)
    slots = {}
    for name in MATERIALS:
        obj.data.materials.append(get_material(name))
        slots[name] = len(obj.data.materials) - 1

    bm = build_decal(text, width, height, slots)
    plate_to_world = Matrix(
        (
            (u.x, v.x, n.x, center.x),
            (u.y, v.y, n.y, center.y),
            (u.z, v.z, n.z, center.z),
            (0, 0, 0, 1),
        )
    )
    bm.transform(obj.matrix_world.inverted() @ plate_to_world)

    decal = bpy.data.meshes.new("plate_decal")
    bm.to_mesh(decal)
    bm.free()

    # Append the decal to the plate mesh, keeping its existing data intact
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.from_mesh(decal)
    bm.to_mesh(obj.data)
    bm.free()
    bpy.data.meshes.remove(decal)
    print(
        f"  {obj.name}: {width * 1000:.0f} x {height * 1000:.0f} mm, normal {tuple(round(c, 2) for c in n)}"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("blendfiles", nargs="+")
    parser.add_argument("--text", default="VEVALABS")
    parser.add_argument(
        "--replace", action="store_true", help="rebuild existing plate decals"
    )
    args = parser.parse_args()

    for blendpath in args.blendfiles:
        print(f"Processing {blendpath}")
        bpy.ops.wm.open_mainfile(filepath=blendpath)
        plates = [
            o
            for o in bpy.data.objects
            if o.type == "MESH"
            and o.name.startswith("License_Plate_")
            and o.parent
            and o.parent.name.startswith("Grp_License_Plate_")
        ]
        if not plates:
            print("  no License_Plate_N meshes found")
            continue
        for obj in plates:
            add_plate(obj, args.text, args.replace)
        bpy.ops.wm.save_mainfile(filepath=blendpath)


if __name__ == "__main__":
    main()
