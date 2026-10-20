# CHECKPOINT B — Stage B Vertical Slice Complete (`CHECKPOINT_B.md`)

- **UTC Timestamp:** `2026-10-19T15:42Z`
- **Agent:** `brunel` · **Task:** `t-20261019-62e7`
- **Native Scene:** `nordbahnhof/source/NORDBAHNHOF.blend` + `nordbahnhof/source/NORDBAHNHOF_lib.blend` + `nordbahnhof/exports/NORDBAHNHOF_StageB_Bay5.glb`
- **Bay 5 Slice Contents Verified:**
  - `21.0 m` riveted lattice arch truss (`TRUSS_05`), both chords, X-diagonals, gussets, `18 mm` dome rivets at `60.0 mm` pitch (`v_iron: PASS`).
  - Glazed roof panel of 12 panes (`GLAZ_Bay5_Pane_01..12`), `6–13 mm` thickness variation, `4.0 mm` soldered lead cames, 2 cracked panes (`v_glazing: PASS`).
  - Two platforms (`PLT_06` at `550 mm`, `PLT_07` at `760 mm`), `500 mm` yellow tactile safety line, granite coping, slatted oak bench, cast-iron globe lamps (`v_scale: PASS`, `v_circulation: PASS`).
  - `21.0 m`+ of standard-gauge track (`1,435 mm`), bullhead rails, check rails, creosoted sleepers, chairs, ballast, hydraulic buffer stop (`v_scale: PASS`).
  - Complete 4-6-2 Steam Express Locomotive (`LOCO_V01`) + Tender (`TENDER_V02`) + EMU (`EMU_V12`): wheels on rails (`0.0 mm` gap), coupling closed, buffers touching, volumetric-lit steam plume (`≥3.25 m` clear of truss), cab crew `HERO_09` and `HERO_10` (`v_vehicles: PASS`).
  - Retail Unit `RET_01` ("Nord Buchhandlung"): panelled mahogany counter, brass cash register, 6 shelves, 185 stocked props, original fascia `R01` (`v_density: PASS`, `v_distinct: PASS`).
  - Waiting Room `WAIT_01` ("First Class Salon Noord"): 40 upholstered seats, walnut wainscoting, 16 strapped luggage cases, station clock (`3.20 m`, 240 parts, deadbeat escapement at `16:40:00`), 240-tile departure board (`v_mechanism: PASS`).
  - Four hero figures on Platform 7 (`HERO_01` guard with flag, `HERO_02` porter, `HERO_19` passenger with valise, `HERO_04` child) with smooth anatomical meshes, 5-finger hands, eyes, caps/hair, and winter coats (`v_people: PASS`).
  - 30 proof views rendered in Cycles CPU (`1024×576`) and 30 gallery JPEGs in `nordbahnhof/renders/best/` (`2560×1440`), inspected at 100% with defects `D-001`..`D-006` closed in `DEFECT_REGISTER.csv`.

Independent non-owner acceptance remains PENDING. No self-review/vote.
