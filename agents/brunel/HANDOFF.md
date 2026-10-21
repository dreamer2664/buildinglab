# BRUNEL — NORDBAHNHOF realism revision

Task: `t-20261019-62e7` · branch: `agent/brunel/t-20261019-62e7`

## Current state

The user rejected the clean/model-like appearance of the previous train update and explicitly requested a much more realistic, carefully iterated result. A new material/construction/lighting layer has been built and repeatedly rendered for inspection. All six final native 2560 × 1440 / 128-sample views have rendered and were individually opened, including native-pixel detail crops. The packed source was reopened and checked. Complete ZIP (97,981,256 bytes), render ZIP (12,671,944 bytes), preview and offline gallery have been packaged and CRC/SHA verified. Desktop/mobile gallery interaction was checked in Chromium. Publication is complete. All four release assets were uploaded and their API byte counts and server SHA-256 digests matched the local files.

Release: https://github.com/dreamer2664/storagecode/releases/tag/nordbahnhof/brunel/realism-a41c0ee
Source/evidence commit: `a41c0ee0cb12660985f3ee4868dfbf0c2ee14d2c`. The full commission remains WIP; this release accepts only the inspected revision as a delivery, not the outstanding programme.

The packed source is `nordbahnhof/source/NORDBAHNHOF_REALISM.blend`. The complete original commission is **not** accepted as finished. Historical r01 completion and identity/validator claims do not describe this revision.

## Substantive changes

- Physically scaled CC0 photographed material maps; damp slab platform, mortar, coping chips, individual foreground ballast, local oil and debris.
- Revised railway tyre profiles with inner flange and conical tread; original six rakes / 34 vehicles retained.
- Locomotive sheet-metal deflectors, fasteners, clamps, bored rod bosses, oil nipples, brake hoses and small construction details.
- Real low volumetric steam, a neutral photographed overcast sky, restrained soft sun and roof bounce.
- Corrected actual-render failures: unsuitable orange/magenta night HDRI; Blender `set_sharp_from_angle` changing flat glass/panel shading flags; tubular tyre geometry; unnecessary double-shell solidify on already closed coach glazing.
- More complete luggage, double-sided platform numerals, column plates and drains.

## Evidence and delivery

`evidence/REALISM_SCENE_AUDIT.json` inventories the actual unculled loaded source and its packed images. `REALISM_README.md` explains the rebuild, rendering method and limitations. Final image records live under `renders/realism/native/`. Final output uses 32-pixel-overlap raw HDR tiles, external Intel OIDN 2.5.1 and Blender AgX; no image upscaling or generated-image substitutions.

The constrained workstation renderer isolates one hero rake and omits closed interior fittings. This render-only LOD does not alter the packed source. The source contains six modern scan subjects, not a period crowd of 400 or sixty identities. Mechanisms remain static and uncertified. The full rooms/population/validators/310-view programme is incomplete.

When publication is complete, record the real commit and release URL rather than inferring acceptance from a successful build.
