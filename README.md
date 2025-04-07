# Esmini Assets

This repository provides simulation assets for use with [Esmini](https://esmini.github.io/), a lightweight OpenScenario simulator that supports the ASAM OpenX standards: [OpenDrive](https://www.asam.net/standards/detail/opendrive/), [OpenScenario XML](https://www.asam.net/standards/detail/openscenario-xml/), and [OpenSimulationInterface](https://www.asam.net/standards/detail/osi/). 

## What's Included

The latest release is available under [Releases](https://github.com/bounverif/esmini-assets/releases) and currently includes:
- ASAM OpenScenario XML vehicle catalogs featuring real-world vehicle models with:
   - Bounding box info ✔️
   - Mass info ✔️
   - Kinematic info ⏳ (needs help)
- Low and medium polygon 3D vehicle model collections for visual enhancement in Esmini. Blender source files are in the repository for customizations.

We also plan to add real-world and procedurally generated road networks in the OpenDrive format.

## For Asset Developers

The current asset pipeline is Blender-based and uses:
- Blender API to export 3D models as `.fbx` 
- `osgconv` (with the FBX plugin) to convert `.fbx` to `.osgb`

Due to licensing restrictions, we cannot distribute the Autodesk FBX SDK, which is needed to convert `.fbx`  models into `.osgb`. However, you can install the plugin inside the devcontainer using the script at `/usr/local/bin/fbxsdk-install.sh`.

## License Information

All assets include a `.license` file in accordance with the REUSE specification. This repository is REUSE-compliant.
