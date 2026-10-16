# Producer visual review — Casa dei Colori

**work in progress. Independent acceptance: PENDING.**

Current native SHA-256: `1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f`
Explicit individually opened current-source originals: **3/29**. These are agent/producer observations, not an independent human-review certificate.

## Real inspect → fix → inspect cycles

Earlier checkpoint narratives are retained as originally logged. Their pending wording is superseded only by the current final observations/defect closures below.

### A / preliminary native diagnostics
- **evidence:** assets/interiors/visual-review.json and assets/exterior/visual-review.json
- **actually opened:** two shell views and eight 1280x720 interior/floor diagnostics
- **issues:** black bedroom camera inside wardrobe; blank-wall cafe; trim caps; bathroom/closet/open-leaf candidates; repeated typical-level views
- **fix:** unobstructed bedroom eye; cafe sightline; butt-jointed reveals; rehinged/stowed leaves; mirrored beds/relocated bedside storage; redistributed saved view subjects
- **reinspection:** B original 2560x1440 L03-detail and 3840x2160 L02-cutaway were individually opened; bedroom obstruction visibly closed. Diagnostic images are not counted as final evidence.

### B / exact-size diagnostic feedback
- **evidence:** evidence/producer/revision-B/ and renders/revision-B/
- **actually opened:** L03-detail, L02-detail and L02-cutaway individually at original requested dimensions
- **issues:** L02 bathroom framing still predominantly wall; technical floor cut showed ceiling discs after ceilings removed; full-building 4K exceeded memory before sampling
- **fix:** saved HOME2C bathroom sightline; actual common-gallery light positions moved outside lift shaft; technical-only ceiling-cap hiding; evaluated-mesh consolidation without decimation preserving names/counts/coordinates; save/reload staging to avoid dependency-graph crash; persistent Main material IDs and palette guards
- **reinspection:** C exact saved native a3221e7cd5c8a44d6505d1546d110aa993e70d8715387d43cb31e54e78540f17: exterior-day and L02-detail opened so far; remaining views still pending.

### B2 / full-size preflight and circulation regression
- **actually opened:** exterior-day, L02-detail, L01-detail, L02-plan individually at original final dimensions
- **evidence:** evidence/producer/revision-B2/
- **issues:** Reception leaf-dominated framing/ergonomics; corridor finish hides structural lift opening; cab/portal alignment; plan label/luminaire overlap
- **fix:** Source shell/interior corrections, actual-geometry ray/level checks, adjusted reception camera and dimensioned label offsets
- **reinspection:** Pending all 29 PNGs from newly rebuilt frozen native; previous source a322... invalidated.

### B3/B4 to frozen C
- **evidence:** evidence/producer/revision-B3/ and revision-B4/
- **actually opened:** Original-size reception images and dimensioned L02 plan, individually
- **issues:** Additional measured reception strips too narrow; black coplanar side slit on primary counter
- **fix:** Metric west/north circulation guard, repositioned reception/staff side and core-door swing; butt-joined worktop
- **reinspection:** Frozen C source 0f8497096094a9c3d24d4fad7f9b95843b613d5a7c5bf4339db3bd0637b55887; first L01-detail actually opened and clear of the prior slit/framing issue. Other 28 final inspections pending as rendering completes.

### D / actual final-image inspection exposes further function and framing
- **actually opened:** 20 original 0f campaign images plus explicit 1280x720 noisy bedroom reframing draft (not final). One original L05-detail failed framing.
- **issues:** Draft revealed wardrobe backside; real component/material-face guards then failed nine north wardrobes; expanded shaft probes failed six ceiling caps; ceiling finishes lacked intended edge overlap. Old limited PASS invalidated.
- **evidence:** evidence/producer/revision-C/ and revision-D/, original immutable superseded 0f public checkpoint
- **fix:** Editable-source wardrobe orientation, saved L05 camera, ceiling edge closure and shaft opening; rebuild/export and wholly regenerate campaign.
- **reinspection:** Pending; no 0f image is counted toward revised-source evidence.

## Defects and actual reinspection

### A-eye-in-wardrobe — major / closed
- **observation:** Actual preliminary L03_DETAIL image was black.
- **fix:** Move saved camera to the unobstructed south-east aisle; revise intersecting furnishings/leaves.
- **reinspection:** Actual B L03-detail opened and showed bed, wardrobe and room rather than black; C exact-source bedroom recheck still to be logged.

