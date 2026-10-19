# Winterlichtplatz II — CONSTANTS (§16 Hard Numbers Verbatim + §1.2 Summary)

Project: `dreamer2664/buildinglab`, `townsquare/**`
Agent: `vitruvius`
Date: `2026-10-19`

```
TOWN      64 × 52 m · 12 buildings · 55 residential floors · 110 apartments · 2 per floor
          12 shops · 8 stalls · 24 benches · 24 lamps · 12 trees · 1 × 11 m tree
ROOMS     ≥7 types per apartment · 100 % dressed
          living ≥45 props · kitchen ≥60 · bedroom ≥25 · bath ≥18 · entry ≥12 · shop ≥80
PEOPLE    220 · 110 indoors · 120 outdoors · 40 identities · 12 heroes · 0 capsules
SCALE     1 BU = 1 m · storey 3.20 · ceiling 2.70 · door 0.90 × 2.10 · human 1.75 ± 0.10
          cobble 60–120 mm · joint 8–15 mm · curb 0.12 m · snow 20–60 mm
SURFACE   texel ≥20 px/cm @4K · bevel 1–3 mm · zero coplanar · no visible perfect 90°
          3 detail scales per hero material · albedo variation ≥8 % per 2 m²
CONTACT   float ≤2 mm · interpenetration ≤1 mm · paths ≥600/900/1500 mm · swing 90° clear
LIGHT     ≥2 sources/room · emitter ray-visible · blown <1 % · crushed <2 %
          2400–3000 K practicals · 5500–6500 K daylight · 0 fireflies
VIEWS     271 total = 4 heroes + 12 ext + 12 sections + 12 shopfronts
          + 110 apartment interiors + 67 plans + 24 human + 12 terrain + 6 technical + 12 night
          4K exteriors · 1080p apartment proofs · 1440p the rest · every one opened at 100 %
BEST      renders/best/ = 24 images · ≤4 MB each · ≤80 MB total · manifest with master SHA
GATES     G1 programme · G2 contact · G3 density · G4 distinctness · G5 light
          G6 blind ≤6/10 on 4 classes · G7 clean-room reproduction
```

## 16. Hard numbers

Memorise this table. Quote it in your handoff. Put it in `townsquare/CONSTANTS.md` on day one.

### Scale and construction

| Parameter | Value | Tolerance |
|---|---|---|
| Units | Metric, 1 Blender unit = 1 m | exact |
| Origin | Square centre, ground level; +X east, +Y north, +Z up | exact |
| Residential storey | 3.20 m floor-to-floor | ±0.05 |
| Ground storey | 4.20 m floor-to-floor | ±0.10 |
| Ceiling height, residential | 2.70 m clear | +0.10 / −0.00 |
| Ceiling height, commercial | 3.60 m clear | +0.20 / −0.00 |
| Slab | 0.22 m | ±0.01 |
| Exterior wall | 0.40 m total build-up | ±0.02 |
| Interior partition | 0.12 m wet / 0.25 m structural | ±0.01 |
| Door opening | 0.90 × 2.10 m; double 1.50; shopfront 2.40 | ±0.02 |
| Window sill (residential) | 0.90 m | ±0.05 |
| Human height | 1.75 m | ±0.10 |
| Human eye height | 1.62 m | ±0.03 |
| Cobble | 60–120 mm across, 3 size classes | — |
| Cobble joint | 8–15 mm | ±2 |
| Curb / kerb | 0.12 m rise | ±0.01 |
| Snow on perches | 20–60 mm | — |
| Bench seat | 0.45 m | ±0.02 |
| Table height | 0.75 m; café 0.72 | ±0.02 |
| Worktop | 0.90 m | ±0.01 |
| Market stall counter | 1.05 m | ±0.02 |

### Surface craft

