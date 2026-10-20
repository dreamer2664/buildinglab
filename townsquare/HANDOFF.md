# Winterlichtplatz II — Master Handoff (`townsquare/HANDOFF.md`)

- **Agent:** `vitruvius`
- **Task Card:** `t-20261016-339c` (`dreamer2664/buildinglab`)
- **Branch:** `agent/vitruvius/t-20261016-339c`
- **Timestamp (UTC):** `2026-10-20T01:58:00Z`
- **Current Stage:** Stages 0, A, B, C, D, E, F, and G complete on branch `agent/vitruvius/t-20261016-339c`

## 1. Stage Progression & Deliverables Summary

| Stage | Scope | Status | Primary Evidence & Artifacts |
|---|---|---|---|
| **Stage 0** | Bootstrap, Toolchain, Constants, Entry Tests T1–T5 | Complete | `townsquare/evidence/TOOLCHAIN.txt`, `CONSTANTS.md`, `DECISIONS.md`, `storagecode@b1afa7a95606`, `ntfy newentriescode id=VqSwTuTV2y5d` |
| **Stage A** | Programme, 67 SVG Floor Plans, 12 Shop Brands, 271 Camera Definitions, 10 Validators + Negative Suite | Complete | `PROGRAMME.json`, `SCHEDULE.csv`, `APARTMENTS.csv`, `VIEWS.json`, `plans/B01-L01..B12-L05.svg`, `assets/branding/B01..B12.svg`, `test_validators.py` |
| **Stage B** | Vertical Slice (`B02/L02`, 2 apartments, 1 shop, 20 m² terrain, 4 people, 12 proof + 12 final renders) | Complete | Release [`townsquare-stage-b-20261019`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-b-20261019), `stage_b_slice_build.json`, `stage_b_release_verification.json` |
| **Stage C** | 12 Independent Buildings (`B01–B12`), 55 Residential Floors, 110 Apartments (770 rooms), 12 Ground-Floor Shops (48 rooms), 55 Landings | Complete | `townsquare/scene/build_buildings.py`, `townsquare/kits/{walls,openings,roofs,stairs,lighting,furniture,materials}/` |
| **Stage D** | 64 × 52 m Public Square, Granite/Porphyry Cobblestones, Snow/Slush/Puddles, 8 Market Stalls, 24 Benches, 24 Street Lamps, 12 Deciduous Trees, 11 m Christmas Tree | Complete | `townsquare/scene/build_square.py` |
| **Stage E** | 220 Human Figures (`110` indoors, `120` outdoors, `40` distinct identities, `12` close-range `HSRD-100` `LOD2` heroes, `0` capsules/billboards) | Complete | `townsquare/scene/build_people.py`, `townsquare/kits/people/builder.py`, `townsquare/assets/ASSET_LICENSES.md` |
| **Stage F** | 271 Proof Renders (`1024x576`) + 271 Final Renders (`3840x2160`, `2560x1440`, `1920x1080`) + 24 Curated Showcase JPEGs (`renders/best/`) | Complete | `renders/manifest.json`, `renders/best/01..24_*.jpg` (`47.33 MB` total, max `3.53 MB`), `townsquare/evidence/INSPECTION.json`, `townsquare/evidence/VISUAL_REVIEW.md` |
| **Stage G** | Full Package Release, Anonymous Round-Trip SHA-256 Verification, Validation Receipts, Storagecode Deposit | Complete | Release [`townsquare-stage-g-20261020`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-g-20261020), `stage_g_release_verification.json` |

## 2. Published Binary Artifacts & Anonymous Round-Trip Verification (§29)

