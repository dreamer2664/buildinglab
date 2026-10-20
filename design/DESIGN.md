# Casa dei Colori — dimensioned design / BLDG-1

**Stage:** original schematic blockout; not a furnished building or final release.

## Geometry and circulation

- Metric coordinates: X east, Y north, Z up. Main entrance faces south.
- Footprint **26 × 20 m**; 520 m² gross plate; six occupied floors, L01–L06.
- Ground storey 3.80 m; five upper storeys 3.20 m. FFLs: 0, 3.80, 7.00, 10.20, 13.40, 16.60 m. Roof bearing 19.80 m, proposed roof slab top 20.02 m, parapet 21.12 m. Roof/parapet are design dimensions, NOT present in the cutaway blockout.
- Slabs 0.22 m. Intended envelope 0.30 m and nominal internal walls 0.20 m (Y partition gaps stretch to about 0.212 m). Cutaway blockout wall strips are 0.20 m per room edge, unioned; exterior full-thickness build belongs to BLDG-2.
- Two independent 4.40 × 5.60 m stair cores at east and west ends; 1.35 m flight widths, 0.28 m treads, approximately 1.20 m landings. Ground: 22 risers at 0.1727 m; upper: 20 risers at 0.16 m. Top occupied floor terminates circulation; no roof access proposed.
- Central corridor has lift and riser exclusion rectangles. Narrowest straight path in front of lift is about 2.55 m before door detailing. All doors in the schedule have measured adjacency and a room-graph route.
- L01: entrance → vestibule → reception → core → either stair → separate east/west exterior exits. Café uses a public passage separate from prep. Waste has a separate eastern external access.
- RC slab/column concept with approximately 6.4 m perimeter bays and stair/lift shear cores. Column sizing, beams, transfer/slab engineering and fire strategy are NOT designed or approved. No code-compliance claim.

## Programme and homes

|Level|FFL m|Storey m|Homes|Rooms/zones|
|---|---:|---:|---:|---:|
|L01|0.00|3.80|0|18|
|L02|3.80|3.20|3|21|
|L03|7.00|3.20|3|21|
|L04|10.20|3.20|3|21|
|L05|13.40|3.20|3|21|
|L06|16.60|3.20|2|17|

|Home|Schematic boundary area m²|Layout|
|---|---:|---|
|2A|86.7|north_west|
|2B|86.7|north_east|
|2C|132.1|south_family|
|3A|86.7|north_west|
|3B|86.7|north_east|
|3C|132.1|south_family|
|4A|86.7|north_west|
|4B|86.7|north_east|
|4C|132.1|south_family|
|5A|86.7|north_west|
|5B|86.7|north_east|
|5C|132.1|south_family|
|6A|174.8|penthouse_south|
|6B|104.6|penthouse_north|

Boundary areas are not surveyed net saleable areas. Four levels contain two north one-bedroom homes and one south two-bedroom family home, plus a shared reading room. The two L06 homes are larger than their corresponding lower-floor types; a separate north-west winter garden remains common. North bay/hall/wet-room dimensions vary by floor; south layouts currently share a repeatable structural template. More unit-specific furnishing/layout variation remains a BLDG-3 obligation, not an accomplished fact.

## Material / façade direction

Warm limestone/cream envelope, terracotta reveals and ground plinth, deep teal metalwork, olive planting, warm timber doors and joinery; restrained glass/bronze accents. The blockout room colours are zoning aids, not final finishes. Continuous window opportunities on north/south elevations serve all living rooms and bedrooms; north wet rooms use mechanical extract risers. Ground café receives south/west glazing; winter garden north/west glazing. Window geometry, reveals, mullions, façade articulation, ceilings and full-height restoration are not yet built.

## Actual blockout contents and limitations

- `scene/blockout.blend`: native meshes, six switchable level collections, 1.05 m cutaway partitions, door openings/thresholds, colored floor zones, dimensioned kitchen planning zones, two modeled stair flights per storey, intermediate/bottom landings and schematic rails; lift floor-stop markers; named orthographic per-level cameras and full-stack camera; floor lighting positions.
- It contains **no completed furnishings**, no completed lift cab/doors, no finished plant equipment, no sanitary fixtures, no roof/envelope restore toggle and no GLB. Kitchen plates are explicitly planning zones, not cabinets.
- Individual isolated upper-floor images omit the preceding collection’s incoming stair flight; the full-stack scene retains connected flights. Rail continuity around openings and landing junction detailing remain unresolved; do not use this as a safe walkable release.
- The full-stack view proves six levels but upper slabs obscure lower rooms; it is not the required final full-building furnished cutaway.
- Final 29-view 4K/1440p evidence, clean GLB re-import, export tests and independent review are outstanding. Schematic images are only 1600 × 1200; vector plan sheets are 1600 × 1240.

## Reproduce

Requires Blender 4.3.2 (Debian build), Python 3.11+, and optional CairoSVG 2.9.1 for raster plan previews. Scripts use no add-ons.

```sh
python3 design/build_design.py
blender -b -t 8 --python-exit-code 1 --python design/build_blockout.py
python3 tools/validate_design.py --geometry
python3 design/test_design_validator.py
BLDG_RENDER_PASS=B blender -b scene/blockout.blend -t 8 --python-exit-code 1 --python design/render_blockout.py
```

Cycles CPU, 32 samples, denoising OFF, AgX, orthographic cameras, PNG RGBA defaults, 1600 × 1200 at 100%. This Blender build lacks OpenImageDenoise: the first render attempt failed; disabling it was necessary. No GPU or final render-performance guarantee. Always include `--python-exit-code 1`: Blender can otherwise exit 0 after a Python exception.
