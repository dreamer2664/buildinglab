# BLDG-3 / furnished native candidate

Original component-modelled furnishings for all 14 homes, every public/service space, the common galleries and L06 winter garden. This is the actual Blender scene, not generated imagery. Mesh families include modular kitchens with hollow sinks, taps, induction rings, oven controls, articulated refrigerators, dishwashers and extraction; upholstery/bed components; wardrobes; basins/toilets/glazed showers; café tables, espresso counter/prep; bicycle frames/spokes/racks; waste bins; plant cylinders/headers/exchangers/panels; mail/parcel lockers; books, original geometric art and planted seating. Each usable room has a practical luminaire/light, not one global point lamp.

Three housing types per typical level: two differently handed north single-bedroom homes and a larger south two-bedroom home. The dimensioned programme varies widths/depths by level. North B beds now face the opposite way from A; alternate south bedrooms are mirrored. Two L06 penthouses include a larger south living room with additional seating. The native saved eye-level cameras cover café, reception/mail, distinct living/kitchen layouts, an actual bathroom, multiple bedrooms, winter garden and penthouse living. No empty floors, proxy furniture or linked external assets are intentionally used.

## Reproduce (official Blender 4.3.2)

```sh
blender -b --python-exit-code 1 --python assets/exterior/build_shell.py
blender -b scene/shell.blend --python-exit-code 1 --python assets/interiors/build_interiors.py
blender -b scene/interiors.blend --python-exit-code 1 --python tools/validate_interiors.py
blender -b scene/interiors.blend --python-exit-code 1 --python assets/interiors/audit_clearances.py
```

`validation.json` is an actual scene inventory/boundary and eye-camera obstruction check. `clearance-audit.json` checks conservative native open-door-leaf/component bounding-box overlap candidates. Neither is a building-code, swept-door-arc, accessibility or complete visual-quality certificate.

## Real inspection and consequential changes

Eight 1280×720 rendered diagnostic PNGs were individually opened: six level heroes, L02 axon and L03 bedroom. These are preliminary diagnostics, **not** the charter-size final package. They revealed repeated hero framing, a blank café wall, coplanar reveal/jamb cap artefacts and an entirely black wardrobe-obstructed bedroom view. The shell/furnishing/camera sources were revised. Further actual clearance candidates exposed artwork across doorways and bedside tables at open leaves; the sources were corrected and the conservative audit now reports zero candidates. North-entry long bathrooms and storage closets were rearranged away from their door landing; door leaves now open into destination rooms and shallow-hall entry doors fold back.

All corrected near/final-resolution images and independent non-owner acceptance remain separate gates. `visual-review.json` records diagnostic observations honestly; final producer evidence lives in the assembly card's `evidence/producer/` subtree. Rights: original model/materials/strokes CC0 1.0; original Python scripts MIT, without warranty. Native scene has no font or image texture dependency. Portable export retains PBR fallbacks rather than pretending procedural wood/bump nodes are portable textures.
