# Producer visual review — Casa dei Colori

**work in progress. Independent acceptance: PENDING.**

Current native SHA-256: `0f8497096094a9c3d24d4fad7f9b95843b613d5a7c5bf4339db3bd0637b55887`
Explicit individually opened current-source originals: **1/29**. These are agent/producer observations, not an independent human-review certificate.

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

## Individually opened final images

### renders/final/exterior-day.png
- PNG SHA-256: `4cf634a599282cfb7216502952e6cd3e8f0cdcb94cc5038c310254c2d71b2499`
- Original dimensions: 3840 × 2160; opened individually: true; logged 2026-10-16T14:06:06.360254+00:00.
- Observation: Opened regenerated original 3840x2160 after runtime recovery, not inferred from prior inspection. Six occupied facade rows, real framed glazing/reveals, projected balcony slabs/guards, coloured trim, roof parapet/plant/overrun and furnished rooms behind glazing are visible. Entrance canopy, steps/ramp rails, service grilles, paving/benches and secondary trees read correctly. Primary building and roof are not clipped; deliberate secondary site-edge cropping only. No large missing facade patch or empty upper floor is apparent.
- Known critical/major in this view: 0.

## Boundaries

Mechanical render success, these producer records and mechanical validators are not non-owner acceptance. No self-review/vote has been cast. Engineering, local code, swept navigation, accessibility/fire/lift/structure/MEP approval are outside this conceptual visual model. Historical diagnostics and negative regressions are deliberately separate from the 29 final PNGs. Publication/upload/redownload/member verification must be recorded in the separate release receipt.
