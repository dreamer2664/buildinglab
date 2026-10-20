# NORDBAHNHOF — after the rain

## Open this first

- **`source/NORDBAHNHOF_REALISM.blend`** — the updated, fully packed Blender 4.3.2 scene. It contains all six rakes / 34 vehicles, the station and the six photographic human scans. Render-only omissions are not saved into this file.
- **`NORDBAHNHOF-realism-gallery.html`** — a self-contained image gallery; no Blender, Internet connection or external fonts required.
- **`renders/realism/native/`** — native 2560 × 1440 JPEGs, actual render records and a consolidated manifest. The JPEGs are the rendered scene, not generative-image replacements.
- **`evidence/REALISM_SCENE_AUDIT.json`** — inventory of the loaded, unculled source, including packed-image checks and source hash.

This is a substantive realism revision of the previous train update, **not a claim that the entire original station commission is complete or that every view is indistinguishable from a photograph**.

## What was rebuilt

### Surfaces and construction

Physically scaled CC0 scanned colour, roughness and normal maps replace the uniform shader treatment across masonry, ballast, platforms and painted / bare metal. The foreground platform has 720 individually modelled slabs with restrained millimetre-scale height and alignment differences, recessed mortar, worn warning paint, separate coping blocks and occasional chipped corners. Dampness changes reflectance and colour in patches rather than coating everything in a uniform mirror finish.

Foreground ballast includes individual angular stones, not only a flat colour plane. There are local oil deposits, seated drain grates, sparse curled paper, weathered timber, bolted column access plates, and luggage with straps, lid seams, handles, corner guards and labels. Small edge paint losses are confined to exposed metalwork rather than distributed indiscriminately over functioning polished surfaces.

### Rolling stock

The previous circular-tube wheel tyres have been replaced by revolved steel profiles with a shallow conical tread and inner flange. The locomotive gains smoke deflectors and mounting stays, clamp hardware, front-door fittings, oil nipples, bored rod bosses and retaining nuts, hanging brake hoses, small step treads, headlamps and low cylinder-drain steam. Six rakes / 34 vehicles remain in the source. This is original historically inspired stock, not a certified exact BR01 replica.

### Glass, shading and light

An iterative render check exposed a Blender 4.3 shading issue: `Mesh.set_sharp_from_angle` also enables smooth shading on polygons. That had unintentionally rounded otherwise flat panes and box panels. The revised material pass preserves the authored flat/smooth face flags, then keeps cylinder caps and glass faces flat as appropriate. Tangent-space box-projected normal maps are not allowed to corrugate machined steel.

Roof panes receive actual 4 mm thickness. The rolling-stock window meshes are already closed thin boxes, so they are not given a second solidify shell. Glass has restrained roughness and microvariation, with a transparent shadow branch for tractable light transport. It is not a spectral glass simulation.

The first photographed environment tested was `winter_evening`, but actual proofs showed inappropriate orange / magenta architectural lighting reflecting in the roof. It was rejected. The final scene uses the neutral `kloofendal_overcast_puresky` photographed sky, a soft low sun and restrained supplementary sky bounce. Both downloaded HDRIs remain in the provenance record; only the neutral sky is used by the final scene.

Steam is an actual noise-modulated volume with a fading boundary, not a painted image or billboard. The lighting is intentionally restrained rather than concealing geometry behind shallow depth of field, aggressive bloom or opaque fog.

## Rendering method and honest limitations

The final JPEGs are rendered at **2560 × 1440, 128 samples per pixel**, as four overlapping raw HDR border tiles per view. Tiles overlap by 32 pixels. Intel Open Image Denoise 2.5.1 runs in a separate CPU process on HDR colour, albedo and normal passes, with a 256 MB working-memory budget. The denoised tiles are cropped and assembled **in linear light without resizing**; Blender applies AgX, Medium High Contrast, exposure +0.1 once to the completed image.

This workstation has about 2 GB of RAM. Full scene rendering repeatedly exceeded that budget during scene/BVH or environment-importance-map allocation. The delivered source retains the complete scene, but the published camera renders use an explicit **render-only hero-rake LOD**: TR01 for views 1–5, TR04 for view 6; other rakes and closed interior fittings are omitted from those render processes. Structural and platform shadow casters remain. Human textures are reduced to 1024 pixels **in render memory only**; the source retains the original packed 2048-pixel textures. These are intentional memory compromises, not claims of full-station validation.

The scene is static. No operational linkage, suspension, brake, clearance or T3 mechanism certification is implied. Six modern scanned people are not a period population of 400, sixty distinct identities or twenty authored heroes. The full 240-room furnishing, population, material, validator/negative-test and 310-view programme remains incomplete. Historical acceptance files from rejected iterations are deliberately not used as evidence for this revision.

The photographs used for visual reference are not included as textures or substituted for rendered geometry. No AI-generated image is used in the scene renders.

## Rebuilding the revision

The archive includes the earlier packed station base, the revised rolling-stock generator and the realism layer. From the **`nordbahnhof` directory**, with Blender 4.3.2 on the path:

```sh
blender -b -t 2 source/NORDBAHNHOF_REBUILD.blend --python build/rebuild_trains.py
blender -b -t 2 source/NORDBAHNHOF_TRAINS.blend --python build/realism_scene.py
```

The first command produces the intermediate `source/NORDBAHNHOF_TRAINS.blend`; the second produces `source/NORDBAHNHOF_REALISM.blend`. The archive need not duplicate the large intermediate file because it is reproducible from the included base. The low-level `build_bay.py` module supplies mesh helpers; its historical scene-building functions are not acceptance evidence and are not called to regenerate the rejected people.

For a raw proof:

```sh
blender -b -t 2 source/NORDBAHNHOF_REALISM.blend --python build/render_realism_raw.py -- --view 1 --res 1024 --samples 48
```

For the final batch, install Python 3.13 packages `OpenEXR`, `numpy` and `Pillow`, and install the official Intel OIDN 2.5.1 Linux binary at the path documented in `build/finish_realism.py` (or edit that path for your installation). Then:

```sh
python3 build/render_realism_final.py 1,2,3,4,5,6
```

The final renderer is restart-safe and reuses existing tile files. **Remove `renders/realism/.cache` before rendering after any scene change**, otherwise old tiles would be reused. Raw EXR/PFM intermediates and denoiser binaries are not included in the download. The saved Blender scene can also be rendered normally on a larger workstation without the constrained-workstation LOD.

## Credits and licences

- Poly Haven scanned materials and HDRIs: **CC0**. Exact asset names, authors, source URLs and SHA-256 hashes are in `assets/realism/PROVENANCE.json`; metadata is retained alongside the maps. See <https://polyhaven.com/license>.
- Six HSRD-100 photographic people: **CC BY 4.0**, Digital Reality Lab / HumanScanRepository. Retain `assets/scans/ATTRIBUTION.md` and `assets/scans/PROVENANCE.json` when redistributing the scans or their derivatives. Textures were reduced to 2048 JPEG, scale/origin normalised and subjects placed in the scene. Source discovery is credited to Vitruvius; the loader was independently implemented.
- Intel Open Image Denoise: an external processing tool; not bundled and not an asset licence for the scene. <https://github.com/RenderKit/oidn>

Provenance and actual inspection records take precedence over superseded numerical claims in earlier releases.