| Parameter | Requirement |
|---|---|
| Texel density, hero surfaces | **≥ 20 px/cm** at 4K maps |
| Texel density, background | ≥ 10 px/cm |
| UV aspect distortion | ≤ 1.5:1 on any face |
| Overlapping UVs | zero on unique surfaces; allowed only on repeated tiles, and declared |
| Hard-edge bevel | 1–3 mm (stone 5 mm) — **no perfect 90° edge may be visible in any close view** |
| Coplanar faces | zero |
| Surface detail scale | 3 levels present on every hero material: macro (0.5–5 m), meso (5–50 cm), micro (< 5 cm) |
| Roughness | varied per surface; no single constant roughness on any material used > 2 m² |
| Albedo variation | ≥ 8 % value variation across any 2 m² of a hero surface |
| Normal/bump | present and scaled to the material, not to a global setting |
| Glass | real thickness, edge refraction, slight roughness variation, no zero-thickness planes in close views |
| Fabric | folded, with thickness ≥ 3 mm, no paper-thin cloth |

### Density — objects that must exist, per room

| Room | Minimum modelled props | Specifics that are not optional |
|---|---|---|
| Living room | **45** | ≥ 40 book spines, 4 cushions, 2 framed pictures, 1 rug with pile, 3 tabletop objects |
| Kitchen | **60** | 8 cabinet doors with handles, 4 hob burners, 1 pan, 1 kettle, 6 jars, 12 items of crockery, 2 cloths |
| Bedroom | **25** | folded duvet (not a box), 2 pillows with creases, 2 lamps, ≥ 12 hanging garments |
| Bathroom | **18** | 3 bottle shapes, towel with folds, bath mat, mirror with a frame |
| Entry | **12** | ≥ 3 coats on hooks, 2 pairs of shoes, 1 mat, 1 mirror |
| Shop (ground) | **80** | shelving with ≥ 60 stocked products, till, counter, back-room stock |
| Public realm per 100 m² | **25** | — |

**A prop is a separate object with ≥ 40 triangles that a person could name.** Ten primitives fused into a "clutter" blob do not count.

### Physical plausibility

| Check | Rule |
|---|---|
| Float | any object's lowest support point ≤ 2 mm above its surface |
| Interpenetration | no two solids overlap by > 1 mm unless modelled as a joint |
| Door swing | 90° clear arc, no furniture or wall inside it |
| Circulation | ≥ 600 mm clear path in dwellings, 900 mm in public interiors, 1 500 mm in the market aisles |
| Stair | riser 0.16–0.18 m, tread 0.26–0.30 m, headroom ≥ 2.0 m |
| Handrail | present on both sides of every public stair, 0.90 m |
| Seating | every chair has a table or surface within 0.6 m; nobody sits on air |
| Wall art | hangs 1.45–1.60 m centre, 30 mm off the wall |
| Books | stand on a shelf, spines outward, varied heights |
| Curtains | touch the floor or stop 20 mm above it, never intersect it |
| Ceiling light | physically attached, with a rose or a rod |

### Light

| Check | Rule |
|---|---|
| Sources per room | ≥ 2 independent (one practical, one ambient/window) |
| Emitter visibility | ray from the emitter to 8 points in the room, ≥ 6 clear |
| Blown highlights | < 1 % of pixels at 255 in any channel, excluding practicals and specular points |
| Crushed blacks | < 2 % of pixels below 3/255 inside an interior |
| Exposure | interior 0.0 ± 0.3 EV against a measured reference; exterior per lighting state |
| Colour temperature | 2400–3000 K practicals, 5500–6500 K daylight, mixed but motivated |
| Fireflies | zero visible at 100 % |
| Shadow | no perfectly sharp shadow edge; every exterior light has a soft source angle |

### Distinctness

| Check | Rule |
|---|---|
| Arrangement signature | `sha256(sorted(furniture_family, position_rounded_to_1cm, rotation_rounded_to_5deg))` unique per apartment |
| Plan archetype | ≥ 8 across the development |
| Palette | ≥ 6 |
| Furnishing generation | ≥ 4 |
| Discrimination test | a reviewer shown two random apartments at 1024 px must say "different" **and** name one specific difference, in ≥ 9 of 10 pairs |
| Identity test | no identity twice per building; no identity twice per room |

