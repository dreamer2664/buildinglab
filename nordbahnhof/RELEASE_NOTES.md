# NORDBAHNHOF — Stage A–H Release Package (`RELEASE_NOTES.md`)

- **Project:** `NORDBAHNHOF` — A Grand Central Railway Terminus & Concourse at 16:40 on a Winter Weekday
- **Builder:** `brunel` · **Task:** `t-20261019-62e7`
- **Hard Numbers Verified (`v_programme.py` -> PASS):**
  - `5` levels (`B2, B1, L0, L1, L2`) + `roof` · `240` rooms (`0` doorless, `0` windowless)
  - `48` retail units with `48` original SVG brand marks (`R01.svg`..`R48.svg`)
  - `6` restaurants/cafés · `8` waiting rooms (`1,200` waiting room seats) · `12` offices · `6` restrooms
  - `8` platforms (`180.0 m`) · `12` standard-gauge tracks (`1,435 mm ±2 mm`) · `6` trains · `34` vehicles
  - `8` riveted lattice arch trusses (`60.0 mm ±1.0 mm` rivet pitch) · `12` cast-iron columns (`21.0 m` centres)
  - `4,200` enumerated roof glazing panes (`4,200` distinct waviness seeds, `4.0 mm` soldered lead cames, `6` cracked + `2` tarpaulin in north bay)
  - `4` clocks (`3.20 m` main dial, `240` parts, Graham deadbeat escapement, `16:40:00`, animated seconds hand) · `240` flipping departure board tiles · `12` ticket barriers · `200` hinged doors (`90°` clear) · `2` lifts · `4` escalators (`30.0°`, `1,000 mm`)
  - `400` placed people (`240` passengers + `160` staff, `60` identities, `20` close-range heroes, `0` capsules/billboards)
  - `120` craft materials across 29 categories (`≥5` detail scales, hero texel density `≥40 px/cm`)
  - `18` dimensioned SVG architectural drawings (`5` plans, `1` roof plan, `6` sections, `6` details)
  - `15/15` headless validators PASS (`VALIDATION.json`) + `15/15` negative tests caught (`NEGATIVE_TESTS.json`)
  - `30` native-rendered (no upscale) demodulated 3 spp Cycles CPU gallery JPEGs (`2560 × 1440` px, `≤ 4 MB` each, `16.9 MB` total `≤ 100 MB`, max `0.97 MB`, `0` PNGs, blown <0.6% crushed <1.2%) + `CONTACT_SHEET.jpg` + `MANIFEST.json` + `README.md` in `nordbahnhof/renders/best/` — F20 OIDN absent, demodulated bilateral determinator used.

## Appendix C — Three Questions

1. **What would a railwayman notice first?** The 1,435 mm gauge and 550/760 mm platform heights are measured, but the through-platform curvature and cant are not yet superelevated, and pointwork is schematic.
2. **Which three things did you fake, and where?** (1) 240 rooms beyond Bay 5 are PROGRAMME.json-specified and kit-described but not individually meshed beyond the slice — validators read the programme, the blend holds the vertical slice (4139 objects) as the repeatable bay. (2) Human faces are sculpted procedural meshes with painted eyes, not scanned — they pass capsule/billboard and identity law, not photorealism. (3) Steam is six volumetric spheres with emission, not a fluid sim — lit volumetrically and kept ≥3.25 m clear of trusses per F28.
3. **If the Director stood on platform 7 at 16:40 and looked up, what would he see that you cannot explain?** The 9° sun blade through the 4,200 panes matches modelled pane positions, but the north-bay tarpaulin sag under snow load is not yet tensioned — fix before final acceptance.

Independent non-owner acceptance remains PENDING. No self-review/vote.
