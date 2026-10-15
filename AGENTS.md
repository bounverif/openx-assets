<!--
SPDX-FileCopyrightText: 2026 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
SPDX-License-Identifier: MPL-2.0
-->

# AGENTS.md

## Turning a raw model into a collection item

A raw model is a third-party download (usually a Sketchfab `.glb`) dropped into
`collections-devel/`, which is git-ignored. A collection item is a finished
vehicle under `src/vehicles/<name>/` that `make assets` can export to GLB, FBX, USDZ,
OSGB and `.xoma`. Never modify the raw file; work on a copy in a `.blend`.

`bpy` (Blender 5.2 LTS, Python 3.13) is needed for every Blender step. Run
scripts as `python script.py` with the `openx-assets` package installed
(`make install`), not inside the Blender GUI.

### 1. Inspect the raw model and record provenance

Before editing, read the glTF JSON chunk and write down:

- Author, source URL and license, from `asset.extras` (Sketchfab puts them
  there). All current items derive from CC-BY-4.0 sources; flag anything
  more restrictive before doing further work.
- World-space bounding box, wheelbase, wheel diameter and track width. Compare
  them with the real vehicle's specs; rescale only if they are clearly off.
- How the wheels are modelled. Sketchfab exports often merge both wheels of
  an axle into one mesh (one tire mesh spanning ±x); these must be split.
- Triangle count, material count, embedded textures and extensions
  (`KHR_materials_transmission` etc.).

A CC-BY label is only the uploader's claim. Stop and ask the maintainer if any
of these checks fails:

- Description and bio: "rework", "port" or "from game" means someone else made
  the base mesh.
- Game leftovers: game textures (a "SAN ANDREAS" plate), converter nodes
  (`*.obj.cleaner.*`), materials named after another car (`body focus` in a
  Volvo).
- Match the page: same `faceCount` and look as the page, named after what the
  mesh really is, with every combined upload (body, wheels) credited.

### 2. Name and place the item

- Name: `<make>_<model>_<year>[_<variant>]`, all lowercase, with no UNECE
  class prefix. If a matching spec file exists in `xom3d/vehicles/<make>/`,
  reuse its name without the `m1_`/`n1_`/`n2_` prefix. Example:
  `volvo_ex30_2024`.
- Files: `src/vehicles/<name>/<name>.blend`, `<name>.xoma`,
  `<name>.thumbnail.webp`. `.blend` files are stored in Git LFS.

### 3. Coordinate frame and origin

In Blender: +X forward, +Y left, +Z up, meters, all object scales applied.
The bounding box is centred on X and Y and the lowest point (the tires) sits
at Z = 0. `xom3d.move_asset_to_origin` (`xom3d_utils.move_asset_to_origin`)
does the centring once the car faces +X. Remove the import wrapper empties
(`Sketchfab_model`, `GLTF_SceneRootNode`, `RootNode`, the 0.01-scaled `.fbx`
node) after applying their transforms.

### 4. Mesh tree (OpenMATERIAL 3D vehicle structure)

The node tree must follow the vehicle model structure in ASAM OpenMATERIAL 3D
v1.1.0, section "Vehicle structure". The source is
`content/07_geometry/object-vehicle/` in
<https://github.com/asam-ev/OpenMATERIAL-3D> (tag `v1.1.0-rc2`); check it when
in doubt.

Create the skeleton with **Object ▸ OpenX Assets ▸ Add Empty Vehicle
Structure** (`xom3d_vehicle_structure.add_empty_vehicle_structure`). Move each
empty to its origin, parent the meshes into it, then run **Trim Vehicle
Structure** to delete unused empties. The helper doesn't create mirror or
hitch groups, so add those by hand.

#### Naming

- Every node, mesh and material name is Capital_Snake_Case: `Body`,
  `Body_Glass`, `Black_Plastic`, `Wheel_0_1`. Some existing items predate this
  and use names like `black_plastic`; don't copy them.
- Empty (group) nodes start with `Grp_`. Use the keywords from the standard
  for standard parts. You may add your own groups, but they must sit under the
  exterior/interior and static/dynamic groups and follow the same naming.
- Suffix order: iterator, then type, then subtype. Iterators are integers
  starting at 0.
- Index order:
  - Axles: front to rear.
  - Wheels on an axle: right to left (+Y).
  - Left/right doors: front to rear.
  - Front/rear doors: right to left.
  - Lights, plates, mirrors, eyepoints: right to left, then front to rear.
  - Seats: `<row>` front to rear, then `<seat>` right to left.

#### Tree for a passenger car

