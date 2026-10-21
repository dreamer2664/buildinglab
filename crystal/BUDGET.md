# BUDGET.md — Census, Memory, Render & Schedule Arithmetic (PAXTON / CRYSTAL)

Every gate count in **CRYSTAL** is governed by closed-form arithmetic so that `census == ledger ± 0` holds by construction and fits within the **2 GB Sandbox Doctrine** (`≤ 1,200 MB` RSS per process, `agency/SANDBOX.md`).

---

## 1. Bay & Glazing Census Arithmetic (`293,655` Panes, `G3`)

The building is partitioned into **85 canonical bay/sector units** (`B000..B084` in `ledgers/BAYS.jsonl`):
- **Nave & Aisle Bays (`B000..B076`, 77 bays along the `564 m` East–West axis):**
  - Bays `B000..B036` (West Nave, 37 bays)
  - Bays `B037..B039` (Central Transept Crossing & North/South Transept Arms, 3 bays wide = `21.96 m`)
  - Bays `B040..B076` (East Nave, 37 bays)
- **North Machinery Annex & End-Screen Sectors (`B077..B084`, 8 specialized structural sectors).**

### Exact Pane Partition across `ledgers/PANES.jsonl`:
1. **74 Standard Nave/Aisle Bays (`B000..B036` and `B040..B076`):**
   - Ridge-and-furrow roof panes per bay: `3,000` panes (`6` ridge slopes × `500` panes along transverse width) = `74 × 3,000 = 222,000` panes.
   - Clerestory & gallery wall sash panes per bay: `580` panes = `74 × 580 = 42,920` panes.
   - **Subtotal (74 Nave Bays):** `264,920` panes (`3,580` panes/bay).
2. **3 Central Transept Vault & Crossing Bays (`B037..B039`):**
   - Barrel-vault laminated rib glazing + lead-flat side aisles: `3 × 6,400 = 19,200` panes.
   - North & South Transept arched radial fanlights and gable walls: `3 × 800 = 2,400` panes.
   - **Subtotal (3 Transept Bays):** `21,600` panes (`7,200` panes/bay).
3. **8 North Annex & East/West End-Screen Bays (`B077..B084`):**
   - Bays `B077..B083` (7 bays × `890` panes) = `6,230` panes.
   - Bay `B084` (East/West entrance lantern & clerestory closure) = `905` panes.
   - **Subtotal (8 Annex/End Bays):** `7,135` panes.
4. **Grand Total (`PANES.jsonl`):**
   $$264,920 + 21,600 + 7,135 = \mathbf{293,655\text{ panes}}$$
   - Every pane row `P000001..P293655` has a unique deterministic seed `seed = 1851000000 + pane_index` (`293,655` unique seeds, zero collisions).

---

## 2. Ironwork Census Arithmetic (`3,300` Columns & `2,224` Girders, `G4`)

### 2.1 Cast-Iron Columns (`3,300` rows in `ledgers/COLUMNS.jsonl`)
- **Ground Floor Tier (`Z = 0.00 → 7.32 m`):** `74` standard bays × `22` columns/rank + transept/end ranks = `1,872` columns (`height_class = "ground_24ft"`).
- **First Gallery Tier (`Z = 7.32 → 13.42 m`):** `10` gallery/nave columns × `77` ranks + transept galleries = `916` columns (`height_class = "gallery_20ft"`).
- **Nave Clerestory Tier (`Z = 13.42 → 19.52 m`):** `6` nave clerestory columns × `77` ranks + `50` transept/end stiffeners = `512` columns (`height_class = "clerestory_20ft"`).
- **Grand Total (`COLUMNS.jsonl`):**
  $$1,872 + 916 + 512 = \mathbf{3,300\text{ columns}}$$
  - Every column has a unique foundry mark `FXH-1851-C0001` through `FXH-1851-C3300`.

### 2.2 Lattice Girders & Trusses (`2,224` rows in `ledgers/GIRDERS.jsonl`)
- **Class A (`24-ft / 7.32 m` Cast-Iron Lattice Girders):** `1,840` girders (`camber_mm = 6.5`, `bolt_holes = 12`).
- **Class B (`48-ft / 14.64 m` Trussed Cast/Wrought Aisle Girders):** `310` girders (`camber_mm = 14.0`, `bolt_holes = 18`).
- **Class C (`72-ft / 21.96 m` Wrought-Iron Nave & Transept Roof Trusses):** `74` trusses (`camber_mm = 25.4`, `bolt_holes = 24`).
- **Grand Total (`GIRDERS.jsonl`):**
  $$1,840 + 310 + 74 = \mathbf{2,224\text{ girders}}$$

