# Casa dei Colori — detailed architecture / producer handoff

**PRODUCER-CHECKED CANDIDATE — NOT independently accepted.** Original six-storey Mediterranean-city mixed-use residence, 14 furnished homes. Native and clean GLB-reimport gates pass; all 29 exact-source final-resolution originals have actually been opened individually and SHA-bound observations recorded. This packet is frozen before archive upload/redownload verification: consult the separate public publication receipt for that later network result. Mechanical PASS and producer inspection are not independent approval.

## Commission and ownership

- Project: https://github.com/dreamer2664/buildinglab
- Architecture: `t-20261016-0d4e`, branch `agent/blender/t-20261016-0d4e`.
- Furnishing: `t-20261016-61b0`, branch `agent/blender/t-20261016-61b0`.
- Assembly/evidence/release: `t-20261016-58d8`, branch `agent/blender/t-20261016-58d8`.
- Final independent review: `t-20261016-08c6`; producer has not self-reviewed/voted. Parent coordination: `t-20261016-3fe5`.
- The producer log is isolated in the card-owned `evidence/producer/visual-review.json`. A charter-level `evidence/visual-review.json` index/mirror requires coordinator integration if its ownership is not explicitly extended.

## Actual programme and design

One Blender unit is one metre. The occupied footprint is 26 × 20 m. Six occupied collections only: L01–L06, FFLs **0.00 / 3.80 / 7.00 / 10.20 / 13.40 / 16.60 m**. Roof/coping top is approximately **21.12 m**. Roof plant/overrun is not an occupied seventh floor.

- **L01:** entrance approach/vestibule, reception/mail, café/separate prep and counter passage, public WC, bicycle/storage, waste/service, plant, parcel room, cleaner and neighbourhood lounge.
- **L02–L05:** three homes on each level, with distinct/mirrored A/B one-bedroom and C two-bedroom arrangements; shared reading rooms.
- **L06:** two larger penthouses and a furnished, planted shared winter garden.
- **14 homes:** shaped kitchen assemblies with cabinets/handles/worktops, sink/tap, induction hob/oven, fridge, dishwasher and hood; actual sofas/chairs/tables/media, bed bases/mattresses/duvets/pillows, wardrobes/storage, basin/vanity/mirror/WC/shower geometry, lighting and secondary objects. Ground/shared functions have real fitted geometry rather than labels alone.
- Two separated continuous stair routes, landings/rails/guards and exit doors; central lift shaft/portals, a static ground cab and service zones. The actual corridor finish now avoids the shaft opening. Cab/landing level and sampled open portal are mechanically checked.
- Cream mineral surfaces, terracotta trim, teal/bronze metal, oak/walnut, textiles, porcelain/tile/glass; actual window openings, reveals and depth, projected balconies and roof parapet/coping. Context/vegetation is deliberately secondary and stylised.

**Conceptual architecture, not engineered or code/permit approved.** Stair/door/cab geometry and conservative clearance samples do not certify accessibility, fire strategy, swept door arcs, structure, lift operation, MEP or local regulations. A qualified architect/engineer must verify these before construction or safety use.

## Files and editability

| Path | Purpose |
|---|---|
| `scene/building-final.blend` | Integrated presentation native, saved with intact building, materials, lights and 29 evidence cameras. Candidate until independent acceptance. |
| `scene/interiors.blend` | Fully furnished unbatched source, retaining individual editable components/modifiers; includes the shell. |
| `scene/shell.blend` | Editable architecture-only source. |
| `assets/exterior/`, `assets/interiors/` | Original procedural builders, component library, alignment and mechanical diagnostics. |
| `design/programme.json` | Programme input; aligned as-built version is `assets/exterior/aligned-programme.json`. |
| `exports/building-final.glb` | Actual portable geometry/material export, clean-reimport tested; native is authoritative for procedural shading/lighting/view modes. |
| `evidence/producer/scene-validation.json` | Current native digest, measured inventory, routes, actual lift samples, missing-file result. |
| `evidence/producer/export-test.json` | Actual GLB bytes/digest, reimport counts/bounds/groups/material names and numeric portable PBR parameters. |
| `evidence/producer/mesh-conservation.json` | Source/evaluated-to-final component, vertex and face counts; no decimation/proxy substitution. |
| `evidence/producer/room-schedule.json` | Room extents/dimensions and real furnished mesh/source-component inventory. Rectangular programme areas are not net lettable areas; the common-core envelope includes separately labelled embedded service/shaft extents. |
| `exports/room-schedule.csv`, `exports/furnishing-schedule.csv` | Editable tabular room extents and actual 14-home furnishing inventory, with clear count/area basis. |
| `assets/interiors/furnishing-schedule.json` | Per-home kitchen placement and primary assembly schedule. |
| `renders/final/*.png`, `evidence/producer/render-*.json` | Individual original-size final evidence, saved camera/projection/settings and disclosed processing. |
| `evidence/producer/screenshot-manifest.json` | Image bytes/digest/camera/time/source-native binding; rendering does not set an inspection flag. |
| `evidence/producer/visual-review.json`, `VISUAL_REVIEW.md` | Explicit producer observations, defects, fixes and reinspection. Historical diagnostic images are not counted toward final 29. |
| `evidence/producer/ASSET_LICENSES.md`, `fonts/` | Rights/dependency record and bundled DejaVu overlay font licence. |

