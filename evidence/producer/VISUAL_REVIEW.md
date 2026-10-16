# Producer visual review — Casa dei Colori

**work in progress. Independent acceptance: PENDING.**

Current native SHA-256: `1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f`
Explicit individually opened current-source originals: **12/29**. These are agent/producer observations, not an independent human-review certificate.

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

### D-shaft-ceiling-caps — major / closed
- **issue:** Stronger actual shaft ceiling rays hit common ceiling finishes on all six levels; earlier floor-only rays did not cover ceilings.
- **evidence:** evidence/producer/revision-D/expected-failed-final-native-check.json
- **fix:** Split common-core ceilings around actual lift shaft and retain explicit ceiling ray guard.
- **reinspection:** Saved corrected native1b7150d6 actual shaft-ceiling rays return zero hits on all six levels; previous0f rays genuinely hit six caps. Split ceiling geometry and all101 finish corner probes pass. Opened structural/core original c6cd4a95d45b525815b28005e074dc4906cd0a9d968fe7651fc305009d9bf1e0 showing all6 slab openings/portals and both connected stair routes. This ceiling-hidden image is context, not the sole proof of finish-ceiling clearance. Native/GLB hashes unchanged and public downloaded native reopened/validated/test-rendered.

### D-ceiling-finish-edges — minor / open
- **issue:** Isolated-floor interior views expose small finish-to-wall seams.
- **fix:** 30mm ceiling finish overlap into enclosing wall faces; actual bounds/corner-ray guards.
- **reinspection:** Pending rebuilt source and actual interior originals.

### E-public-plan-names — major / closed
- **issue:** Actually opened full-size L01 plan uses generic STORE/BATH rather than bicycle/parcel/cleaner/public-WC programme names.
- **evidence:** evidence/producer/revision-E/L01-plan.png and SHA-bound inspection.json
- **fix:** Use original programme room names for public storage/bathroom spaces in disclosed overlays; native geometry/camera unchanged. Public old PNG remains immutable; corrected PNG will have a digest-suffixed public asset name.
- **reinspection:** Actually regenerated and individually reopened corrected 2560x1440 plan, SHA e282d0fb7dd558f581cf970d51a4be84816c388fe79e85c24a6b478f287712dc from unchanged native 1b7150d6ce4536d19058cc1088a2ac063c495c41925c65d1f74c28fe1c773f0f. All four explicit programme names read clearly; original failed plan/inspection/public asset remain in revision-E. No scene geometry, saved camera or room boundary was painted/changed.

### F-top-plan-incoming-stairs — major / closed
- **issue:** Actual L06 top-down plan hides saved incoming L05 stair meshes with the lower-level collection; top stair shafts misleadingly read as empty. Native continuity exists and guards pass.
- **fix:** L06 plan-only visibility includes actual L05 stair/flight/rail/landing meshes from saved native, hiding all other lower-level objects. No geometry, saved camera, lens or native switch script is changed; this explicit render visibility convention is recorded in metadata/reproduction helper.
- **reinspection:** Actual corrected original opened individually: a1af5e3eb4e29c4a9f0afde0d5dbd4da604c12924cfe34d7f8688882da5c06d9. Both descending flights now visible. Metadata records plan-only visibility of actual saved L05 stair meshes; native SHA and saved camera pose unchanged. Original failed plan retained in revision-F.
- **evidence:** evidence/producer/revision-F/ actual original, metadata, failed inspection and immutable public asset URL

### G-technical-overview-framing — major / closed
- **issue:** Actually opened technical frame clips upper column ends/ground edge in steep technical camera.
- **fix:** Choose already saved CAM_FULL_CUTAWAY for structural overview, keeping its exact saved pose and same native SHA. No runtime camera transform override or model change.
- **reinspection:** Actually reopened corrected original c6cd4a95d45b525815b28005e074dc4906cd0a9d968fe7651fc305009d9bf1e0; full six plates, column ends/base and both stair stacks visible using exact already saved CAM_FULL_CUTAWAY pose; no native edit or runtime camera transform.
- **evidence:** evidence/producer/revision-G/

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