Omit groups the vehicle doesn't have. (T) marks a group with its own local
frame (see the table below). (T) only appears in the docs, never in node
names.

```
Grp_Root                                        bbox centre on the ground, X fwd, Y left, Z up
  Grp_Exterior                                  identity transform
    Grp_Exterior_Dynamic                        identity transform
      Grp_Wheel_<axle>_<wheel> (T)              translation only (suspension along Z)
        Grp_Wheel_Steering_<axle>_<wheel> (T)   steers, doesn't roll: brake caliper
        Grp_Wheel_Steering_Rotating_<axle>_<wheel> (T)
          Wheel_<axle>_<wheel>                  steers and rolls: tire, rim, brake disc
      Grp_Rear_Axle_Center (T)                  empty; ASAM OSI host-vehicle frame
      Grp_Door_Left_<n> (T)                     door incl. its inner trim
        Grp_Mirror_Side_Mounting_Left_<n> (T)   door-mounted mirror
          Grp_Mirror_Side_Joint_Left_<n> (T)
            Grp_Mirror_Side_View_Left_<n> (T)   empty on the mirror glass
      Grp_Door_Right_<n> (T)
        Grp_Mirror_Side_Mounting_Right_<n> (T)
          Grp_Mirror_Side_Joint_Right_<n> (T)
            Grp_Mirror_Side_View_Right_<n> (T)
      Grp_Door_Front_<n> (T)                    bonnet
      Grp_Door_Rear_<n> (T)                     tailgate / trunk lid
      Grp_Door_Top_<n> (T)                      sunroof
      Grp_Convertible_Top
      Grp_License_Plate_<n> (T)
        License_Plate_<n>
      Grp_Light_<Type>_<Left|Right>_<n> (T)
        Light_<Type>_<Left|Right>_<n>
      Grp_Light_Brake_Center_<n> (T)            third brake light
      Grp_Light_License_Plate_<n> (T)
      Grp_Light_Warning_<n> (T)
      Grp_Hitch_Rear (T)                        tow bar, if modelled
        Grp_Hitch_Rear_Contact_Point (T)
    Grp_Exterior_Static                         identity transform
      Body, Body_Glass, lamp housings and lenses, ...
  Grp_Interior                                  identity transform
    Grp_Interior_Dynamic                        identity transform
      Grp_Eyepoint_<n> (T)                      empty
      Grp_Steering_Wheel (T)
        Steering_Wheel
      Grp_Seat_<row>_<seat> (T)
      Grp_Mirror_Rearview_Mounting_<n> (T)
        Grp_Mirror_Rearview_Joint_<n> (T)
          Grp_Mirror_Rearview_View_<n> (T)
    Grp_Interior_Static                         identity transform
      Interior_Static
```

`<Type>` is one of `Corner`, `Day`, `Fog`, `High_Beam`, `Indicator`,
`Low_Beam`, `Park`, `Position`, `Reverse`, `Tail` or `Brake`. Each light group
holds only the emitting part, such as a bulb or LED strip. Housings and clear
lenses that never change state belong in `Grp_Exterior_Static`.

#### Local frames of (T) groups

The empty's location and rotation define the frame. Meshes inside it have
their geometry relative to that frame, so apply the parent inverse (**Move
Empty Parent to Child** does this). The Y axis always completes a
right-handed frame.

| Group | Origin | X axis | Z axis |
|---|---|---|---|
| `Grp_Wheel_*`, `Grp_Wheel_Steering_*`, `Grp_Wheel_Steering_Rotating_*` | wheel geometric centre | vehicle forward | up |
| `Grp_Rear_Axle_Center` | centre of the rear axle | vehicle forward | up |
| `Grp_Door_*` | centre of the virtual hinge axis | along the closed door | along the hinge, so opening is a positive rotation |
| `Grp_License_Plate_*` | centre of the plate surface | out of the plate face | up |
| `Grp_Light_*` | centre of the light element | main emission direction (rear lights point backwards) | up |
| `Grp_Mirror_*_Mounting_*` | base of the mounting | vehicle forward | up |
| `Grp_Mirror_*_Joint_*` | the mirror's pivot joint | vehicle forward | up |
| `Grp_Mirror_*_View_*` | centre of the mirror glass | glass surface normal, outwards | up along the glass |
| `Grp_Eyepoint_*` | eye point | view direction | up |
| `Grp_Steering_Wheel` | wheel centre | along the steering column | up in neutral position |
| `Grp_Seat_*` | centre of the seat cushion | direction the seat faces | up |
| `Grp_Hitch_*` | mount point (`_Contact_Point`: coupling point) | vehicle forward | up |

