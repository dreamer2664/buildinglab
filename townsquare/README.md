## Renders of every building + the whole square, and the full 3D model

**Release:** https://github.com/dreamer2664/storagecode/releases/tag/townsquare/blender/r14-exteriors-20261019

| What | File | Bytes | SHA-256 |
|---|---|---|---|
| Rendered images (16 PNG + gallery + manifests) | `Winterlichtplatz-Renders-r14-d10116969530.zip` | 29690932 | `fa9e96811b6b9ce6f06fed586afdb5ce94fe923990e96a010b4671a8e06674b6` |
| Full editable Blender model | `Winterlichtplatz-Full-3D-Editable-r14-d10116969530.zip` | 616777731 | `704904a2455db1e446c95ef742e2440f4f44a0a900678196e9103586bed27586` |
| Portable glTF model + viewer | `Winterlichtplatz-Portable-3D-r14-d10116969530.zip` | 415110630 | `4d5586273a7f5b85c34f848aafa809951161bc0d741d4238da9621684dc17c2a` |

All three were re-downloaded without credentials and CRC / entry-count / listed-member-SHA verified.

- Images: 12 building exteriors (`B01_exterior` … `B12_exterior`) and 4 whole-village elevated views (`V01` … `V04`), 1600×900, actual Cycles renders of the saved editable source, normal/albedo-guided OIDN, no generative retouching. `gallery-selfcontained.html` is one self-opening page with every image embedded.
- Editable model: `Editable/Winterlichtplatz-full-editable.blend`, SHA-256 `d101169695309b387d8150ecfcf07bf96741d96dbf0068d1460d1cc2b1181e3f` (548390483 bytes), Blender 4.3.2, all photographs packed, 108 camera presets inside the file.
- Portable model: `Portable/Winterlichtplatz.glb` (263,030,884 bytes) plus `P01..P12.glb` variants, a clean-reimport `.blend`, and a local viewer (`HOW-TO-OPEN.txt` explains the one-line static server).

Framing was solved, not eyeballed: each building exterior camera is picked from a candidate grid inside the square, with nine ray-cast sight lines to the measured frontage and a 13×9 frame-grid near-occluder limit, then the lens is solved against the measured envelope.

**Inspection status (honest):** 16 of these 16 views were opened individually. Recorded fixes: B09 (a market-stall roof filled the frame — camera re-solved, residual near-occluder coverage measured at 1.7 %), V01–V04 (the render-only ground extension magnified the cobble texture — replaced with a plain snow field), and the first twelve fits (camera parked inside a tree canopy — discarded). Recorded and NOT fixed: mirrored lettering on the playground surface (source of the reversed glyphs not identified), twelve near-identical bare trees, plain windowless building backs, some sparse shop interiors. B05 keeps a `FIX_REQUIRED` verdict in the ledger.

This is a working production asset: **not photoreal, not architectural/code certification, and not independently accepted.** People are licensed photographic scans (Digital Reality Lab HSRD-100, CC BY 4.0, 12 poses from 8 source individuals); all brands are original fictional ones.

## Current state — detailed, stocked, camera-corrected working model (not a finished delivery)

Current editable natives (all built, checked and preserved):

- `53c32b17eaebb1c41adec52035bb6f9bf0380070d8f30ffb0a75cd9df9620731` — 551 original grocery products on 15 **measured** shelf surfaces; scan duplicate-face repair with exact unique-geometry/UV proofs; required packed source photos restored.
- `0cd688a59879cab523f119518514b45d8d8a541f558be54be79c51c9731e4a74` → `26f3d577…`/`0cd688…` studio-camera refit: six pair-studio cameras fitted to actual paired actor bounds so both complete silhouettes sit inside frame; presets written back to native + design file.
- Current public native archives (anonymous CRC/every-member/SHA/bytes PASS, storage ledger appended): `…53c32b17eaeb-88b5a01c088b.zip` (614160232 B, SHA `2f165f31…`) and `…97e0004aba8c…`/`26f3d577…` studio-refit ZIP 617875453 B (SHA `052c6b39…`, ledger `fdc0a586…`).
- Verified **current** component/portable packages (r2, `R14-stocked-component-public-packages.json`, ledger `3d6a9731…`): Buildings01–06 353670430 B, Buildings07–12 363305330 B, Public-realm 80027107 B, Portable-town 561579337 B.

