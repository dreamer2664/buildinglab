# CONSTANTS.md — PAXTON / CRYSTAL

Canonical structural, optical, acoustic, astronomical, and census constants for **CRYSTAL** (The Crystal Palace of 1851, Hyde Park, London). Every generator, ledger, and validator (`validate/v_*.py`) reads or checks against these numbers.

## 1. Coordinate System & Units (G1, G2)

| Constant | Symbol | Value | Tolerance / Rule |
|---|---|---|---|
| Blender unit | `UNIT_M` | `1.0 m` (`scale_length = 1.0`) | Exact (`metric`) |
| Origin `(0, 0, 0)` | `ORIGIN` | Center of the Crossing (intersection of Central Nave and Transept axes at ground floor datum `Z = 0.000 m`) | Exact |
| Axes | `+X, +Y, +Z` | `+X` = East (towards Hyde Park Corner / Exhibition East End), `+Y` = North (towards Rotten Row), `+Z` = Up | Right-handed ENU |
| Structural module | `MODULE_M` | `7.32 m` (`24 ft` nominal; `7.3152 m` exact Imperial) | Every structural column/girder node on grid `±10 mm` (`G2`) |
| Half-module (8-ft ridge pitch) | `RIDGE_PITCH_M` | `2.44 m` (`8 ft`) | 3 ridge-and-furrow waves per `7.32 m` bay |
| Nave clear span | `NAVE_SPAN_M` | `21.96 m` (`72 ft` = `3 × 7.32 m`) | Central nave width between inner column lines |
| Transept clear span | `TRANSEPT_SPAN_M` | `21.96 m` (`72 ft` = `3 × 7.32 m`) | Vaulted arch clear span |

## 2. Building Envelope & TierElevations (G2, G4, G16)

| Parameter | Value | Imperial Equivalent | Notes / Citation |
|---|---|---|---|
| Overall length (E–W) | `564.00 m` (`77 × 7.32 m = 563.64 m` grid + `0.36 m` end casings) | `1,851 ft` | Tolerance `±0.2 m` (`REF-001`) |
| Overall width (N–S main body) | `124.44 m` (`17 × 7.32 m`) + North machinery projection `13.56 m` = `138.00 m` | `454 ft` (`408 ft` main + `46 ft` north annex) | Tolerance `±0.2 m` (`REF-002`) |
| Ground tier column height | `Z = 0.00 m → 7.32 m` | `24 ft` | Including base socket and connecting piece (`REF-015`) |
| First gallery tier height | `Z = 7.32 m → 13.42 m` | `20 ft` clear (`44 ft` cumulative) | Gallery floor at `Z = 7.32 m` (`REF-016`) |
| Second (nave clerestory) tier | `Z = 13.42 m → 19.52 m` | `20 ft` clear (`64 ft` cumulative) | Flat ridge-and-furrow nave roof at `Z = 19.52 m` (`REF-017`) |
| Transept barrel-vault spring | `Z = 19.52 m` | `64 ft` | Semicircular wrought-iron laminated/trussed ribs (`REF-028`) |
| Transept barrel-vault crown | `Z = 33.00 m` | `108 ft` (`108 ft 3 in`) | Tolerance `±0.1 m` (`G4`, `v_transept`, `REF-029`) |
| Underfloor ventilation void | `Z = -1.22 m → 0.00 m` | `4 ft` sub-floor cavity | `38 mm` (`1.5 in`) floorboards with `12.7 mm` (`0.5 in`) dust/air gaps (`G16`, `REF-042`) |

## 3. Glazing Law (G3, F35)

| Parameter | Value | Rule |
|---|---|---|
| Total panes | `293,655` | Exact (`PANES.jsonl` rows = mesh census ± 0) |
| Pane length × width × thickness | `1,245 mm × 254 mm × 2.0 mm` (`49 in × 10 in`, 16 oz/sq ft blown cylinder/crown sheet glass) | Tolerance `±0.5 mm` (`REF-010`) |
| Sash-bar rebate seating depth | `16.0 mm` (`≥ 15 mm` required per `F3`) | With modelled linseed-oil putty fillet |
| Furrow-to-ridge slope angle | `21.8°` (`2.5 : 1` horizontal-to-vertical pitch on `2.44 m` ridge spacing) | Self-draining into Paxton gutters & condensation grooves |
| Per-pane seed & ripple | `293,655` distinct deterministic integer seeds (`seed_i`) | Drives both vertex-level crown-glass wave displacement (`δz ∈ [0.18, 0.85] mm`) and per-pane material IOR/roughness micro-perturbation (`F35`) |

## 4. Cast & Wrought Iron Law (G4, F39, F40)

