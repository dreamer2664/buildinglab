# NORDBAHNHOF — CONSTANTS (§15 Hard Numbers Verbatim + §1.2 / §39 Numbers Card)

Project: `dreamer2664/buildinglab`, `nordbahnhof/**`
Agent: `brunel`
Date: `2026-10-19`

```
FOOTPRINT  240 × 120 m · 28,800 m² · origin at entrance centreline · +Z up · north = +Y
SHED       180 × 84 m · ridge +26.0 · eaves +14.0
LEVELS     B2 · B1 · L0 · L1 · L2 · roof
COLUMNS    12 cast iron, 21.0 m centres      TRUSSES 8 riveted lattice
RIVETS     60 mm pitch ±1 mm                 PANES   4,200 (enumerated)
PLATFORMS  8 · TRACKS 12 · GAUGE 1,435 ±2 mm · PLATFORM 180 m · height 550/760 ±10 mm
TRAINS     6 · VEHICLES 34 · every wheel on rail · every coupling closed
ROOMS      240 · RETAIL 48 · RESTAURANTS 6 · WAITING 8 · OFFICES 12 · RESTROOMS 6
DOORS      200 (all to 90°) · BARRIERS 12 · LIFTS 2 · ESCALATORS 4
CLOCK      3.20 m dial, 240 parts, correct time
BOARD      240 tiles, flipping, reads the timetable
PEOPLE     400 · IDENTITIES 60 · HEROES 20 · CAPSULES 0
MATERIALS  120 · 5 detail scales · TEXEL ≥40 px/cm
FLOAT      ≤1 mm · INTERPENETRATION ≤0.5 mm · UV ≤1.15:1 · BEVEL 0.5–1.5 mm ±0.5
PROOFS     310 at 1024 px · FINALS 310 · INSPECTED 310
BEST       30 images ≤4 MB each ≤100 MB total
VALIDATORS 15 + 15 negative tests
BLIND      20 trials × 6 classes · pass ≤9/20 each
GATES      G1–G8 · STAGES 0,A–H
```

| **G3** | **Density** | prop counts + inspection | any room under §15.4 |
| **G4** | **Distinctness** | signature + discrimination | two retail units, waiting rooms or offices indistinguishable |
| **G5** | **Light** | histograms + inspection | a dark room, a blown frame, an unmotivated source |
| **G6** | **Realism** | **blind 2AFC, 20 trials × 6 classes** | judge scores better than 9/20 on any class |
| **G7** | **Mechanism** | T1/T2/T3 validators | a rivet off spacing, a pane missing, a hand that does not turn, a gate that does not open |
| **G8** | **Reproduction** | clean-room re-run | any validator needs a file outside repo/release |

A card is done when all eight pass on **one frozen native SHA** and two non-owners have inspected that SHA.

## 15. Hard numbers — the strictest set in the agency

### 15.1 Scale and construction

| Parameter | Value | Tolerance |
|---|---|---|
| Units | Metric, 1 BU = 1 m | exact |
| Footprint | 240 × 120 m | ±0.05 |
| Shed | 180 × 84 m, ridge +26.0, eaves +14.0 | ±0.03 |
| Platform length | 180 m | ±0.10 |
| Platform height | 550 / 760 mm | ±10 mm |
| Track gauge | **1,435 mm** | **±2 mm** |
| Rail head to platform | per type, measured and recorded | ±10 mm |
| Storey, L0 | 6.40 m clear | ±0.05 |
| Storey, L1 | 4.60 m clear | ±0.05 |
| Storey, B1 | 4.20 m clear | ±0.05 |
| Storey, B2 | 4.80 m clear | ±0.05 |
| Column grid | 21.0 m centres in the shed | ±0.02 |
| Door | 0.90 × 2.10; double 1.60 × 2.20; goods 2.60 × 3.20 | ±0.010 |
| Human | 1.75 m | ±0.08 |
| Eye height | 1.62 m | ±0.02 |
| Seat height | 0.45 m | ±0.010 |
| Handrail | 0.90 m | ±0.010 |
| Clock dial | 3.20 m | ±0.005 |

### 15.2 Surface craft

| Parameter | Requirement |
|---|---|
| Texel density, hero surfaces | **≥40 px/cm** at 4K maps |
| Texel density, background | ≥20 px/cm |
| UV aspect distortion | **≤1.15:1** |
| Overlapping UVs | zero on unique surfaces |
| Hard-edge bevel | **0.5–1.5 mm**, ±0.5 mm |
| Coplanar faces | zero |
| Detail scales | **5 levels** on every hero material: macro (0.5–10 m), meso (5–50 cm), micro (5–50 mm), nano (0.5–5 mm), wear (<0.5 mm) |
| Albedo variation | ≥15 % across any 2 m² |
| Roughness variation | ≥0.10 across any hero surface |
| **Rivets** | modelled geometry, **60 mm pitch ±1 mm**, head diameter 18 mm ±0.5, on every hero truss, girder and plate within 6 m of any camera |
| **Weld beads** | modelled on every modern steel joint, 6–10 mm |
| **Cast iron** | flanges, spandrels, bolt heads, foundry marks on every column within 4 m |
| **Glass** | per-pane thickness 6–14 mm, waviness 0.2–1.2 mm, lead came 4 mm, condensation on the cold face |
| **Terrazzo** | real aggregate chips, 4 sizes, brass divider strips, a 1:1 study |
| **Timber** | displacement grain on every visible plank; end grain on every cut |
| **Paint** | 3-layer build-up with a chip revealing the layer beneath on 20 declared objects |
| **Grime** | a dirt gradient at every hand height, every door push plate, every stair nosing |