Portable pipeline is now genuinely gated rather than "balanced by wish": every one of 25 components and the merged 263030884 B whole GLB passed **clean import**; scan people use measured ~50k-face/2048 px portable LODs (sampled source-to-portable RMS ≤ 0.272 mm, max ≤ 1.64 mm) while the **native keeps the 150k-face meshes and 4k photographs**.

Actual current full-resolution evidence produced and individually opened this session: MARKETGRUEN plan (2560×1440), supermarket interior (MARKTGRUEN brand + dense original product stock visible), storefront H03 (after discovering the previous H03 camera sat *inside* a lamp post — geometry untouched, camera moved and re-checked), and pair-studio D01–D04. Remaining D05/D06/D07/D08 and the 26 plan/cutaway/interior plus 6 hero frames are still queued; the 2 GB runtime kills some full-frame renders (documented, not hidden).

Interactive viewer: real headless Chromium/WebGL test PASSED with the current GLB (33 textures, real draw calls), including building selection, floor cutaway (triangles drop to the selected floor) and restore; browser screenshots retained in `evidence/current-production/viewer-*.png`. The in-app preview cannot load the 263 MB local GLB, so the shipped preview page carries a documented fallback; the browser test proves it works locally.

Digital Reality Lab HSRD-100 (2025), CC BY 4.0 for the human scans — attribution, pinned revision, source archives, changes and limitations retained. Original fictional merchandise/labels and buildings remain project work.

**Still open and not claimed:** remaining full-resolution frames with individual inspect→fix→reinspect, final package/gallery, independent non-owner acceptance. Counts, integrity, or a renderer finishing are not realism acceptance.


# Current editable candidate — measured exterior craft and photographic people

Native `b8ea5ed69e0af9436a6b9fa80be9409ec506ef4a233f10b4e2ddea4c02fd23fb` (548200008bytes) adds144editable facade-detail groups:112measured upper-window surrounds/joinery assemblies, alternating corner quoins/pilasters, cornices, varied shutters, gutters/downpipes, gable vent covers and8real striped canvas canopies. Actual144world-bound/clear-glass checks passed with0pane intrusions. Original preexisting shell/interior/crowd geometry,UVs,poses and material indices were conserved; fresh reopen passed26furnished floors/164rooms/36people/92cameras, no missing images. This is an **unpromoted working candidate**, not final/independent/high-realism acceptance.

The photographic visitors now use own source-UV-correct150k-class editable meshes from original high-detail scans, rather than supplied lower-LODtexture bakes with faults.12poses from8source subject IDs, **not12distinct people or rigged scans**. Original photographed maps4k packed; source-surface error sampled under strict2mmRMS/10mmmaximum limits, source-foot cleanup/placement documented. All12own-source body originals were individually opened; source hair/heel/beanie capture details remain recorded. Original generic rigs remain separate alternatives.

Most recent verified public model before the facade additions: [original-UV photographic town7594archive](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-rebuilt-editable-75945c0b9c4f-4fdecb089faf.zip),692119646bytes/SHA`01661ce24872c0695487218bd089aea0c6a5afed29726c59d22864ee4883ac0e`, anonymousCRC/everymemberPASS; ledger65d03a0f7bb4864f96510478d53987a115a222b5. Current facade candidate backup/visual studies and25component/whole portable tests have separate receipts as they actually finish; no completion inferred.

Actual source5fD01people andH01square overview were opened. H01exposed overly plain facades and motivated this new geometry. Full scene rendering fits the2GB runtime only with declared distant-visitor geometricLOD (sampled<=1full-resolutionpixel, testedmax0.390px), image-map caps and disabled light-tree acceleration. Authoritative native/export and closepeople views keep full geometry; no capsule/image-only substitutes. New b8candidate exterior originals, final92inspect-fix-reinspect, final packages and independent non-owner acceptance remain open. Earlier chronological notes below are historical.

---

# Latest working checkpoint — detailed licensed winter people / not a finished release

