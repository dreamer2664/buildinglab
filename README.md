# Buildinglab — the six-storey Blender model

An independent, code-first project for an **original, coloured six-floor building with complete, furnished interiors on every level**. The final result is a usable Blender scene and portable export, supported by dimensioned plans, floor-by-floor visualisations, actual screenshots, visual inspection/revision evidence, and a reproducible package.

## Start here

1. Read [the complete Blender commission](briefs/BLENDER.md) before touching the model.
2. Check the live Chatcode project parent and your own open child work card. Claim only as `blender` after you have actually woken; the commissioner will not register or claim on your behalf.
3. Work in `agent/blender/<task-id>`. Use only the paths owned by your card. Preserve other workers' changes.
4. Treat renders as evidence only after opening each required full-size image, logging what you saw, fixing defects, and re-opening the final image.

## Project boundaries

- Source repo: `dreamer2664/buildinglab` (this repo); public source must contain no credentials.
- Task board: `dreamer2664/chatcode`, tags `buildinglab,blender`.
- Durable model, exports and inspection evidence: `dreamer2664/storagecode` under `data/buildinglab/blender/<release-id>/` and a matching Release. `storagecode` is the sole primary archive; retired `dreamer2664/storage` is read-only.
- No dependency on Frameforge, Kinetic, Parallax, Glyphcraft, Riveter/Floodline, Roblox Studio, or the paused Mars/PC bridge. Do not touch those projects.

The model is not started at commissioning. A repo, card, brief or timestamp is not an awake agent, a model, a render or acceptance. The parent card and review cards describe bounded work and independent verification; read their exact live state before acting.

## Release bar

The exact floor count is six above-ground levels including the ground floor. All six interiors must be furnished, accessible in the saved scene, and separately visualisable. Minimum visual evidence is 29 individually named, high-resolution images from the saved Blender scene, opened and inspected one by one across multiple fix/re-inspect passes. “Perfect” means zero known critical/major defects and a complete independent audit—not an unsupported guarantee.

Final `.blend`, `.glb`, renders, hashes, visual-review manifest, rights record and handoff belong in the primary storagecode Release/archive; binaries and working renders do not belong in Git history. See the charter for exact contents and commands.

## Activity and truthfulness

Post concise factual checkpoints only while actually working. Keep one exhaustive `agents/blender/HANDOFF.md`; record blockers, failures, exact file hashes and continuation instructions. No fake heartbeats, invented progress, unreviewed screenshots or claims of code compliance. Keep credentials in the mode-0600 private commissioning packet only.
