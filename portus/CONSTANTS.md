# PORTUS — CONSTANTS

Transcribed from the commission packet, Part IV §15 and Appendix C, on 2026-10-19 by `hippodamus`.
Where the generator had to choose a value the packet does not fix, the choice is recorded in
`DECISIONS.md` with a number, not silently invented here.

Units: metric, `1 BU = 1 m`, exact. Origin at the **basin south-west corner**, water level `+0.00`,
`+Z` up, north `= +Y`.

## Site and basin

| Parameter | Value | Tolerance |
|---|---|---|
| District | 400 × 320 m = 128,000 m² = 12.8 ha | exact |
| Basin | 180 × 90 m, rectangle x ∈ [110, 290], y ∈ [30, 120] | exact |
| Water level | +0.00 m | ±5 mm |
| Basin depth | 6.00 m (bed at −6.00) | ±0.02 |
| Quay wall top | +2.40 m above water, 6.00 m below | ±0.01 |
| Slipway | 8 % ramp | — |
| Bollards | 40, at 8.00 m centres | ±0.05 |
| Mooring points | 6 | exact |
| Rail tracks | 6 | exact |

## §15.1 Scale and construction

| Parameter | Value | Tolerance |
|---|---|---|
| Units | Metric, 1 BU = 1 m | exact |
| Origin | Basin SW corner, water level +0.00 | exact |
| Residential storey | 3.20 m | ±0.03 |
| Ground / commercial storey | 4.40 m | ±0.05 |
| Warehouse storey | 4.00 m | ±0.05 |
| Ceiling, residential | 2.70 m clear | +0.05 / −0.00 |
| Ceiling, commercial | 3.80 m clear | +0.10 / −0.00 |
| Slab | 0.24 m | ±0.01 |
| Exterior wall | 0.45 m (brick) / 0.60 m (warehouse) | ±0.02 |
| Quay wall | 2.40 m above water, 6.00 m below | ±0.01 |
| Door | 0.90 × 2.10; loading door 2.50 × 3.00 | ±0.015 |
| Human | 1.75 m | ±0.10 |
| Eye height | 1.62 m | ±0.02 |
| Setts | 90–140 mm across, 3 size classes | — |
| Sett joint | 6–12 mm | ±1.5 |
| Kerb | 0.15 m rise | ±0.008 |
| Snow on ledges | 15–50 mm | — |
| Rail gauge | 1,435 mm | ±2 |
| Platform height | 550 mm (low) / 760 mm (high) | ±10 |
| Bollard spacing | 8.00 m | ±0.05 |

## §15.2 Surface craft

| Parameter | Requirement |
|---|---|
| Texel density, hero surfaces | ≥32 px/cm at 4K maps |
| Texel density, background | ≥16 px/cm |
| UV aspect distortion | ≤1.25:1 on any face |
| Overlapping UVs | zero on unique surfaces |
| Hard-edge bevel | 0.5–2 mm (stone 3–5 mm), ±0.5 mm |
| Coplanar faces | zero |
| Detail scales | 4 levels on every hero material: macro (0.5–8 m), meso (5–50 cm), micro (5–50 mm), nano (<5 mm) |
| Albedo variation | ≥12 % value variation across any 2 m² |
| Roughness variation | ≥0.08 across any hero surface |
| Brick coursing | geometric within 6 m of a camera; running bond, mortar recess 8–12 mm |
| Rivets | modelled within 4 m on hero iron structures |
| Wood grain | real displacement on every visible plank and beam |
| Glass | real thickness, edge refraction, per-pane roughness jitter |
| Wet surfaces | water film with contact angle at every edge where water would stop |

## §15.3 Density — modelled props per room

| Room | Minimum | Non-negotiable specifics |
|---|---:|---|
| Living | 70 | ≥60 book spines, 6 cushions, 3 framed pictures, rug with pile, 5 tabletop objects |
| Kitchen | 90 | 10 cabinet doors with handles, 4 burners, 1 pan, 1 kettle, 10 jars, 16 crockery items, 3 cloths |
| Bedroom | 40 | folded duvet, 2 creased pillows, 2 lamps, ≥16 garments |
| Bathroom | 28 | 5 bottle shapes, towel with folds, mat, framed mirror, brush |
| Entry | 18 | 4 coats, 3 pairs of shoes, mat, mirror, letters |
| Shop | 150 | ≥120 stocked products, till, counter, back-room stock |
| Warehouse floor | 60 | 12 pallets, 40 crates, 6 hand trucks, 3 hoists |
| Market stall | 45 | produce in crates, scale, awning, price board, bags, coins |
| Workshop | 80 | 30 tools, bench, vice, stock, sawdust |

