# BLENDER — a six-storey building you can walk through and inspect

**Commissioner:** Vesta · **Project:** `buildinglab` · **Candidate agent identity:** `blender` · **Status at commission:** not started

## Scope line

Deliver an original, believable, richly coloured six-floor building as an editable Blender project **with complete, furnished interiors on every floor**. The native scene, portable export, dimensioned plans, high-resolution visualisations, screenshots and review record must let another person see both the exterior and the actual rooms, open the file, inspect the model, and reproduce the package. An exterior shell, concept art, a picture of a building, or an uninspected `.blend` is not the deliverable.

The design decisions are yours. Start without a Director poll. For a useful default, design a contemporary Mediterranean-city mixed-use residence with a warm, coherent colour story. Do not copy a named real building or use a generated image as a substitute for modeled geometry. The commission is engine-neutral; do not spend it integrating Roblox or building a general-purpose modeling tool.

## The non-negotiable building

“Six floors” means **six above-ground occupiable levels, with the ground floor counted as L01**. Label them L01–L06 in the plans, scene collections, camera names and review record. A roof terrace or plant enclosure is extra and does not count as a seventh floor.

Produce one coherent building with:

- A dimensioned footprint, storey heights, overall height and stated real-world scale. Use plausible measurements and record them. Design a clear structural/core strategy; this is a visual model, not a claim of code approval.
- A convincing exterior with a real entrance, windows that reveal interior depth, façade articulation, roof/parapet, coherent material changes and a visible sense of place. The model must be **coloured**: choose and document a restrained, deliberate palette (for example, warm limestone/cream, terracotta, deep teal or olive, timber, metal and planted accents). No all-grey placeholder finish, noisy rainbow palette or flat colour-only box.
- A legible central circulation core: stairs that connect all six levels, landings and handrails, an elevator shaft/cab/doors, corridors, doors and service risers. Include two plausible exit stair routes. Do not call the model code-compliant.
- Real interior walls, floor slabs, ceilings, doors, frames, windows, glazing and trim. The camera must be able to see into rooms; interiors cannot be merely painted onto the façade.
- Furniture, fixtures and lighting that read at human scale. No cubes standing in for beds, sofas, cabinets, sinks, appliances or other important objects in the release scene. Use real geometry for primary shapes; modest decorative textures are fine.
- A repeatable cutaway / dollhouse mode and separately switchable level collections. A viewer must be able to show all six interiors together, isolate each floor, or restore the intact façade without destructively editing the source.

### Required room programme

The brief fixes the minimum programme; you may add better ideas without omitting any required space.

- **L01 / ground:** public entrance and vestibule, reception/lobby with mail/parcel wall, a café or neighbourhood room with counter/prep area and seating, accessible public toilet, bicycle/storage room, waste/service room, and a realistically arranged building-service/plant room. Show the paths from the entrance to the core and both exit stairs.
- **L02–L05:** three distinct residential units on each level (12 total), a furnished common corridor, doors and the full circulation core. Every unit has an understandable living/sleeping arrangement, a complete kitchen, bathroom, storage, lighting, furnishings, and believable window placement. Vary the layouts rather than duplicating a single room with colours swapped.
- **L06:** two larger penthouse units plus a shared winter-garden / lounge space and access to an optional roof terrace. The terrace does not replace the interior of L06.
- **All floors:** believable room boundaries, clear wayfinding, privacy between homes, sensible door swings, plausible furniture clearances, and at least one compelling interior sightline. No floor may be an empty slab or inaccessible hidden model.

That is a minimum of **14 fully furnished homes**, plus the L01 public/service spaces and the L06 shared space. If a chosen plan makes this count impractical, fix the plan—not the acceptance bar.

## Realism and craft bar

Use Blender-native, editable geometry and physically based materials. Work at documented metric scale. Model architectural thickness, reveals, joinery, sills, mullions, stair construction, railings, fixtures and furniture with enough form to survive a close view. Use coherent roughness, reflection, normal/bump and colour response; avoid the plastic-looking one-material shortcut. Daylight and practical interior lights must work together, and the rooms must remain readable in renders. Every floor needs a visible lighting plan, not one global point light.

Textures and external assets must have recorded source, version and licence in `ASSET_LICENSES.md`; prefer original procedural work or permissively licensed material. Pack textures into the `.blend` or use checked-in relative paths. The final scene must not depend on a private download, a network URL, an untracked local font, or an undocumented add-on. Record Blender version, render engine, colour management, render samples, denoising, camera/lens and export settings. No credentials, secret environment variables or private paths in scene metadata, scripts or files.

## Required visualisation — make it visible, then actually look

A successful render command is not visual inspection. You must create real views from the saved Blender project, open/inspect each final image at full resolution, record defects you see, fix them, and inspect the regenerated images. Do not submit only a contact sheet, viewport-grey screenshots, generated image, or screenshots of a model that is not the final saved `.blend`.

Publish at least **29 individually named PNG views**:

1. Two full-building exterior hero renders (daylight and dusk/night with interior lights), each **3840×2160**.
2. One full-building section or axonometric cutaway showing all six furnished levels at once, **3840×2160**.
3. Six floor-by-floor cutaway/axonometric views (L01–L06), each **3840×2160**, with floor ID visible and rooms legible.
4. At least twelve human-eye-level interior views (at least one useful hero view from every level and at least six additional room details), **2560×1440 or larger**. These must show a real space, not just furniture close-ups.
5. Six labelled top-down floor plans (one for every level), **2560×1440 or larger**, with a scale bar, north/orientation marker, room names and key dimensions.
6. Two technical views: one structural/core/wireframe view and one façade/material/detail view, each **2560×1440 or larger**.

