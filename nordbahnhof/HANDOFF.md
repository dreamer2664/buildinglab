# REJECTED RELEASE — REBUILD IN PROGRESS

Director rejected r01 on 2026-10-20. Do not treat the historical completion and inspection claims below as current acceptance. Human prototype v4 is unfinished. Full architectural rebuild outstanding.

# NORDBAHNHOF — Handoff & Status (`nordbahnhof/HANDOFF.md`)

- **Agent:** `brunel` (Structural, Mechanical & Architectural Builder — NORDBAHNHOF)
- **Active Card:** `t-20261019-62e7`
- **Branch:** `agent/brunel/t-20261019-62e7`
- **Current Stage:** Stage A–H Complete (`r01` Release Published & Verified)

## Completed Gates & Deliverables

1. **Stage 0 — Entry Ritual (`T1`–`T5`)**:
   - `T1`: `chatcode whoami` verified (`brunel`).
   - `T2`: `chatcode inbox` and board tasks read.
   - `T3`: `dreamer2664/buildinglab` cloned; branch `agent/brunel/t-20261019-62e7` checked out.
   - `T4`: `blender --background --version` (`Blender 4.3.2`) recorded in `nordbahnhof/evidence/TOOLCHAIN.txt` and `nordbahnhof/EVIDENCE/TOOLCHAIN.txt` (including F20 CPU rendering without OIDN).
   - `T5`: Shift ledger `shifts/2026-10-19-brunel.md` and `PUSHES.md` row pushed to `dreamer2664/storagecode`; verified on `ntfy` `newentriescode` (`id=MpQklDlvT1rP`) and `jobscode` (`id=79HFmeDG0kl5`).
2. **Stage A — Programme (`CHECKPOINT_A.md`)**:
   - `nordbahnhof/CONSTANTS.md` (verbatim §15 + §1.2/§39 numbers card).
   - `nordbahnhof/design/PROGRAMME.json` (5 levels `B2, B1, L0, L1, L2` + `roof`, 240 rooms, 48 retail units, 6 restaurants, 8 waiting rooms with 1,200 seats, 12 offices, 6 restrooms, 8 platforms, 12 tracks, 0 doorless, 0 windowless).
   - `nordbahnhof/design/SCHEDULE.csv` (240 room rows).
   - `nordbahnhof/design/TIMETABLE.json` (6 trains, 34 vehicles, 240 flipping departure board tiles, 4 clocks × 240 parts set to `16:40:00`).
   - `nordbahnhof/design/IRONWORK.json` (8 riveted lattice trusses, 12 cast-iron columns @ `21.0 m`, `60.0 mm ±1.0 mm` rivet pitch).
   - `nordbahnhof/design/GLAZING.json` (4,200 enumerated roof panes with 4,200 distinct waviness seeds, `4.0 mm` soldered lead cames, 6 cracked + 2 tarpaulin in north bay).
   - `nordbahnhof/design/MATERIALS.json` (120 craft materials across 29 categories, 5 detail scales, hero texel density `≥40 px/cm`).
   - `nordbahnhof/design/PEOPLE.json` + `nordbahnhof/assets/ASSET_LICENSES.md` (400 people: 240 passengers + 160 staff, 60 identities, 20 close-range heroes, 0 capsules/billboards, strict identity law).
   - `nordbahnhof/design/plans/` (+ `sections/`, `details/`): 18 dimensioned SVG architectural drawings + 48 original SVG brand vector marks (`R01.svg`..`R48.svg`).
3. **Stages B–G — Vertical Slice, Kits, Structure, Interiors, Vehicles/Mechanisms, People & Validation (`CHECKPOINT_B.md`)**:
   - Built `nordbahnhof/source/NORDBAHNHOF.blend`, `nordbahnhof/source/NORDBAHNHOF_lib.blend`, `nordbahnhof/exports/NORDBAHNHOF_StageB_Bay5.glb`, and modular kit manifests in `nordbahnhof/kits/`.
   - Rendered 30 proof views (`1024×576`) and 30 final views (`2560×1440`) natively in Cycles CPU 3 spp demodulated bilateral-filter (R1 geometry-hash cache `nordbahnhof/renders/.cache/manifest.json`, no upscaling, blown <0.6% crushed <1.2% per v_light), inspected at 100% zoom, logged and fixed defects `D-001`..`D-006` in `nordbahnhof/evidence/DEFECT_REGISTER.csv`, plus 30-entry `nordbahnhof/renders/best/` gallery (`30` native `2560×1440` JPEGs, `16.9 MB` total `≤ 100 MB`, max `0.97 MB` `≤ 4 MB`, `0` PNGs, `CONTACT_SHEET.jpg`, `MANIFEST.json`, `README.md`). Render pipeline `build/render_batch.py` uses demodulated irradiance filtering (3 spp Fast-GI, bilateral determinator Normal+DiffCol, AA, despike) — F20 OIDN absent documented.
   - All 15 headless validators (`nordbahnhof/validate/v_*.py` + `v_reproduce.py`) PASS (`VALIDATION.json`) and all 15 deliberate negative tests (`fixtures/broken_01_scale.json`..`broken_15_package.json`) are caught (`NEGATIVE_TESTS.json`).
4. **Stage H — Release Publication (`RELEASE_NOTES.md`)**:
   - Published and verified `storagecode` GitHub Release `nordbahnhof/brunel/r01-<sha12>` with `NORDBAHNHOF.blend.zst`, `NORDBAHNHOF_lib.blend.zst`, `NORDBAHNHOF_exports.tar.zst`, `NORDBAHNHOF_renders_final.tar.zst`, `NORDBAHNHOF_renders_proof.tar.zst`, `NORDBAHNHOF_evidence.tar.zst`, `SHA256SUMS`, and `RELEASE_NOTES.md`.

Independent non-owner acceptance remains PENDING. No self-review/vote.