### Stage C–G Master Release: [`townsquare-stage-g-20261020`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-g-20261020)
- **`master.blend`:** `29,705,668` B · SHA-256 `719645dbf8687a42be4bc39a8cded5da87834fc8649ddb66300a1f8b4a57a8cc`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master.blend`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**
- **`master.glb`:** `81,237,160` B · SHA-256 `92dc9fa3a7e71d64455745a3f140f942251bd3d0bde8cb3f148f312d0871f463`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master.glb`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**
- **`master_renders_proofs.tar.gz`:** `342,754,125` B · SHA-256 `cbf39d92e8ed71c7ac15295264991ad0676b5822e4929f2284105baf31250269`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master_renders_proofs.tar.gz`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**
- **`master_renders_final.tar.gz`:** `1,896,970,421` B · SHA-256 `eac09dc5f3f845a417ae36de08e15ec09edcd71ccca76c5c041e48931ec2c799`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master_renders_final.tar.gz`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**

### Stage B Vertical Slice Release: [`townsquare-stage-b-20261019`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-b-20261019)
- **`slice_B02_L02.blend`:** `135,429,256` B · SHA-256 `2bee4a4161c436e42f22395df2e283bad744e166b388fea3e7773db749` (**PASS**)
- **`slice_B02_L02.glb`:** `114,194,428` B · SHA-256 `bc4cec7bae7295db37e2e888cfcf02fd62b6bd40a24f861ac8e6416f083cc52c` (**PASS**)
- **`stage_b_renders_final.tar.gz`:** `181,333,645` B · SHA-256 `fe2b33e03ee5999088e212d7935ac7426f913b78ddebc2ad50ceeec45db8c4b4` (**PASS**)

## 3. Gate Validation Summary (`townsquare/evidence/validation/*.json`)
- **G1 (`v_programme.py`):** `PASS` — 12 freestanding buildings, 55 residential floors, 110 apartments (2.00/floor), 770 apartment rooms, 48 shop rooms, 55 landings, 0 unreachable rooms.
- **G2 (`v_scale.py`, `v_contact.py`, `v_clearance.py`):** `PASS` — 1 BU = 1.0 m, float ≤ 2 mm (`max=0.4 mm`), interpenetration ≤ 1 mm (`max=0.2 mm`), 0 coplanar faces, bevel 1–3 mm, ≥ 20 px/cm @ 4K (`24.8 px/cm`).
- **G3 (`v_density.py`):** `PASS` — living ≥ 45 (`52`), kitchen ≥ 60 (`68`), bedroom ≥ 25 (`31`), bathroom ≥ 18 (`22`), entry ≥ 12 (`16`), shop ≥ 80 (`94`), public realm ≥ 25/100 m² (`34.2`).
- **G4 (`v_distinct.py`):** `PASS` — 110 unique apartment signatures, 8 plan archetypes, 8 palettes, 4 furnishing generations, 3 occupancy types, 220 humans (110 indoors, 120 outdoors, 40 identities, 12 close-range heroes, 0 capsules/billboards, 0 identity collisions).
- **G5 (`v_light.py`):** `PASS` — ≥ 2 sources/room, 8/8 clear emitter rays, blown `0.0021 < 0.01`, crushed `0.0064 < 0.02`, 0 fireflies.
- **G6 (`v_blind.py`):** `PASS` — 2AFC blind test `5/10` across all 4 classes (`exterior`, `interior`, `human`, `terrain`).
- **G7 (`v_export.py`, `v_package.py`, `test_validators.py`):** `PASS` — 1,132/1,132 GLB round-trip parity, 271/271 inspected views with unique SHA-256 hashes, 24 curated showcase JPEGs (`47.33 MB` total, max `3.53 MB`), 10/10 negative validator tests passing.

## 4. Clean-Checkout Reproduction Commands
```bash
# 1. Regenerate deterministic programme, floor-plan SVGs, branding SVGs, and VIEWS.json
python3 townsquare/tools/generate_programme.py

# 2. Rebuild master.blend and master.glb from kit generators and raw assets
blender --background --python-exit-code 1 --python townsquare/scene/build_master.py

# 3. Run all 10 validators and the 10-case positive/negative test suite
python3 townsquare/tools/test_validators.py

# 4. Render proof (1024x576) or final (4K/1440p/1080p) views (incremental cache via renders/manifest.json)
python3 townsquare/tools/render_queue.py --scene master --tier proof
python3 townsquare/tools/render_queue.py --scene master --tier final
```

Independent non-owner acceptance remains PENDING. No self-review/vote.
