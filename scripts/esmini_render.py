"""Render every vehicle of the esmini bundle in esmini and tile the frames into one image.

Needs the `esmini` binary from https://github.com/esmini/esmini, Pillow, and an X
display (run it under `xvfb-run` on a headless machine). Each vehicle drives along
a straight road and the last frame is kept. Exits with status 1 if esmini fails or
logs a warning for any vehicle.
"""

import argparse
import pathlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 960, 540
TILE_WIDTH, TILE_HEIGHT, COLUMNS = 480, 270, 5
# Camera relative to the vehicle: x, y, z, heading, pitch.
CAMERA = "6,-8,2.2,2.2,0.15"
# The esmini binary package lacks the textures of its generated road; the road renders without them.
IGNORED_WARNINGS = ("asphalt.jpg not located", "grass.jpg not located")

ROAD = """<?xml version="1.0" encoding="UTF-8"?>
<OpenDRIVE>
  <header revMajor="1" revMinor="5" name="straight"/>
  <road name="straight" length="200" id="1" junction="-1">
    <planView><geometry s="0" x="0" y="0" hdg="0" length="200"><line/></geometry></planView>
    <lanes><laneSection s="0">
      <left><lane id="1" type="driving" level="false">
        <width sOffset="0" a="3.5" b="0" c="0" d="0"/>
        <roadMark sOffset="0" type="solid" color="standard" width="0.15"/>
      </lane></left>
      <center><lane id="0" type="driving" level="false">
        <roadMark sOffset="0" type="broken" color="standard" width="0.15"/>
      </lane></center>
      <right><lane id="-1" type="driving" level="false">
        <width sOffset="0" a="3.5" b="0" c="0" d="0"/>
        <roadMark sOffset="0" type="solid" color="standard" width="0.15"/>
      </lane></right>
    </laneSection></lanes>
  </road>
</OpenDRIVE>
"""

SCENARIO = """<?xml version="1.0" encoding="UTF-8"?>
<OpenSCENARIO>
  <FileHeader revMajor="1" revMinor="0" date="2024-01-01T00:00:00" description="Render {name}" author="openx-assets"/>
  <CatalogLocations><VehicleCatalog><Directory path="{catalogs}"/></VehicleCatalog></CatalogLocations>
  <RoadNetwork><LogicFile filepath="{road}"/></RoadNetwork>
  <Entities>
    <ScenarioObject name="{name}"><CatalogReference catalogName="{catalog}" entryName="{name}"/></ScenarioObject>
  </Entities>
  <Storyboard>
    <Init><Actions><Private entityRef="{name}">
      <PrivateAction><LongitudinalAction><SpeedAction>
        <SpeedActionDynamics dynamicsShape="step" dynamicsDimension="time" value="0"/>
        <SpeedActionTarget><AbsoluteTargetSpeed value="5"/></SpeedActionTarget>
      </SpeedAction></LongitudinalAction></PrivateAction>
      <PrivateAction><TeleportAction><Position>
        <LanePosition roadId="1" laneId="-1" offset="0" s="50"/>
      </Position></TeleportAction></PrivateAction>
    </Private></Actions></Init>
    <StopTrigger><ConditionGroup><Condition name="end" delay="0" conditionEdge="rising">
      <ByValueCondition><SimulationTimeCondition value="2" rule="greaterThan"/></ByValueCondition>
    </Condition></ConditionGroup></StopTrigger>
  </Storyboard>
</OpenSCENARIO>
"""


def write_catalog(bundle, workdir):
    """Copy the bundle catalog to <catalog name>.xosc, which is where esmini looks for it.

    Model paths become absolute, since esmini resolves them relative to the scenario.
    """
    catalog_path = next((bundle / "catalogs").glob("*.xosc"))
    tree = ET.parse(catalog_path)
    catalog = tree.getroot().find("Catalog")
    vehicles = []
    for vehicle in catalog.iter("Vehicle"):
        model = (catalog_path.parent / vehicle.get("model3d")).resolve()
        vehicle.set("model3d", str(model))
        vehicles.append(vehicle.get("name"))
    (workdir / "catalogs").mkdir()
    tree.write(workdir / "catalogs" / f"{catalog.get('name')}.xosc")
    return catalog.get("name"), vehicles


def render(esmini, workdir, catalog, name):
    """Render one vehicle and return its last frame and a list of problems."""
    rundir = workdir / name
    rundir.mkdir()
    scenario = rundir / "scenario.xosc"
    scenario.write_text(
        SCENARIO.format(
            name=name,
            catalog=catalog,
            catalogs=workdir / "catalogs",
            road=workdir / "road.xodr",
        )
    )
    log = rundir / "log.txt"
    proc = subprocess.run(
        [
            esmini,
            "--osc", scenario,
            "--window", "0", "0", str(WIDTH), str(HEIGHT),
            "--aa_mode", "0",
            "--info_text", "0",
            "--fixed_timestep", "0.1",
            "--custom_camera", CAMERA,
            "--camera_mode", "custom",
            "--capture_screen",
            "--logfile_path", log,
            "--disable_stdout",
        ],
        cwd=rundir,
        capture_output=True,
        text=True,
    )  # fmt: skip
    problems = []
    if proc.returncode:
        problems.append(f"esmini exited with status {proc.returncode}")
    if log.exists():
        problems += [
            line.strip()
            for line in log.read_text().splitlines()
            if ("[warn]" in line or "[error]" in line)
            and not any(ignored in line for ignored in IGNORED_WARNINGS)
        ]
    frames = sorted(rundir.glob("screen_shot_*"))
    if not frames:
        problems.append("esmini wrote no frames")
        return None, problems
    return Image.open(frames[-1]).convert("RGB"), problems


def contact_sheet(frames):
    """Tile the frames, labelled with the vehicle names, into one image."""
    rows = (len(frames) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGB", (TILE_WIDTH * COLUMNS, TILE_HEIGHT * rows), "white")
    font = ImageFont.load_default(size=16)
    for i, (name, frame) in enumerate(frames):
        tile = frame.resize((TILE_WIDTH, TILE_HEIGHT))
        draw = ImageDraw.Draw(tile)
        draw.rectangle((0, 0, TILE_WIDTH, 22), fill="black")
        draw.text((6, 2), name, fill="white", font=font)
        sheet.paste(tile, ((i % COLUMNS) * TILE_WIDTH, (i // COLUMNS) * TILE_HEIGHT))
    return sheet


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("bundle", type=pathlib.Path, help="unpacked esmini bundle")
    parser.add_argument("--esmini", default="esmini", help="esmini binary")
    parser.add_argument("--output", type=pathlib.Path, default="esmini-render.png")
    args = parser.parse_args()

    failed = False
    frames = []
    with tempfile.TemporaryDirectory() as tmp:
        workdir = pathlib.Path(tmp)
        (workdir / "road.xodr").write_text(ROAD)
        catalog, vehicles = write_catalog(args.bundle.resolve(), workdir)
        for name in vehicles:
            frame, problems = render(args.esmini, workdir, catalog, name)
            print(f"{name}: {'; '.join(problems) or 'ok'}")
            failed |= bool(problems)
            if frame:
                frames.append((name, frame))

    if frames:
        contact_sheet(frames).save(args.output)
        print(f"Wrote {len(frames)} renders to '{args.output}'")
    sys.exit(1 if failed or not frames else 0)


if __name__ == "__main__":
    main()
