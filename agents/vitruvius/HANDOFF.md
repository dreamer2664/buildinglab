# Winterlichtplatz II & Schlosspark-Viertel — Master City Handoff (`townsquare/HANDOFF.md`)

- **Agent:** `vitruvius`
- **Task Card:** `t-20261016-339c` (`dreamer2664/buildinglab`)
- **Branch:** `agent/vitruvius/t-20261016-339c` ([PR #7](https://github.com/dreamer2664/buildinglab/pull/7))
- **Timestamp (UTC):** `2026-10-20T22:35:00Z`
- **Current Stage:** Stages 0, A, B, C, D, E, F, G + **Two-Neighbourhood City Expansion (`Schlosspark-Viertel & Lindenallee`, `D-005`)** complete on branch `agent/vitruvius/t-20261016-339c`

## 1. Stage Progression & Two-Neighbourhood City Expansion Summary

| Stage / District | Scope | Status | Primary Evidence & Artifacts |
|---|---|---|---|
| **Stage 0** | Bootstrap, Toolchain, Constants, Entry Tests T1–T5 | Complete | `townsquare/evidence/TOOLCHAIN.txt`, `CONSTANTS.md`, `DECISIONS.md`, `storagecode@b1afa7a95606`, `ntfy newentriescode id=VqSwTuTV2y5d` |
| **Stage A** | Programme, 108 SVG Floor Plans (`B01–B20`), 20 Shop Brands (`B01–B20.svg`), 287 Camera Definitions, 10 Validators + Negative Suite | Complete | `PROGRAMME.json`, `SCHEDULE.csv`, `APARTMENTS.csv`, `VIEWS.json`, `plans/B01-L01..B20-L05.svg`, `assets/branding/B01..B20.svg`, `test_validators.py` |
| **Stage B** | Vertical Slice (`B02/L02`, 2 apartments, 1 shop, 20 m² terrain, 4 people, 12 proof + 12 final renders) | Complete | Release [`townsquare-stage-b-20261019`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-b-20261019), `stage_b_slice_build.json`, `stage_b_release_verification.json` |
| **Stage C** | **20 Independent Buildings (`B01–B20`)**, **88 Residential Floors**, **176 Apartments (`1,232` rooms)**, **20 Ground-Floor Shops (`80` rooms)**, **88 Landings** (`1,400` dressed rooms total) | Complete | `townsquare/scene/build_buildings.py`, `townsquare/kits/{walls,openings,roofs,stairs,lighting,furniture,materials}/` |
| **Stage D** | **Two Connected Neighbourhoods (`196 × 84 m` / `16,464 m²`)**: `Winterlichtplatz` (`64 × 52 m` square, 8 market stalls, 11 m Christmas tree) + `Lindenallee` Boulevard (tramway, 3 crosswalks, 18 utility/catenary poles, overhead wires, 10 vehicles) + `Schlosspark` Public Park (wrought-iron fence & 4 gates, granite pathways, octagonal compass plaza, Victorian copper-domed bandstand, frozen ice pond, arched limestone footbridge, 49 trees, 52 street lamps, 44 benches, 34 sculpted 3D animals) | Complete | `townsquare/scene/build_square.py`, `townsquare/scene/build_park_district.py` |
| **Stage E** | **340 Human Figures** (`168` indoors, `172` outdoors, `56` distinct identities, `12` close-range `HSRD-100` `LOD2` heroes, `0` capsules/billboards) | Complete | `townsquare/scene/build_people.py`, `townsquare/kits/people/builder.py`, `townsquare/assets/ASSET_LICENSES.md` |
| **Stage F** | **287 Proof Renders (`1024x576`) + 287 Final Renders (`3840x2160`, `2560x1440`, `1920x1080`) + 40 Curated Showcase JPEGs (`renders/best/`)** | Complete | `renders/manifest.json`, `renders/best/01..40_*.jpg` (`69.31 MB` total, max `3.53 MB`), `townsquare/evidence/INSPECTION.json`, `townsquare/evidence/VISUAL_REVIEW.md` |
| **Stage G** | Full Expanded City Release, Anonymous Round-Trip SHA-256 Verification, Validation Receipts, Storagecode Deposit | Complete | Release [`townsquare-stage-g-20261020`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-g-20261020), `stage_g_release_verification.json` |

## 2. District 2 (`Schlosspark-Viertel & Lindenallee`) Inventory Breakdown

- **8 New Buildings (`B13`–`B20`) & Ground-Floor Shops (`32` shop rooms + `66` residential apartments = `462` new apartment rooms):**
  - `B13` — *Kino Astoria* (Art-Deco cinema & café with illuminated vertical marquee blade sign, 5 storeys, North Lindenallee)
  - `B14` — *Galerie & Kunsthandlung Lindner* (Neoclassical limestone gallery, 5 storeys, North Lindenallee)
  - `B15` — *Brauhaus zum Goldenen Hirsch* (Half-timbered Fachwerk brewery & tavern with central stone bay, 6 storeys, North Lindenallee)
  - `B16` — *Musikinstrumente & Geigenbau Stradivari* (Violin luthier & conservatory house, 5 storeys, East Park Terrace)
  - `B17` — *Confiserie & Chocolaterie König* (Pastel plaster with wrought-iron Juliet balconies, 5 storeys, East Park Terrace)
  - `B18` — *Antiquariat & Kupferstiche Humboldt* (Rare books & copperplate print shop, 6 storeys, East Park Terrace)
  - `B19` — *Weinhandlung & Sektkellerei Mosel* (Wine merchant & vaulted cellar shopfront, 5 storeys, South Lindenallee)
  - `B20` — *Markthalle Ost* (Dark slate/zinc neighbourhood market hall, 5 storeys, South Lindenallee)
- **Vehicles (`10` multi-material 3D vehicles in `CITY_VEHICLES_D2`):**
  - `TRAM_01_LINDENALLEE`: Articulated green/cream electric streetcar with 3-pane glowing front/rear driver windscreens, illuminated destination box (`LINIE 4 SCHLOSSPARK`), roof pantograph on overhead catenary wire, steel bogies, and warm-lit passenger cabin.
  - `CARRIAGE_01`: Horse-drawn Viktoria park carriage with burgundy coachwork, gold-leaf trim, velvet seats, folded leather hood, glowing coach lanterns, and spoked wooden wheels.
  - `8` Motor Vehicles: Municipal delivery/snowplow truck (`VEHICLE_04`), yellow postal van (`VEHICLE_07`), cream vintage taxi (`VEHICLE_03`), and 5 winter sedans (`VEHICLE_01, 02, 05, 06, 08`).
- **Animals (`34` smooth-sculpted 3D animals in `CITY_ANIMALS`):**
  - `2` harnessed draught horses (`ANIMAL_HORSE_01..02`), `8` dogs with collars (`ANIMAL_DOG_01..08`), `4` cats (`ANIMAL_CAT_01..04`), `10` mallard ducks along the frozen pond (`ANIMAL_BIRD_01..10`), `8` grounded city pigeons along the pathways (`ANIMAL_BIRD_11..18`), and `2` red squirrels on park benches (`ANIMAL_SQUIRREL_01..02`).
- **Park Architecture, Trees, Poles & Street Furniture:**
  - `18` steel utility & tram catenary T-poles (`UTILITY_POLE_01..18`) with porcelain insulators and overhead catenary/power wires (`BOULEVARD_POLES_AND_WIRES`).
  - `49` trees total: `32` winter deciduous trees (`DECIDUOUS_TREE_01..32`), `16` snow-laden park spruces (`PARK_TREES_SPRUCE`), and the `11 m` centerpiece Christmas tree (`SQUARE_CHRISTMAS_TREE`).
  - Victorian octagonal copper-domed bandstand (`PARK_BANDSTAND`), elliptical frozen pond & arched limestone footbridge with turned balusters (`PARK_POND_AND_BRIDGE`), wrought-iron park fence & 4 gates (`PARK_FENCE_AND_GATES`), `52` street lamps, `44` benches, `3` Litfaßsäule columns, `2` red glass telephone booths, `4` postboxes, `6` fire hydrants, `12` litter bins, and `2` tram shelters.

## 3. Published Binary Artifacts & Anonymous Round-Trip Verification (§29)

### Stage C–G Master Release: [`townsquare-stage-g-20261020`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-g-20261020)
- **`master.blend`:** `57,523,288` B · SHA-256 `2a369754cf4c965f215b1a5c849488bdba3cbe05ab416fa459a0028745525536`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master.blend`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**
- **`master.glb`:** `137,508,380` B · SHA-256 `de669fad5e75f69a83528eb037a5a403d6cf3050495755b650acd2be3e4b844d`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master.glb`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**
- **`master_renders_proofs.tar.gz` (`287` proof PNGs):** `367,586,527` B · SHA-256 `24ac7979892fdee282c75b98305608c0626a76451ab9131a0d769b02639d7455`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master_renders_proofs.tar.gz`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**
- **`master_renders_final.tar.gz` (`287` final PNGs):** `2,110,891,862` B · SHA-256 `20b3e948cc91254509a877d6b11529ff0e5caa3cdf1c7f85a576950dca5b90f6`
  - URL: `https://github.com/dreamer2664/storagecode/releases/download/townsquare-stage-g-20261020/master_renders_final.tar.gz`
  - Anonymous HTTP 200 & round-trip SHA-256 match: **PASS**

### Stage B Vertical Slice Release: [`townsquare-stage-b-20261019`](https://github.com/dreamer2664/storagecode/releases/tag/townsquare-stage-b-20261019)
- **`slice_B02_L02.blend`:** `135,429,256` B · SHA-256 `2bee4a4161c436e42f22395df2e283bad744e166b388fea3e7773db749` (**PASS**)
- **`slice_B02_L02.glb`:** `114,194,428` B · SHA-256 `bc4cec7bae7295db37e2e888cfcf02fd62b6bd40a24f861ac8e6416f083cc52c` (**PASS**)
- **`stage_b_renders_final.tar.gz`:** `181,333,645` B · SHA-256 `fe2b33e03ee5999088e212d7935ac7426f913b78ddebc2ad50ceeec45db8c4b4` (**PASS**)

## 4. Gate Validation Summary (`townsquare/evidence/validation/*.json`)
- **G1 (`v_programme.py --people`):** `PASS` — 20 freestanding buildings (`B01–B20`), 88 residential floors, 176 apartments (2.00/floor), 1,232 apartment rooms, 80 shop rooms, 88 landings (`1,400` rooms total), 0 unreachable rooms.
- **G2 (`v_scale.py`, `v_contact.py`, `v_clearance.py`):** `PASS` — 1 BU = 1.0 m, float ≤ 2 mm (`max=0.4 mm`), interpenetration ≤ 1 mm (`max=0.2 mm`), 0 coplanar faces, bevel 1–3 mm, ≥ 20 px/cm @ 4K (`24.8 px/cm`).
- **G3 (`v_density.py`):** `PASS` — living ≥ 45 (`52`), kitchen ≥ 60 (`68`), bedroom ≥ 25 (`31`), bathroom ≥ 18 (`22`), entry ≥ 12 (`16`), shop ≥ 80 (`94`), public realm ≥ 25/100 m² (`38.6`).
- **G4 (`v_distinct.py --people`):** `PASS` — 176 unique apartment signatures, 8 plan archetypes, 8 palettes, 4 furnishing generations, 3 occupancy types, 340 humans (`168` indoors, `172` outdoors, `56` identities, `12` close-range heroes, `0` capsules/billboards, `0` identity collisions).
- **G5 (`v_light.py`):** `PASS` — ≥ 2 sources/room, 8/8 clear emitter rays, blown `0.0021 < 0.01`, crushed `0.0064 < 0.02`, 0 fireflies.
- **G6 (`v_blind.py`):** `PASS` — 2AFC blind test `5/10` across all 4 classes (`exterior`, `interior`, `human`, `terrain`).
- **G7 (`v_export.py`, `v_package.py`, `test_validators.py`):** `PASS` — 1,823/1,823 GLB round-trip parity (`7,892,418` triangles), 287/287 inspected views with unique SHA-256 hashes, 40 curated showcase JPEGs (`69.31 MB` total, max `3.53 MB`), 10/10 negative validator tests passing.

## 5. Clean-Checkout Reproduction Commands
```bash
# 1. Regenerate deterministic 20-building programme, 108 floor-plan SVGs, 20 branding SVGs, and 287 VIEWS.json entries
python3 townsquare/tools/generate_programme.py

# 2. Rebuild master.blend and master.glb (Winterlichtplatz + Schlosspark-Viertel & Lindenallee)
blender --background --python-exit-code 1 --python townsquare/scene/build_master.py

# 3. Run all 10 validators and the 10-case positive/negative test suite
python3 townsquare/tools/test_validators.py

# 4. Render proof (1024x576) or final (4K/1440p/1080p) views (incremental cache via renders/manifest.json)
python3 townsquare/tools/render_queue.py --scene master --tier proof
python3 townsquare/tools/render_queue.py --scene master --tier final
```

Independent non-owner acceptance remains PENDING. No self-review/vote.
