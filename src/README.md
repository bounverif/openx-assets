<!--
SPDX-FileCopyrightText: 2026 Dogan Ulus <dogan.ulus@bogazici.edu.tr>
SPDX-License-Identifier: MPL-2.0
-->

# OpenX Assets

3D vehicle models and vehicle catalogs for driving simulation, built for the
ASAM OpenX standards (OpenDRIVE, OpenSCENARIO XML, OpenMATERIAL 3D) and the
[esmini](https://esmini.github.io/) simulator.

## Model conventions

- Units are metres, at real-world scale.
- Vehicle frame: X forward, Y left, Z up. The origin is the centre of the
  bounding box, on the ground. glTF stores it Y-up, as the glTF specification
  requires; importers convert it automatically.
- The node tree follows the ASAM OpenMATERIAL 3D v1.1.0 vehicle structure:
  `Grp_Root` › `Grp_Exterior` / `Grp_Interior` › static and dynamic groups.
  Wheels (`Grp_Wheel_<axle>_<wheel>`), doors, lights, mirrors and license
  plates are separate groups with their own local frames, so a simulator can
  steer and spin the wheels, open doors and switch lights. Axles are numbered
  front to rear and wheels right to left.
- Materials are flat PBR without textures. Glass is semi-transparent.

## License

The models are licensed under `MPL-2.0 AND CC-BY-4.0`. Most are derived from
works by third-party authors under CC BY 4.0, so if you redistribute or show
them, credit the original author.

The `REUSE.toml` in each bundle lists the copyright holders and license of
every file. The same notice is in each model's `.xoma` file under
`copyrights`. The license texts are in `LICENSES/`.
