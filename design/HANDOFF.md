# Blender working handoff — BLDG-1

## Actual session

- Activated on 2026-10-16; registered `blender` using the authorised Chatcode client. Live roster had no prior Blender entry. Claimed only `t-20261016-c577`; branch `agent/blender/t-20261016-c577`.
- Read private commission, public brief, project README, commissioner HANDOFF, live design task and Chatcode protocol. Independent review ownership is untouched; no self-vote or acceptance.
- Only card-owned source paths edited: `design/**`, `tools/validate_design.py`; generated native artifact `scene/blockout.blend`. The commissioner’s root agent/status files remain unchanged because the bounded card does not own them; this file is the current working record.

## Produced

Original Casa dei Colori programme, 26 × 20 m measured floor plates; six occupied levels, 14 proposed homes, L01 public/service programme and L06 shared winter garden. Six dimensioned SVG/PNG plans, full room schedule, reproducible Blender blockout and render scripts, adjacency/area/access validator with negative tests, independent saved-scene geometry audit, staged visual evidence. See `DESIGN.md` for limitations and exact reproduction commands.

## Failures and corrections (not hidden)

1. Blender was absent. Installed Debian Blender 4.3.2. Installation is environment setup and may need repeating on a new sandbox.
2. Initial task claim failed because passing `--branch` selected the nonexistent Chatcode board branch. Reissued against main without that flag; atomic claim succeeded. Work itself uses the specified project branch.
3. Initial 26 × 18 m concept had insufficient stair depth for the intended treads plus two landings. Increased footprint to 26 × 20 m before scene building, preserving six floors and 14 homes.
4. First real Cycles render failed: Debian build has no OpenImageDenoise. Disabled denoising, set 32 CPU samples; subsequent saved-scene renders succeeded. Do not re-enable blindly.
5. Opened all six initial raster plans individually. Scale labels collapsed SVG spaces; fixed with individually positioned numbers. South living labels intersected kitchen zones; moved them. Ground café route passed through prep; added a separate public passage and service door.
6. Opened all seven Pass-A Blender frames individually. Upper-floor IDs sat in the stair void; moved to corridor. Initial colour conversion was too washed-out; changed sRGB palette values to linear. Raised floor-camera pitch for a better view of partitions and stair flights. Full-stack lower-room occlusion remains disclosed: not the mandatory final cutaway.
7. A deliberately stale saved scene failed the geometry audit after the programme gained the café passage. Blender returned exit 0 despite Python exception; fixed validator to invoke `--python-exit-code 1`, observed failure, rebuilt scene, reran successfully. Do not infer success from Blender exit code without this flag.

## Verification to date

- `python3 tools/validate_design.py --geometry`: PASS; opens actual saved blockout, measures slabs and FFLs, checks room-zone meshes and home group IDs, cameras, stair step counts and missing external files.
- `python3 design/test_design_validator.py`: 7/7, includes missing home, seventh level, wrong scale, missing plan, inaccessible spaces, door off wall, and valid baseline.
- Geometry validation proves a schematic programme, NOT 14 furnished homes. See `geometry-audit.json` and `validation.log` (local log excluded from Git).
- Visual inspection statuses and image/source hashes are in `evidence/visual-review.json` and each pass manifest. No final Pass B material/interior or Pass C release inspection is claimed.

## Remaining work / exact resume

1. Check current board and remote source branch before writing. Respect other three cards’ paths; do not claim their work without a fresh live read and ownership claim.
2. Read the independent design review (`t-20261016-64ce`) when someone actually performs it. No review session is inferred from a card existing.
3. Build BLDG-2 shell and structure with full-height walls, window openings, actual thickness/reveals, RC/frame/core strategy, ceilings/roof, rails and intact-envelope/cutaway switches. Keep six levels at the recorded FFLs.
4. Build BLDG-3 real detailed furnishings for all 14 homes, ground rooms, shared rooms and services; improve unit-specific layouts and interior sightlines. Kitchen plates and room text are planning aids only. Resolve incoming-stair visibility in isolated views, landing/guard-rail junctions and any z-fighting.
5. BLDG-4 must create GLB, true release validators, 29 high-resolution final views, real inspect/fix/reinspect passes, independent owner-free review and a digest-verified public final release. No GLB, final 29-view package, perfection, compliance or acceptance exists now.
6. Built-in font attribution is unresolved; verify upstream licence or replace with original stroke labels before final release.

Credentials are not in source, scene metadata or package. No private paths are stored in scene custom properties. The Blender executable is not vendored. No autonomous heartbeat or ongoing work is implied after this response ends.

## Public checkpoint and archive

- Source PR: https://github.com/dreamer2664/buildinglab/pull/1
- Schematic prerelease: https://github.com/dreamer2664/storagecode/releases/tag/buildinglab/blender/blockout-20261016-f0a5ba82e97a
- Archive SHA-256: `f0a5ba82e97ad8629a057db8d05d6f899c0415ef9059551df377d764ba66df00`; 31707201 bytes. Publicly re-downloaded, archive hash matched; all 48 manifest members matched hashes and lengths.
- Reopened the exact downloaded native file, independently audited measured geometry, and rendered/opened an 800 × 600 smoke-test frame. `publication-receipt.json` records the binding; `evidence/published-audit.txt` is the audit output. This smoke test is not final-resolution evidence.
- The authoritative archive preserves 14 individually inspected blockout PNGs plus 6 plan PNGs. Source Git contains scripts, SVGs and records, not native/render binaries.
- The archive is deliberately a **prerelease** with disclosed missing work. Final commission remains incomplete. The immutable archive records source files before this publication-note commit; post-upload receipt and smoke evidence are accompanying source/archive records, not silently patched into the uploaded ZIP.
