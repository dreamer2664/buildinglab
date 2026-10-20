# NORDBAHNHOF — current asset attribution

This replaces the superseded procedural identity schedule. That schedule was not evidence of sixty completed humans. Do not reuse its identity hashes or completion claims.

## Photographic human scans — CC BY 4.0

Six HSRD-100 subjects, Digital Reality Lab / HumanScanRepository:

- HSR0015-Body-009
- HSR0023-Body-017
- HSR0027-Body-004
- HSR0028-Body-010
- HSR0040-Body-004
- HSR0042-Body-002

Dataset: https://huggingface.co/datasets/digitalrealitylab/HSRD-100

Licence: https://creativecommons.org/licenses/by/4.0/

Retain `scans/ATTRIBUTION.md` and `scans/PROVENANCE.json`, including the pinned source revision and exact hashes. Changes: metric scale/origin normalisation, 2048-pixel JPEG diffuse maps and scene placement; render processes may downsample textures in memory, while the packed source retains the original 2048 maps. No endorsement is implied. These are modern scanned people, not a period crowd or sixty identities.

Source discovery is credited to Vitruvius, buildinglab commit c0ac4a3c363c8a728898c660aa7dd83a5ef2b9cb; the scan loader was independently written.

## Scanned surfaces and photographed skies — CC0

Poly Haven assets used or evaluated for this realism revision:

- rusty_painted_metal
- metal_plate
- concrete_floor_worn_001
- brick_wall_001
- gravel_floor
- worn_concrete_floor
- kloofendal_overcast_puresky — the final scene environment
- winter_evening — evaluated and rejected after proof inspection; not used by the final scene

Licence: https://polyhaven.com/license

`realism/PROVENANCE.json` contains per-file author credits, source URLs and SHA-256 hashes. Original API metadata is retained next to the maps. CC0 attribution is not mandatory, but these credits are preserved for provenance.

## Authored geometry and processing

Railway/station meshes and construction details are original procedural modelling work within this project, except for the explicitly attributed human scans. They are not certified replicas or operational engineering assets. External reference photographs were used only for observation; they are not bundled as scene imagery.

The displayed scene renders come from Blender geometry and shaders, not an AI image generator. Intel Open Image Denoise is used to remove render noise; it is an external Apache-2.0-licensed processing tool, not a scene asset, and its binaries are not redistributed in the archive.

Earlier MakeHuman experiments are not the six humans used in the delivered realism scene. The old experimental assets are not needed to open the packed source and are not part of this realism download.
