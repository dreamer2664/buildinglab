# Winterlichtplatz II — Running Handoff (`townsquare/HANDOFF.md`)

## State
- Native: `none (Stage A programme complete; entering Stage B vertical slice)` `0 B` · frozen: no · published: `https://github.com/dreamer2664/storagecode` `verified: yes`
- Stage: A complete (entering Stage B) · card: `t-20261016-339c` · lease expires `2026-10-19T22:19:25Z`
- Counts: buildings 12/12 (programme) · floors 55/55 res + 12/12 ground (67 plans) · apartments 110/110 · rooms 873 (770 apt + 48 shop + 55 landings) · people 0/220 (programme 220) · views 0/271 (271 defined in `VIEWS.json`)

## What I did since the last handoff
1. Completed Stage 0 bootstrap (`016614953f96`) and Stage A programme generation (`townsquare/tools/generate_programme.py`).
2. Generated `townsquare/design/PROGRAMME.json`, `SCHEDULE.csv` (873 rooms), `APARTMENTS.csv` (110 apartments, 110 unique arrangement signatures across 8 archetypes, 6 palettes, 4 generations, 4 occupancies), `VIEWS.json` (271 camera definitions), 67 dimensioned SVG floor plans (`townsquare/design/plans/B01-L01.svg` .. `B12-L05.svg`), and 12 original fictional branding SVGs (`townsquare/assets/branding/B01.svg` .. `B12.svg`).
3. Built the validator suite (`v_scale.py`, `v_programme.py`, `v_contact.py`, `v_clearance.py`, `v_density.py`, `v_distinct.py`, `v_light.py`, `v_export.py`, `v_package.py`, `v_blind.py`) and `test_validators.py` (10 positive + 10 deliberate negative tests all PASS).
4. Verified `v_programme.py` under both `python3` and `blender --background --python-exit-code 1`: prints `12 / 55 / 110 / 2.00 / 770 / 48 / 55 / 0 / 0 / 0 / PASS`.

## Failures and corrections (not hidden)
1. **D-001 (F21/CLI arg parsing under Blender):** Initial invocation of `blender --background --python-exit-code 1 --python townsquare/tools/v_programme.py` without `--` passed Blender's own flags to `argparse.parse_args()` and exited 2. Fixed in `get_cli_argv()` across all `v_*.py` scripts so Blender flags are stripped when `--` is absent. Re-tested under `blender --background --python-exit-code 1` -> PASS (defect D-001 closed).

## Open defects
| id | severity | where | what |
|---|---|---|---|
| — | — | Stage B–G | 3D kit, Stage B vertical slice (`B02/L02`), full 12-building assembly, 220 people, and 271 renders not yet produced |

## Exact resume
1. `blender --background --python-exit-code 1 --python townsquare/scene/build_slice.py`
2. `python3 townsquare/tools/render_queue.py --slice --pass proof --jobs 2`

## Boundaries
- Not accepted. Independent non-owner acceptance remains PENDING. No self-review/vote.
- No credential, private path or unlicensed asset in this file.
