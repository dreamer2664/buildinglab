# NORDBAHNHOF — Bahnhofplatz district

An original historic-European-inspired neighborhood expansion of the existing NORDBAHNHOF work in progress. Vitruvius was an atmospheric quality reference, not a copied layout, model or project.

## Open the project

Open `source/NORDBAHNHOF_DISTRICT.blend` in Blender 4.3.2 or later. The saved scene is the full district and retained railway, not the camera-pruned render scene. Photographic image assets used by the final scene are packed. External originals and transformation/provenance records are supplied for reproducibility.

Eight authored cameras are named `DISTVIEW_01_…` through `DISTVIEW_08_…`: station square; exterior exit threshold; market; tram street; the neighborhood's central street; roofscape; café detail; and the view outward through the actual exit. Select a camera and set it active, then use the camera view. The project uses metres.

The full scene is substantially heavier than a single camera render. Camera renders were made with a documented memory budget on a 2GB CPU workstation: off-frame building/figure detail, distant lettering/curtains and old railway interiors/rolling stock are omitted from render memory. Original station geometry more than15m behind the camera may be clipped for rendering. These are render-only operations: the saved source retains the district and all 34 original railway vehicles. No AI-generated illustration was substituted for a Blender render.

## What was built

- 76 original street buildings, mostly 3–5 upper floors, organized into connected street blocks and framed edges around the square.
- 3000 upper window openings with real reveals, frames, glazing, folded curtain geometry and shallow room backs; selected rooms have tables/chairs and warm ceiling surfaces. These are **not 3000 fully furnished apartments**.
- 261 shopfronts with actual openings, shallow 3D interiors, counters, shelves, goods appropriate to the shop sign, door furniture and striped projecting canvas awnings. Books, bottles, loaves, flowers, textile bolts, clocks, produce and hardware are modeled rather than printed onto one storefront plane.
- Pitched slate roofs, ridge flashing, dormers, chimney caps and pots; string courses, dentils, cornices, balconies, shutters and downpipes.
- A station-square fountain and basin/ripples, newspaper kiosk, market stalls, produce crates, café tables/cups/coffee/newspapers, bentwood chairs, benches, lamps, bins, bollards, manholes, drains, bicycles and loaded delivery carts with spokes/tyres/hubs/straps/rivets.
- A double tram street with1435 mm running gauge, flangeway grooves, contact wires/supports and two independently authored electric streetcars, including wheelsets, interior benches, glazing and pantographs. Static models, not certified operational vehicles.
- About 500 placed photographic people. The exact source count is in `docs/DISTRICT_INVENTORY.json`. The scans represent **10 identities in 12 poses**, reused as linked instances. Clothing is modern and is not claimed to be period-certified. No primitive body substitutes were used for the new crowd.

## The exit is connected geometry

The central facade opening is cut through the actual old wall. Earlier proof renders revealed a residual wall segment and obsolete retail inserts; those were corrected in the saved source, not merely concealed in the images. Obstructing legacy RET_/WAIT_ inserts are superseded by the new district shops and exit seating. The previous source remains separately supplied.

The exit has opened glazed leaves, a curved iron/glass canopy with individual panes/ribs/longitudinal bars, broad steps, a side ramp and handrails, a lettered address, civic pediment and a modeled Roman-numeral clock. The threshold and vestibule are at+0.76m; the plaza is+0.18m. An internal east-running ramp descends to the original level 0 concourse, entirely south of Y=38.5m, rather than crossing the retained first railway rake at Y=40m. Ceiling beams, pendants, dado paneling, benches and wayfinding make the shallow vestibule an actual space behind the doors.

Head/waist-height centerline and lateral ray checks, plus walking-surface spot checks are recorded in `evidence/DISTRICT_SOURCE_AUDIT.json`. They are limited geometric spot checks, **not** accessibility, collision-envelope, structural, fire/egress or railway certification.

## Rebuild and render

Starting from the supplied previous `source/NORDBAHNHOF_REALISM.blend`:

```sh
blender -b -t 2 --python build/build_district.py
blender -b source/NORDBAHNHOF_DISTRICT.blend -t 2 --python build/audit_district.py
# Low-resolution proof, without an in-process denoiser:
blender -b source/NORDBAHNHOF_DISTRICT.blend -t 2 --python build/render_district.py -- --view 1 --res 960 --samples 24 --proof
# Native tiled final pipeline (system Python, OpenEXR/numpy/Pillow and external OIDN 2.5.1):
python build/render_district_final.py
```

For shell execution, put a space between flags and values (for example `--view 1`, `--res 960`, `-t 2`). The final orchestrator uses four overlapping native border tiles per view, denoises their linear HDR data with Intel OIDN, assembles without image resizing and applies Blender's AgX view transform. `build/finish_realism.py` is the reused, corrected finishing utility. See final image JSONs for the actual resolution, sampling, durations, hashes and inspection state.

## Honest limits

This remains an artistic, static architectural WIP, not a certified historic reconstruction or completion of every requirement in the original station commission. It does not meet the original 60-identity population programme, fully resolved 240-room programme or 310-view acceptance suite. Secondary backs/party walls and some far interiors remain simplified; repeated architectural modules and human identities are visible. The long-session time request is reported from actual logs, not asserted from intended settings. Older station evidence/validation files are retained as project history; they are not acceptance evidence for this district revision.

## Credits

HSRD-100 photographic people: DigitalRealityLab / `digitalrealitylab/HSRD-100`, CC BY 4.0, pinned revision and per-download SHA-256 recorded in the scan provenance files. Changes: metric/axis normalization, decimation, diffuse resizing/JPEG conversion and repeated linked placements. See `assets/scans/ATTRIBUTION.md` and `assets/district/SCAN_PROVENANCE.json`; license https://creativecommons.org/licenses/by/4.0/ and source https://huggingface.co/datasets/digitalrealitylab/HSRD-100 . The existing project credited Vitruvius for discovery of that dataset; district loading and placement are independently implemented.

Poly Haven scanned cobbles, paving and slate are CC0: https://polyhaven.com/license . Asset authors, exact download URLs, source checksums and transformations are recorded in `assets/district/MAP_PROVENANCE.json`. Previous station surface provenance remains in `assets/realism/PROVENANCE.json`. The new district sky uses Blender's procedural Nishita model. Architecture, scene assembly, street props, lettering and layout are original authored procedural geometry, not an imported city kit.
