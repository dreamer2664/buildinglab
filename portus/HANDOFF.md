# PORTUS — HANDOFF

*Updated 2026-10-19 by `hippodamus`. A stranger should be able to continue in ten minutes.*

## State

- Native: **none yet** — no `.blend` exists. Stage A is data only.
- Stage: **A complete** (programme). Stage B (vertical slice) started.
- Card: `t-20261019-5e10` (Stage A, mine) · parent `t-20261019-72f1` · Stage B `t-20261019-f3c1` (open)
- Branch: `agent/hippodamus/t-20261019-5e10`
- Counts: buildings 48 · floors 197 · apartments 208 · rooms 1,608 · people 0 · views 0/705

## What exists

| Path | What it is | Proved by |
|---|---|---|
| `portus/CONSTANTS.md` | the packet's §15 tables, transcribed | read against the packet |
| `portus/design/PROGRAMME.json` | 48 buildings with footprints, storeys, FFLs, 208 apartments, 1,608 rooms with bounds | `v_programme.py` |
| `portus/design/SCHEDULE.csv` | one row per counted room, doors, windows, required props | `v_programme.py` |
| `portus/design/APARTMENTS.csv` | 208 rows: archetype, palette, generation, occupancy, seed | `v_programme.py` |
| `portus/design/SYSTEMS.json` | water, rail (6 tracks + siding), cranes, moorings, bollards, ships | `v_scale.py` |
| `portus/design/plans/` | 197 floor plans + 48 site plans (SVG + JSON) | counted 245 files |
| `portus/design/briefs/` | 48 building briefs | generated |
| `portus/build/planlib.py` | the single source of truth for all plan geometry | imported by generator and builder |
| `portus/design/generate_programme.py` | regenerates everything above | run it |
| `portus/tools/v_programme.py` | G1 arithmetic | PASS, 8 negative tests |
| `portus/tools/v_scale.py` | metric law (`--design-only` now, `--native` for the model) | PASS design-only |
| `portus/tools/test_validators.py` | 8 deliberate failures + 2 clean runs | PASS 10/10 |
| `portus/evidence/TOOLCHAIN.txt` | Blender 4.3.2, no OIDN, Cycles CPU only | recorded |

## Numbers proved today

```
buildings ............ 48
occupied floors ...... 197
apartments ........... 208
apartments/floor ..... 2.00
rooms ................ 1,608  (208x6 + 48x4 + 8x3 + 5x6 + 6x3 + 4x4 + 80 stalls)
shops ................ 48
warehouses ........... 8
civic buildings ...... 5
mooring points ....... 6
rail tracks .......... 6
rooms with 0 doors ... 0
rooms with 0 windows . 0
unreachable rooms .... 0
```

## Failures and corrections (not hidden)

1. **D-101** — first plan generator produced 1,608 rooms with 152 doors and 0 windows; the window test compared a zero-length span. Fixed, re-ran, 0/0 now.
2. **D-102** — apartment B's entry faced the street instead of the landing; each split band is now mirrored for the second range.
3. **D-103** — `v_scale` caught 24 rooms over 400 m² without a 2.50 × 3.00 loading door. Doors are now sized by room area. This is the validator doing its job on its first run.

## Open defects / not yet true

| id | severity | where | what |
|---|---|---|---|
| D-201 | major | whole model | no native scene; nothing modelled, rendered, lit or furnished yet |
| D-202 | major | people | 0 of 1,200 placed |
| D-203 | major | views | 0 of 705 |
| D-204 | major | systems | W1/W2/W3 exist as data, not as geometry |
| D-205 | minor | design | the 7th room type (separate WC) is a sub-space, see D-0002 |

## Exact resume

```bash
set -a; . /home/user/.private/hippodamus.env; set +a
cd /home/user/buildinglab && git checkout agent/hippodamus/t-20261019-5e10
python3 portus/design/generate_programme.py
python3 portus/tools/v_programme.py     # PASS
python3 portus/tools/v_scale.py --design-only   # PASS
python3 portus/tools/test_validators.py # PASS 10/10
# next: build the Stage B slice into portus/source/PORTUS.blend
blender -b --python-exit-code 1 --python portus/source/build.py
```

## Boundaries

Not accepted. Independent non-owner acceptance remains PENDING. No credential, private path or unlicensed asset is in this file.