### B-bath-framing — major / closed
- **observation:** B L02-detail mostly showed blank wall/weak fixture coverage.
- **fix:** Correct saved HOME2C eye-height camera.
- **reinspection:** C L02-detail opened individually; basin/tap/mirror, WC and shower all legible. Exact current PNG hash in final_inspections.

### B-floating-ceiling-discs — minor / closed
- **fix:** Hide room-lighting mesh caps only in technical modes; keep actual illumination; move real CORE lights outside shaft.
- **reinspection:** Exact frozen-source L02-plan and full-building cutaway individually opened; round room-lighting caps absent in technical modes, actual light-position symbols and native suspended pendants distinguished. Intact lighting retained.

### B-full4K-memory — major / closed
- **observation:** Unbatched full-building 4K failed before sampling.
- **fix:** Two-stage evaluated-mesh consolidation, preserving original geometry and material IDs.
- **reinspection:** Exact final 3840x2160 exterior-day completed and was actually opened; full six-storey geometry and furnishings behind glazing visible.

### batch-material-persistence — major / closed
- **observation:** First saved batched intermediate had no material slots. Prior weak name-comparison checks were insufficient; that intermediate/export was invalidated and never published.
- **fix:** Bind copied meshes to Main materials by name, assert saved slots after reload, require actual named palette on native meshes and source export.
- **reinspection:** Rebuilt native has 22 used materials; full-size exterior-day and L02-detail actually show cream/terracotta/teal/wood/porcelain/metal palettes. Numeric portable PBR fallback comparison being added before final export release.

### B2-lift-floor-plug-and-cab-step — major / closed
- **observation:** Actual common-core finish fills lift void; cab floor 100 mm above landing; sampled open portal obstructed by half-retracted leaves. New negative native test fails on this actual candidate.
- **fix:** Split finish around lift, flush cab/sill, fully retract ground leaves and close upper leaf seams.
- **reinspection:** New saved native: five actual upper-shaft samples have zero horizontal-floor hits; cab and landing tops both 0.04 m within tolerance; all sampled ground portal points clear. Native digest and coordinates in scene-validation.json. Final plans/technical views independently opened as they complete.

### B2-reception-framing-and-layout — major / closed
- **observation:** Actual preflight reception frame dominated by near entrance leaf; staff-chair direction/desk ergonomics poor.
- **fix:** Recompose from south-west; articulated transaction ledge/lower staff top/knee space/monitor stand and correctly directed chair; taped labelled parcels.
- **reinspection:** Exact new-native L01-detail actually opened; desk/mail/parcel geometry and unobstructed composition readable. Actual nominal bounding strips 1.18 m west / 1.08353 m north; no compliance claim.

### B3-reception-bounding-strips — major / closed
- **observation:** Measured prior saved native had only 0.58 m west and 0.58353 m north strips despite zero furnishing/open-leaf overlap candidates. Negative regression preserved.
- **fix:** Shift reception east, tuck staff worktop/chair and swing core door into ample gallery.
- **reinspection:** New native actual strips 1.18/1.08353 m; source full-size L01-detail opened. Not a swept navigation or code certificate.

### B4-coplanar-counter-side — minor / closed
- **observation:** Actual preflight 202d... L01-detail showed a black horizontal side slit at overlapping worktop/front body.
- **fix:** Butt-join lower worktop at rear face of tall front and give a non-coplanar overhang.
- **reinspection:** Actual final 0f849... L01-detail opened; black slit no longer visible.

### C-L05-bedroom-framing — major / closed
- **issue:** Actual final L05-detail opened: predominantly glazing/wall/door and only bed foot; does not adequately demonstrate bedroom furnishing.
- **evidence:** evidence/producer/revision-C/inspection.json
- **fix:** Render-only camera-pose revision from same unchanged saved native; original and revised matrices disclosed. No native/export geometry edit.
- **reinspection:** Actually opened corrected full-resolution L05-detail original, SHA 28ee507c41d6e042ac9a27317ad270eff4c637af06bde66b08a2fc3e4e25da6d, from native 1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f. Clearly visible inward-facing white wardrobe panels/handles and bed/headboard/two pillows/two bedside lamps. All nine actual source component positions and final-batched material-face checks pass, with +0.292m inward panel offset; new saved camera pose recorded in final metadata. Does not grant independent acceptance.

