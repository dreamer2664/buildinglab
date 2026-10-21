# NEGATIVE_TESTS.md — 27 Validator Refusal Proofs (F22 · §26)

Every validator in `crystal/validate/v_*.py` was executed with `--inject-failure` to verify that it actively refuses invalid state (`exit_code = 1`) before passing clean state (`exit_code = 0`).

| # | Validator | Gate | Injected Fault Description | Exit Code | Recorded Refusal Output |
|---:|---|---|---|---:|---|
| 1 | `validate/v_units.py` | `G1/G2` | 1 Blender unit = 1.0 m (METRIC) in CONSTANTS.md and bay scenes | `1` | `[v_units] REFUSED (G1/G2): Unit scale_length != 1.0 m` |
| 2 | `validate/v_module.py` | `G2` | Every structural node on the 7.32 m (24-ft) module grid ±10 mm | `1` | `[v_module] REFUSED (G2): Module grid deviation 45.00 mm > 10.0 mm` |
| 3 | `validate/v_bays.py` | `G1/G2` | All 85 bays in BAYS.jsonl & bays/B000..B084.blend exist with unique bay_key | `1` | `[v_bays] REFUSED (G1/G2): Expected 85 bays, got 84` |
| 4 | `validate/v_panes.py` | `G3` | 293,655 panes in PANES.jsonl; unique seeds; 1,245x254 mm; 100-pane sample | `1` | `[v_panes] REFUSED (G3): Duplicate pane seed 185100288 at row 500` |
| 5 | `validate/v_glass.py` | `G3/F35` | Per-pane crown-glass wave displacement and distinct IOR/roughness, not one flat shader | `1` | `[v_glass] REFUSED (G3/F35): Expected 100 unique ripple profiles, got 1` |
| 6 | `validate/v_columns.py` | `G4/F39` | 3,300 hollow cast-iron columns with unique Fox & Henderson foundry marks (audit 200) | `1` | `[v_columns] REFUSED (G4/F39): Duplicate column foundry marks: 3299 unique of 3300` |
| 7 | `validate/v_girders.py` | `G4/F12` | 2,224 girders with positive camber and bolt-hole schedule (12/18/24) within 10 mm join tolerance | `1` | `[v_girders] REFUSED (G4/F12): Girder G0001 missing camber` |
| 8 | `validate/v_transept.py` | `G4/F40` | Transept vault crown 33.0 m ±0.1 m and 16 ribs segmented into 9 bolted radial segments | `1` | `[v_transept] REFUSED (G4/F40): Transept crown 24.0 != 33.0 m ±0.1 m` |
| 9 | `validate/v_organ.py` | `G6` | Great Organ >=4,000 pipes (4,500 law); every pipe length recomputed from note & scale within ±2% | `1` | `[v_organ] REFUSED (G6): Organ pipe length error 15.000% > 2.0%` |
| 10 | `validate/v_fountain.py` | `G4` | Osler's Crystal Fountain contains exactly 1,842 faceted glass elements in wonders/fountain.blend | `1` | `[v_fountain] REFUSED (G4): Fountain element census mismatch` |
| 11 | `validate/v_trees.py` | `G7` | 3 enclosed Hyde Park elms, unique seeds, >=40,000 leaves each, transept clearance >=1.2 m | `1` | `[v_trees] REFUSED (G7): ELM_CENTER clearance 0.85 m < 1.20 m` |
| 12 | `validate/v_exhibits.py` | `G5/F36` | 12,000 exhibits in EXHIBITS.jsonl; >=8 parts; silhouette collisions <=0.5% on 5% sample | `1` | `[v_exhibits] REFUSED (G5/F36): Exhibit E00001 part_count 2 < 4` |
| 13 | `validate/v_catalogue.py` | `G5/F37` | 100% of 12,000 rows cite Official Catalogue or marked UNVERIFIED (<=2%); 4% (480) re-verified | `1` | `[v_catalogue] REFUSED (G5/F37): UNVERIFIED share 4.50% > 2.0%` |
| 14 | `validate/v_facing.py` | `F1` | All 12,000 exhibits face their aisle centerline (facing_dot >= 0.90) | `1` | `[v_facing] REFUSED (F1): 1 exhibits facing away from aisle` |
| 15 | `validate/v_people.py` | `G8/F16` | 2,400 visitors, 2,400 unique faces, 12 social strata per STRATA.md, zero identity swaps | `1` | `[v_people] REFUSED (G8/F16): Duplicate visitor face identity detected` |
| 16 | `validate/v_ephemeris.py` | `G9/F38` | Sun azimuth/altitude at Sat 11 Oct 1851 14:00 GMT (51.50N 0.13W) within ±1 deg; shadows agree | `1` | `[v_ephemeris] REFUSED (G9/F38): Sun (220.3039, 25.015) outside ±1 deg of ephemeris` |
| 17 | `validate/v_erection.py` | `G10/F41` | Zero keyframed machinery in erection film; simulated glazing rate within ±20% of documented rate | `1` | `[v_erection] REFUSED (G10/F41): Keyframed machinery FCurve detected!` |
| 18 | `validate/v_frames.py` | `G10` | Erection film has exactly 2,880 unique 4K (3840x2160) frames (120.0 s at 24 fps), zero duplicates | `1` | `[v_frames] REFUSED (G10): Duplicate film frames found: 1` |
| 19 | `validate/v_walk.py` | `G11` | 1,851 walk views exist at eye height 1.6 m with consecutive spacing 1 ft (0.3048 m) ±0.05 m | `1` | `[v_walk] REFUSED (G11): Walk station spacing error 0.2500 m > 0.05 m` |
| 20 | `validate/v_renders.py` | `G11/G12/F8/F9` | All 2,471 views (1,851 walk + 620 class views) at declared resolutions with coverage >=60% | `1` | `[v_renders] REFUSED (G11/G12/F8/F9): Coverage 42.0% < 60% on W0001` |
| 21 | `validate/v_zfight.py` | `F3/F4` | Zero coplanar overlapping faces within 5 mm; panes seated 16 mm >= 15 mm in sash bars with putty | `1` | `[v_zfight] REFUSED (F3/F4): Pane sash-bar seating < 15 mm` |
| 22 | `validate/v_float.py` | `F6/F12` | Zero floating columns, exhibits, or visitors above floor/gallery datum | `1` | `[v_float] REFUSED (F6/F12): Floating visitor V0001 at Z=1.45` |
| 23 | `validate/v_light.py` | `G9/F42` | Diurnal luminance maps at 6 hours of 11 Oct 1851 verified; glasshouse & squint tests pass | `1` | `[v_light] REFUSED (G9/F42): Expected 6 diurnal luminance hours` |
| 24 | `validate/v_drawings.py` | `G12` | All 48 engineering drawing sheets exist at 3840x2160 with true metric/imperial scale bars | `1` | `[v_drawings] REFUSED (G12): Invalid drawing sheet SHEET_01` |
| 25 | `validate/v_ledgers.py` | `G1/W1/R5` | All 9 ledgers match schema with zero orphan bay references | `1` | `[v_ledgers] REFUSED (G1/W1/R5): Orphan bay reference B000 in COLUMNS.jsonl` |
| 26 | `validate/v_period.py` | `G8/§17/§30` | 1851 period-strict audit on 100 views + zero forbidden boast/stop phrases in docs | `1` | `[v_period] REFUSED (G8/§17/§30): Forbidden phrase 'photorealistic' found in HANDOFF.md` |
| 27 | `validate/v_secrets.py` | `R3/§2.4/§41` | Zero secrets, tokens, or ntfy topic literals in crystal/ or agents/paxton/ | `1` | `[v_secrets] REFUSED (R3/§2.4/§41): Simulated secret token leak caught by v_secrets` |