### 15.3 The three mechanism suites

**T1 · ironwork**

| Check | Rule |
|---|---|
| Trusses | 8 hero trusses; rivet pitch 60 mm ±1; no missing rivet in a loaded joint |
| Members | no two members interpenetrate; every gusset plate has its bolts |
| Columns | base plate, holding-down bolts, capital, foundry mark |
| Bracing | every bay braced; every turnbuckle modelled |
| Catenary | contact wire 5.50 m ±0.02, droppers every 7.5 m, tension weights |

**T2 · glazing**

| Check | Rule |
|---|---|
| Pane count | **exactly 4,200**, enumerated in `GLAZING.json` |
| Cames | one per pane edge, 4 mm, soldered at every intersection |
| Variation | thickness, waviness, tint and dirt vary per pane by seed, recorded |
| Breakage | 6 panes cracked in the north bay, 2 missing with a tarpaulin |
| Reflection | every pane reflects the shed interior, not the HDRI |
| Condensation | on the outer face below +2 °C; on the inner face in the waiting rooms |

**T3 · mechanism**

| Check | Rule |
|---|---|
| Clock | 240 parts, escapement, hands set to scene time, seconds hand advancing in animation |
| Departure board | 240 tiles, each flipping in a scripted test; the timetable reads true |
| Ticket barriers | 12, gates open and close in a scripted test, no clipping |
| Doors | 200 doors modelled with hinges; 100 % open to 90° without intersecting |
| Lifts | 2, doors and cars animated between floors |
| Escalators | 4, steps and handrails modelled, moving in the animation |

### 15.4 Density — modelled props per room

| Room | Minimum | Non-negotiable |
|---|---:|---|
| Retail unit | **180** | ≥140 stocked products, till, counter, 6 shelves, back-room stock, signage, bags |
| Restaurant | **200** | ≥40 plates/glasses, kitchen line, 8 tables set, 24 chairs, bar, menu, staff |
| Waiting room | **90** | seats, tables, bins, clocks, posters, luggage, a vending machine |
| Office | **70** | desks, 2 chairs each, files, phones, lamps, shelves, plants, a coat stand |
| Restroom | **40** | 6 cubicles, 4 basins, mirrors, dispensers, tiles, 3 bins, a mop |
| Concourse (per 100 m²) | **60** | benches, bins, signs, columns, lamps, barriers, luggage, litter |
| Platform (per 100 m) | **80** | benches, lamps, bins, signs, a clock, vending, trolleys, litter |
| Left luggage | **220** | 200 cases and bags, shelving, tags, a counter |
| Plant room | **60** | boilers, pumps, pipes, valves, gauges, a coal bunker, tools |

A prop is a separate object with ≥40 triangles that a person could name.

### 15.5 Contact and circulation

| Check | Rule |
|---|---|
| Float | **≤1 mm** |
| Interpenetration | **≤0.5 mm** unless modelled as a joint |
| Passenger path | ≥1,200 mm |
| Platform edge | ≥1,500 mm clear behind the yellow line, line at 500 mm from the edge |
| Concourse | ≥3,000 mm main axis |
| Retail aisle | ≥1,000 mm |
| Door swing | 90° clear |
| Stair | riser 0.15–0.17, tread 0.28–0.32, headroom ≥2.2 |
| Escalator | 30° ±0.5, 1,000 mm step width |
| Seating | every seat with 0.60 m clear in front |
| Luggage | every case on a rack, a floor, or in a hand |

### 15.6 Light

| Check | Rule |
|---|---|
| Sources per room | ≥3 independent (practical, window/daylight, fill) |
| Shed light | the sun blade on the platforms matches the modelled 9° sun and the pane positions |
| Emitter visibility | ray to 10 room points, ≥9 clear |
| Blown highlights | <0.6 % of pixels at 255 |
| Crushed blacks | <1.2 % below 3/255 indoors |
| Exposure | interior 0.0 ±0.20 EV |
| Colour temperature | 2200–2700 K practicals; 4200–5200 K winter daylight |
| Steam | volumetrically lit, density recorded, no flat sprite |
| Fireflies | zero at 100 % |

### 15.7 Distinctness

| Check | Rule |
|---|---|
| Retail signature | `sha256(family, position to 5 mm, rotation to 2°)` unique per unit |
| Brand identity | 48 original vector marks, 48 fascias, 48 window schemes |
| Waiting room character | 8 rooms, each with a distinct palette, seating type and purpose |
| Office character | 12 rooms, each with a distinct layout |