The latest preserved complete editable town is native `55340889139dc89ac0ecaa2a6028ecc346ccd9778646d3f1331ade303b551d94`, with the corrected26furnished floors and six native physical-groom instances. [Verified native archive](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-rebuilt-editable-55340889139d-0f7a99f5a06e.zip),307545949bytes, archiveSHA`41be657a8facd43bc2eb554733f2cd9e716324ff42a6b4ef9245a4d0e35563e4`. Exact native/ZIPCRC/member checks passed. Latest25component +175937196-byte whole GLB clean import passed, wholeSHA`fb2f0d3864134d781e8c3e51e5b0ddb432e30a413b4beb5debe28c1fd9e19fad`; these new portable binaries are reproducible but not yet separately published after cache loss. The8c component archives below remain valid unchanged architecture alternatives, not the latest hair source.

**Human detail upgrade now actually built:**12winter-clothed photographic scan poses from8source subject IDs, original photographic UV/materials,4k resampled packed textures, scoped sole-floor cleanup with strict upper-body conservation checks. Static editable meshes, **not12distinct identities and not rigged scans**. Digital Reality Lab HSRD-100, CC BY4.0; source pin, attribution/licence and actual changes in `assets/people-scan-sources/` and per-asset digest receipts. [Verified twelve-native intake archive](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-Licensed-winter-scan-native-intake-e32db400b0a54314.zip),405972813bytes, SHA`d5e1d239d4db5d40a85067fb8315d8857af718a8d072af655c8a0a32d5c6bd9b`; anonymousCRC/everymemberPASS, ledger`962b9fa0a0cd70879bee8a99f431edf963320d19`. Original12generic anatomical rig sources remain separate alternatives. Scans have not yet been substituted into the saved town.

The actual new native studio originals are being individually inspected; photographic clothing folds, knit, footwear and expressions are a significant improvement over the previously opened stylized people, but captured hair edges and a possible heel fragment remain declared. A1million-face alternative was actually rendered/opened and did not automatically resolve scan roughness. See source-bound actual-inspection records, not author previews. No generated-image people/interiors are substituted.

**Still open:** scanned-town integration/ground contact/collisions/lighting checks, fresh native/export checks, the92final-resolution views with individual inspect–fix–reinspect, final package and independent non-owner acceptance. Counts and file integrity do not confer high-realism or final acceptance. Earlier chronological records follow; superseded stage statements below are historical.

---

# Current actual unpromoted production checkpoint

Full editable source `8cf939dc13f9b122270273259bcc2683c02bedd9d1544259b7fd36c1bab7088d` has corrected room/floor placement and26measured wall-overlap repairs. Three exact saved-source eye originals were actually opened: bicycle/workbench, writer shelving, artist reference storage; the sharp wall streaks are gone. Actual25component clean imports plus merged155070748-byte portable town clean import passed; GLB SHA `1602c1d3885b643150676e40ffcb12d4d610eae9e8897de955bb990279a7ae84`. Exact13public editable building/public files were separately reopened read-only and their hashes matched public archive members. These are technical/scoped producer observations, **not final visual or high-realism acceptance**.

| Actual preserved asset | Download |
|---|---|
| Packed editable town study | [Native archive](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-rebuilt-editable-8cf939dc13f9-80be1837147b.zip) |
| Winterlichtplatz-UNPROMOTED-Study-Buildings-01-06 | [Verified immutable ZIP](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-Study-Buildings-01-06-8cf939dc13f9.zip) |
| Winterlichtplatz-UNPROMOTED-Study-Buildings-07-12 | [Verified immutable ZIP](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-Study-Buildings-07-12-8cf939dc13f9.zip) |
| Winterlichtplatz-UNPROMOTED-Study-Public-realm | [Verified immutable ZIP](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-Study-Public-realm-8cf939dc13f9.zip) |
| Winterlichtplatz-UNPROMOTED-Study-Portable-town | [Verified immutable ZIP](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-Study-Portable-town-8cf939dc13f9.zip) |

All listed archives were anonymously downloaded and actually passed CRC/every-member SHA/byte checks. OriginalSVGbranding, licence/provenance notes and component/export/import reports are included. Portable exports are static and use resampled photographic maps/PBR approximations; Blender HDRI/area lights/procedural shaders are not promised to match. Original12rig source package remains separately preserved and unmodified. Experimental new scalp hair is not in these native/portable files.