| Parameter | Value | Rule |
|---|---|---|
| Hollow cast-iron columns | `3,300` | Exact (`COLUMNS.jsonl`); unique foundry mark per casting (`FXH-1850/1851-C0001..C3300`, Fox, Henderson & Co., London Works, Smethwick) |
| Column outer diameter | `203.2 mm` (`8 in`) with4 flattened fillet faces | Wall thickness schedule `9.5 mm` (`3/8 in`) to `28.6 mm` (`1-1/8 in`) by tier load (`REF-018`) |
| Lattice girders (cast & wrought) | `2,224` | Exact (`GIRDERS.jsonl`); spans `7.32 m` (`24 ft`), `14.64 m` (`48 ft`), `21.96 m` (`72 ft`) |
| Girder depth | `914.4 mm` (`3 ft 0 in`) standard | Camber `6.5 mm` (`24 ft`), `14.0 mm` (`48 ft`), `25.4 mm` (`72 ft`); bolt-hole counts `12`, `18`, `24` per schedule (`REF-022`) |
| Owen Jones decorative palette | Interior ironwork: Blue (`#2B5B84`) on concavities, Red (`#B63125`) on soffits/under-surfaces, Yellow (`#E5B822`) on projecting fillets; White canvas roof cloth | Cited in `REF-035..038` |

## 5. The Three Wonders (G4, G6, G7)

| Wonder | Census / Law | Specification |
|---|---|---|
| **Crystal Fountain** (F. & C. Osler, Birmingham) | `1,842` faceted flint-glass elements | `8.23 m` (`27 ft`) total height; octagonal water-jet basin (`7.32 m` diameter), central shaft, 3 progressive dish tiers, tier rods, and pendant prism chains (`v_fountain`) |
| **Great Organ** (Gray & Davison, London) | `4,500` speaking pipes (`≥ 4,000` required; adjudicated in `CONFLICTS.md` C-001) | 3 manuals (Great, Swell, Choir) + Pedal, 60 stops; hall temperature `T = 16.0 °C` (`c = 340.87 m/s`); pitch `A4 = 440.0 Hz` (`1851 Philharmonic / Gray & Davison tuning fork schedule documented in CONFLICTS.md`); every pipe length `L = (c / (2 f · k_scale)) - Δ_end` recomputed within `±2%` (`v_organ`) |
| **Three Hyde Park Elms** (*Ulmus × hollandica* / English elm) | `3` distinct trees (`ELM_NORTH`, `ELM_CENTER`, `ELM_SOUTH`) | Unique procedural seeds (`185101`, `185102`, `185103`), `≥ 40,000` leaves each (`42,400`, `44,800`, `41,600`), crown heights `26.8 m`, `29.4 m`, `25.9 m`, clearance to transept arch ribs `≥ 1.20 m` (`v_trees`) |

## 6. The Great Exhibition & Crowd (G5, G8, G9)

| Parameter | Value | Rule |
|---|---|---|
| Modelled exhibits | `12,000` rows in `EXHIBITS.jsonl` | Real exhibitor, real city/country, Class I–XXX, Official Catalogue citation (`UNVERIFIED ≤ 2%`, `0.0%` target; `4%` = `480` rows re-verified; `≥ 8` parts per non-Class-I exhibit; silhouette collision `≤ 0.5%`) |
| Visitors | `2,400` individual figures / `2,400` unique faces | Distributed across `12` Victorian social strata per `STRATA.md`; zero identity swaps (`F16`) |
| Fixed scene date & hour | `Saturday 11 October 1851, 14:00:00 GMT` | Shilling day near close of Exhibition |
| Fixed solar position | Azimuth `216.8039°`, Altitude `25.0150°` (`±1.0°`) | Hyde Park (`51.50°N, 0.13°W`), row `EPH-18511011-1400-FIXED` in `EPHEMERIS.json` |

## 7. Erection Film & Image Campaign (G10, G11, G12, G13)

| Parameter | Value | Rule |
|---|---|---|
| Erection film | `2,880` unique 4K frames (`3840 × 2160`, `24 fps`, `120.00 s`) | Sim-driven travelling towers, rope winches, and Paxton glazing wagons; simulated glazing rate within `±20%` of documented rate (`~18,350 panes/week` fleet or `~1.25 panes/min` per wagon pair, `RATES.jsonl`) |
| The 1,851-ft Walk | `1,851` views at `1920 × 1080` (`W0001..W1851`) | Eye height `Z = 1.60 m`, consecutive station spacing `0.3048 m` (`1.0 ft`) `±0.05 m` along East-to-West nave axis |
| Class views | `620` views (`12` classes across `3840×2160` and `2560×1440`) | Total required views = `1,851 + 620 = 2,471`; tagged geometry coverage `≥ 60%` |
| Publication best-of (`renders/best/`) | `30` images (`2560 px` long edge, `≤ 4 MB` each, `≤ 100 MB` total) | Plus rolling GitHub release `best-renders-crystal` (`BEST.zip` + 5-line status body per `§41`) |
