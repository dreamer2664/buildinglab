# DEFECTS.md — Honest Ledger of Known Limitations & Container Constraints (§29)

1. **Container Memory Ceiling (`1,982 MB` RAM / `0 MB` Swap / `MEM_CEILING_MB = 1200`):**
   - Because the execution container has `1,982 MB` of total RAM and no GPU (`CPU-only Cycles`, `openimagedenoise = False`), loading all 85 bays (`293,655` panes + `12,000` exhibits + `2,400` visitors) into a single monolithic Blender process simultaneously would require ~28 GB of RAM and trigger the kernel OOM killer.
   - **Mitigation implemented:** The building is partitioned into 85 deterministic bay `.blend` files (`bays/B000.blend .. B084.blend`) plus 3 wonder `.blend` files (`wonders/{fountain,organ,elms}.blend`) and 5 modular kit `.blend` files (`kit/*.blend`), all rebuilt from `ledgers/*.jsonl` with `< 350 MB` peak RSS per process.
2. **Cycles CPU Sample Count Under `openimagedenoise = False`:**
   - The Ubuntu `blender 4.3.2` package in this sandbox was compiled without Intel OpenImageDenoise (`openimagedenoise: False` in `evidence/TOOLCHAIN.txt`). Low-sample Monte Carlo path tracing on 2 vCPUs exhibits mild diffuse grain in shadow regions.
   - **Mitigation implemented:** `sc.cycles.use_denoising = False` is enforced across all scripts, and a radius-1 bilateral/box smoothing filter is applied in `render_best_and_window.py` to suppress single-pixel fireflies without blurring structural iron members.
3. **Catalogue Unverified Tail (`1.00%` of 12,000 rows):**
   - `120` minor provincial/foreign sub-exhibits (`1.00% <= 2.00%` allowed by G5/F37) whose exact page number in the 3-volume Official Descriptive and Illustrated Catalogue could not be cross-checked offline are explicitly tagged `UNVERIFIED` in `ledgers/EXHIBITS.jsonl` and `evidence/CATALOGUE_AUDIT.json`.
4. **Independent Blind-Test Ballot (`evidence/BLINDTEST.json`):**
   - Per §16, the 24-trial screening run across the 6 classes is recorded in `evidence/BLINDTEST.json`; final blind-test scoring is reserved for an independent non-owner reviewer.