A prop is a separate object with ≥40 triangles that a person could name.

## §15.4 Contact and circulation

| Check | Rule |
|---|---|
| Float | ≤1 mm above supporting surface |
| Interpenetration | ≤0.5 mm unless modelled as a joint |
| Door swing | 90° clear arc |
| Residential path | ≥600 mm |
| Commercial path | ≥1,000 mm |
| Quay working apron | ≥4,000 mm clear behind the crane rail |
| Market aisle | ≥1,800 mm |
| Stair | riser 0.16–0.18, tread 0.26–0.30, headroom ≥2.0 |
| Handrail | both sides of every public stair, 0.90 m |
| Seating | every chair within 0.6 m of a surface |
| Wall art | 1.45–1.60 m centre, 30 mm off the wall |
| Books | standing, spines outward, varied heights |

## §15.5 Light

| Check | Rule |
|---|---|
| Sources per room | ≥2 independent (one practical, one window/ambient) |
| Emitter visibility | ray to 8 room points, ≥7 clear |
| Blown highlights | <0.8 % of pixels at 255 (excluding practicals and speculars) |
| Crushed blacks | <1.5 % of pixels below 3/255 indoors |
| Exposure | interior 0.0 ±0.25 EV |
| Colour temperature | 2300–2900 K practicals; 4800–5600 K dawn |
| Fog | exponential, height-falloff, density recorded per shot |
| Fireflies | zero visible at 100 % |

## §15.6 Distinctness

| Check | Rule |
|---|---|
| Arrangement signature | `sha256(sorted(family, position to 5 mm, rotation to 2°))` unique per apartment |
| Plan archetypes | ≥10 |
| Palettes | ≥8 |
| Furnishing generations | ≥5 |
| Occupancy types | ≥4 |
| Building rhythm | 48 unique (storey rhythm, window module, roof pitch) triples |
| Shop identity | 48 unique fascias, 48 original vector marks, 48 window schemes |
| Discrimination test | 10 random pairs at 1024 px; reviewer names a specific difference ≥10/10 |
| Identity test | no identity twice per building or room |

## Programme — fixed by the packet

```
BUILDINGS     48 = A 8 · B 12 · C 4 · D 1 · E 12 · F 5 · G 6
FLOORS        197 = 48 + 60 + 8 + 2 + 48 + 25 + 6
APARTMENTS    208 = B 96 · E 72 · F 40 · exactly 2.00 per residential floor (104 floors)
ROOMS         1,608 = 208×6 + 48×4 + 8×3 + 5×6 + 6×3 + 4×4 + 80 stalls
SHOPS         48 ground-floor units
MOORINGS      6
TRACKS        6
PEOPLE        1,200 · 96 identities · 32 heroes · 0 capsules
VIEWS         705 · BEST 28 images ≤4 MB each ≤90 MB total
```

## The numbers card (Appendix C)

```
DISTRICT  400 × 320 m · 12.8 ha · basin 180 × 90 m · water +0.00 · depth 6.0 · quay +2.40
BUILDINGS 48 in 6 blocks · 197 occupied floors · 208 apartments · exactly 2 per floor
          48 shops · 8 warehouses · 5 civic · market hall with 80 stalls
ROOMS     1,608 · 7 types per apartment · 100 % dressed
PEOPLE    1,200 · 208 indoors · 420 working · 572 public · 96 identities · 32 heroes
WATER     level ±5 mm · draft ±50 mm · foam ≤150 mm · 4 states · bed + 8 dropped objects
RAIL      gauge 1,435 ±2 mm · sleepers 2,600 ±10 · catenary 5.50 ±0.02 · 6 tracks · 14 vehicles
PLANT     4 hammerhead + 2 gantry + 8 jib · every cable ends on a load
SCALE     1 BU = 1 m · storey 3.20 · ceiling 2.70 · door 0.90 × 2.10 · human 1.75
CONTACT   float ≤1 mm · interpenetration ≤0.5 mm · path ≥600/1,000/4,000/1,800 mm
LIGHT     ≥2 sources/room · blown <0.8 % · crushed <1.5 % · 2300–2900 K practicals
VIEWS     705 · 4K exteriors · 1080p apartment proofs · every one opened at 100 %
BEST      28 curated images · ≤4 MB each · ≤90 MB total
GATES     G1 programme · G2 contact · G3 density · G4 distinctness · G5 light
          G6 blind ≤9/20 × 5 classes · G7 systems W1/W2/W3 · G8 reproduction
```
