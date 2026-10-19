# Winterlichtplatz — production rights and provenance

This is original town, building, room-layout, public-realm, furniture-component, packaging, pose/accessory and brand-design work, with explicitly identified third-party graphical assets. No named real building was copied and no generated picture is used as a substitute for town geometry. No trademark-clearance or likeness-exclusivity claim is made.

## Project-authored work

- Project scripts: MIT; see `LICENSE`. `tools/model_lib.py` and `tools/furniture.py` reuse the same author's earlier original component-modelling library, not an external building model.
- Original town/building geometry, room layouts, fixtures, public-realm additions, human pose/accessory derivatives, packaging graphics and twelve fictional vector marks: CC0-1.0 under the project licence. The marks began as vector drafts and are now physically applied as printed sign materials; independent design/realism acceptance remains separate.
- Built-in Blender font geometry and rasterised text are used. No external font software is bundled. SVG font names have ordinary fallback behaviour; editable curves/mesh lettering and rendered sign pixels require no network font service.

## Poly Haven (CC0-1.0)

Exact URLs, source metadata, authors, byte lengths and verified MD5/SHA-256 digests are in `production-intake.json`. Intake downloaded nine complete asset selections, not just web-page thumbnails:

- `cobblestone_01`: measured photographic paving maps; initial three 1K proof maps remain separately documented in `materials/manifest.json`; production uses the verified 2K selection.
- `wood_floor`, `rough_plaster_brick`, `fabric_pattern_05`, `snow_02`: photographic surface maps. Plaster/fabric normal/roughness maps may be used with original colour values rather than their original diffuse colour; wood maps are directly connected through real UV coordinates.
- `sofa_02` (Kirill Sannikov), `modern_arm_chair_01`: licensed furniture meshes and maps; see the exact author metadata in the intake. Original room layouts and other furnishings are project-authored.
- `fir_tree_01` (Rico Cilliers / Rob Tuytel): actual branch/needle mesh, LOD2 for the public tree, not stacked cone silhouettes. Needle alpha and normal maps remain physically applied. Some nominal 1K atlas files are larger in one dimension; public-realm copies are memory-bounded derivatives.
- `cobblestone_street_night`: photographic illumination/reflection environment. Direct camera rays see an authored blue sky, not photographed buildings standing in for the modelled town.

Licence: https://polyhaven.com/license . Source pages and per-file endpoints are retained in the intake.

## MakeHuman / MPFB graphical assets

- `people/intake.json` pins the downloaded MPFB **v2.0.18** source archive and the **280,737,770-byte** MakeHuman system **CC0** graphical asset pack, with SHA-256 digests.
- The system pack was actually opened, all 517 ZIP members CRC-tested, and extracted. Used `.mhclo` files carry the explicit September 2020 CC0 release notice, naming Data Collection AB, Joel Palmius and Jonas Hauquier; used source-file digests/notices are retained in `people/source-files.json`.
- Core body/targets/skins and the selected eyes, eyebrows, eyelashes, teeth, tongue, hair, winter parka, trousers and footwear are CC0 graphical assets. Current licence explanation: https://static.makehumancommunity.org/about/license.html ; asset-pack listing: https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html . Old software licence statements must not be confused with current graphical-asset terms.
- **MPFB code is GPL**, a separate build-time dependency, not relabelled MIT or CC0. Its source archive includes its own licence; it is not needed to open the supplied editable rig natives, the assembled static town native, or the GLB. MakeHuman software licensing is likewise separate from output graphical rights.
- Twelve authored winter variants use anatomical base meshes and real photographed clothing/skin maps, varied macro settings, height, colourway, hair/accessories and rig poses. These are generic CG people, **not commissioned scans of twelve unique real people**. Master/GLB crowd is static evaluated geometry; the separately supplied person natives retain their armatures. Dye-colour derivatives preserve the source quilting/denim atlas; scarves, fitted beanies and bags are original geometry. The source/variant ledgers record actual assets and settings.

## Rendering and portability

The high-resolution production native and detailed building/person natives preserve packed source maps. A separately labelled render derivative resamples photographic maps for the sandbox memory budget; its geometry/UV/pose signature is checked against the production native. Render-only frustum culling and any close-human texture upgrades are recorded per frame. This derivative is not silently substituted for the higher-resolution source.

Cycles images may be denoised with standard OpenImageDenoise colour-only display-sRGB processing in overlapping tiles; noisy originals and digests are retained. No image generation or painted architecture/people replacement is used. Four camera-border tiles, when used for a 4K image, preserve exact native pixel dimensions and are assembled without scaling.

GLB is a portable PBR/static-geometry derivative, not a promise that every engine reproduces Blender's area lights, photographic world, colour management, or glass identically. Exact export/reimport limitations must be read with its validation report. This is conceptual visual architecture and playground design, **not structural, fire, accessibility, medical-facility, photometric, or playground certification**.

Rights intake does not constitute visual acceptance or independent project acceptance.