Model everything in its default state: neutral load, wheels straight, doors
closed, lights off.

#### Rules this repository's tooling relies on

- `xom3d_utils.get_axle_info` reads `Grp_Wheel_0_*` (front) and
  `Grp_Wheel_1_*` (rear), where `_0` is right (−Y) and `_1` is left (+Y). It
  uses the empty's local location, so `Grp_Root`, `Grp_Exterior` and
  `Grp_Exterior_Dynamic` must keep identity transforms. `wheelDiameter` is
  computed as 2 × Z, so the car must sit on the ground (step 3).
- The wheel groups must have no rotation. Steering (Z), camber (X) and
  rolling (Y) are applied at run time.
- Sketchfab models often merge both wheels of an axle into one tire, rim or
  disc mesh. Split them by side before parenting.

#### Mesh requirements (OpenMATERIAL 3D §7.2)

- Real-world scale in metres.
- Meshes have outward-facing normals. Quads are fine in the `.blend`: the
  spec requires triangulated meshes, but the glTF and FBX exporters
  triangulate on export, so don't triangulate by hand.
- No empty meshes, LODs, duplicate or degenerate faces, or loose geometry.
- Every face has a PBR material.
- Recommended: one-sided faces, no n-gons, and as few polygons as the shape
  allows.

### 5. Geometry and materials

- Budget: the finished vehicles have 15k–80k triangles, 15–60 meshes and a
  GLB under 5 MB. Merge static parts by material and decimate or delete
  interior detail (seats, screens, door cards) first.
- Models must not include textures: use flat PBR materials only, and remove
  every image texture (baked AO, badges, tire sidewalls included).
- Glass: non-metallic, alpha 0.2, no transmission. Lamp and caliper
  materials must be opaque.
- Give materials descriptive Capital_Snake_Case names (`Body`, `Body_Glass`,
  `Black_Plastic`, `Lens_Red`, ...) and fix typos from the source.
  `Lamp_*` materials are for light-group emitters only; chrome reflector
  bowls in the static lamp housings use `Reflector`, retro-reflectors use
  `Reflector_Red` or `Reflector_Amber`. The exporter
  merges `.001` duplicates and strips clearcoat, but only in the exported
  files.
- Add license plates with
  `python scripts/add_tr_license_plates.py src/vehicles/<name>/<name>.blend`,
  then their lamps with
  `python scripts/add_license_plate_lights.py src/vehicles/<name>/<name>.blend`
  and check them with `python scripts/test_lights.py`.

### 6. `.xoma` metadata

Copy an existing `.xoma` (e.g. `volvo_ex30_2024.xoma`) and edit the
hand-written fields:

- `name`, `description`, `authors`.
- `license`: `"MPL-2.0 AND CC-BY-4.0"`.
- `copyrights`: our line plus
  `"(c) <year> <author> <https://sketchfab.com/<user>>, licensed under CC-BY-4.0"`.
  Never commit the `TODO` placeholder.
- `vehicleClassData`: `vehicleCategory`, `mass`, `performance` and
  `maxSteering`, taken from `xom3d/vehicles/<make>/<name>.xoma` or real-world
  specs.

`boundingBox`, axle geometry, `meshCount`, `triangleCount` and `uuid` are
recomputed on export, so don't edit them by hand.

### 7. Licensing

Add the item to the matching `[[annotations]]` block in
`src/REUSE.toml` (one block per original author), or create a new
block:

```toml
[[annotations]]
path = ["vehicles/<name>/**"]
SPDX-FileCopyrightText = [
    "<year> Dogan Ulus <dogan.ulus@bogazici.edu.tr>",
    "<year> <author> <https://sketchfab.com/<user>>, licensed under CC-BY-4.0"
]
SPDX-License-Identifier = "MPL-2.0 AND CC-BY-4.0"
```

### 8. Export, render and verify

```sh
openx-assets export src/vehicles --pattern '<name>/*.blend' --destdir /tmp/openx-assets/vehicles
openx-assets render src/vehicles --pattern '<name>/*.blend'   # writes <name>.thumbnail.webp
```

Then check:

- The exported `.xoma` bounding box and axles match the real vehicle within a
  few centimetres, and `positionZ` ≈ `wheelDiameter / 2`.
- The exported GLB's node names match the step 4 tree. Every (T) empty is at
  its defined origin, and each wheel spins about its own centre.
- `reuse lint` passes.
- The thumbnail looks right; add it to the gallery table in `README.adoc`.
