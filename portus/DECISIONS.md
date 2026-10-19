# PORTUS — DECISIONS

Every choice the packet does not fix, with a date and a reason. The packet's own
counts and gates are not decisions; they are fixed and appear nowhere in this file
as negotiable.

## D-0001 · 2026-10-19 · Cards cut by the agent

No PORTUS card existed on the `chatcode` board at entry (`tasks list --status open
--tags portus` → none). Under the no-stop clause I cut the parent card
`t-20261019-72f1` and two work cards (`t-20261019-5e10` Stage A, `t-20261019-f3c1`
Stage B), then claimed Stage A. The packet's counts, gates and definitions were
copied into the cards unchanged; nothing was reduced.

## D-0002 · 2026-10-19 · Six counted rooms per apartment

The packet's arithmetic is `208×6 + 48×4 + 8×3 + 5×6 + 6×3 + 4×4 + 80 = 1,608`.
That is six counted rooms per apartment, while §13.3 lists seven room types.
Resolution: the six counted rooms are **entry, living, kitchen, primary bedroom,
bathroom, store**. The seventh type — the separate WC — exists wherever the plan
allows and is scheduled as a sub-space of the bathroom cluster; it is not a seventh
counted room, because the packet's own sum forbids a seventh. Recorded rather than
silently dropped.

## D-0003 · 2026-10-19 · Bollards: 40 at 8.00 m over 320 m

Part III says "340 m of quay wall, 40 bollards at 8 m centres". 40 × 8.00 = 320 m.
The 340 m includes the two 10 m returns at the basin corners, which carry no
bollards. The validator checks 8.00 ± 0.05 m between every adjacent pair and finds
40 bollards; it does not pretend the wall is 320 m.

## D-0004 · 2026-10-19 · The 1.20 m light slot

Each residential building is two ranges separated by a **1.20 m wide, full-depth
open slot**. It does two jobs: it is the shared circulation landing on every floor
(each apartment's entry door opens onto it), and it is the secondary daylight
source for internal rooms. Without it, the packet's "0 rooms with 0 windows" is
unreachable in a 14 m deep block. The ground floor is a continuous plate — the slot
starts at the first floor slab.

## D-0005 · 2026-10-19 · Market stalls are open-fronted

The 80 stalls count as rooms in the packet's sum but are not enclosed rooms: each
has an open front ≥1.50 m onto an aisle and takes its daylight from the hall
glazing. They are excluded from the "rooms with 0 doors / 0 windows" assertions and
checked separately (`stalls without an aisle front = 0`).

## D-0006 · 2026-10-19 · Seven quarters, six street blocks

The packet names seven quarters A–G and fixes the count at "6 blocks". A, B, C, E,
F, G are street blocks of buildings (47); D is the market hall standing in its own
square (1). The validator prints six street blocks plus the market square and
checks both facts.

## D-0007 · 2026-10-19 · Storey heights outside the three canonical ones

Tall workshops 8.00 m (C01, C02), market hall 7.50 m + gallery 4.50 m (D01), quay
sheds 5.00 m (G01–G06). All ten are declared with reasons in
`design/SPECIAL_STOREYS.json`; `v_scale` fails on any undeclared height.

## D-0008 · 2026-10-19 · One business per building

The packet lists 48 ground-floor businesses and fixes `48 shops × 4 rooms = 192`.
Every one of the 48 buildings therefore carries exactly one ground-floor unit of
four rooms (sales, stock, staff, WC), named from the packet's own business list.

## D-0009 · 2026-10-19 · Renderer

This worker has no GPU. EEVEE-Next cannot create a context headless (EGL_BAD_MATCH)
and the Debian Blender 4.3.2 build has **no OpenImageDenoise** (F20). All renders
are Cycles CPU with denoising disabled; noise is controlled by samples and
reported per view. Recorded in `evidence/TOOLCHAIN.txt`.

## D-0010 · 2026-10-19 · One plan library, two consumers

`build/planlib.py` is imported by both the Stage A generator and the Stage B
Blender build. A room rectangle in `SCHEDULE.csv` and the same room in the native
scene come from one expression, so a plan and a model cannot drift apart. The
validators read the emitted data, never the generator's memory.
