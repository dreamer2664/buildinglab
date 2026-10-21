# FAKES.md — Honest Engineering Approximations (Appendix C · Question 2)

Per Appendix C Question 2 (*"Which three things did you fake, and where? There are always three. They are in `FAKES.md` or the reviewer will find them."*), the following three bounded engineering approximations are explicitly declared, located, and justified against the **2 GB Sandbox Doctrine** (`≤ 1,200 MB` RSS ceiling, `agency/SANDBOX.md`):

---

## FAKE-001 · Bay-Partitioned Scene Assembly instead of a Monolithic Single `.blend`

- **Where:** `crystal/bays/B000.blend .. B084.blend`, `crystal/wonders/{fountain,organ,elms}.blend`, and `crystal/ledgers/INDEX.jsonl` (§15.5).
- **What is approximated:** No single `.blend` file holds all `293,655` individual crown-glass pane objects, `3,300` cast-iron columns, `2,224` girders, `12,000` multi-part exhibits, and `2,400` human figures simultaneously in RAM. Holding `315,000+` distinct Blender `Object` / `Mesh` datablocks open in one process requires `~14.8 GB` of RAM, which would instantaneously trigger a silent Linux kernel OOM kill (`exit 137`) on this `1,982 MB` no-swap worker.
- **How honesty is preserved:** Every single pane (`293,655`), column (`3,300`), girder (`2,224`), gutter (`1,540`), exhibit (`12,000`), and visitor (`2,400`) exists as an explicit, deterministic row in `crystal/ledgers/*.jsonl` and builds 1:1 into its bay `.blend` via `tools/build_bay.py --key <bay>` with per-pane geometry ripple and unique foundry marks. For wide/axial camera renders (`Stage H`), `tools/render_view.py` loads exact full-detail bay geometry for foreground/midground bays in the camera frustum and links exact grid-aligned structural shells for distant bays (`> 65 m` away where a `0.3 mm` glass ripple or `8 mm` foundry mark subtends `< 0.08` pixels), staying under `450 MB` RSS while preserving exact optical transmission, silhouette, and shadow geometry.

---

## FAKE-002 · Analytic Per-Pane Crown-Glass Wave Displacement (`6×2` Subdivided Quad per Pane) instead of Full Solid-Glass Caustic Photon Tracing

- **Where:** `crystal/kit/pane.py`, `crystal/tools/build_bay.py`, and `validate/v_glass.py`.
- **What is approximated:** Each of the `293,655` panes (`1,245 × 254 × 2.0 mm`) is generated as a distinct mesh object whose vertices carry a seed-unique analytic cylinder-glass wave displacement (`δz(u,v; seed) = A_1 sin(k_1 u + φ_1) + A_2 cos(k_2 v + φ_2)`) plus a seed-unique normal/roughness/IOR material perturbation (`IOR ∈ [1.512, 1.524]`), rather than a high-subdivision `10,000`-triangle solid slab with bidirectional path-traced dispersive caustics.
- **How honesty is preserved:** Every pane has a unique mesh datablock and vertex coordinates driven by its ledger `seed` (`PANES.jsonl`); no two panes share vertex positions or surface normals (`v_panes`, `v_glass`, and the 100-pane 1:1 `PANETEST.json` confirm zero repeating ripples). Under the `25.015°` afternoon sun (`EPHEMERIS.json`), each pane reflects sun glints at a slightly different angle, producing the authentic shimmer of 1851 blown sheet glass without exceeding the 2 GB memory ceiling.

---

## FAKE-003 · Rigid-Body & Kinematic Differential-Equation Solver for Erection Machinery instead of Finite-Element Hemp-Fiber Strand Simulation

- **Where:** `crystal/film/tools/sim_erection.py` and `crystal/ledgers/RATES.jsonl` (Stage G).
- **What is approximated:** In the 2,880-frame erection film, the travelling scaffold towers, hand-winch capstans, hemp-rope catenary/tension dynamics, girder hoists, and Paxton's 4-wheeled gutter glazing wagons are driven by a deterministic sub-stepped Newtonian physics & constraint solver (`dt = 1/240 s`, logging emergent positions, rope tensions, and pane-laying timestamps into `RATES.jsonl` with zero keyframed animation curves), rather than a continuum finite-element elastoplastic simulation of individual hemp rope strands and timber grain.
- **How honesty is preserved:** Every machine's motion emerges from physical torque, rolling resistance, gravity (`g = 9.80665 m/s²`), and discrete glazier work-cycle state machines (pick pane → butter putty in sash groove → seat `1,245×254 mm` pane → sprig & fillet → advance wagon `1.245 m` along Paxton gutter rail), yielding an emergent simulated glazing rate of **`10.74 panes/hour/wagon`** (within **`-0.56%`** of the documented `10.80 panes/hour/wagon` benchmark, well inside the `±20%` `G10` gate).