### D-wardrobe-fronts — major / closed
- **issue:** Actual source and batched-native face-position checks fail for nine north-bedroom wardrobes: panels face the south wall rather than the room.
- **evidence:** evidence/producer/revision-D/expected-failed-wardrobe-check.json
- **fix:** Rotate south-wall north-home wardrobes by pi in editable source; strengthened unbatched and batched actual-geometry guards.
- **reinspection:** Actually opened corrected full-resolution L05-detail original, SHA 28ee507c41d6e042ac9a27317ad270eff4c637af06bde66b08a2fc3e4e25da6d, from native 1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f. Clearly visible inward-facing white wardrobe panels/handles and bed/headboard/two pillows/two bedside lamps. All nine actual source component positions and final-batched material-face checks pass, with +0.292m inward panel offset; new saved camera pose recorded in final metadata. Does not grant independent acceptance.

### D-shaft-ceiling-caps — major / open
- **issue:** Stronger actual shaft ceiling rays hit common ceiling finishes on all six levels; earlier floor-only rays did not cover ceilings.
- **evidence:** evidence/producer/revision-D/expected-failed-final-native-check.json
- **fix:** Split common-core ceilings around actual lift shaft and retain explicit ceiling ray guard.
- **reinspection:** Pending positive actual-source geometry and technical images.

### D-ceiling-finish-edges — minor / open
- **issue:** Isolated-floor interior views expose small finish-to-wall seams.
- **fix:** 30mm ceiling finish overlap into enclosing wall faces; actual bounds/corner-ray guards.
- **reinspection:** Pending rebuilt source and actual interior originals.

## Individually opened final images

### renders/final/L05-detail.png
- PNG SHA-256: `28ee507c41d6e042ac9a27317ad270eff4c637af06bde66b08a2fc3e4e25da6d`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T15:48:21.986876+00:00.
- Observation: Opened corrected 2560x1440 original: bed, green upholstered headboard, two pillows, terracotta runner, both bedside drawers/lamps and two actual inward-facing wardrobe doors with bronze handles are clearly visible. Saved northeast aisle composition replaces the failed wall/window/bedfoot view. Wardrobe door face visible rather than its former blank back; actual native regressions additionally confirm +0.292m inward panel/body offsets in all nine corrected wardrobes. No known major issue in this view; close, deliberately cropped photographic framing, not an entire-room plan.
- Known critical/major in this view: 0.

### renders/final/L02-interior.png
- PNG SHA-256: `795f57bb8d24bc71a2c7674a3280f9da3fc42ef60e7f13d8c27764e99b874e51`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T15:53:52.250433+00:00.
- Observation: Opened corrected original at 2560x1440: Home2A living/kitchen shows upholstered sofa and two cushions, set four-chair dining table, two framed glazed openings, sink/tap, induction/oven/hood, dishwasher, handled cupboards and fridge, plus open circulation doorway. The previous bright isolated ceiling corner/edge slit is now closed by real finish overlap; continuous shaded wall/ceiling join is visible. Some low-sample softness and local fridge-wall shading remain a rendering limitation, not missing geometry. No known major issue in this composition.
- Known critical/major in this view: 0.

### renders/final/L06-detail.png
- PNG SHA-256: `9ce863ae07ddcfdf0c24601102b6a331271edc22b18c88e795124e62666d8fd4`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T15:59:06.688420+00:00.
- Observation: Opened actual 2560x1440 Penthouse6A living original: large dining table/settings and upholstered chairs in foreground, sofa/two cushions and coffee table/rug, real framed balcony glazing/rails, complete kitchen/fridge at rear and an open entry leaf. Differently arranged long living room and usable centre aisle are legible, not an empty top floor. Continuous enclosed ceiling and two luminaires; mild low-sample softness and stylised planting are disclosed visual limitations. No known major issue in this view.
- Known critical/major in this view: 0.

## Boundaries

Mechanical render success, these producer records and mechanical validators are not non-owner acceptance. No self-review/vote has been cast. Engineering, local code, swept navigation, accessibility/fire/lift/structure/MEP approval are outside this conceptual visual model. Historical diagnostics and negative regressions are deliberately separate from the 29 final PNGs. Publication/upload/redownload/member verification must be recorded in the separate release receipt.
