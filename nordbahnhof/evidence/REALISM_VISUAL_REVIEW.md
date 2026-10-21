# NORDBAHNHOF — actual realism revision review

## Status

Iterative proofs have been opened and reviewed. All six current native JPEGs have now been opened and visually reviewed individually after rendering. This document does not certify the full station commission.

## Failures found by looking at the rendered images

1. **Inappropriate environment colour.** The first 768-pixel Cycles proof had orange / magenta roof reflections. The photographed `winter_evening` HDRI itself was opened and showed pink architectural illumination and orange night sky. It was rejected for this scene and replaced by `kloofendal_overcast_puresky`. Later arrival proofs were opened and the cast was gone.
2. **Bulging panes and panels.** Coach and cab glass looked like crumpled reflective foil. Diagnostic renders with the glass bump disconnected, and a raw normal-pass image, showed that geometry shading rather than merely roughness was involved. Checking the actual mesh flags found authored-flat window boxes had become smooth. Blender 4.3's `Mesh.set_sharp_from_angle` changes polygon smooth flags. The material pass now preserves the original flags and keeps glazing / large caps flat; the redundant solidify shell is no longer applied to already closed rolling-stock windows. The revised 1024-pixel coach/electric/arrival images were opened.
3. **Tubular railway tyres.** The previous tyres had circular torus cross-sections. They were replaced in the generator by a revolved tread/flange profile with a slight tread taper. This is geometric improvement, not operational clearance certification.
4. **Wrong material on functioning metal.** The first assembled native arrival image exposed a repeating raised-diamond appearance on buffer faces that small proofs did not make obvious. The actual `metal_plate` diffuse map was opened and confirmed to be tread/checker plate. That image was rejected. All exposed metal now uses authored directional microsurface/roughness and restrained anisotropy rather than that scanned pattern. The other diffuse-map assets were also opened; a peeling-green floor scan was rejected for unpainted limestone/coping and replaced by a warm neutral mineral surface. Gravel was made less yellow and less saturated. A new 1280-pixel / 48-sample proof of this corrected source was opened and the buffer pattern / painted-stone problem was absent.
5. **EXR channel layout.** The first native assembly was corrupted despite valid individual tiles. The final EXR writer had been handed non-contiguous interleaved NumPy channel views. Explicit contiguous channel copies fixed the problem. The corrected assembly was opened before the later material correction; the damaged image was not accepted or packaged.
6. **Construction refinements.** The deflector sheet was reduced to 3.5 mm and its fastener placement adjusted. Drain-bar height was corrected to the slab surface. The flange profile was refined relative to the nominal gauge. These are reviewed modelling changes, not a substitute for a full engineering interference check.

## Current source evidence

See `REALISM_SCENE_AUDIT.json` for the hash and actual loaded-source inventory. The audit is captured before render-only LOD / texture downsampling. It records six rakes, 34 vehicle IDs, six photographic scan objects and 19 packed image assets. It is an inventory, not fifteen passed validators.

The full-resolution batch uses 2560 × 1440 native pixels, 128 samples, raw HDR border tiles with 32-pixel overlap, external Intel OIDN and one final Blender AgX output transform. No generated-image substitution, resizing to pretend higher resolution, or capped acceptance statistics is used.

## Final native images — inspection log

All six final JPEGs were opened via the image viewer at their native 2560 × 1440 output resolution. Each per-image JSON records the actual inspection timestamp and notes; the source hash is recorded in every tile metadata record.

1. Arrival after rain — checked assembly, neutral light, machined buffer faces, wet stone, hardware, humans and steam. No visible quadrant seam or checker-plate contamination.
2. Oil, steel and spokes — checked actual tread/flange profile, rod boss, oil nipple, paint losses, coping and warning line. Mechanisms remain simplified/static.
3. Winter travellers — checked photographed clothing folds/silhouettes, handles/straps/labels, cab glazing, boiler clamps and metal treatment. Intentionally cropped candid framing; modern subjects remain modern.
4. Glass, iron and distance — checked broad roof/platform framing, bench placement, wet slab reflections, ballast and absence of floating labels from omitted rakes. Large-scale architecture remains stylised and incomplete.
5. Coach at platform — checked livery roughness, flat window faces, reflections, trim, lettering, damp floor and lamp reflection. The documented glass/shadow approximation remains.
6. Electric and contact wire — checked electric livery/lettering, glazing, trim and pantograph silhouette/contact-wire context. No operational certification is implied.

Native-pixel (unresized) crops were also opened for all six final images, including buffer faces/hoses, the wheel/rod region across the central tile join, winter clothing/luggage, bench/floor, coach glass/trim and the pantograph. No visible centre-tile discontinuity or export corruption was found in these current outputs. The close crops also make clear that some fabrication, fittings and furniture remain simplified CG geometry rather than fully resolved photoreal objects. No rejected earlier native image belongs to this delivery. This is a realism revision, not a claim of indistinguishable-from-photography quality or completion of the entire commission.

## Limits retained

The saved scene is full and unculled, while camera renders isolate the hero rake and omit closed interior fittings to fit RAM. The mechanisms are static; the rolling stock is historically inspired, not an exact certified replica. Six modern scanned people do not satisfy the original period-population or identity programme. The full room/furnishing/population/material/validator/310-view commission remains incomplete. No numerical score or release upload converts those open requirements into completed work.
