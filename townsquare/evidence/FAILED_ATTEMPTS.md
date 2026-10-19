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
