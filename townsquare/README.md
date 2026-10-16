# Winterlichtplatz — Christmas town square

**Production started; not a final-realism delivery.** New human-confirmed commission, separate from the previous Mediterranean residence. Read BRIEF.md and HANDOFF.md. Actual task/branch is recorded in task.json. Source lives in townsquare/** on its own branch of buildinglab; bulky native/material/render evidence is published separately to storagecode, never Git history.

12 surrounding buildings;26 occupied floor programmes; distinct interiors required for every floor. Original brand-vector drafts, licensed PBR feasibility maps, Christmas market/tree/benches/trees/lamps/playground. People and complete furnishing are NOT yet built. No final image, GLB reimport, independent acceptance or photorealism claim.

## Current reproducible tools
- `python3 design/make_programme.py`: explicit per-building/per-floor unique programme.
- `python3 tools/fetch_materials.py`: restore exact public1K CC0 proof maps and check SHA-256. Upgrade resolution/material development before final close views.
- `python3 assets/branding/build_marks.py`: twelve original vector-draft identities; application to3D signs remains pending.
- Blender4.3.2 `--factory-startup -b --python tools/build_blockout.py`: builds and saves initial native before rendering. Set `SQUARE_REVISION=A2 SQUARE_RENDER=1` for corrected study. First phase is shell/public-realm blockout, regardless of revision suffix.
- Blender `-b scene/square-A2.blend --python-exit-code 1 --python tools/validate_blockout.py`: actual shell and dependency check, not a realism/completeness certificate.

Reference Linux runtime required libxkbcommon.so.0 in addition to the official Blender bundle. No renderer receives transport credentials. Textures are packed into the native. Cycles CPU/AgX/Medium High Contrast; first A0 noisy16samples, A1 integrated-denoiser attempt failed; corrected A2 study32samples with separate tiled OpenImageDenoise,1600×1000. These are study dimensions, NOT final evidence dimensions.