**Still open:** close-up human/hair realism (old stock hair visibly helmet-like); fresh full-resolution92-view production/individual fix-reinspect loop; independent non-owner acceptance. Frozen R11 remains unchanged, with16historical/public originals and2FIX_REQUIRED; do not count those as current8cfinal views. Counts/licensing/technical integrity are not realism certification. Earlier chronological notes follow.

---

# Winterlichtplatz — editable Christmas town square / R11 producer candidate

**12 buildings · 26 furnished occupied floors · 164 modeled rooms · 36 anatomical CG people / 12 licensed variants.** Central European historic Christmas-market concept with supermarket, bakery, café and other distinct businesses/homes, original fictional business marks, eight market stalls, benches, lamps, trees and playground. Metric conceptual architecture, not code-certified.

## Current source / honest status

R11 packed full-map native `.cache/master/Winterlichtplatz-R11.blend`, SHA256 `7fb9ce64d02030beac15b2adb8df32831e885acfabca51ca26a28a0f2d5a77b1`. Geometry-identical image-budget derivative SHA256 `3706a6b317d7d9100434e42df62484081a192aa2e499de4d7bef6e79e63d6ccf`; shared geometry/UV/material-index/world-pose signature `484aa5d5a9444a267b42b387b28bd1009fded04ab4ad9c67eeb867183d140d5b`. Both ACTUALLY fresh-reopened:164furnished rooms/36people/92cameras/packed maps PASS. These numeric tests do not grant visual acceptance.

Actual R10 interior inspection led to ray-tested discovery of ceiling emitters buried60mm inside upper slabs. R11 corrects actual ceilings, existing physical fixtures/emitters and high interior brand headers together:338 object translations,150 corrected emitter centre rays checked clear. Existing light power/colour/materials and anatomical body/poses preserved. Three actual1024prototype originals separately opened show readable stocked supermarket, bakery and home at native0.35EV without high-exposure compensation.26standard photographic camera exposures measured from actual low-resolution HDR renders and baked into offline presets. All25editable component natives and GLBs plus whole-town GLB have actual reopen/import and byte rehash PASS; four model archives are anonymously CRC/every-member verified. Final92source-bound originals/individual image checks are still being produced; no photographic-quality, perfection or independent acceptance claim.

## Open and edit

Blender4.3.2 / metric metres. Full native has original packed photographic maps, named building/floor/room collections, editable architectural/furnishing geometry and92cameras. Twelve full editable human rigs are separate from36static posed town instances. The people are licensed generic anatomical CG with photographic skins, not unique person scans or animation-certified costumes.

In Blender's Text Editor run embedded `VIEW_TOOLS.py`, then `apply_view('B01_L01_interior')`, `apply_view('B01_L01_plan')`, `apply_view('B01_L01_cutaway')` or `apply_view('H02')` to restore the whole town. This applies saved camera, floor visibility, original scene lighting and per-view standard AgX exposure. No addon, network or private download needed. Full native is intended for a normal desktop with adequate RAM; bounded derivative/scripts are provided for this2GB worker.

Final camera output targets:6heroes at3840×2160;26plans+26cutaways+26interiors+8human/detail views at2560×1440. Cycles with recorded sample counts, AgX, ordinary non-generative OIDN; four-by-four exact camera-border native-pixel hero assembly for memory budget, no image upscaling. Plans add explicitly declared technical labels/scale/orientation from actual saved native camera/room geometry. A render log/hash is not an image inspection; only individually opened originals enter the producer ledger.

## Portable model / limitations

Fresh-import-tested portable GLB, per-building native/GLB, public-realm model and12human variants are separate deliverables. Area lights, HDR world, procedural shader details, glass and colour management are NOT fully portable through coreglTF. Neutral portable proof lights are explicitly reconstructed; no authored native-light parity claim. Portable photographic maps capped512px; originals remain in packed full native. The optional WebGL viewer uses local MIT Three.js. Actual Chromium/SwiftShader loaded the145MBmodel, selected the supermarket floor and reset the town without JS errors; two unique corrected original screenshots were separately opened. Sidebar/title/framing and furniture-truncating global clipping were corrected; semantic cutaway hides upper walls/ceilings without slicing shelves. It is an approximate pale WebGL preview, not native Cycles/photographic acceptance. Exact public GLB3neutral proof originals were also individually opened; see R11-public-glb-proof-*.json.

