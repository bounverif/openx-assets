"""Check the light groups of vehicle .blend files against the AGENTS.md rules.

For every Grp_Light_* empty this checks the name, side, emitter mesh, local
frame (origin on the element, Z up, X along the main emission direction),
materials (Lamp_*, opaque, switched off), that the emitter can be seen from
its emission direction through glass only, left/right mirror symmetry and
index order. Licence plate lamps must instead see their plate.

Usage: python scripts/test_lights.py [src/vehicles/<name>/<name>.blend ...]
Without arguments every src/vehicles/*/*.blend is checked.
Prints the failures (all checks with -v) and exits with status 1 if any fail.
Never saves the files.
"""

import argparse
import re
import sys
from pathlib import Path

import bpy  # must come first: it makes bmesh and mathutils importable
import bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

TYPES = "Corner|Day|Fog|High_Beam|Indicator|Low_Beam|Park|Position|Reverse|Tail|Brake"
GROUP_NAME = re.compile(
    rf"^Grp_Light_(?:(?P<type>{TYPES})_(?P<side>Left|Right)"
    r"|(?P<center>Brake_Center|License_Plate|Warning))_(?P<index>\d+)$"
)
UP = Vector((0, 0, 1))
# Lamps that the default state hides on purpose: (file stem, group name).
HIDDEN = {
    # pop-up headlamps, modelled retracted
    ("honda_prelude_1983", "Grp_Light_High_Beam_Left_0"),
    ("honda_prelude_1983", "Grp_Light_High_Beam_Right_0"),
    ("honda_prelude_1983", "Grp_Light_Low_Beam_Left_0"),
    ("honda_prelude_1983", "Grp_Light_Low_Beam_Right_0"),
}


class Report:
    def __init__(self, verbose):
        self.verbose = verbose
        self.failures = 0

    def check(self, ok, name, message):
        if not ok:
            self.failures += 1
        if not ok or self.verbose:
            print(f"  {'PASS' if ok else 'FAIL'} {name}: {message}")

    def info(self, name, message):
        print(f"  INFO {name}: {message}")


def occluder_tree():
    """BVH of every mesh face except glass (blended materials) and lamp emitters."""
    occ = bmesh.new()
    for obj in bpy.data.objects:
        if obj.type != "MESH" or obj.name.startswith("Light_"):
            continue
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.transform(obj.matrix_world)
        glass = {
            i
            for i, slot in enumerate(obj.material_slots)
            if slot.material and slot.material.surface_render_method == "BLENDED"
        }
        bmesh.ops.delete(
            bm, geom=[f for f in bm.faces if f.material_index in glass], context="FACES"
        )
        mesh = bpy.data.meshes.new("occluder")
        bm.to_mesh(mesh)
        occ.from_mesh(mesh)
    return BVHTree.FromBMesh(occ)


def world_bbox(obj):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    lo = Vector([min(v[i] for v in verts) for i in range(3)])
    hi = Vector([max(v[i] for v in verts) for i in range(3)])
    return lo, hi


def check_plate_lamp(report, name, lamp, centre, tree):
    """The lamp must see points spread over the face of its nearest licence plate."""
    plates = [
        o
        for o in bpy.data.objects
        if o.type == "MESH" and re.match(r"^License_Plate_\d+$", o.name)
    ]
    if not plates:
        report.check(False, name, "no License_Plate_<n> mesh to light")
        return
    plate = min(plates, key=lambda p: (p.matrix_world.translation - centre).length)
    lo, hi = world_bbox(plate)
    outwards = Vector((-1 if plate.matrix_world.translation.x < 0 else 1, 0, 0))
    normal = (lamp.matrix_world.to_3x3() @ lamp.data.polygons[0].normal).normalized()
    targets = []
    for dy in (-0.12, 0.0, 0.12):
        y = min(max(centre.y + dy, lo.y + 0.02), hi.y - 0.02)  # stay on the plate
        for z in (lo.z + 0.015, (lo.z + hi.z) / 2, hi.z - 0.015):
            start = Vector((lo.x if outwards.x < 0 else hi.x, y, z)) + outwards * 0.3
            hit = tree.ray_cast(start, -outwards, 0.6)[0]  # a point on the plate face
            if hit is not None:
                targets.append(hit)
    seen = 0
    for target in targets:
        d = target - centre
        dist = d.length
        d.normalize()
        hit = tree.ray_cast(centre + d * 0.002, d, dist + 0.05)
        if (
            normal.dot(d) > 0
            and hit[0] is not None
            and hit[3] >= dist - 0.003
            and lo.z <= hit[0].z <= hi.z
        ):
            seen += 1
    report.check(seen >= 7, name, f"lamp sees {seen}/9 points on {plate.name}")


def check_emission_path(report, name, lamp, x_axis, tree):
    """At least 60% of the emitter area facing along X must see out through glass only.

    Rays start at each face centre and at points halfway to its corners, so a
    seam across one large face doesn't hide all of it. Side walls are skipped:
    a recessed lamp's walls are meant to be covered.
    """
    rot = lamp.matrix_world.to_3x3()
    facing = clear = 0.0
    for poly in lamp.data.polygons:
        if (rot @ poly.normal).normalized().dot(x_axis) < 0.2:
            continue  # side walls and back faces
        points = [poly.center] + [
            poly.center.lerp(lamp.data.vertices[v].co, 0.6) for v in poly.vertices
        ]
        unblocked = sum(
            tree.ray_cast(lamp.matrix_world @ p + x_axis * 0.002, x_axis, 5.0)[0]
            is None
            for p in points
        )
        facing += poly.area
        clear += poly.area * unblocked / len(points)
    ratio = clear / facing if facing else 0.0
    report.check(
        ratio >= 0.6,
        name,
        f"{100 * ratio:.0f}% of the emitting area unobstructed along X",
    )