### renders/final/exterior-day.png
- PNG SHA-256: `cef96bd8e36173b95fc4e78121e4008e35470a1e7dc3d53361fcc27d5476abb9`
- Original dimensions: 3840 × 2160; opened individually: true; logged 2026-10-16T16:06:01.919801+00:00.
- Observation: Opened corrected-source 3840x2160 original: six occupied storeys read clearly above the entrance/plaza; cream masonry, terracotta sill/band/reveal depth, teal balcony guards, actual glazing with furnishings behind it, roof parapet/coping and plant are visible. Entrance canopy, ramp/handrails, benches and planted urban edge establish scale. No missing facade panel or known major intersection visible. Vegetation/context are deliberately stylised and secondary; this is conceptual architectural rendering, not a photorealism or code claim.
- Known critical/major in this view: 0.

### renders/final/exterior-dusk.png
- PNG SHA-256: `33ff7361423e7353958d7396e3c978671071de150cf06017836905129f2cc6bf`
- Original dimensions: 3840 × 2160; opened individually: true; logged 2026-10-16T16:12:12.991406+00:00.
- Observation: Opened corrected-source 3840x2160 dusk original: all six occupied storeys and roof edge fit the frame; warm interior lighting reveals beds, seating, cabinetry and depth behind actual glazing, not facade-painted rooms. Different corner angle from the day hero makes balcony depth, teal rails, terracotta bands/reveals and entrance/ramp readable. Darker plaza/context remains secondary; no known major facade gap or camera clipping. Conceptual/stylised setting, not a night-lighting engineering certificate.
- Known critical/major in this view: 0.

### renders/final/L03-plan.png
- PNG SHA-256: `680283f5f235894c561974ea4eaacb86dc396750a383d1bc49461cf74642e864`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T16:17:01.200732+00:00.
- Observation: Opened actual 2560x1440 L03 plan: distinct north 3A/3B homes with opposing bed heads and living/kitchen/dining/bath/entry arrangements, south two-bedroom 3C with storage/long bath, and furnished shared reading room are legible. Both separated stairs, open lift-shaft plan, risers and common-core doors/benches connect to unit entries. Corrected north wardrobes are on south bedroom walls; actual orientation regression covers their fronts. Labels, room/footprint dimensions, FFL+7.00, door-swing arcs, light symbols, scale bar and north marker are readable; no known major presentation omission.
- Known critical/major in this view: 0.

### renders/final/L01-plan.png
- PNG SHA-256: `e282d0fb7dd558f581cf970d51a4be84816c388fe79e85c24a6b478f287712dc`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T16:18:22.558549+00:00.
- Observation: Actually reopened regenerated 2560x1440 L01 plan: public Bicycle / storage, Parcel / community store, Cleaner / supplies and Accessible public WC now have explicit programme names rather than generic STORE/BATH. Cafe/public passage/separate prep, reception/mail, vestibule, neighbourhood room, plant and waste/service are legible, with actual furniture/fixtures, core/lift/two exit stairs and door arcs. FFL0,26x20m footprint, room dimensions, metric scale, north and native light symbols remain readable. Accessibility wording is design intent, not certification; no known major presentation issue. Same saved native/camera, only disclosed overlay text corrected.
- Known critical/major in this view: 0.

### renders/final/L04-plan.png
- PNG SHA-256: `b0de2f0237686d259730a01b3bfe421c9cb88aa678510519a424e0715b85dcc2`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T16:19:49.737371+00:00.
- Observation: Opened actual 2560x1440 L04 plan: furnished 4A/4B single-bedroom homes use 6.60m-wide living rooms and deeper4.20x3.97m bedrooms/different bath depths; 4C has two opposite-handed bedrooms, complete kitchen/living, bath and storage. Shared reading/dining room, two stairs, lift/risers, core benches/doors and clear unit entries are visible. FFL+10.20, dimensions, native light symbols, door arcs, north and scale are readable. Technical low-wall/top-down convention is explicit; no known major missing function or label.
- Known critical/major in this view: 0.

