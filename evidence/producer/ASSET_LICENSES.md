# Asset rights / dependency record — Casa dei Colori

## Original model and artwork

**Version:** current bounded-card source commits and immutable release manifest identify the exact revision. **Source:** this project's procedural builders (`design/`, `assets/exterior/`, `assets/interiors/`, `evidence/producer/`). Original geometry, UV-free procedural PBR materials, geometric wall art, modelled planting/furniture, and original single-stroke mesh signs are offered under **CC0 1.0 Universal**: https://creativecommons.org/publicdomain/zero/1.0/ . No named real building was copied. No downloaded architectural/furniture/plant models, photographs, image textures, generated-image facades, audio or stock imagery are used in the final scene.

The native model has no `FONT` objects, linked libraries or required file-image textures. Final architectural lettering is original mesh strokes, not an undocumented local font. The earlier schematic archive is a separate checkpoint; its historical default-font notes are not a dependency of this release.

Lossless final mesh batching copies every source evaluated vertex, face, material index and corner normal. `SOURCE_GENERATED` vertex attributes preserve original per-component procedural coordinates. Full unbatched `scene/interiors.blend` and `scene/shell.blend` are also delivered for individual-component/modifier editing. See `mesh-conservation.json`; this is not mesh decimation or proxy replacement.

## Raster plan/view typography

- **Asset:** bundled `fonts/DejaVuSans.ttf`, DejaVu Sans Book **2.37**, Debian package `fonts-dejavu-core` **2.37-8**.
- **Source:** Debian-distributed DejaVu Fonts; upstream https://dejavu-fonts.github.io/ . The exact bundled font SHA-256 is `57f73e11f51999432bf7ab22ce55b6f945d5eca1bf824404cfa9ec2e3718c84e`.
- **Licence:** Bitstream Vera font licence with DejaVu changes in the public domain; redistribution terms/reserved names and full upstream/Debian copyright text are copied verbatim in `fonts/DEJAVU-LICENSE.txt`. The font is unmodified.
- **Use:** only disclosed Pillow-generated captions, plan room labels, door-swing symbols, footprint dimensions, north arrows, lighting-point symbols and metric scales over actual saved-scene renders. Not required to open the native model or GLB. Reproduction uses this checked-in relative font, never an untracked local font.

## Software/toolchain (not redistributed as scene assets)

- Official **Blender 4.3.2**, build `32f5fdce0a0a`, Cycles CPU, from https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz . Blender is GPL software; standard bundled glTF 2.0 I/O is used, with no private or third-party modelling add-on dependency.
- AgX / Medium High Contrast. Native final render default and evidence pipeline: **16 samples**, integrated denoising **OFF**. View-specific exposure/lens/camera/settings are recorded per PNG. Mesh batching is a memory workaround, not a resolution reduction.
- Bundled **Intel Open Image Denoise 2.3.0** runtime (Apache 2.0), used in a **separate** CPU process with overlapping 640-pixel tiles, display-referred sRGB colour-only. It removes Monte Carlo noise; it does not synthesize an alternate design or replace model geometry. The official runtime is not redistributed in the model archive. No claim is made that colour-only denoising equals a high-sample albedo/normal-guided reference.
- External helpers were run with **Python 3**, **NumPy 2.3.5**, **Pillow 12.3.0**. Their software licences do not impose a stock-asset licence on these original rendered views. Install dependencies to reproduce helpers; the native/GLB itself does not require Pillow or NumPy outside Blender.

## Portable representation notes

The GLB retains the actual modelled mesh geometry, material slots/PBR base colour, roughness, metalness/transmission/emission where supported, named occupied-level anchors, cameras and extras. Native procedural wood/bump nodes use their explicitly documented PBR-colour/roughness fallbacks rather than pretending to contain baked textures. glTF does not support Blender analytic **area lights**: the native practical luminaires/light layout are authoritative; mesh luminaires/emissive surfaces and the directional sun are portable, and a GLB viewer needs suitable environment lighting. These are documented format limitations, not missing asset downloads or placeholder geometry.

## Original Python code licence (MIT)

Copyright (c) 2026 buildinglab contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

No code/structural/accessibility approval, photorealism, perfection or independent acceptance is conferred by this rights record.

## Recorded external helper runtime

Python 3.13.16; Pillow 12.3.0; NumPy 2.3.5. `requirements.txt` pins the two external Python packages. Blender uses its own bundled Python. No runtime binaries or third-party model libraries are redistributed.

The portable GLB fallback is explicit: export-only in-memory copies disconnect procedural base-colour/normal links and use the declared base colour and constant PBR parameters. Native procedural materials on disk are not modified. Clean reimport compares base RGBA, roughness, metallic and transmission values within 0.0001, in addition to material names. This is a disclosed approximation of procedural shading, not a texture-baked exact match.
