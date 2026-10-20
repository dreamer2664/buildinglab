# Independent review — BLDG-1 measured plan and blockout

**Review card:** `t-20261016-64ce`
**Target work card:** `t-20261016-c577` — BLDG-1 dimensioned plan, six-floor programme and blockout
**Reviewer:** `vesta` (non-owner)
**Reviewed:** 2026-10-16 17:45 UTC
**Stage result:** **PASS for the bounded BLDG-1 checkpoint.** This is not acceptance of the complete building or a code-compliance finding.

## Target and artifact identity

- Source PR #1 was inspected at head `8ca1ee431054907da2fd6a939d89ed64947d7d9b` (branch `agent/blender/t-20261016-c577`).
- I downloaded the public schematic prerelease from [storagecode](https://github.com/dreamer2664/storagecode/releases/tag/buildinglab/blender/blockout-20261016-f0a5ba82e97a). The 31,707,201-byte ZIP SHA-256 is `f0a5ba82e97ad8629a057db8d05d6f899c0415ef9059551df377d764ba66df00`, matching the published value.
- All **48/48** paths in the ZIP's `design/package-manifest.json` independently matched their declared byte counts and SHA-256 values. The native scene hash is `96bd265d5347ca4e2473bb79d13673f2aeb7f39bab71a9fb2704db61c10edc78`.
- Of the 48 manifest members, 26 also exist in the PR tree: 25 match byte-for-byte; the only difference is `design/HANDOFF.md`, updated in the source tree after the archive snapshot. The publication notes disclose that the immutable ZIP predates that post-upload note; the programme, six SVG plans, validation code and other overlapping files match.

## Checks I ran

| Check | Result |
|---|---|
| `python3 tools/validate_design.py` at the PR head | **PASS** — six ordered levels, 26 × 20 m footprint, stated heights, six scaled/labelled plans, 14 proposed homes and required shared/service spaces. |
| `python3 tools/validate_design.py --geometry` against the exact downloaded `.blend` | **PASS** in Blender 4.3.2 — reopened the native file, measured six slabs and FFLs, found the proposed home mesh groups, two stair flights per side and per-level cameras; no missing linked files or external textures. |
| `python3 design/test_design_validator.py` | **PASS, 7/7** — valid baseline plus negative tests for missing home/plan, extra level, wrong scale, blocked access and a door outside its wall. |
| Archive/package integrity | **PASS, 48/48** manifest members. |
| Visual inspection | Opened all six individual 1600 × 1240 plan PNGs and all seven individual Pass-B blockout views (L01–L06 and FULL_STACK); no contact-sheet-only inference. Opened one additional render made directly from the archived `.blend`. |

The independently rendered L01 image is `evidence/independent-L01.png` (1600 × 1200; SHA-256 `9b74e95827fac8f3a90303ea422c0472501fbb2c4a43a149c65cf8482dbcc85e`). It was rendered from the exact archived scene in Blender 4.3.2 using `CAM_L01_AXON`; no external image was used.

## Floor-by-floor plan review

Each plan is labelled with the level, FFL and storey height; each shows the 26.00 m × 20.00 m footprint, north arrow and 0–5 m scale bar. All six PNGs are 1600 × 1240 and visually legible at the delivered size.

| Plan | FFL / storey | Homes | Independent observation |
|---|---:|---:|---|
| L01 | 0.00 / 3.80 m | 0 | Shows the vestibule and reception/mail, neighbourhood café plus separate prep/public passage, neighbourhood room, accessible public WC, bicycle/storage, waste/service, plant, parcel/community store, lift and both stairs. |
| L02 | 3.80 / 3.20 m | 3 | Two north one-bedroom units and a south family unit, shared reading room, corridor/core, lift and two stairs. |
| L03 | 7.00 / 3.20 m | 3 | Same three-home programme with level-specific room dimensions and labels. |
| L04 | 10.20 / 3.20 m | 3 | Same three-home programme; shared room and core remain represented. |
| L05 | 13.40 / 3.20 m | 3 | Same three-home programme; shared room and core remain represented. |
| L06 | 16.60 / 3.20 m | 2 | Two larger penthouse homes plus the separately labelled shared winter garden, central core and two stairs. |

The programme schedule and JSON agree with the displayed plan counts: 0 + (3 × 4) + 2 = **14 proposed homes**. The validator's per-floor adjacency/reachability checks pass. This only establishes schematic placement and graph connectivity; it is not a fire, accessibility or building-code certification.

## Blockout and disclosed limitations

I independently reopened the native scene with Blender and ran its geometry audit. The blockout is a measured six-level planning model, not a finished building. It supports the BLDG-1 card's plan/programme/blockout objective. The following remain explicitly open for later building cards and **are not being represented as fixed**:

- The isolated floor renders omit an incoming flight from the previous level; the full-stack model shows the stacked levels. Stair/landing/guard-rail junctions are still schematic.
- Pass-B L01 has a conspicuous dark strip at the lower stair landings. The producer's own record calls it possible coplanar slab/landing shading and leaves it open. It should be rechecked in the detailed stair work before any final release.
- Fine labels are small and some render shadows are noisy. The plan PNGs themselves are clearer than the axonometric labels.
- No finished homes/furnishings, complete envelope/windows/roof, finished lift cab/doors, final GLB or final 29-view package is present. The design notes correctly say so.
- The built-in Bfont attribution remains unresolved; clear or replace it before final distribution.
- No structural engineering, safe-egress determination, accessibility certification or code approval was performed or claimed.

These limitations do not contradict the bounded BLDG-1 work card, which asks for the measured programme, plans and blockout. They would prevent treating this as the final building deliverable.

## Recommendation

**PASS / recommend `accept-inspected` on `t-20261016-c577` for BLDG-1 only.** The required checkpoint evidence is present, the independent validators and seven regression tests pass, and all plans and blockout views were opened individually. Carry the stair-landing visual issue and the other disclosed finishing/licensing work into the later building cards; do not reuse this result as acceptance of the full commission.
