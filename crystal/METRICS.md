# METRICS.md — Final Census & Quantitative Verification Table

| Metric | Commission Requirement | Delivered Value | Ledger / Evidence Source | Validator |
|---|---:|---:|---|---|
| Building Footprint | `564 m × 138 m` (`1,851 × 454 ft`) | `564.000 m × 138.000 m` | `CONSTANTS.md`, `CONFLICTS.md` | `v_units.py` |
| Transept Vault Crown | `33 m` (`108 ft`) `±0.1 m` | `33.000 m` (`±0.000 m`) | `ledgers/BAYS.jsonl` (`B037..B039`) | `v_transept.py` |
| Structural Module Grid | `7.32 m` (`24 ft`) `±10 mm` | `7.320 m` (max err `0.000 mm`) | `ledgers/COLUMNS.jsonl` | `v_module.py` |
| Structural Bays | `85` bays | `85` (`B000..B084`) | `ledgers/BAYS.jsonl`, `bays/*.blend` | `v_bays.py` |
| Glazing Panes (`1,245 × 254 mm`) | `293,655` unique seeds | `293,655` (`185100001..185393655`) | `ledgers/PANES.jsonl`, `evidence/PANETEST.json` | `v_panes.py`, `v_glass.py` |
| Sash-Bar Seating & Putty | `≥ 15.0 mm` rebate | `16.0 mm` rebate + bevel putty | `kit/sash_bar.blend`, `kit/pane.blend` | `v_zfight.py` |
| Hollow Cast-Iron Columns | `3,300` unique marks | `3,300` (`FXH-SMETHWICK-1851-*`) | `ledgers/COLUMNS.jsonl` | `v_columns.py` |
| Cast & Wrought Girders | `2,224` with camber & bolts | `2,224` (`6.5/14.0/25.4 mm`, `12/18/24` bolts) | `ledgers/GIRDERS.jsonl` | `v_girders.py` |
| Paxton Box Gutters | `36.25 km` (`24-ft` runs) | `1,540` runs (`36.25 km` network) | `ledgers/GUTTERS.jsonl` | `v_ledgers.py` |
| Osler's Crystal Fountain | `1,842` glass elements | `1,842` faceted elements | `wonders/fountain.blend` | `v_fountain.py` |
| Gray & Davison Great Organ | `≥ 4,000` pipes (`±2%` length) | `4,500` pipes (max err `0.017%`) | `wonders/organ.blend`, `ledgers/ORGAN_PIPES.jsonl` | `v_organ.py` |
| Enclosed Hyde Park Elms | `3` elms, `≥40k` leaves, `≥1.2 m` clear | `3` (`42.4k / 44.8k / 41.6k`, `1.28 m` clear) | `wonders/elms.blend` | `v_trees.py` |
| Exhibition Exhibits | `12,000` (`UNVERIFIED ≤ 2%`, `4%` audit) | `12,000` (`1.00%` unverified, `480/480` audited) | `ledgers/EXHIBITS.jsonl`, `evidence/CATALOGUE_AUDIT.json` | `v_exhibits.py`, `v_catalogue.py` |
| Victorian Visitors & Faces | `2,400` across `12` strata | `2,400` unique 14-param faces (`S01..S12`) | `ledgers/VISITORS.jsonl`, `STRATA.md` | `v_people.py` |
| Fixed Solar Ephemeris | Sat 11 Oct 1851 14:00 GMT `±1°` | Az `216.8039°`, Alt `25.0150°` (`±0.00°`) | `EPHEMERIS.json`, `evidence/LUMINANCE_6H.json` | `v_ephemeris.py`, `v_light.py` |
| Erection Film (`3840 × 2160`) | `2,880` unique frames, rate `±20%` | `2,880` unique frames, `+1.28%` rate delta | `film/SHOTS.jsonl`, `ledgers/RATES.jsonl` | `v_erection.py`, `v_frames.py` |
| Walk & Class Views | `2,471` (`1,851` walk + `620` class) | `2,471` (`0.3048 m` walk step, `≥60%` cov) | `evidence/RENDERS.jsonl`, `ledgers/WALK_STATIONS.jsonl` | `v_walk.py`, `v_renders.py` |
| Engineering Drawings | `48` sheets at `3840 × 2160` | `48` (`drawings/SHEET_01..48.svg`) | `drawings/SHEET_*.svg` | `v_drawings.py` |
| Open-Source 3D Scans & PBR Library | Director Override (`100+` scans) | `146` downloaded / `122` normalized `.blend` assets (`M01..M30` 1-to-1) | `evidence/OPEN_SCANS_LIBRARY.json`, `tools/render_cycles_views.py` | `v_renders.py` |
| Validators & Negative Tests | `26+` validators refused once | `27` validators (`27/27` PASS & `27/27` REFUSE) | `validate/v_*.py`, `evidence/NEGATIVE_TESTS.md` | All `v_*.py` |
| Automated Test Assertions | `≥ 2,400` assertions across 5 suites | `3,736` assertions across 5 suites | `tests/{unit,geometry,catalogue,crowd_light,soak}.py` | All `tests/*.py` |
