"""Add licence plate lamps above the rear plate of vehicle .blend files.

Each lamp is a small downward-facing Lamp_White quad in its own
Grp_Light_License_Plate_<n> group (X rearward, Z up), parented like the plate
so it follows a tailgate. Lamps go on the underside of the ledge above the
plate, as a pair if both fit, else one in the middle. Where nothing overhangs
the plate, a small Black_Plastic hood is added above it to carry one lamp.
Every placement must pass the plate visibility check of test_lights.py.

Usage:
    python scripts/add_license_plate_lights.py src/vehicles/*/*.blend [--replace]
"""

import argparse
import contextlib
import io
import math

import bpy  # must precede bmesh when using the bpy module
import bmesh
from mathutils import Matrix, Vector

from test_lights import Report, check_plate_lamp, occluder_tree

HALF_DEPTH = 0.004  # lamp quad, along the vehicle X axis
HALF_WIDTH = 0.025
PAIR_OFFSET = 0.12  # lamp pair at the plate centre +- this, in Y
HOOD = "License_Plate_Lamp_Housing"
UP = Vector((0, 0, 1))
REAR = Vector((-1, 0, 0))


def plate_face(tree, plate):
    """World bbox of the plate and the x of its face near the top edge."""
    verts = [plate.matrix_world @ v.co for v in plate.data.vertices]
    lo = Vector([min(v[i] for v in verts) for i in range(3)])
    hi = Vector([max(v[i] for v in verts) for i in range(3)])
    hit = tree.ray_cast(
        Vector((lo.x - 0.3, (lo.y + hi.y) / 2, hi.z - 0.008)), -REAR, 0.6
    )[0]
    return lo, hi, hit.x if hit else lo.x


def ledge_spot(tree, x_face, y, top):
    """Centre and normal of a lamp quad under the ledge above the plate, or None."""
    for step in range(16):
        dx = HALF_DEPTH + 0.0025 * step
        hit, normal = tree.ray_cast(Vector((x_face - dx, y, top + 0.002)), UP, 0.08)[:2]
        if hit is None or normal.z > -0.5:
            continue
        # the whole quad must sit under the same surface
        corners = [
            tree.ray_cast(
                Vector(
                    (x_face - dx + sx * HALF_DEPTH, y + sy * HALF_WIDTH, top + 0.002)
                ),
                UP,
                0.08,
            )[0]
            for sx in (-1, 1)
            for sy in (-1, 1)
        ]
        if all(c is not None and abs(c.z - hit.z) < 0.004 for c in corners):
            return hit + normal * 0.0005, normal
    return None


def sees_plate(tree, centre, normal):
    """Run test_lights' plate check on a throwaway quad."""
    lamp = make_quad("Probe", Matrix.Translation(centre), centre, normal)
    report = Report(verbose=False)
    with contextlib.redirect_stdout(io.StringIO()):
        check_plate_lamp(report, "probe", lamp, centre, tree)
    mesh = lamp.data
    bpy.data.objects.remove(lamp)
    bpy.data.meshes.remove(mesh)
    return report.failures == 0


def make_quad(name, frame, centre, normal):
    """Mesh object with one quad facing `normal`, vertices relative to `frame`."""
    u = (REAR - normal * REAR.dot(normal)).normalized()
    v = normal.cross(u)
    corners = [
        centre + u * a * HALF_DEPTH + v * b * HALF_WIDTH
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    to_local = frame.inverted()
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([to_local @ c for c in corners], [], [(0, 1, 2, 3)])
    if (frame.to_3x3() @ mesh.polygons[0].normal).dot(normal) < 0:
        mesh.flip_normals()
    mesh.materials.append(bpy.data.materials["Lamp_White"])
    return bpy.data.objects.new(name, mesh)


def add_hood(tree, plate_group, lo, hi, x_face):
    """Black box above the plate, from the body (or just behind the plate) out past its face."""
    yc = (lo.y + hi.y) / 2
    z0, z1 = hi.z + 0.012, hi.z + 0.032
    hit = tree.ray_cast(Vector((x_face - 0.05, yc, (z0 + z1) / 2)), -REAR, 0.2)[0]
    back = hit.x + 0.003 if hit else hi.x + 0.005
    x0, x1 = x_face - 0.035, back
    verts = [
        (x, y, z) for x in (x0, x1) for y in (yc - 0.06, yc + 0.06) for z in (z0, z1)
    ]
    faces = [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
    ]
    mesh = bpy.data.meshes.new(HOOD)
    parent = plate_group.parent
    if parent.name == "Grp_Exterior_Dynamic":
        parent = bpy.data.objects["Grp_Exterior_Static"]
    to_local = parent.matrix_world.inverted()
    mesh.from_pydata([to_local @ Vector(p) for p in verts], [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    material = bpy.data.materials.get("Black_Plastic")
    if material is None:
        material = bpy.data.materials.new("Black_Plastic")
        material.node_tree.nodes["Principled BSDF"].inputs[
            "Base Color"
        ].default_value = (0.02, 0.02, 0.02, 1)
    mesh.materials.append(material)
    hood = bpy.data.objects.new(HOOD, mesh)
    bpy.context.scene.collection.objects.link(hood)
    hood.parent = parent
    return Vector(((x_face - 0.015), yc, z0 - 0.0005)), Vector((0, 0, -1))


def add_lamp(index, plate_group, centre, normal):
    group = bpy.data.objects.new(f"Grp_Light_License_Plate_{index}", None)
    group.empty_display_size = 0.05
    frame = Matrix.Translation(centre) @ Matrix.Rotation(math.pi, 4, "Z")
    lamp = make_quad(f"Light_License_Plate_{index}", frame, centre, normal)
    for obj in (group, lamp):
        bpy.context.scene.collection.objects.link(obj)
    group.parent = plate_group.parent
    group.matrix_world = frame
    lamp.parent = group


def add_lights(replace):
    old = [
        o
        for o in bpy.data.objects
        if o.name.startswith(("Grp_Light_License_Plate_", "Light_License_Plate_", HOOD))
    ]
    if old and not replace:
        print(f"  has {sorted(o.name for o in old)}, skipping")
        return False
    for obj in old:
        bpy.data.objects.remove(obj)
    plates = [
        o
        for o in bpy.data.objects
        if o.type == "MESH" and o.name.startswith("License_Plate_") and o.parent
    ]
    plate = min(plates, key=lambda p: p.matrix_world.translation.x)  # the rear plate
    tree = occluder_tree()
    lo, hi, x_face = plate_face(tree, plate)
    yc = (lo.y + hi.y) / 2
    for ys in ([yc - PAIR_OFFSET, yc + PAIR_OFFSET], [yc]):
        spots = [ledge_spot(tree, x_face, y, hi.z) for y in ys]
        if all(s and sees_plate(tree, *s) for s in spots):
            break
    else:
        spots = [add_hood(tree, plate.parent, lo, hi, x_face)]
        print("  nothing above the plate: added", HOOD)
    for index, (centre, normal) in enumerate(spots):
        add_lamp(index, plate.parent, centre, normal)
    print(
        f"  {len(spots)} lamp(s) under {plate.parent.parent.name}/{plate.parent.name}"
    )
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("blendfiles", nargs="+")
    parser.add_argument(
        "--replace", action="store_true", help="rebuild existing plate lamps"
    )
    args = parser.parse_args()

    for blendpath in args.blendfiles:
        print(f"Processing {blendpath}")
        bpy.ops.wm.open_mainfile(filepath=blendpath)
        if add_lights(args.replace):
            bpy.ops.wm.save_mainfile(filepath=blendpath)


if __name__ == "__main__":
    main()