### 2.3 Paxton Gutters (`1,540` runs in `ledgers/GUTTERS.jsonl`)
- Each of the `77` main E–W bay lines carries `20` transverse/longitudinal Paxton box-gutter runs (`178 mm × 152 mm` seasoned red deal timber with cambered iron tie-rod shoes and twin side condensation channels), totaling **`1,540` gutter runs** (`36,252 m` / `22.5 miles` total length, matching Paxton's documented 20+ miles of guttering).

---

## 3. Exhibition, Wonders & Crowd Census Arithmetic (`G5, G6, G7, G8`)

| Ledger / Asset | Exact Count | Partition Law |
|---|---|---|
| `EXHIBITS.jsonl` | `12,000` exhibits | `30` Official Catalogue Classes (`I..XXX`) × `400` exhibits per class = `12,000` (`E00001..E12000`), distributed across `33` National/Foreign/Colonial & British Courts (`FLOORPLAN.md`). `100%` cited (`UNVERIFIED = 0% ≤ 2%`); `480` rows (`4.0%`) independently re-verified in `evidence/CATALOGUE_AUDIT.json`. |
| `wonders/fountain.blend` | `1,842` glass elements | Octagonal basin surround (`288`), lower water-column pedestal (`312`), first tier dish & prism fringe (`420`), second tier dish & pendants (`410`), upper spire & lotus crown (`412`) = `1,842` faceted elements. |
| `wonders/organ.blend` | `4,500` organ pipes | Great (`1,512`) + Swell (`1,350`) + Choir (`1,026`) + Pedal (`480`) + Case/Solo (`132`) = `4,500` pipes (`CONFLICTS.md` C-001). |
| `wonders/elms.blend` | `3` elms (`128,800` leaves) | `ELM_NORTH` (`42,400` leaves), `ELM_CENTER` (`44,800` leaves), `ELM_SOUTH` (`41,600` leaves); each `≥ 40,000` leaves, clearance to arch `≥ 1.28 m ≥ 1.20 m`. |
| `VISITORS` (`STRATA.md`) | `2,400` visitors | `12` social strata (`S01..S12`), `2,400` unique facial geometry/proportion descriptors & material palettes, zero identity swaps (`F16`). |

---

## 4. Per-Process RAM Budget (2 GB Sandbox Doctrine, `agency/SANDBOX.md`)

| Process Type | Peak RSS Measured / Budgeted | Safety Margin vs 1,200 MB Ceiling |
|---|---|---|
| Single bay build (`blender --background bays/B###.blend`) | `~210 MB` (3,580 pane meshes + 40 columns + 28 girders + exhibits) | `990 MB` headroom |
| Wonder build (`fountain.blend`, `organ.blend`, `elms.blend`) | `~240–340 MB` | `860 MB` headroom |
| Cycles CPU render (`1920×1080` / `2560×1440` / `3840×2160`, `use_denoising = False`) | `~185–390 MB` | `810 MB` headroom |
| Validator suite (`for v in validate/v_*.py`) | `~65 MB` | `1,135 MB` headroom |

---

## 5. Campaign & 1,120-Hour Schedule Budget (§19)

| Stage | Budgeted Hours | Key Deliverable |
|---|---:|---|
| **Stage 0 · Bootstrap** | `0–4 h` (`4 h`) | `RUN.json`, `TOOLCHAIN.txt`, beat/reconcile/watchdog + kill test |
| **Stage A · Sources + Module** | `4–64 h` (`60 h`) | `CONSTANTS.md`, `REFERENCES.md` (125 rows), `CONFLICTS.md`, `EPHEMERIS.json`, `FLOORPLAN.md`, `STRATA.md`, `DENSITY.md`, `BUDGET.md`, `FAKES.md` |
| **Stage B · Kit + First Bays** | `64–180 h` (`116 h`) | Versioned kit (`column`, `girder`, `sash_bar`, `pane`, `gutter`), `B000.blend`, `B042.blend`, transept bay `B038.blend`, `best-renders-crystal` window opened |
| **Stage C · The Nave** | `180–420 h` (`240 h`) | All 85 bays indexed in `BAYS.jsonl`, `293,655` panes in `PANES.jsonl`, `3,300` columns in `COLUMNS.jsonl`, `2,224` girders in `GIRDERS.jsonl`, `1,540` gutters in `GUTTERS.jsonl` |
| **Stage D · Transept + Wonders** | `420–560 h` (`140 h`) | Segmented transept ribs (`33.0 m` crown), `fountain.blend` (`1,842`), `organ.blend` (`4,500` pipes + arithmetic), `elms.blend` (`3` elms, `≥40k` leaves each) |
| **Stage E · The Exhibition** | `560–760 h` (`200 h`) | `12,000` exhibits in `EXHIBITS.jsonl`, 100% cited, 480 rows (`4%`) re-verified in `CATALOGUE_AUDIT.json` |
| **Stage F · The Crowd** | `760–840 h` (`80 h`) | `2,400` visitors across 12 strata (`VISITORS.jsonl`), bound to Sat 11 Oct 1851 14:00 GMT ephemeris |
| **Stage G · The Erection Film** | `840–920 h` (`80 h`) | `2,880` unique 4K frames (`SHOTS.jsonl`), sim-driven towers/winches/glazing wagons, `RATES.jsonl` within `±20%` |
| **Stage H · The Image Campaign** | `920–1,060 h` (`140 h`) | `1,851` walk stations (`1.0 ft` spacing at `Z=1.6 m`) + `620` class views = `2,471` views in `RENDERS.jsonl` |
| **Stage I · Package** | `1,060–1,090 h` (`30 h`) | 48 engineering drawings, `renders/best/` (30 views), `BLINDTEST.json`, `PANETEST.json`, rolling window `best-renders-crystal`, release `r01` |
| **Stage J · Reproduction** | `1,090–1,120 h` (`30 h`) | Clean-room rebuild of bay `B042`, 26 validators + 26 negative tests + 5 test suites (`≥2,400` assertions) green |
| **Total** | **`1,120 h`** | All 16 gates `G1–G16` green |
