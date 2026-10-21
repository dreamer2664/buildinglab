# WEAR_SCHEDULE.md — density is a gate (F17, F40)

The network is a workplace, not a corridor. Every chunk carries a seeded deviation set; the wear below is applied per zone from it, and `v_distinct` samples 100 chunks for pairwise difference (F35: no two chunks are twins).

## Zones by height above the invert

| zone | band | what lives there |
|---|---|---|
| `invert` | 0 – 0.15 m | sediment, scour polish, a central gully channel that sets up the vortex (R-019), grit, tide-borne debris |
| `flow` | 0.15 m – dry-weather depth | biofilm, a dark tide line, wet sheen, the sediment line's upper edge |
| `splash` | DWF depth – +0.45 m | tide marks, lime bloom, salt efflorescence, iron staining where fittings penetrate |
| `wall` | +0.45 m – springing | soot and gas-lamp blackening near lamps, tool scars, repairs, weeping joints |
| `crown` | springing – crown | lime bloom, dry dust, cobweb anchors, the driest brick in the section |

## Conditions and their frequencies (seeded per chunk, ±25 % of the base rate)

| code | condition | base rate | where |
|---|---|---|---|
| 0 | stock, sound | remainder | everywhere |
| 1 | lime bloom / efflorescence | 7 % | crown, splash |
| 2 | chipped arris | 4 % | wall, invert (barrow and shovel strikes) |
| 3 | repaired / patched with a cut brick | 1.2 % | wall; repairs cluster (a bad patch of ground) |
| 4 | sediment-crusted | 9 % | invert |
| 5 | sooted / gas blackening | 3 % | wall within 3 m of a lamp or shaft |
| 6 | tool scar (trowel drag, gauge-rod mark) | 2 % | any, biased to the course below a joint |
| 7 | cracked (hair, not structural) | 0.6 % | crown and wall, biased to settlement zones |

## Per-chunk deviation set (`ledgers/DEVIATIONS.jsonl`)

`{chunk, key, stain_density, bloom_density, repair_clusters, sediment_mm, tide_mark_m, soot_bands, tool_scar_bias, settlement_zone, grit_seed, colour_drift}` — all seeded from the chunk key. Two chunks with different keys have different sets; `v_distinct` proves it pairwise on a 100-chunk sample.

## Colour drift

London stock brick is grey-yellow with a soot-darkened face in service (R-041). Drift is a single 0–255 value per brick mapping to ±6 % lightness and ±4 % hue inside the stock family, plus the zone darkening above. No brick leaves the family: an out-of-family brick is a period defect (G8).

## What must never appear

Clean brick everywhere (F40: a toy set at 1:1) · a chunk with no repairs · a sediment-free invert · identical stain density across chunks · modern cement patching · any material the schedule does not name.