To bound render memory, final evaluated meshes are consolidated **by level/room/function**, with original component names retained as custom properties and original Generated coordinates as a mesh attribute. No source geometry is decimated or replaced by a primitive. Use Edit Mode in the integrated file, or the fully unbatched `interiors.blend` for individual component/modifier editing. The batched presentation file is not falsely presented as preserving thousands of separate object handles.

## Native switches and cameras

A clean machine needs Blender, not an add-on or automatic startup execution. Native `START_HERE.txt` explains the file. In Blender's Text Editor open embedded `VIEW_MODES.py` and Run Script, or in Python Console:

```python
exec(bpy.data.texts['VIEW_MODES.py'].as_string())
set_view('floor', 'L03')
# Other modes: intact, interior, plan, section, structure
set_view('intact')
```

Per-level collections separate slab, low/high partitions, façade, ceiling, stairs, lift, furnishings and lighting. Technical modes remove ceiling-light mesh caps when ceilings are removed; actual lighting remains. Interiors restore the real enclosing shell. Camera identifiers are in `evidence/producer/views.py` and the native report. Final reception composition is overridden in `assemble.py`; source-file preliminary cameras are not all the final campaign poses.

## Disclosed final-image visibility and labels

The saved native geometry and all render camera transforms remain unchanged at native `1b7150d6…`. The structural overview selects the already saved `CAM_FULL_CUTAWAY` at its exact pose rather than the steeper, clipped preliminary technical camera; the latter remains editable in the native but is not the final evidence camera. The L06 **plan only** additionally displays the actual incoming L05 stair meshes through its open wells, while hiding all other lower-level objects. This explicit selection is in `render_one.py` and per-view metadata; it is not painted stair geometry or a native edit. Embedded level-only isolation remains a simpler default; the supplied render helper reproduces the exact evidence selection. All render metadata records saved/render camera matrices, and the package gate requires equality/no render-only pose override.

Ground-floor public storage/WC overlays now use actual programme names (bicycle, parcel, cleaner, public WC), not generic STORE/BATH. The first generic-label plan, first empty-looking L06 isolated plan and first clipped structural overview are retained with actual failed observations in revisions E/F/G. Any older public raw recovery PNGs remain immutable historical assets; authoritative corrected originals are identified by the current screenshot manifest, digest-bound checkpoint receipt and final ZIP/member manifest. Earlier bad asset names are not claims of final inspection or acceptance.

## Exact evidence bar

Minimum **29 separate PNGs**, not a contact sheet:

- 2 exteriors + 1 full-building cutaway + 6 level cutaways, **3840 × 2160**.
- 12 human-height interiors + 6 labelled/dimensioned furnished plans + 2 technical views, **2560 × 1440**.

Every final view must be generated from the *same saved native SHA*, opened individually, and have a specific SHA-bound observation. No old preliminary image may be relabelled as final after a model change. Plan overlays use actual programme bounds, saved camera projection, door poses and native light positions; no synthetic architecture is painted into evidence. Exterior/context and interior images remain actual Blender renders. Disclosed caption/technical typography is not scene geometry.

The visual-package validator checks image format/dimensions/bytes/digest/uniqueness, camera and source binding, metadata, explicit inspection records and unresolved defects. **It cannot prove that someone looked at an image and cannot grant independent acceptance.** See the readable review and actual image-opening history.

## Toolchain, rendering and limitations

