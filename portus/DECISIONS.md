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

## D-0015 · 2026-10-19 · Terraces are continuous; joints are pilasters

B, E and F were laid as 14.40 m fronts on a 15.00 m pitch, leaving a 0.60 m slot
between neighbours. From every street camera that slot is a black stripe, and it
is not how a 19th-century quay terrace is built. Fronts are now 14.95 m (a 50 mm
joint) and every joint carries a `PARTYWALL_*` pilaster standing 60 mm proud of
both facades, so the joint reads as a pilaster and nothing is coplanar.

## D-0016 · 2026-10-19 · No two boxes share a plane

The black bands across every elevation were not shadows: ray-casting the dark
pixels named `B04_FS_L4` — the facade band itself. Each band was built 0.24 m
below its floor line while the band beneath reached that same line, so two
coplanar boxes self-shadowed along the seam. Bands now start exactly at the floor
line and each level is 3 mm proud of the one below, alternating. Dark pixels in
`CAM_03` fell from 4.3 % to 1.1 %, and the residual is window reveals.

## D-0017 · 2026-10-19 · A punched hole is not a window

One accurate ray-cast reading is worth ten guesses.

Every opening in the envelope now carries a pane, a frame and a dark room behind
it (`glaze_envelope`, `facade_band`). An open hole in a hollow massing box reads
as a black cave; a pane with a dark surface 220 mm behind it reads as a window.

## D-0018 · 2026-10-19 · One Blender process per view

At 1024 px with 1.17 M triangles a single process rendering all 24 views is
killed by the kernel at 1.27 GB RSS (observed twice, `oom-kill`, exit 137).
`scripts/run_proofs.sh` starts one process per camera: ~2 s to load the blend and
a clean heap for every frame. Peak RSS per view is now 162 MB at 1024 px.

## D-0019 · 2026-10-19 · Merge per building, not per facade

Emitting one object per facade, one per glazing run and one per reveal produced
1,920 objects for the massing alone; Cycles spent its budget on BVH nodes and
thrashing, not samples. Facades, glazing and reveals are now merged per building
(48 × 3 objects), and the object count fell from 6,861 to 4,913.

## D-0020 · 2026-10-19 · The model does not end in mid-air

`QUAY_SKIRT` carries the site down 6 m to the water on all four sides, an
outer water plane surrounds it, and `city_fringe()` puts 130+ low-detail blocks
behind the site so an aerial view shows a district inside a city, not a diorama.

## D-216 — contact gate: what is measured, and what is not (2026-10-20)
`v_contact` now tests interpenetration at triangle level (BVH overlap) instead of
bounding boxes. A bounding box cannot tell a book resting on shelf 3 of a
bookcase from a book buried in the carcass, and the old test reported 1,671 false
positives on that basis. The triangle test removes the false positives but the
depth it reads is the closest approach between two intersecting triangle planes,
which over-reports for objects that merely touch at an edge (a till standing on a
counter reads ~1 m). **Therefore `v_contact` reports the interpenetration item as
a measured candidate count and the gate is OPEN (FAIL).** Zero-area faces are
fixed (a wall panel emitted a zero-width box when a hole reached the panel end;
`_emit()` now refuses any box with a dimension under 0.1 mm). Floating and shadow
items pass. Correctly proving the 0.5 mm rule needs proper mesh-mesh depth
(SDF or exact intersection volume), which is not built.

## D-217 — 149 props stand in a door approach (2026-10-20, OPEN)
`v_clearance` finds 149 props overlapping the 1.05 m gate in front of a door
leaf, e.g. `ROOM_R00265_counter_469` (0.73 m into the approach, 0.39 m across the
leaf). The placer has a keep-out list and `settle_keepout()` runs after
furnishing, so the cause is that shop fixtures and some room builders place at
fixed offsets in world-relative coordinates — the counter sits in the 1.0 m party
wall recess, i.e. outside the room's own local frame, where the keep-out
rectangle does not reach. Fix belongs in the shop/warehouse builders, not in the
validator. Gate OPEN.

