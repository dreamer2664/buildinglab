# Winterlichtplatz II — Failed Attempts & Rejected Studies (`FAILED_ATTEMPTS.md`)

Every rejected build or render pass is preserved here with its native SHA-256, proof hashes, and exact root cause (§10 rule 6, §32).

## 1. Stage B Slice Attempt 1 — Rejected after 12/12 proof inspection (`2026-10-19T14:36Z`)
- **Native:** `townsquare/scene/slice_B02_L02.blend` · SHA-256 `c973df5963d7f323192cf54e347a3cc1d47e3cb6a7554d921fa0d52b3158f3cf` · 1,340 mesh objects · 131,538 triangles.
- **Proofs inspected (12/12 opened at 100%):**
  - `slice_01_ext_blue_hour.png` (`1024x576`)
  - `slice_02_ext_day.png` (`1024x576`)
  - `slice_03_cutaway_L02.png` (`1024x576`)
  - `slice_04_int_B02_L02_A.png` (`1024x576`)
  - `slice_05_int_B02_L02_B.png` (`1024x576`)
  - `slice_06_shop_bakery.png` (`1024x576`)
  - `slice_07_human_daylight_close.png` (`1024x576`)
  - `slice_08_human_bakery_warm.png` (`1024x576`)
  - `slice_09_terrain_cobbles_slush.png` (`1024x576`)
  - `slice_10_plan_B02_L02.png` (`1024x576`)
  - `slice_11_technical_facade.png` (`1024x576`)
  - `slice_12_ext_night.png` (`1024x576`)
- **Defects found by visual inspection (reason for rejection):**
  - **D-002 (Major — Human scan facing direction):** In `slice_07_human_daylight_close.png` and `slice_08_human_bakery_warm.png`, `HSRD-100` scans (`HSR0015-Body-009` and `HSR0027-Body-004`) had `rot_z ~ 0`, which points their face toward `+Y` (away from the camera at `-Y`), showing the back of their beanie/hood instead of their face.
  - **D-003 (Critical — Chamfer ratio & missing interior partition walls):** `make_bevelled_box_pydata` used fixed `0.42` octagon ratios instead of `hx - bevel`, making rectangular floor finishes and furniture look octagonal in `slice_10_plan_B02_L02.png`. Interior `0.12 m` partition walls between rooms were omitted on `L02`, and procedural stand-in figures in `slice_04`/`slice_05` blocked the camera foreground.
  - **D-004 (Major — Exterior framing & upper-floor lighting):** `slice_01_ext_blue_hour.png` and `slice_12_ext_night.png` aimed too high (`z = 9.5 m` from `14.5 m` distance), cropping out the ground-floor bakery arcade and street cobbles, while upper floors `L03–L06` lacked warm interior window emitters and dusk fill illumination was too dim (`crushed blacks > 2%`).
  - **D-005 (Major — Cobble joint spacing):** In `slice_09_terrain_cobbles_slush.png`, cobblestones (`95 mm`) were placed on a `210 mm` grid instead of tight `8–15 mm` mortar joints.
- **Corrective action in Attempt 2:** Fixed `make_bevelled_box_pydata` to exact `hx - bevel` corner offsets; added interior partition walls with doorways; rotated `HSRD-100` scans by `pi` (`180°`) to face cameras and used licensed `HSRD-100` scans for all visible figures; tightened cobble pitch to `8–12 mm` mortar joints; added upper-floor window emitters, street/sky fill lighting, and full-height `28 mm` exterior framing.

## 2. Stage C–F Master Scene Attempt 1 — Rejected after `hero_01_square_blue_hour` & `int_B01_L02_A` inspection (`2026-10-19T23:30Z`)
- **Native:** `townsquare/scene/master.blend` · SHA-256 `b685144a017b09ec0aa0b5d9a16f710d9f5650c74bc6062d4781f9ab46a01a7a` · 1,132 mesh objects · 4,536,054 triangles.
- **Defects found by visual inspection (reason for rejection):**
  - **D-006 (Major — Square paver course spacing & foreground tree crown geometry):** In `hero_01_square_blue_hour.png`, `Sq_PaverCourse` iterated with `step=2` (`2.90 m` spacing for `1.96 m` courses), leaving `0.94 m` dark gaps between paver slabs; additionally, `DECIDUOUS_TREE` placed at `r = 25 m, 20 m` with box-plank boughs (`Tree_.._Bough`) obstructed the foreground sightline of `hero_01_square_blue_hour`.
  - **D-007 (Major — Unculled indoor room lights causing Monte Carlo shadow-ray speckle):** `render_queue.py` checked `if "WarmBounce" in o.name` instead of `CeilingPendant` / `FloorStand`, leaving all `1,746` indoor lights active across all 12 buildings during both outdoor and single-room indoor renders (`int_B01_L02_A.png`, `int_B02_L02_A.png`), so Cycles' Light Tree sampled occluded off-building lights 98% of the time.
- **Corrective action in Attempt 2 (`master.blend` SHA-256 `719645dbf8687a42be4bc39a8cded5da87834fc8649ddb66300a1f8b4a57a8cc`):** Changed `Sq_PaverCourse` to `step=1` (`1.438 m` courses on `1.450 m` pitch = continuous `12 mm` mortar joint across the entire 64 × 52 m square); relocated `DECIDUOUS_TREE_01..12` to the outer sidewalk perimeter (`28.5 m × 22.8 m`) with tapered `spawn_lathe` winter crowns; updated `render_queue.py` to cull off-room `CeilingPendant` / `FloorStand` lights and per-floor/per-apartment geometry, eliminating indoor Monte Carlo speckle.