Official **Blender 4.3.2**, build `32f5fdce0a0a`, CPU Cycles, 16 samples, AgX / Medium High Contrast. Native integrated denoising is off to bound peak RAM. PNGs receive separate tiled OpenImageDenoise, display-referred sRGB **colour-only** processing (not normal/albedo-guided HDR denoising), followed by disclosed typography. No AI-generated image is used as a substitute for the model. Settings/poses are recorded per render. Interior exposure adjustment is stated in the native/render reports.

The GLB intentionally converts procedural base colour/bump to documented constant base colour + numeric PBR roughness/metal/transmission fallback while retaining real geometry/normals. Numeric parameters are compared after clean import, not merely material names. Blender procedural noise/Generated-coordinate shading, world setup, analytic AREA lights, native collections/switch scripts and viewport state do not port faithfully to all glTF engines. Punctual supported lights and emissive geometry are exported; consumers may choose their own lighting. There are no external image/model links to download.

### Reproduce (no credentials required)

From the archive/project root; choose an official Blender executable:

```bash
B=/absolute/path/to/blender-4.3.2/blender
"$B" -b -t 4 --python-exit-code 1 --python assets/exterior/build_shell.py
"$B" -b scene/shell.blend -t 4 --python-exit-code 1 --python tools/validate_shell.py
"$B" -b scene/shell.blend -t 4 --python-exit-code 1 --python assets/interiors/build_interiors.py
"$B" -b scene/interiors.blend -t 4 --python-exit-code 1 --python tools/validate_interiors.py
"$B" -b scene/interiors.blend -t 4 --python-exit-code 1 --python assets/interiors/audit_clearances.py
"$B" -b scene/interiors.blend -t 4 --python-exit-code 1 --python evidence/producer/batch_meshes.py
"$B" -b "$HOME/.cache/buildinglab-batch-stage.blend" -t 4 --python-exit-code 1 --python evidence/producer/assemble.py
"$B" -b scene/building-final.blend -t 4 --python-exit-code 1 --python tools/validate_scene.py
"$B" -b scene/building-final.blend -t 4 --python-exit-code 1 --python tools/test_export.py
python3 evidence/producer/render_package.py --blender "$B" --oidn-lib /absolute/path/to/blender/lib --resume
# Actually open/inspect each original PNG. Only then explicitly record observations:
python3 evidence/producer/record_inspection.py --view VIEW_ID --observations 'Actual observed result, not render success.'
python3 evidence/producer/record_inspection.py --sync-manifest
python3 tools/validate_visual_package.py
```

The reference automated render/denoise pipeline is CPU/Linux; native/GLB deliverables remain portable. External Python helpers use Python 3.13.16 / Pillow 12.3.0 / NumPy 2.3.5 in this build; package pins are in `evidence/producer/requirements.txt`. `--resume` validates current source SHA, image digest and dimensions; it does not infer inspection. Batched assembly must run in a **fresh Blender process** on the cache-stage file: deleting evaluated source IDs within the batching process caused a dependency-graph crash. This is a deliberate tested two-process pipeline, not a one-process shortcut.

## Real defects / failures and review history

The producer log preserves preliminary A diagnostics, corrected B exact-size diagnostics and later full-size preflight/actual-geometry regression, followed by final C. Genuine fixes include eye camera inside wardrobe, café/bath framing, window-trim corner caps, open leaves/bedside storage and bathroom entry arrangement, technical ceiling discs, actual common-gallery lights outside the lift shaft, entry ramp, plant headers, and reception layout/framing.

Operational failures are not hidden: distro EGL/OIDN incompatibility, integrated denoising/full-scene memory failures, evaluated dependency-graph crash during one-process deletion, and a first batched intermediate losing all material slots. The grey intermediate/export was invalidated, persistent Main material references and palette guards added, and real coloured native/reimport checks rerun. The first full-size preflight also exposed a corridor finish re-sealing the lift opening and cab/portal alignment. A negative regression on that actual saved native correctly failed; source geometry and final gates were corrected before final evidence freezing.

Source/render-count tests are not a substitute for visual reinspection or independent review. Known unresolved issues remain listed explicitly; do not claim zero major issues until the current-source image set and reinspection log are complete.

## Publication and independent acceptance

Bulky binaries/images belong in **`dreamer2664/storagecode` Release assets**, not Git history. The source repository carries code, compact reports/manifests and handoff. Publication must use an immutable candidate tag, upload the native/GLB/all release images in an archive, re-download it, verify archive digest **and every member including `.blend`, `.glb` and all PNGs**, and append `storagecode/PUSHES.md` and `data/INDEX.md`. Release receipts are separate from the archive to avoid circular self-hashes.

