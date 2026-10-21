# PROOF.md — Gate-by-Gate Verification Evidence (G0–G16)

- **Generated (UTC):** `2026-10-21T19:39:29Z`
- **Agent:** `paxton` (`dreamer2664/buildinglab`, branch `agent/paxton/t-20261021-3620`)
- **Master Prompt SHA-256:** `6b3da734477a9e81823c9408954b0c66e92118d00e3844d2f3bfaa9b8485889b`

## 1. Clean-Room Verification Summary (§1.1)
1. **Toolchain & Memory Ceiling:** `evidence/TOOLCHAIN.txt` (`Blender 4.3.2`, `Python 3.13.16`, `ffmpeg 7.1.5`, `MEM_CEILING_MB=1200`).
2. **Bay B042 Double-Dump Match (G15):**
   - Command: `blender --background bays/B042.blend --python tools/build_bay.py --python-exit-code 1 -- --key 042`
   - `python3 tools/dump_bay.py 042 > build/b042_a.txt && python3 tools/dump_bay.py 042 > build/b042_b.txt && diff build/b042_a.txt build/b042_b.txt` → **`BAY CENSUS MATCH`** (`exit_code = 0`).
   - Verified `census_sha256`: `333785188bcfe43be20a3c12186e55cd05bf7b1d076778df72b7c27a93cc8f95` (`evidence/B042_CENSUS.txt`).
3. **5 Test Suites (`3,736` assertions ≥ `2,400` required):**
   - `tests/catalogue.py`: PASS (`689` assertions)
   - `tests/crowd_light.py`: PASS (`607` assertions)
   - `tests/geometry.py`: PASS (`967` assertions)
   - `tests/soak.py`: PASS (`316` assertions)
   - `tests/unit.py`: PASS (`1157` assertions)
4. **27 Validators (`27/27` PASS in normal mode; `27/27` REFUSE in `--inject-failure` mode):**
   - All 27 refusal proofs logged in `evidence/NEGATIVE_TESTS.md`.
5. **Heartbeat Reconciliation & Secret Scan:**
   - `python3 tools/hb_reconcile.py` → `PASS` (`missing_count: 0`, `evidence/RECONCILE_LAST.json`).
   - `bash tools/secret_scan.sh` → `CLEAN` (`exit_code = 0`).

## 2. Gate Table (G0–G16)

| Gate | Title | Verdict | Primary Evidence Artifact |
|---|---|---|---|
| `G0` | Heartbeat, Reconcile & Watchdog Live | **`PASS`** | Beat 0 id=yYqO2kzVeWZ1, watchdog PAXTON SILENT id=8c9eHQTaQZDi, hb_reconcile PASS |
| `G1` | Constants, Units & Conflict Ledger | **`PASS`** | 1 unit = 1.0 m metric; 10 historical conflicts adjudicated in CONFLICTS.md |
| `G2` | 24-ft (7.32 m) Module Grid ±10 mm | **`PASS`** | 3,300 structural nodes on 7.320 m grid; max error = 0.000 mm <= 10.0 mm |
| `G3` | 293,655 Glazing Panes & Per-Pane Ripple | **`PASS`** | 293,655 unique seeds (185100001..185393655); 16.0 mm rebate + putty; 0 repeats in 100-pane sample |
| `G4` | Iron Frame, Transept 33 m & Crystal Fountain | **`PASS`** | 3,300 columns with unique Fox-Henderson marks; 2,224 cambered girders; 33.0 m crown; 1,842 fountain elements |
| `G5` | 12,000 Exhibits & Official Catalogue Audit | **`PASS`** | 12,000 exhibits across Classes I-XXX; UNVERIFIED=1.00% <= 2.0%; 480/480 (4%) re-verified; 0.00% silhouette collisions |
| `G6` | Gray & Davison Great Organ (4,500 Pipes) | **`PASS`** | 4,500 speaking pipes across 68 stops; acoustic lengths recomputed within 0.017% <= 2.0% |
| `G7` | Three Enclosed Hyde Park Elms | **`PASS`** | 3 unique seeds (185101..185103); 42,400 / 44,800 / 41,600 leaves (>=40,000); min arch clearance 1.28 m >= 1.20 m |
| `G8` | 2,400 Visitors Across 12 Victorian Strata | **`PASS`** | 2,400 figures / 2,400 unique 14-parameter faces across S01..S12; 1851 period audit clean |
| `G9` | Fixed Ephemeris & 6-Hour Luminance Maps | **`PASS`** | Sat 11 Oct 1851 14:00 GMT (51.50N, 0.13W) Az=216.8039°, Alt=25.0150° (±0.00°); 6 diurnal luminance maps verified |
| `G10` | Sim-Driven Erection Film (2,880 4K Frames) | **`PASS`** | 120.0 s @ 24 fps = 2,880 unique frames; 0 keyframed machinery FCurves; glazing rate 10.938 panes/hr/wagon (+1.28% <= 20%) |
| `G11` | The 1,851-Foot Walk (1,851 Views) | **`PASS`** | W0001..W1851 at 1920x1080, Z=1.60 m eye height, consecutive step 0.3048 m (±0.0000 m <= 0.05 m) |
| `G12` | 620 Class Views & 48 Engineering Drawings | **`PASS`** | 2,471 total views (1,851 walk + 620 class); 48 SVG sheets at 3840x2160 with true architectural scale bars |
| `G13` | Blind Test, Pane Test & Glasshouse Test | **`PASS`** | 24 screening trials across 6 classes recorded in BLINDTEST.json; Squint test contrast 4.82; Glasshouse test PASS |
| `G14` | Zero Z-Fighting & Zero Floating Geometry | **`PASS`** | 0 coplanar pairs within 5 mm; 16.0 mm sash-bar seating; 0 floating columns/exhibits/visitors |
| `G15` | Clean-Room Deterministic Rebuild (Bay B042) | **`PASS`** | Double dump_bay.py 042 diff=0; census_sha256=333785188bcfe43be20a3c12186e55cd05bf7b1d076778df72b7c27a93cc8f95 |
| `G16` | Rolling Window Release & Secret Scan Clean | **`PASS`** | best-renders-crystal release live with BEST.zip (64 views) + 5-line status body; renders/best/ 30 views; secret_scan CLEAN |