### renders/final/L05-plan.png
- PNG SHA-256: `021d72a17f7bb547fd187c5966371e50fc2aa5e6d634e97f4fa242fc8b4b4248`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T16:21:55.895347+00:00.
- Observation: Opened original 2560x1440 L05 plan and a native-pixel crop of the south bedrooms/store/bath: 5A/5B one-bedroom layouts and 5C two-bedroom home, kitchen/dining/seating, wardrobes, bath fixtures, reading room and common circulation are present. Native-pixel crop confirms narrow store and bath labels/dimensions stay readable and bedroom door/bed/storage positions are legible. FFL+13.40,26x20m dimensions, light symbols, door arcs, north and scale appear correctly. No known major presentation defect; conservative geometry guards, not this plan alone, assess component/door clearances.
- Known critical/major in this view: 0.

### renders/final/L02-plan.png
- PNG SHA-256: `a2f949ab63b2b0f241768391950646dfb91c7fc9fb48b10c60ead83fe3722d77`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T17:15:36.994521+00:00.
- Observation: Opened corrected-source 2560x1440 L02 furnished plan: 2A/2B living/dining/kitchen, opposite-handed bedrooms, baths/entries, south two-bedroom2C with bath/store and shared reading room are clear. Two separated stairs, lift/risers, common core and actual light symbols/door arcs are present; FFL+3.80,26x20m extents, room dimensions, scale and north are legible. Wardrobe corrections are in the same saved native; no known major presentation omission.
- Known critical/major in this view: 0.

### renders/final/L06-plan.png
- PNG SHA-256: `a1af5e3eb4e29c4a9f0afde0d5dbd4da604c12924cfe34d7f8688882da5c06d9`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T17:16:47.469693+00:00.
- Observation: Actually reopened corrected 2560x1440 top-floor plan: both stair wells now show the real incoming L05 flights/rails beneath L06 landings, rather than empty grey voids. This is explicit plan-only visibility of existing saved native meshes; no model/camera transform or drawn substitute stairs. Penthouse6A two bedrooms/large living/bath/store,6B living/bed/bath, and planted shared winter garden with seating/dining/books are legible. FFL+16.60, dimensions, light symbols/door arcs/north/scale readable. No known major presentation issue.
- Known critical/major in this view: 0.

### renders/final/technical-structure-core.png
- PNG SHA-256: `c6cd4a95d45b525815b28005e074dc4906cd0a9d968fe7651fc305009d9bf1e0`
- Original dimensions: 2560 × 1440; opened individually: true; logged 2026-10-16T17:18:45.603152+00:00.
- Observation: Actually opened corrected 2560x1440 structure/core original using already saved full-cutaway camera at its unchanged native pose. All six plates, full column ends and ground edge now fit; both five-connection stair stacks show real treads/rails/landings, central lift portals/guides and open slab shafts are visible. Tight but complete framing replaces clipped steep view. Small exposed native overhead lighting/guide parts remain a schematic visibility convention, not missing architecture. Physical finish-ceiling shaft clearance is established by the six actual saved-native ray checks, not by this ceiling-hidden picture. No known major presentation issue; no structural/code approval.
- Known critical/major in this view: 0.

## Boundaries

Mechanical render success, these producer records and mechanical validators are not non-owner acceptance. No self-review/vote has been cast. Engineering, local code, swept navigation, accessibility/fire/lift/structure/MEP approval are outside this conceptual visual model. Historical diagnostics and negative regressions are deliberately separate from the 29 final PNGs. Publication/upload/redownload/member verification must be recorded in the separate release receipt.
