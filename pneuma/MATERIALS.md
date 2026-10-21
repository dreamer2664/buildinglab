# MATERIALS.md — first century AD, Alexandria

Law for every part in every artifact in this lane. A material outside this table
is a G10 failure until `FAKES.md` declares it.

| Material | Where it appears | Colour (sRGB) | Roughness | Metallic | Notes |
|---|---|---|---|---|---|
| **Oak** | cart chassis, wagon rails, drum barrels, hopper walls, workshop bench | 0.42, 0.30, 0.18 | 0.72 | 0.0 | the structural wood; quartersawn for barrels |
| **Pine** | periaktoi frames, scenery flats, packing crates | 0.68, 0.55, 0.38 | 0.80 | 0.0 | lighter, softer; takes paint |
| **Olive wood** | small gears, cams, valve seats | 0.55, 0.42, 0.24 | 0.68 | 0.0 | dense, close grain, machines well |
| **Bronze** | bearings, hopper throat, dispenser valve, temple-door hardware | 0.72, 0.52, 0.28 | 0.35 | 0.85 | the bearing metal; poured, not cast-to-tolerance |
| **Flax rope** | drive ropes, temple-door lines | 0.78, 0.70, 0.52 | 0.90 | 0.0 | laid strand, S or Z twist recorded per system |
| **Hemp rope** | heavy hawsers, counterweight lines | 0.66, 0.58, 0.42 | 0.92 | 0.0 | coarser than flax |
| **Iron** | pivots, pins, nails only | 0.30, 0.28, 0.26 | 0.55 | 0.95 | pivots and pins ONLY (§13.7) |
| **Lead** | counterweights, the descending weight | 0.42, 0.42, 0.44 | 0.45 | 0.60 | soft, cast, easily cut |
| **Wax** | pivot bearings, lubrication | 0.85, 0.80, 0.62 | 0.60 | 0.0 | the lubricant |
| **Linen** | painted scenery faces, costumes | per paint | 0.85 | 0.0 | the periaktos faces are painted linen on pine |
| **Millet** | the 48,000 grains | 0.78, 0.66, 0.38 | 0.75 | 0.0 | true millet ~2 mm; sim runs 4× (see `GRAIN.md`) |
| **Water** | the swim scene, the dispenser | simulated surface | 0.10 | 0.0 | a simulated surface, never a blue plane |
| **Fire** | the false beacon, the temple altar | simulated emitter | — | — | sim flame with a sim fuel feed |
| **Glass (cast, small)** | the beacon lens | 0.90, 0.94, 0.96 | 0.05 | 0.0 | small cast pieces only; no drawn glass |

## Deliberately absent, and why

| Absent | Reason |
|---|---|
| Steel cable | did not exist; wire drawing is medieval at the earliest |
| Nylon, rubber, synthetics | anachronistic by ~1,900 years |
| Wood screws | **zero, anywhere, in any artifact** (G10; F39) |
| Aluminium, brass* | brass is bronze with zinc; Roman "brass" is bronze — treat all as bronze |
| Printed paper, modern paint | anachronistic |

\* Any "brass" in a Heron translation means bronze.

## How this table is enforced

`v_period` audits every material slot in every `.blend` against the names above.
A slot whose name is not in this table fails the artifact until `FAKES.md` names
it. Material names in the `.blend` are the exact strings in column 1, uppercased,
so the audit is a set comparison and not a judgement call.