## Storage, sources, rights and evidence

Bulky natives/GLBs/renders belong in immutable public `dreamer2664/storagecode` Release assets, NOT Git history. Current verified archive URLs/digests are in `evidence/production/R11-public-checkpoint.json` and `R11-additional-public-packages.json`; R10 history remains in its own receipts/releases. Every promoted public archive must be anonymously downloaded, CRC checked and EVERY manifest payload digest verified. Public exact-native reopen and exact-GLB clean import/proof are separate gates. Source draftPR6: https://github.com/dreamer2664/buildinglab/pull/6 .

`assets/ASSET_LICENSES.md`, original vector logos under `assets/branding/`, frozen build reports, explicit inspection/failure history and `HANDOFF.md` are authoritative. Native authoring is original, with recorded CC0 MakeHuman/MPFB-derived assets and Poly Haven photographic assets; Three.js MIT separated from model rights. No generated-image replacement for modeled people or rooms.

**Producer checks are not independent approval.** Final quality/package audit and non-owner acceptance remain open until explicitly evidenced. Previous Casa dei Colori residence project is preserved separately and not overwritten.

## Actual recovery after disposable cache loss

Run `python3 tools/bootstrap_runtime.py --runtime-only`, install any reported OS shared-library dependencies, then `python3 tools/restore_current_delivery.py`. These commands were actually executed after this worker cache was cleared: current native/derivative,12editable rigs,all4model archives and8final images restored with archive/member digests verified;25components rehashed PASS. Remaining historical22render records included14not-yet-backed-up images; these were separated into history and queued for actual rerender, never counted as currently available. From a blank factory Blender scene run `tools/production/restore_packed_source_maps.py` to recover112exact original photographic map byte streams. See `evidence/production/R11-runtime-cache-loss-recovery.json` for current scope/smoke status. Do not assume temporary `.cache` files survive a new session.

## Additional required correction found in actual inspection

The individually opened B02_L02 plan/cutaway visibly duplicate B01_L03 domestic furniture/partition arrangements despite different programme titles. **The requested distinct-interiors criterion is therefore NOT accepted.** Further R11 final rendering was stopped at16completed/individually inspected originals (two marked FIX_REQUIRED), preserving the public14-view checkpoint and all model backups. Actual editable furnishing differentiation and physical-hair studies are underway in separate unpromoted files; the frozen R11 download has NOT silently changed. Final92/high-realism/independent acceptance remain incomplete.


## Further actual floor-by-floor corrective study (not a promoted release)
All26separate first-draft plan originals were individually opened. This caught doorway obstructions introduced by whole-room furniture rotation/new entry-wall cases and a visually duplicated hotel upper floor, despite distinct numeric hashes. That draft is rejected. A second actual editable geometry study now restores safe bed/armchair relationships, scopes sofa/table edits, refits the hotel and enriches staff/atelier functions. New render/reinspection is in progress; public R11 remains unchanged and is not final/high-realism accepted. See current HANDOFF and R12-all-interiors-first-study.json.


## Latest actual unpromoted editable interior study

Packed native SHA `8cf939dc13f9b122270273259bcc2683c02bedd9d1544259b7fd36c1bab7088d` is preserved in [this immutable study archive](https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/Winterlichtplatz-UNPROMOTED-rebuilt-editable-8cf939dc13f9-80be1837147b.zip). Archive 252046841bytes, SHA `89ebf727e565f444dbe741d6c2d595a8275c230bfd95eb070a07fdb23bbf8d50`; anonymous CRC/every-member SHA/size verification actually passed. New home/business fit-outs, real generated-prop placement correction, and measured wall-overlap repair are included. This is **not final delivery or high-realism/independent acceptance**: exact new saved-source regression views and new portable roundtrip are still being executed; experimental hair remains unadopted. Older R11 production stopped after16historical/public originals; missing local final originals after cache reset do not count as newly inspected files.