**At archive freeze: all 29 exact-source originals were regenerated, actually opened individually and SHA-bound; producer gates PASS.** Archive upload/public redownload/every-member verification happens after this immutable packet is built and is recorded in a separate publication receipt. Independent non-owner acceptance remains pending.

The original 0f model/checkpoint remains explicitly superseded/not accepted, with original failures and observations retained under revisions C/D. Current native is `1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f`, portable GLB is `06940c1254f6d7499d93c2798e7ea564c0f0e780a184ec8d008481aff37e67e6`. The corrected native/export/public-open tests pass. Original failed label/visibility/framing frames and actual reinspection are retained in E/F/G; immutable old recovery PNG assets are historical, not substitutes for corrected manifest originals.

Current WIP/model recovery release, subsequently receiving the verified final archive: https://github.com/dreamer2664/storagecode/releases/tag/buildinglab/blender/candidate-20261016-1b7150d6ce45

No final archive digest or reviewer vote is invented. The earlier verified schematic release remains historical, not acceptance of the detailed scene:
https://github.com/dreamer2664/storagecode/releases/tag/buildinglab/blender/blockout-20261016-f0a5ba82e97a

The independent reviewer must inspect the actual native/export and every final image against the live charter, verify hashes/gates and record acceptance or specific failures on their non-owner review card. The producer cannot approve their own work. No credentials, private packet, transport helper or private environment is part of the deliverable.


## Frozen producer evidence summary

- Native SHA-256: `1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f`.
- GLB SHA-256: `06940c1254f6d7499d93c2798e7ea564c0f0e780a184ec8d008481aff37e67e6`.
- Current original inspections: **29/29**, from one unchanged saved native. See `evidence/producer/VISUAL_REVIEW.md` and JSON; no renderer-success inference.
- `renders/GALLERY.html` is an offline embedded preview of the actual PNGs, not evidence replacements.
- Ceiling finish seams and shaft caps were physically corrected and re-tested rather than painted out or merely disclosed. Stylised vegetation, technical low-wall art/pendant convention and documented GLB procedural-to-constant PBR approximation are intentional limitations. No unresolved producer-recorded critical/major defect; independent review remains mandatory.
- Dimensioning convention: labelled storey FFLs are nominal level datums; the modelled 40 mm finish lies above each datum. Landings, lift sill and grounded furnishing checks use the actual finish surface, not a claim of an as-built survey.
- Earlier runtime original-image losses are explicitly retained in recovery/history records. Surviving B3/B4 negative PNGs and real failing geometry reports support the correction trail; no absent historical PNG is fabricated.
- The packager creates an identical `evidence/visual-review.json` and `evidence/VISUAL_REVIEW.md` ZIP mirrors without writing coordinator-owned source paths.
- Independent reviewer: open actual native/unbatched source and GLB, inspect every original, verify reports/hashes/release receipt against live charter, and record acceptance or failures on the non-owner review card. Producer has cast no vote.


## Post-freeze public publication verification

This addendum is later than the immutable ZIP handoff. The ZIP is not silently rebuilt.

- Actual anonymous public ZIP download, CRC, archive SHA and all **219 archive entries / 218 payload members** verified at `2026-10-16T18:36:37.574686+00:00`; all 29 final original PNGs and all three native files plus GLB verified.
- [Complete ZIP](https://github.com/dreamer2664/storagecode/releases/download/buildinglab/blender/candidate-20261016-1b7150d6ce45/Casa-dei-Colori-candidate-20261016-1b7150d6ce45.zip) · [Public verification receipt](https://github.com/dreamer2664/storagecode/releases/download/buildinglab/blender/candidate-20261016-1b7150d6ce45/Casa-dei-Colori-verification-1b7150d6ce45.json) · [Append-only storage ledger](https://github.com/dreamer2664/storagecode/commit/2f45bfea2efe5c6039a38a93d8dfb270942c7a9e).
- Archive SHA-256: `70130eb4f823fc274e52191dadde47bf75de68b2414b260d7f74c11f22b3b118`.
- Receipt SHA-256: `7d2c54646510e7a6328bb569f0d0fe757d16ff7d3bb830939e8fcec95962e2ef`.
- Independent non-owner acceptance is still **pending**. This is publication/integrity verification, not self-review or a vote.
