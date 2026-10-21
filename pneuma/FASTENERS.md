# FASTENERS.md — the fasteners of a first-century Alexandrian workshop

This file is law. **Zero screws of any kind** — the wood screw did not exist in
the first century; one screw anywhere in any artifact fails G10 (F39).

| Fastener | Where used | How it is modelled |
|---|---|---|
| **Wooden pin (treenail)** | every joint in the cart frame; drum axles; periaktos pivots | a tapered cylinder, 8–14 mm, driven through a bored hole; modelled as its own named part |
| **Wedge** | locking pins, drum retention, hopper throat adjustment | a tapered prism driven alongside a pin; named |
| **Mortise-and-tenon** | frame corners, wheel spokes into hub, drum staves into end plates | real geometry, not a texture; the tenon has a shoulder |
| **Lashing** | rope bundles, the periaktos frames, hopper suspension | simulated rope, not a solid |
| **Hide glue** | staves into barrels, linen onto pine frames | a material property, recorded in `MECHANISMS.md` |
| **Iron nail** | thin scenery flats, minor sheathing | a square-shanked rod, hand-forged head |
| **Soft solder** | bronze throat seams, dispenser valve seat | a thin film, recorded not modelled where it is sub-millimetre |
| **Iron pivot / pin** | every rotating joint | a pin in a bronze bearing, waxed |

## What is banned, stated plainly

- Screws of any kind, wood or metal, slotted or otherwise.
- Bolts and nuts (threaded fasteners of any kind).
- Welds.
- Adhesives that are not hide glue.
- Modern hinges — a first-century hinge is a pin in a bored hole, and it is modelled that way.
- Zip ties, staples, rivets.

## Why this file exists as a separate document

Because modelling toolkits default to screws and modern hardware, and F39 is
exactly that failure: "Wood screws and modern hinges creep into a first-century
machine because the modelling toolkit defaults to them." Every fastener object in
every `.blend` in this lane is named from the vocabulary above, and `v_period`
audits the names. A part named `SCREW*`, `BOLT*`, `NUT*` or `RIVET*` is an
automatic artifact failure.

## The modelling convention that keeps this honest

Every fastener is a **named object with real geometry**, not a boolean and not a
texture. A tenon has a shoulder. A wedge is tapered. A treenail is a tapered
cylinder standing proud of the wood by 2–3 mm, because that is what a driven
wooden pin looks like — and a reviewer pausing on any frame can see it.
