# Winterlichtplatz — factual production handoff

## State: STARTED, NOT complete / NOT a realism pass
Human confirmed large10–12 buildings, complete distinct interiors on every occupied floor, Central European Christmas-market style, licensed realistic people and original business brands. Adopted12 buildings/26 occupied floors; all26 floor programmes differ. Previous residence is preserved, independently pending; do not replace or self-accept it.

Task `t-20261016-339c`, branch `agent/blender/t-20261016-339c`, source namespace `townsquare/**` in buildinglab. Actual blender identity refreshed from this running session; new task read open/unowned, claimed and announced. Do not claim or heartbeat reviewer cards. All source changes for this new commission are isolated here.

## What actually exists
- `BRIEF.md`, `design/programme.json`:64×52m square;12 surrounding footprints,26 occupied floors,12 businesses, per-floor programme, furniture/people/material/lighting realism gates, planned90 final views.
- `scene/square-A2.blend`: current EDITABLE SHELL BLOCKOUT, not furnished scene.2531 scene objects;26 real floor collections and slabs, walls/window openings/glazing/frame geometry, roofs, basic public furnishings/tree/stalls/playground/lights/cameras. Packed3 CC0 proof maps.
- `scene/square-A0.blend`: actual earlier saved native with the original playground-tree conflict; historical only. `square-A1.blend`: saved intermediate whose render was killed; NO A1 image is claimed.
- `renders/A0-overview.png`, `A2-overview.png`: two real1600×1000 study originals actually opened individually; final evidence count remains ZERO. SHA/source-bound observations and explicit outstanding realism gaps in `evidence/visual-review.json`/`screenshot-manifest.json`.
- Actual old-native FAIL/new-native PASS regression: original tree trunk centre(24.075,0) is inside playground, corrected tree moved away. Both actual report files retained. Shell counts/dependency tests are NOT furnished-interior, circulation, people, photorealism or independent-acceptance checks.
- Twelve ORIGINAL vector-draft logo identities (`assets/branding`); vector marks not yet applied to3D shop signs, packaging or interiors, and not visually approved. Initial native uses name-placement typography only.
- Three downloaded/MD5-and-SHA-verified CC0 Poly Haven cobblestone01 proof maps,1K. Actual filenames/URLs/licences in manifests. Not final close-up resolution. MakeHuman/MPFB core asset licensing checked; human meshes/skins/clothes NOT yet acquired/generated/accepted.

## What remains unbuilt / unproven
ALL26 occupied-floor furnishing and detailed room/vertical circulation layouts; all realistic people; completed shop branding/sign systems; distinct facade/joinery/weathering development; detailed real foliage/fir and credible snow accumulation; realistic wetness/reflections/practical-light calibration; full playground fall-zone/circulation geometry audit; the separate climbing/play structure; crowd ground-contact/pose/collision audit; all final-resolution evidence, exact-final inspect/fix/reinspect, textured GLB/export reimport and final public reopen/render gates, non-owner acceptance. The A-stage inventory must not be relabelled final. No frozen schedule is a built room.

## Executed failures and recovery
Initial operator-per-primitive builder was still CPU-bound at actual4m25s with no native/render. Stopped; replaced object operators with direct mesh construction; builder then completed quickly. Historical source digest in runtime notes. A0 render completed in37.17s but16samples were visibly noisy. Actual inspection found playground trunk collision. Corrected A1 used32samples/integrated OIDN; actual exit137 during render, no image. A2 uses integrated denoising OFF and separate proven tiled colour-only OIDN,640px/48px overlap. This is display-referred sRGB processing, NOT guided HDR denoising. Preserve these facts; do not retry the failed identical integrated pipeline.

Official Blender4.3.2 restored; cache-busting query was needed after bare download URL returned403. Runtime needed libxkbcommon.so.0, extracted from libxkbcommon0 package into excluded cache. Public material API initially403; explicit browser user-agent/cache-busted metadata request succeeded, hashes checked. No transport secret is passed to Blender/render/denoise.

## Immediate next step
Build a high-fidelity pilot, not another broad low-detail copy pass: B01 supermarket shopfront/retail + actual fixtures/stock/branding and one complete upper floor; a contrasting B03 cafe interior; at least one anatomically credible textured winter-clothed person in a natural pose, close-view test, individual visual rejection/fix as needed. Prove the visual standard BEFORE expanding across26 floors/36 people. Human asset candidates and per-item licence obligations are in asset ledger. Raise samples/material maps appropriately, keep memory bounded, inspect actual images. Do not describe conical fir, bare scaffolds, uniform roofs or empty glowing rooms as photorealism.

## Reproduce current A2 study
Run from townsquare source root; restore exact proof maps first with `python3 tools/fetch_materials.py`. Supply official Blender library dependencies via local `LD_LIBRARY_PATH` if needed. Use a credential-free environment:

```
SQUARE_REVISION=A2 SQUARE_RENDER=1 blender --factory-startup -b -t 6 --python-exit-code 1 --python tools/build_blockout.py
python3 tools/denoise_png.py renders/A2-overview.png /path/to/blender/lib
blender --factory-startup -b scene/square-A2.blend --python-exit-code 1 --python tools/validate_blockout.py
```

Do not overwrite preserved historical originals or public immutable assets. Pick a new revision name for subsequent changes. Public study checkpoint/receipt, if present, is a STARTED/BLOCKOUT backup only, never a final package or approval. Final bulk storage uses separate `townsquare/blender/...` tags/ledgers. Text/code may be committed; native/renders/maps must not enter Git history.