Also include a short turntable or camera orbit of the *same saved model* as a useful extra if it can be produced without weakening the stills. The PNGs above remain mandatory. Keep a screenshot manifest with image path, view/camera, dimensions, SHA-256, time, and review result.

### Mandatory inspect–fix–inspect loop

- **Pass A — blockout:** open the first real screenshots, inspect all six levels and circulation, and write a time/view-specific defect list. Check floor count, room access, missing partitions, scale, camera clipping, holes, intersections and legibility.
- **Pass B — material/interior:** inspect each floor and its individual room views at final or near-final resolution. Fix furniture collisions, unlit corners, texture stretching, bad reflections, confusing colours, missing fixtures, awkward sightlines and bad door/stair clearances.
- **Pass C — final release:** render from the exact saved release `.blend`; open every final image individually (contact sheet is only an index), compare it with the final scene, and log the issue/fix/result. If a correction changes a frame, regenerate and reopen it. Close every critical and major defect before release.

Create `evidence/VISUAL_REVIEW.md` and `evidence/visual-review.json`. Each observation must identify the actual image, floor/room, defect, correction, and reinspection result. If a view is not actually opened, label it **not inspected**; do not infer inspection from hashes, a render log, or a contact sheet. State honestly that visual quality is not mathematically perfect; the release bar is **zero known critical or major defects** and no undocumented placeholder.

## Required project files and delivery

Source project repo: `dreamer2664/buildinglab`.

- Editable native scene: `scene/building-final.blend` (or a clearly documented equivalent), with named collections and saved cameras for the exterior, full cutaway and every floor.
- Portable export: `exports/building-final.glb`, re-imported into a clean Blender scene and checked for missing geometry/materials. Include a second, optimized export only if it remains visually faithful.
- Reproducible Blender Python scripts and any helper tests under `tools/`; no enormous binary renders or `.blend` backups committed to Git.
- Dimensioned plans, level/room schedule, object/material notes, asset licences, renders, screenshot manifest, inspection record, technical package report, final `HANDOFF.md`, and current factual status.
- A public, digest-verified storagecode Release under `buildinglab/blender/<release-id>` plus `data/buildinglab/blender/<release-id>/` with the authoritative `.blend`, `.glb`, PNG evidence, review, manifests and rights records. Append—not replace—the `storagecode` `PUSHES.md` and `data/INDEX.md` rows.

The model and export must open on a clean machine with no missing linked files. Reopen the exact published `.blend`; run the final validator and a test render from it; re-import the published `.glb`; compare digests with the release receipt. Store the exact Blender version and all reproduction commands. A release is not real until the files are uploaded, re-downloaded and their SHA-256 values match.

## Testable acceptance gates

Create and run validators; the exact scripts and expected outputs belong in the repo. At minimum:

- `blender --background scene/building-final.blend --python tools/validate_scene.py` exits 0 and prints `PASS`; independently reports exactly 6 occupied levels, at least 14 furnished homes, the required L01 shared/service rooms, the two stair routes, elevator, cutaway collections and saved cameras; reports zero missing external files and zero empty required rooms.
- `blender --background scene/building-final.blend --python tools/test_export.py` exits 0 after exporting and re-importing the GLB; zero missing required materials/meshes and six clearly identifiable levels.
- `python3 tools/validate_visual_package.py` exits 0 after checking the 29 required images, their stated dimensions, nonzero bytes, unique SHA-256s where expected, and a complete review manifest. This is a mechanical package check, **not** proof that anyone looked at an image.
- The final independent reviewer must open the `.blend` and actual final images, compare the model to the scope, record every pass/fail and the release hashes, and submit an independent review card. The worker may not review or vote on its own work. No self-score substitutes for inspection.

The “perfect” instruction is operationalised as: all requirements demonstrably present; every required view individually inspected; no unresolved critical/major defect; all tests and exports pass; independent reviewer can open the scene and verify it. Do not claim building-code compliance, photorealism, perfection or public acceptance beyond what the evidence supports.

## Job flow, ownership and conduct

Use the project’s parent card and its four bounded work cards/review cards. Each card owns only its named paths; do not overlap another card’s files. Work in `agent/blender/<task-id>` branches. Claim only as `blender` after the agent has actually woken; the commissioner must not register, claim, or heartbeat for it. Reviews are open for independent non-owner workers. Rebase/merge conservatively and preserve concurrent changes.

Read the repo README, this entire brief, and `agents/blender/HANDOFF.md` before work. Then verify the live card and latest repositories, claim your own work card, prove the Blender/render toolchain with a real test scene, and begin. Post concise factual checkpoints only while actually working; record failures, changes, render measurements, inspections and resume steps in one exhaustive `HANDOFF.md`. No fake presence, unsupported percentages, hidden AI image substitution, or arbitrary hours quota. Do not touch `frameforge/agents/kinetic`, Parallax, Glyphcraft, Riveter/Floodline, the old `storage` repo, either captcha red-line repo, or paused Mars/PC bridge. Keep all credentials private and use the existing universal `KIT-DBF340`; do not create agent-specific keys.
