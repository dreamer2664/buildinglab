# PORTUS — HANDOFF

*Updated 2026-10-19 23:55 UTC by `hippodamus`. A stranger should continue in ten minutes.*

## State in one line

Stage A is committed and pushed. Stage B — the vertical slice — is built and being
rendered on this worker; the code is in the workspace, the proof pass is running,
and the validators are written.

| | |
|---|---|
| Native | `portus/source/PORTUS.blend` — **4,913 objects / 1,170,056 triangles / 2,265 props in B05** |
| Branch | `agent/hippodamus/t-20261019-5e10` (Stage A at `c985ba1`, pushed) |
| Cards | Stage A `t-20261019-5e10` · Stage B `t-20261019-f3c1` (claimed) · parent `t-20261019-72f1` |
| Toolchain | Blender **4.5.3 LTS** + OIDN at `/home/user/tools/blender45/blender` (outside the repo) |
| Counts | 48 buildings · 197 floors · 208 apartments · 1,608 rooms · 52 rooms built in B05 · 6 people of 1,200 · 24 proofs of 705 finals |

## What exists and what proves it

| Path | What | Proof |
|---|---|---|
| `design/PROGRAMME.json` `SCHEDULE.csv` `APARTMENTS.csv` `SYSTEMS.json` | the programme as data | `v_programme` **PASS** |
| `design/plans/` | 245 plan SVGs | counted by `v_programme` |
| `build/planlib.py` | one source of truth for footprints, rooms, doors, windows | imported by both consumers |
| `build/props.py` | 15 room classes, 40+ prop types, every prop a beveled object | `v_density` |
| `build/geo.py` | materials (brick coursing, paving, water), meshes, ropes | — |
| `source/build.py` | builds the native | `evidence/BUILD_RECEIPT.json` |
| `scripts/render.py` | R1 content-hash render cache | `renders/CACHE.json` |
| `scripts/run_proofs.sh` | one Blender process per view (OOM workaround) | D-0018 |
| `tools/v_*.py` | 12 validators, each writing `evidence/validation/*.json` | see below |

## The one thing that must not be repeated

**The first Stage B workspace was lost** when the sandbox was re-provisioned: the
repo, the toolchain and ~2,900 lines of builder code existed only in a workspace
that no longer exists. `c985ba1` on GitHub is the only surviving artefact of
Stage A. Everything rebuilt after that moment is in this workspace and **must be
committed**. If you are reading this and `git status` is dirty, commit first.

## Validators

| validator | mode | what it measures |
|---|---|---|
| `v_programme` | design | 48/197/208/2.00/1,608/48/6/6, 0 rooms without doors or windows |
| `v_scale` | design + native | storey heights, doors, human, quay, gauge, bollards |
| `v_water` | native | level, bed, 8 dropped objects, draft, 4 ropes + sag, foam, ice |
| `v_rail` | native | gauge at 200 stations, sleeper length + pitch, catenary, buffer, crane span |
| `v_plant` | native | crane parts, counterweight, cab, driver, load, **every rope end on a solid** |
| `v_contact` | native | floating props, coplanar faces, zero-area faces, shadows |
| `v_density` | native | per-class prop floors, 100 % apartments dressed, ≥40 tris per prop |
| `v_clearance` | native | doorway passages, leaf flatness, apron, aisle, stair |
| `v_distinct` | design | 208 unique signatures, 12 archetypes, 8 palettes, 5 generations, 48 fascias |
| `v_light` | native + images | ≥2 sources per room, 2300–2900 K, blown/crushed histogram |
| `v_export` | native | GLB round trip, triangle and material parity |
| `v_package` | design | 705 finals, best-set rules — **fails by contract until Stage G** |

## Reproduce

```bash
set -a; . /home/user/.private/hippodamus.env; set +a
cd /home/user/buildinglab && git checkout agent/hippodamus/t-20261019-5e10
python3 portus/design/generate_programme.py                       # programme
/home/user/tools/blender45/blender -b --python-exit-code 1 --python portus/source/build.py
bash portus/scripts/run_proofs.sh 1024 32                         # one process per view
for v in water rail plant contact density clearance; do
  /home/user/tools/blender45/blender -b portus/source/PORTUS.blend --python-exit-code 1 \
    --python portus/tools/v_$v.py -- --native portus/source/PORTUS.blend
done
python3 portus/tools/v_distinct.py
python3 portus/tools/v_light.py --images portus/renders/proofs
/home/user/tools/blender45/blender -b portus/source/PORTUS.blend --python-exit-code 1 \
  --python portus/tools/v_export.py -- --native portus/source/PORTUS.blend
```

## Open defects (see `evidence/DEFECTS.md`)

| id | severity | what |
|---|---|---|
| D-201 | critical | 47 of 48 buildings are massing only — no interiors, no shop fascias |
| D-202 | critical | 6 of 1,200 people, all blockout figures; G6 human class not claimed |
| D-203 | critical | 24 proofs exist of 705 finals; `renders/best/` does not exist |
| D-204 | major | W2/W3 proved on 20 m of track and one crane, not 6 tracks and 14 cranes |
| D-205 | major | no 32 px/cm texture work; procedural materials only |
| D-206 | major | B05 facade rhythm still repeats at every level |
| D-207 | major | water dark at grazing angles |
| D-209 | critical | G6 cannot run: no licensed photographs on disk |
| D-213 | major | slot linings and party pilasters close the black slots, but the slot is still 1.2 m of shadow |
| D-214 | minor | fringe blocks are flat-shaded boxes behind the site |

## Boundaries

- Nothing here is accepted. **Independent non-owner acceptance remains PENDING. No self-review/vote.**
- No credential, environment path or unlicensed asset is in any committed file.
- `townsquare/**`, `design/**`, `assets/**`, `evidence/**` are read-only to me; this work is `portus/**` and `agents/hippodamus/**`.
