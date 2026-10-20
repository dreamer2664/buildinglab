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

The model is not started at commissioning. A repo, card, brief or timestamp is not an awake agent, a model, a render or acceptance. All cards below were created open and unowned; the `blender` identity has not been registered, and no model exists yet.

## Parent, work and verification cards

Parent project: [t-20261016-3fe5](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-3fe5.json).

| Stage | Work card | Independent review |
|---|---|---|
| Dimensioned plan + blockout | [t-20261016-c577](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-c577.json) | [t-20261016-64ce](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-64ce.json) |
| Exterior shell + structure | [t-20261016-0d4e](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-0d4e.json) | [t-20261016-2223](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-2223.json) |
| Complete six-floor interiors | [t-20261016-61b0](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-61b0.json) | [t-20261016-008a](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-008a.json) |
| Assemble, inspect, revise + release | [t-20261016-58d8](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-58d8.json) | [t-20261016-08c6](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-08c6.json) |

The parent card and four read-only reviewer cards are separate from the Blender work. Read their exact live state before acting.

## Release bar

The exact floor count is six above-ground levels including the ground floor. All six interiors must be furnished, accessible in the saved scene, and separately visualisable. Minimum visual evidence is 29 individually named, high-resolution images from the saved Blender scene, opened and inspected one by one across multiple fix/re-inspect passes. “Perfect” means zero known critical/major defects and a complete independent audit—not an unsupported guarantee.

Final `.blend`, `.glb`, renders, hashes, visual-review manifest, rights record and handoff belong in the primary storagecode Release/archive; binaries and working renders do not belong in Git history. See the charter for exact contents and commands.

## Activity and truthfulness

Post concise factual checkpoints only while actually working. Keep one exhaustive `agents/blender/HANDOFF.md`; record blockers, failures, exact file hashes and continuation instructions. No fake heartbeats, invented progress, unreviewed screenshots or claims of code compliance. Keep credentials in the mode-0600 private commissioning packet only.
