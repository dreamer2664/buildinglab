# BLDG-2 detailed architecture

Original 26 × 20 m six-storey shell. Source `build_shell.py`, shared original mesh/material library `model_lib.py`, updated stair-door alignment and 133 actual facade openings in JSON schedules. Reversible level facade/high-partition/ceiling collections, roof/parapet, balconies, 10 paired-flight connections, two stair routes, one lift cab with six portals, context and procedural PBR materials. No external fonts: signage is original single-stroke mesh geometry.

Run official Blender 4.3.2 (hash 32f5fdce0a0a):
```sh
blender -b --python-exit-code 1 --python assets/exterior/build_shell.py
blender -b scene/shell.blend --python-exit-code 1 --python tools/validate_shell.py
```

This is visual architectural work, not code/structural approval. Shell QA found/fixed a roof soffit gap, corner overlap, terminal guard and framing. Reinspection accompanies the assembled model. All geometry/materials/sign strokes are original CC0 1.0; original scripts MIT, copyright 2026 buildinglab contributors, without warranty. No imported asset/textures/add-ons. Procedural bumps/wood grain have PBR-colour fallbacks in GLB rather than unrecorded baked textures.

Environment: 1.81 GiB process-group RAM budget. EEVEE and integrated full-frame OIDN caused OOM; do not rerun unchanged. Cycles CPU with integrated denoising OFF succeeds; `denoise_png.py` uses standard bundled OpenImageDenoise, display-referred sRGB colour-only, overlapping 640px tiles in a separate process. Record this post-processing in release metadata; it is not generative image substitution.

## Actual final-image regression cycle D

Original 0f final-image inspection led to stronger actual geometry probes, which failed six common-core ceiling caps over the lift shaft and 101 finish edge-overlap checks. The corrected source splits common-core ceilings around the real elevator rectangle, overlaps wall faces by 30mm, and tags each finish by room for final-batched corner-ray checks. Rebuilt shell and integrated native passed actual empty-shaft ceiling rays at all six levels and all 101 finish-edge checks. Failed original-native reports are retained under `evidence/producer/revision-D/`. No operation/code/structural approval is implied. Exact-current-source final imagery and independent acceptance remain separate.
