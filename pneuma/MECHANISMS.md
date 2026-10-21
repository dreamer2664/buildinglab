# MECHANISMS.md — the 34 mechanisms, their drivers, and their masses

**This table is the naming vocabulary for every part in every `.blend`.** A part
whose name is not in the vocabulary below is a `v_parts` failure. Masses are
*derived* from material and volume, never guessed (§13.3).

**Driver column** answers G6: what actually pulls, holds, or falls. Every row must
end in **grain**, **weight**, **water**, **steam**, or a **human-declared cue**.
A row ending in "animation" fails G6 and fails the artifact.

## Part 1 — the cart and its drive (7)

| # | Mechanism | Driver chain (joint ← rope ← drum ← grain) | Mass | Source |
|---|---|---|---|---|
| 1 | Cart chassis and running gear | wheels ← ground reaction; the cart does not drive itself | 14.2 kg oak | *Automata* I |
| 2 | Descending weight (the motor) | **grain** escapes ← weight descends | 18.0 kg lead | *Automata* I/II |
| 3 | Millet-heap metering tube | grain discharge rate sets the descent rate | 0.148 kg millet | *Automata* I |
| 4 | Sand clepsydra (stationary variant) | sand discharge rate | 0.30 kg sand | *Automata* II |
| 5 | Drive axle with projecting pegs | rope ← weight ← grain | 2.1 kg oak | *Automata* I |
| 6 | Rope drums, differing diameters | rope ← weight ← grain | 9 × drums | *Automata* I |
| 7 | Bidirectional winding (fwd/still/reverse) | rope lay direction on the axle | — | *Automata* I |

## Part 2 — the stage and its scene changes (13)

| # | Mechanism | Driver chain | Mass | Source |
|---|---|---|---|---|
| 8 | Proscenium facade with hanging doors | doors ← cord ← drum ← weight ← grain | 22.4 kg pine | *Automata* II |
| 9 | Stage doors, opened/closed by cord | cord ← drum ← weight ← grain | 4.8 kg pine | *Automata* II |
| 10 | Scene-change backdrops (cord-drawn, trigger-released) | cord ← drum ← weight ← grain | 2.9 kg linen on pine | *Automata* II |
| 11 | Rolling sea panorama | cord ← drum ← weight ← grain | 3.4 kg linen on pine | *Automata* II |
| 12 | Ships on concealed rails | cord ← drum ← weight ← grain | 1.6 kg oak ×5 | *Automata* II |
| 13 | The dolphins (wheel + cut-outs + floor slots) | wheel ← cord ← weight ← grain | 0.9 kg oak | *Automata* II |
| 14 | Nauplius's beacon fire | wood shavings + hidden lamp; **fire**, revealed by a drawn plate | — | *Automata* II.XXVIII |
| 15 | The fire-reveal plate | plate ← cord ← drum ← weight ← grain | 0.12 kg bronze | *Automata* II |
| 16 | The lightning bolt (descending) | bolt ← cord ← drum ← weight ← grain | 0.35 kg oak+gilt | *Automata* II |
| 17 | The thunder drum (14 stones) | pin ← cord ← weight ← grain releases the stone | 0.42 kg hide on oak | *Automata* II |
| 18 | The shipbuilders' arms | arm ← cord ← weight ← grain | 0.28 kg ×4 | *Automata* II |
| 19 | The hammering sound | small counterweight ← cord; beam strikes a peg | 0.31 kg lead | *Automata* II |
| 20 | Athena's circling motion (slot-guided) | base ← cords ← weight ← grain; rotates on its own axis | 0.9 kg oak | *Automata* II.XXIX–XXX |

## Part 3 — the temple doors (3)

| # | Mechanism | Driver chain | Mass | Source |
|---|---|---|---|---|
| 21 | Altar fire → heated air → displaced water | **fire** heats air; air displaces water | — | *Pneumatica* I.37 |
| 22 | The water bucket and its weight | bucket ← water ← air ← fire; weight opens the doors | 6.4 kg water+bucket | *Pneumatica* I.37 |
| 23 | The counterweighted return | counterweight ← gravity; doors close as water returns | 4.1 kg lead | *Pneumatica* I.37 |

