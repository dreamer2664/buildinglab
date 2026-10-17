# Winterlichtplatz

Editable original Central European Christmas-square scene:12 surrounding buildings,26 occupied furnished floors/164 rooms,8 market stalls,24 benches,24 lamps,12 bare deciduous trees, a real licensed fir mesh, playground,36 winter-clothed CG people from12 variants and12 original fictional business identities.

**Current status: R10 producer candidate, not final visual or independent acceptance.** The actual full-map native has reopened and passed structural/packing/room-furnishing/ground-contact tests. Final-resolution rendering, individual image checks, portable-export roundtrip and final public delivery checks are still in progress. The earlier A2 study in `PREVIEW.html` is historical, not the current model.

## Native versions
- Full-map `Winterlichtplatz-R10.blend`: packed photographic source maps and all actual geometry, with original licensed hair/clothing; optional procedural hat/scarf studies were rejected and excluded from final outfits and original cafe/branding additions.
- Separately labelled lighter render derivative: identical geometry, UVs, material assignment indices and poses, with resampled photographic maps. Per-frame close-detail map upgrades and memory-only culling/LOD are explicitly recorded; no generated picture replaces architecture, furniture or people.
-12 separate full-map building components and a public-realm component are being exported from the final candidate, not the early blockout.12 separate person natives preserve the anatomical armatures, clothing and authored poses; the assembled town/GLB crowd is static.

The master contains92 camera presets and embedded `VIEW_TOOLS.py`, `VIEW_PRESETS.json`, `READ_ME.txt`. In Blender's Text Editor, run:

```python
exec(bpy.data.texts['VIEW_TOOLS.py'].as_string())
apply_view('B01_L01_cutaway')
# 'B01_L01_plan', 'B01_L01_interior', etc.
# 'H02' restores complete town visibility.
```

Technical plans/cutaways intentionally hide ceilings/high walls; this is reversible visibility, not missing source geometry. People-detail presets use an honestly labelled physical inspection studio; town integration is shown in the exterior views. The native retains its original1000m legacy horizon plus a redundant auxiliary500m plane. Portable GLB omits the auxiliary plane and crops only the legacy horizon solid to a112x100m snow context, preserving UV metre density; the actual64x52m plaza and all architecture/furnishings remain unchanged.

## Reproduction and evidence
`tools/production/` contains anonymous source recovery and digest verification, original inspect-driven modelling corrections/details, native assembly, self-contained view control, bounded rendering, standard OIDN postprocessing, static GLB export/clean reimport and a geometry-preserving glTF component merger. `evidence/production/` records actual results. `design/production-views.json` schedules6 four-K exteriors,26 plans,26 cutaways,26 interiors and8 people details; a schedule is not proof of rendered or inspected images.

Blender4.3.2 is used. Rendering in this2GB runtime requires memory-bounded working copies; additional RAM is recommended for uncullled full-resolution rendering (no minimum-RAM benchmark is claimed). Renderer environments are credential-free. Bulky source/model/render artifacts use verified public storage releases, not Git history.

## Rights and honest limitations
See `assets/ASSET_LICENSES.md` and recovered per-asset URL/hash/author metadata. Project-authored geometry, layout, branding and derivatives are CC0; project code MIT. Poly Haven and used MakeHuman graphical assets are CC0. MPFB build-time code is separately GPL; it is not required to open the packed natives. These are generic CG people, **not twelve commissioned scans of unique real people**. Fictional marks are original, not trademark-clearance promises.

GLB is an engine-neutral static PBR derivative with a512px portable photographic texture budget; Blender area lights, photographic world, procedural detail, glass and colour management do not all translate identically. The full-map native is authoritative for the authored lighting/material appearance. Read the actual export/reimport results before asserting portability gates passed.

Conceptual visual architecture and playground design only: no structural, fire, accessibility, medical-facility, photometric or playground certification, perfection claim, or self-awarded independent acceptance.
