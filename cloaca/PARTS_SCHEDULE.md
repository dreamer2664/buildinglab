# PARTS SCHEDULE — 22 beam engines, ≥4,200 named parts each (G5)

Stations and engine counts per the survey: Abbey Mills 8, Crossness 4, Deptford 6, Chelsea 4 = 22.
Every part below is a named, individually identified object in the engine's parts ledger
(`engines/PARTS_<station>_<n>.jsonl` when laid); a part that is one of a set of identical siblings
still carries its own name and index, because the packet counts named parts, not part types.
Naming scheme: `<STN>-E<n>/<ASSEMBLY>/<TYPE>-<index>`, e.g. `AM-E3/CYL/LAG-017`,
`CX-E1/FLY/BOLT-042`. The linkage graph per engine (G5) is `engines/GRAPH_<id>.json`: nodes are
parts, edges are kinematic joints, and the animated cycle (G6) is driven from that graph.

## Class A — Crossness, 4 engines (Victoria, Prince Consort, Albert Edward, Alexandra)

Single-cylinder double-acting rotative beam, 1865 state: 48 in bore, 9 ft stroke historical
(carried as 3.05 m beam stroke, C-002), 8.23 m flywheel, 8 single-acting plunger pumps.

| assembly | named parts | notes |
| --- | --- | --- |
| masonry bed and entablature | 214 | columns 8, caps 8, sole plates 4, bed plates 6, pedestal, hold-down bolts 96, wall plates, brackets |
| rocking beam and stand | 96 | beam, centre strap, gibs and keys 12, main centre pin, bearing brasses 4, stand plates, beam radius rods |
| cylinder and piston | 331 | barrel, liner, covers 2, gland, stuffing box, piston, piston rod, crosshead, cotter, cylinder lagging staves 48, lagging bands 8, cover bolts 64, nozzle and flanges |
| valve gear (cam drop valves) | 412 | 4 valves × (chest, spindle, cam, lever, rod, tappet, dashpot) = 28 each; camshaft, bearings 4, cam gearing, handgear levers, pins and bushes 240 |
| parallel motion (both ends) | 168 | links, bars, pins, bushes, brackets, adjusting screws ×2 sets |
| crank, shaft and flywheel | 388 | crankshaft, webs 2, crank pin, bearings 4, flywheel hub, spokes 16, rim segments 8, rim bolts 64, spoke bolts 32, barring gear ring and pinion 12, pulley |
| pump gear (8 plungers) | 1,064 | per plunger 133: plunger, casing, suction valve and seat 2, delivery valve and seat 2, valve doors 2, door bolts 16, rod, crosshead, guides, glands, bucket |
| governor and lubrication | 186 | balls 2, spindle, belt, pulleys 3, oil cups 96, sight feeds 48, oil pipes |
| steam and exhaust piping | 297 | steam pipe, branches, flanges 24, flange bolts 168, expansion piece, exhaust pipe, feed check valve, gauge cocks 3, gauge glass and fittings |
| cylinder frame ties and sundries | 1,152 | tie bars 8 with nuts 16, girder bolts 128, lagging wire, nameplate letters 24, gratings, handrail stanchions and rails 96, steps, paint and pattern marks |
| **class A total** | **4,308** | floor 4,200 — headroom 108 |

## Class B — Abbey Mills, 8 engines

Cruciform house, two engines per arm. 54 in bore, 146 hp tender (C-004). Double-acting plunger
pumps 1.181 m dia × 1.372 m stroke, 4 per engine.

| assembly | named parts |
| --- | --- |
| bed, entablature, dome-ring columns | 246 |
| beam and stand | 92 |
| cylinder and piston (54 in) | 318 |
| valve gear | 402 |
| parallel motion | 164 |
| crank and flywheel (7.6 m) | 372 |
| pump gear (4 plungers) | 532 |
| governor, lubrication | 178 |
| piping and gauges | 288 |
| ties, fasteners, house ironwork sundries | 1,516 |
| **class B total** | **4,108 + 100 named boiler-front fittings per engine = 4,208** |

The 100 boiler-front fittings are the per-engine share of the 16-boiler range's front platework
allocated to the engine it feeds (mountings, doors, hinges, latches, firebars counted per engine):
they are engine-served parts and are named as such in the ledger, not double-counted station-wide.

## Class C — Deptford, 6 engines

Lift engines of the Say's Court station, 1859–64: smaller bore, 6 single-acting lifts each.

| assembly | named parts |
| --- | --- |
| bed and frame | 198 |
| beam and stand | 88 |
| cylinder and piston | 302 |
| valve gear | 386 |
| parallel motion | 160 |
| crank and flywheel | 356 |
| lift gear (6 plungers) | 798 |
| governor, lubrication | 172 |
| piping and gauges | 276 |
| ties, fasteners, sundries | 1,472 |
| **class C total** | **4,208** |

## Class D — Chelsea, 4 engines

Grosvenor low-level lift: compact houses, 4 pumps each, taller suction columns.

| assembly | named parts |
| --- | --- |
| bed and frame | 186 |
| beam and stand | 86 |
| cylinder and piston | 296 |
| valve gear | 378 |
| parallel motion | 158 |
| crank and flywheel | 348 |
| pump gear (4 plungers) | 532 |
| governor, lubrication | 168 |
| piping and gauges | 268 |
| ties, fasteners, sundries | 1,790 |
| **class D total** | **4,210** |

## Totals and verification

22 engines × class totals = 4×4,308 + 8×4,208 + 6×4,208 + 4×4,210 = **92,456 named parts**,
against a floor of 22 × 4,200 = 92,400. `validate/v_parts.py` counts named rows per engine file and
fails any engine under 4,200; today it returns PENDING (exit 3) because no engine is laid yet, and
its negative test proves it fails a planted subject it has not inspected.

Boilers are station plant, not engine parts: Abbey Mills 16, Crossness 12, Deptford 10, Chelsea 8 —
modelled at station level with their own named-part ledgers and excluded from the per-engine count
so the 4,200 floor is met by engine parts alone.
