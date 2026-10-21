# CONSTANTS.md — CLOACA VICTORIA

The numbers the generator is not allowed to improvise. Every constant cites `REFERENCES.md` (R-nnn) or the master packet (§). Where the record and the packet disagree, `CONFLICTS.md` adjudicates and the adjudication is binding on the generator.

## 1 Units and frames

| constant | value | source |
|---|---|---|
| Blender unit | 1 unit = 1 metre, exact | §15.1 |
| axis | +X = down-sewer (chainage), +Z = up, +Y = lateral | lane convention |
| chainage origin | each line's upstream head; station = metres from origin | §13.8 continuous numbering |
| levels datum | invert level in metres above a per-line declared datum; tide levels above Chart Datum (≈LAT) | R-118, C-008 |
| time | UTC everywhere; all evidence timestamps `%Y-%m-%dT%H:%M:%SZ` | §1 |

## 2 Brick law

| constant | value | source |
|---|---|---|
| London stock brick | 229 × 114 × 76 mm | R-041 |
| nominal mortar joint | 10 mm | R-042 |
| course module (axial) | 86 mm | derived: 76 + 10 |
| brick module (circumferential) | 239 mm | derived: 229 + 10 |
| wythe thickness (radial) | 114 mm | R-043 |
| ring thickness | 228 mm (2 wythes) or 342 mm (3 wythes) | R-043, §15.1 |
| per-brick deviation | position, dimensions and colour drift within ±2 mm of nominal | §13.2 |
| closure brick | one cut brick per course closes the ring; joint widths stay nominal | C-006 |
| hand-placed bricks | do not exist — every brick is laid from its ledger row (R5) | §1.8 R5, §17.12 |

## 3 Profile law (`PROFILE.json`)

| constant | value | source |
|---|---|---|
| ovoid construction | lower semicircle radius *r* + upper half-ellipse (*a*=*r*, *b*=3*r*), tangent-continuous at the springing | R-022, C-002 |
| ovoid overall | height 4*r*, width 2*r*; canonical *r* = 0.675 m → 2.700 × 1.350 m | R-142 (±20 mm) |
| circular bores | used only where the schedule cites them | R-024, F39 |
| rectangular chambers | head-shafts, junction chambers, outfall culverts (e.g. 3 × 9 ft × 9 ft at Abbey Mills) | R-024 |
| small end | down — dry-weather flow rides the narrow invert so scour velocity holds | R-018, R-019 |

## 4 Mesh law (how a brick exists in a `.blend`)

| rule | value | source |
|---|---|---|
| one brick | one closed 8-vertex island with its own ±2 mm deviation, in a course-band object | C-009 |
| object granularity | one mesh object per (wythe, 100-course band); island count = brick count | C-009, measured in `evidence/CENSUS/` |
| census | island count recomputed from mesh connectivity, never declared | G4, F15 |
| linkage | every ledger row's position is recomputed from (key, seed, profile, gradient row); `v_bricks` proves geometry exists at each sampled row | F42 |
| chunk open time | < 120 s headless on the declared worker (2 cores, 1.9 GB, no swap) | §15.5 |
| memory ceiling | ≤1.2 GB per process | agency `SANDBOX.md`, 2 GB doctrine |

## 5 Key law (R1, R4)

```
chunk_key = sha256( GENERATOR_VERSION || "\n" || seed || "\n" || profile_row_json || "\n" || gradient_row_json )
```
An unchanged key is never rebuilt. An edit to `INDEX.jsonl` invalidates exactly the affected keys. A chunk rebuilt with a stale key is F29.

## 6 Gradient law (G3)

| constant | value | source |
|---|---|---|
| minimum fall | 0.378 m/km (2 ft/mile) on every line | R-012, R-013 |
| declared falls | per line in `PROFILE.json` (`fall_m_per_km`), 0.40–1.05 m/km | R-014 (2–4 ft/mile), R-015 (≈1:1000) |
| uphill metres | zero, at every one of the 1,319 joins | §15.1, F36 |
| per-chunk fall variance | seeded, held inside 0.6×–1.4× nominal and always > 0 | §13.1, F35 |
| join tolerance | invert continuity ±10 mm across every join | §15.1, F12 |
| self-cleansing velocity | ≥0.67 m/s half-full; ≥0.9 m/s at dry-weather depth on the ovoid small end | R-016, R-017 |

## 7 Water law (G7)

| constant | value | source |
|---|---|---|
| constituents | M2, S2, N2, K1, O1 — speeds 28.9841042, 30.0, 28.4397196, 15.0410686, 13.9430356 °/h | R-108 |
| equilibrium amplitudes | M2 0.2424, S2 0.1129, N2 0.0460, K1 0.1414, O1 0.1003 m | R-109 |
| synthesis | h(t) = Z0 + Σ fᵢ·Aᵢ·cos(Vᵢ + uᵢ − gᵢ), nodal factors f and u computed astronomically | R-110, R-111 |
| sim window | 28 days from 1865-04-04T00:00Z (Crossness opened by the Prince of Wales) | R-079 |
| gauges | 6, hourly → 4,032 samples, tolerance ±0.15 m | §15.4 |
| overflows | 6 storm reliefs, actuated by sim conditions alone; zero scripted actuations | §15.4, F38 |
| interior flow depth | equals the station's `HYDRAULICS.jsonl` row; dry-weather flow rides the ovoid small end | §13.5, R-018 |

## 8 Engine law (G5, G6)

| constant | value | source |
|---|---|---|
| engines | 22 = Abbey Mills 8 · Crossness 4 · Deptford 6 · Chelsea 4 | §13.4 |
| parts per engine | ≥4,200 individually modelled and individually named | §13.4 |
| beam stroke | 3.05 m (packet declaration; historical Crossness 2.743 m logged) | §15.3, C-003 |
| speed | 14 strokes/min ±0.5 = 7.0 rev/min for a double-acting rotative engine | §15.3, C-004 |
| flywheel | angular velocity within ±2 % across the cycle, sampled every 5° | §15.3 |
| flywheel geometry | Crossness: 8.23 m diameter, 52 t, built up in 8 parts | R-068 |
| beam geometry | Crossness: 12.8–13.1 m long, 6 ft deep, 28 t each, two per pair of wheels | R-069 |
| cylinder | Crossness 1.219 m bore; Abbey Mills 1.372 m bore (54 in) | R-064, R-085, C-005 |
| pumps | Crossness: 8 × 1.372 m plungers in a 3.66 m casing, single-acting, 5.5–6 t/stroke, lift 9.1–9.8 m | R-071, R-073, C-007 |
| P-V diagram | derived from the cylinder simulation per engine, never drawn by hand | §13.4, F37 |
| floating parts mid-cycle | zero | §15.3 |

## 9 Period law (G8, G10)

| constant | value | source |
|---|---|---|
| period | 1858–1875 | §1.2 |
| light | gas, fire, daylight — and nothing else; every render lists its sources | §17.5, G10 |
| Crossness engines | modelled in their 1865 single-cylinder state; the 1895–1901 triple-expansion rebuild is out of period | R-081, C-010 |
| anachronisms | zero in a 100-view random audit | G8 |

## 10 Delivery law

| constant | value | source |
|---|---|---|
| chunks | 1,320 × 100 m, each its own `.blend` + key; `INDEX.jsonl` **is** the network | §13.1 |
| chunk binaries | release payloads, never Git history | §8 |
| every push | → one `storagecode/PUSHES.md` row | §8 |
| window | rolling release `best-renders-cloaca`, `BEST.zip` + five-line status body | §41 |
| forbidden words | §30 list — enforced mechanically by `v_language` | §30 |