def check_group(report, group, tree):
    """Run the per-group checks and return (position, face count) for the pair checks."""
    name = group.name
    m = GROUP_NAME.match(name)
    report.check(bool(m), name, "name follows Grp_Light_<Type>_<Left|Right>_<n>")
    if not m:
        return None

    frame = group.matrix_world
    pos = frame.translation.copy()
    x_axis = frame.col[0].xyz.normalized()
    z_axis = frame.col[2].xyz.normalized()
    meshes = [c for c in group.children if c.type == "MESH"]
    report.check(
        len(meshes) == 1 and meshes[0].name == name[4:],
        name,
        f"one emitter mesh named {name[4:]} (got {[c.name for c in meshes]})",
    )
    if not meshes:
        return None
    lamp = meshes[0]
    report.check(
        lamp.matrix_basis == Matrix.Identity(4)
        and lamp.matrix_parent_inverse == Matrix.Identity(4),
        name,
        "emitter has an identity transform",
    )

    lo, hi = world_bbox(lamp)
    centre = (lo + hi) / 2
    report.check(
        (centre - pos).length < 0.03,
        name,
        f"origin {1000 * (centre - pos).length:.0f} mm from element centre",
    )
    if m["side"]:
        report.check(
            (pos.y > 0) == (m["side"] == "Left"),
            name,
            f"{m['side']} lamp at y = {pos.y:+.3f}",
        )
    report.check(z_axis.dot(UP) > 0.999, name, "Z axis up")
    if m["type"] == "Indicator" and abs(x_axis.y) > 0.9:
        report.check(x_axis.y * pos.y > 0, name, "side repeater X points outwards")
    elif m["center"] != "Warning":
        front = pos.x > 0
        report.check(
            abs(x_axis.x) > 0.999 and (x_axis.x > 0) == front,
            name,
            f"X points {'forward' if front else 'rearward'} (main emission direction)",
        )

    materials = sorted({s.material.name for s in lamp.material_slots if s.material})
    report.check(
        materials and all(n.startswith("Lamp_") for n in materials),
        name,
        f"Lamp_* materials only (got {materials})",
    )
    for slot in lamp.material_slots:
        bsdf = (
            slot.material.node_tree.nodes.get("Principled BSDF")
            if slot.material
            else None
        )
        report.check(
            bsdf is not None
            and bsdf.inputs["Alpha"].default_value == 1
            and bsdf.inputs["Emission Strength"].default_value == 0,
            name,
            f"{slot.material.name if slot.material else None} is opaque and switched off",
        )
    report.check(
        all(p.area > 1e-7 for p in lamp.data.polygons),
        name,
        f"{len(lamp.data.polygons)} faces, none degenerate",
    )

    if m["center"] == "License_Plate":
        check_plate_lamp(report, name, lamp, centre, tree)
    elif (Path(bpy.data.filepath).stem, name) in HIDDEN:
        report.info(
            name, "hidden in the default state by design; emission path not checked"
        )
    else:
        check_emission_path(report, name, lamp, x_axis, tree)
    return pos, len(lamp.data.polygons)


def check_pairs(report, lamps):
    """Left lamps mirror right lamps; indices run front to rear (plates: right to left)."""
    for name, (pos, faces) in sorted(lamps.items()):
        if "_Left_" not in name and "_Right_" not in name:
            continue
        other = (
            name.replace("_Left_", "_Right_")
            if "_Left_" in name
            else name.replace("_Right_", "_Left_")
        )
        if other not in lamps:
            report.info(
                name, f"no {other}; fine for a single lamp such as a rear fog light"
            )
            continue
        if "_Right_" in name:
            continue  # each pair is checked once, from its left lamp
        opos, ofaces = lamps[other]
        mirrored = (
            opos - Vector((pos.x, -pos.y, pos.z))
        ).length < 0.01 and ofaces == faces
        report.check(mirrored, name, f"mirrored by {other}")

    bases = {}
    for name, (pos, _) in lamps.items():
        base, index = name.rsplit("_", 1)
        bases.setdefault(base, []).append((int(index), pos))
    for base, entries in sorted(bases.items()):
        if len(entries) < 2:
            continue
        entries.sort(key=lambda e: e[0])
        if base.endswith("License_Plate"):
            ok = all(a[1].y < b[1].y for a, b in zip(entries, entries[1:]))
            report.check(ok, base, "indices run right to left")
        else:
            ok = all(a[1].x > b[1].x for a, b in zip(entries, entries[1:]))
            report.check(ok, base, "indices run front to rear")


def check_file(path, verbose):
    """Check one .blend file and return the number of failed checks."""
    bpy.ops.wm.open_mainfile(filepath=path)
    report = Report(verbose)
    tree = occluder_tree()
    lamps = {}
    for group in sorted(
        (o for o in bpy.data.objects if o.name.startswith("Grp_Light")),
        key=lambda o: o.name,
    ):
        result = check_group(report, group, tree)
        if result:
            lamps[group.name] = result
    check_pairs(report, lamps)
    print(f"{path}: {len(lamps)} light groups, {report.failures} failures")
    return report.failures


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "blends", nargs="*", help=".blend files to check (default: all vehicles)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="print passing checks too"
    )
    args = parser.parse_args()
    vehicles = Path(__file__).resolve().parent.parent / "src" / "vehicles"
    blends = args.blends or [str(p) for p in sorted(vehicles.glob("*/*.blend"))]
    failures = sum(check_file(path, args.verbose) for path in blends)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