## D-218 — CAM_03 stood inside the coaster hull (2026-10-20, CLOSED)
Framed at (158, 104, 6.5) looking at B05, the camera sat inside `HULL_COASTER`
(basin y 105.65–119.15); the hull deck filled the lower third of the frame and
the basin, water and shore were invisible. Moved to (196, 124, 4.10) on the quay
apron looking west-north-west at the frontage. Re-rendered; verified at 1024 px.

## D-219 — windows read as holes (2026-10-20, OPEN)
In CAM_03 the openings are recessed boxes whose glazing transmits 92 % to an
unbuilt interior, so they read as holes rather than glazing. Glass needs an
interior backing plane per apartment, or a tinted low-transmission variant for
unbuilt apartments. Until Stage C furnishes the other 200 apartments, the fronts
of unbuilt buildings are expected to read thin.

## D-220 — export round-trip check named objects (2026-10-20, CLOSED)
`v_export` asserted that the round-tripped meshes kept their `BLDG*` names; glTF
does not preserve names. Rewritten to identify blocks by footprint (plan span
> 8 m): 720 of 5,094 meshes, PASS. Geometry and material counts round-trip
exactly (1,189,892 tris, 60 materials).

## D-221 — the detail library, and what it costs (2026-10-20)
`portus/build/detail.py` replaces the four-box `facade_band` with real
architectural elements: individual bricks in running bond, window openings with
reveal returns, stone sills with drip and lintels, sash frames with meeting rails
and glazing bars, panelled doors with fanlights, plinths, string courses, dentilled
cornices, quoins, tiled roofs as oriented slabs with ridges and gutters, chimney
stacks with pots, downpipes with brackets and hoppers, tie plates and air bricks.

Every element is emitted as an axis-aligned rect and merged per building, so the
object count stays flat (~5,400) while the triangle count carries the detail.

**Measured cost, on this machine:**

| build | triangles | renders? |
|---|---|---|
| original flat facades | 1.01 M | yes, 1024/32 in 69 s |
| joinery + stone + tiled roofs | 2.00 M | yes |
| + ground-storey brickwork, r=18 m | 2.40 M | yes, 1024/32 in 105 s |
| + brickwork, r=35 m | 4.03 M | **OOM-killed** |
| full brickwork everywhere | 9.11 M | **OOM-killed** |

The render ceiling on this box is ~2.5 M triangles. That is a machine limit, not
a design choice: the same 1024/32 frame that renders at 2.4 M is killed at 4.0 M.

## D-222 — detail is placed by camera distance (2026-10-20)
Individual bricks are spent only on buildings within `PORTUS_RADIUS` of a proof
camera, and only on their ground storey. Everything else gets the material's
procedural coursing, which costs nothing. This is a deliberate budget, and it is
visible: a wall 60 m away has no individual bricks. Raising `PORTUS_DETAIL=3`
builds full bricks everywhere and cannot be rendered on this machine.

## D-223 — coursing must be brick-shaped, not a proud band (2026-10-20, CLOSED)
The first version of `coursed_relief` drew one projecting horizontal band per
course and emitted it into the stone material. On CAM_03 it read as white
venetian blinds across the facade — a rendering artifact no amount of geometry
would fix. Replaced with coarse running-bond brickwork in the wall material.

## D-224 — OIDN denoising is the 1024 memory spike (2026-10-20)
At 1024 px the render was killed at sample 17 of 32 with a flat memory profile
before the spike. Isolating it: the same scene at 1024/32 completes in 73 s with
`use_denoising = False`. OpenImageDenoise needs roughly 600 MB on top of the
render, which this box does not have. Proofs at 1024 therefore render denoised-
off for the moment; the noise is visible and is logged as a defect.

## D-225 — party walls were being glazed (2026-10-20, CLOSED)
Terraced houses had windows punched into the walls they share with their
neighbours. `party_sides()` now detects shared faces by footprint adjacency
(52 faces across the 48 buildings) and suppresses openings and dressings on them.
This is both correct architecture and half the window geometry.