## Part 4 — the aeolipile and pneumatics (7)

| # | Mechanism | Driver chain | Mass | Source |
|---|---|---|---|---|
| 24 | The aeolipile | **steam** jet reaction; no motor of any kind | 1.8 kg bronze | *Pneumatica* II.50 |
| 25 | Jet of steam supporting a sphere | **steam** pressure | 0.24 kg bronze | *Pneumatica* II.45 |
| 26 | Trumpet in an automaton's hands | **compressed air** | 0.31 kg bronze | *Pneumatica* II.49 |
| 27 | Boiler → blackbird / Triton horn | **steam** selects the path | 3.6 kg bronze | *Pneumatica* II.75 |
| 28 | Altar organ, manual labour | **human-declared cue** (a hand-turned blower) | 8.2 kg bronze/oak | *Pneumatica* II.76 |
| 29 | Wind-wheel organ | **wind** — the first wind-driven machine | 2.4 kg oak | *Pneumatica* II.77 |
| 30 | Rotating singing-bird shrine | **human-declared cue** (worshipper turns a wheel) | 1.1 kg oak | *Pneumatica* II.68 |

## Part 5 — the dispenser and water devices (4)

| # | Mechanism | Driver chain | Mass | Source |
|---|---|---|---|---|
| 31 | Coin-operated dispenser | coin weight ← lever ← valve ← **water head** | 0.68 kg bronze | *Pneumatica* I.21 |
| 32 | Birds singing / silent alternately | **water** admits air in turn | 0.44 kg bronze | *Pneumatica* I.15 |
| 33 | The whistling bird | **water** drives air through a whistle | 0.21 kg bronze | *Pneumatica* I.14 |
| 34 | Trumpets by flowing water; door-open sounds | **water** drives the sound | 0.55 kg bronze | *Pneumatica* I.16–17 |

---

## Driver census (G6's arithmetic)

| Driver | Mechanisms | Share |
|---|---|---|
| **grain** (via weight, rope, drum) | 1–13, 15–20 | 19 |
| **fire / steam / compressed air** | 14, 21, 24–27 | 7 |
| **water** | 22, 31–34 | 5 |
| **wind** | 29 | 1 |
| **human-declared cue** | 28, 30 | 2 |

**The law:** disable the grain and the cart does not move. Mechanisms 14, 21,
24–27, 29, 31–34 are *other artifacts* (temple doors, aeolipile, dispenser,
water devices) whose drivers are their own declared causes — the cart-theatre's
motion still terminates in grain. `v_motion` checks both, separately.

## Naming vocabulary

Part names are `MECHANISM_INDEX_PART` with the mechanism's own stem. Stems in
use: `CHASSIS_`, `WHEEL_`, `AXLE_`, `DRUM_`, `ROPE_`, `HOPPER_`, `GRAIN_`,
`STAGE_`, `DOOR_`, `BACKDROP_`, `SEA_`, `SHIP_`, `DOLPHIN_`, `BEACON_`,
`PLATE_`, `BOLT_`, `THUNDER_`, `ARM_`, `HAMMER_`, `ATHENA_`, `ALTAR_`,
`BUCKET_`, `COUNTERWEIGHT_`, `AEOLIPILE_`, `NOZZLE_`, `TRUMPET_`, `BOILER_`,
`ORGAN_`, `WINDWHEEL_`, `SHRINE_`, `DISPENSER_`, `VALVE_`, `BIRD_`.

Fasteners: `PIN_`, `WEDGE_`, `TENON_`, `NAIL_`, `LASHING_` (`FASTENERS.md`).
Materials: the exact uppercase names in `MATERIALS.md`.

## Mass derivation, stated

Masses above are volume × material density, computed in the build script and
written to the part's custom properties, so `v_parts` can recompute them. They
are **not** measurements of a physical object; they are the mass of the modelled
volume. Any part whose mass matters to timing (the weight, the bucket) gets its
own derivation row in `evidence/BUDGET.md`.
