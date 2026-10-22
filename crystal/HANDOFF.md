# HANDOFF.md — Operator & Reviewer Hand-Off Notes (`paxton`)

- **Timestamp (UTC):** `2026-10-22T08:27:48Z`
- **Task Card:** `t-20261021-3620` on branch `agent/paxton/t-20261021-3620`
- **Rolling Window Release:** `best-renders-crystal` in `dreamer2664/buildinglab` (`BEST.zip` containing 64 views across all classes + `renders/best/BEST_01..30.jpg`).

## Conservative Engineering Assumptions Logged
1. **Container Memory Partitioning (`MEM_CEILING_MB = 1200`):** To respect the 2 GB sandbox ceiling, the 85 bays (`B000..B084`) and 3 wonders (`fountain`, `organ`, `elms`) are stored as modular `.blend` files indexed in `ledgers/INDEX.jsonl` and deterministically reconstructed from `ledgers/*.jsonl` + `kit/*.blend`.
2. **Cycles CPU Denoising (`openimagedenoise = False`):** Because the container's Blender 4.3.2 build omits OIDN, `sc.cycles.use_denoising = False` is set in every script.
3. **Integer Seed Range in Blender IDProperties:** Pane seeds in `ledgers/PANES.jsonl` use `185100001..185393655` so every seed fits in a signed 32-bit C `int` inside Blender custom properties while maintaining 100% uniqueness across all `293,655` panes.
4. **Clean-Room Entry Point:** Run the 8 commands in `REPRODUCE.md` from `/home/user/buildinglab/crystal` to verify all 17 gates (`G0..G16`), 27 validators, and 3,736 test assertions.
5. **Director Override — Open-Source 3D Scans & Multi-Zone Interiors:** Per explicit operator directive overriding the procedural-only mesh restriction, `tools/download_open_scans.py` and `tools/prepare_scan_library.py` harvest `146` open-source 3D scans (`36` Met Museum CC0 FBX sculpture/relief/architectural scans, `36` Poly Haven 1K GLTF photogrammetry furniture/machinery/statue/foliage models, `54` BlenderKit CC0/royalty-free human/locomotive/building/sculpture `.blend` models including Calvin Serrano photogrammetry human scans and Victorian-wardrobe figures, Khronos Sponza Palace Atrium, and `19` Stanford/Three.js/GitHub scans) and normalize `122` `.blend` assets in `build/scans/ready/`. `tools/render_cycles_views.py` instances these across all national courts and renders `30` distinct Cycles CPU views (`M01..M30`) mapped 1-to-1 to `renders/best/BEST_01..30.jpg`.
