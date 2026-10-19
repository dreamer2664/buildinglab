"""Fit one occlusion-checked exterior camera per building plus four whole-village orbit cameras.

For every building a grid of candidate viewpoints is tested inside the square:
  * the camera must stay inside the public square,
  * a set of rays from the camera to sampled points on the measured building envelope must reach
    the target building without hitting anything else (this is what keeps lamps, the Christmas
    tree and market stalls out of the lens),
  * the lens is then solved numerically so the whole building sits inside the frame margin.

Only camera presets are written. Geometry, materials, lights and poses are untouched.
"""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/production'))
from fingerprints import file_sha256, geometry_uv_pose_material_signature

base = json.loads((R / 'evidence/production/R14-camera-corrected-stocked-town.json').read_text())
assert file_sha256(bpy.data.filepath) == base['native_sha256'], 'opened native does not match receipt'
EXTERIOR_LAYERS = {'exterior', 'roof', 'signage', 'wall_low', 'wall_high', 'slab', 'door', 'stairs'}
scene = bpy.context.scene
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()


def bbox_of(objs):
    lo = Vector((1e9, 1e9, 1e9)); hi = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
    return lo, hi


camdata = bpy.data.cameras.new('FRAME_TMP')
cam = bpy.data.objects.new('FRAME_TMP', camdata)
scene.collection.objects.link(cam)
camdata.sensor_fit = 'HORIZONTAL'
camdata.sensor_width = 36.0


def project(lo, hi, pos, target, lens):
    camdata.lens = lens
    cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    pts = [world_to_camera_view(scene, cam, p) for p in corners]
    ext = [min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts)]
    return ext, all(p.z > 0 for p in pts)


def solve_lens(lo, hi, pos, target, margin=0.045, lo_lens=14.0, hi_lens=70.0):
    """Largest focal length that still contains the whole measured envelope."""
    ext, front = project(lo, hi, pos, target, lo_lens)
    if not front:
        return None
    if not all(margin <= v <= 1 - margin for v in ext):
        return None
    best = lo_lens
    for _ in range(22):
        mid = (best + hi_lens) / 2
        ext, front = project(lo, hi, pos, target, mid)
        if front and all(margin <= v <= 1 - margin for v in ext):
            best = mid
        else:
            hi_lens = mid
    ext, _ = project(lo, hi, pos, target, best)
    return best, ext


def blocked(pos, target_points, bid):
    """True when a ray from the camera reaches something that is not the target building."""
    blockers = []
    for tp in target_points:
        d = tp - pos
        hit, loc, nrm, idx, obj, mw = scene.ray_cast(dg, pos, d.normalized(), distance=d.length * 0.999)
        if hit and obj is not None:
            own = obj.get('building_id') == bid or obj.get('layer') in {'decorations'}
            if not own:
                blockers.append(obj.name)
    return blockers


prog = json.loads((R / 'design/programme.json').read_text())
rows, frames = [], []
for b in prog['buildings']:
    bid = b['id']
    objs = [o for o in scene.objects if o.get('building_id') == bid and o.type in {'MESH', 'CURVE', 'CURVES'} and o.get('layer') in EXTERIOR_LAYERS]
    lo, hi = bbox_of(objs)
    h = hi.z - lo.z
    centre_xy = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0.0))
    inward = -centre_xy.normalized()
    front_z = lo.z + 0.62 * h
    # sampled reception points across the square-facing frontage
    half_w = (hi.x - lo.x) / 2 if abs(inward.y) > abs(inward.x) else (hi.y - lo.y) / 2
    lateral = Vector((-inward.y, inward.x, 0.0))
    targets = []
    for fx in (-0.75, 0.0, 0.75):
        for fz in (0.18, 0.5, 0.82):
            p = centre_xy + inward * min(half_w, 8.0) + lateral * (fx * half_w * 0.9)
            targets.append(Vector((p.x, p.y, lo.z + fz * h)))
    best = None
    for az in (-46, -34, -22, -12, 0, 12, 22, 34, 46):
        for d in (15, 19, 24, 30, 37, 45):
            rot = Matrix.Rotation(math.radians(az), 3, 'Z')
            pos = centre_xy + (rot @ inward) * d
            if abs(pos.x) > 30.0 or abs(pos.y) > 24.5:
                continue  # stay inside the public square
            height = min(max(3.0, 0.30 * h), 6.0)
            pos = Vector((pos.x, pos.y, height))
            target = Vector((centre_xy.x, centre_xy.y, lo.z + 0.5 * h))
            bl = blocked(pos, targets, bid)
            if bl:
                continue
            res = solve_lens(lo, hi, pos, target)
            if not res:
                continue
            lens, ext = res
            score = lens  # tightest framing wins
            if best is None or score > best[0]:
                best = (score, pos, target, lens, ext, az, d)
    assert best, bid
    score, pos, target, lens, ext, az, d = best
    rows.append({'building': bid, 'brand': b['brand'], 'business': b['business'],
                 'bounds_min': [round(v, 3) for v in lo], 'bounds_max': [round(v, 3) for v in hi],
                 'height_m': round(h, 3), 'camera': [round(v, 3) for v in pos],
                 'camera_height_m': round(pos.z, 2), 'camera_distance_m': d, 'orbit_offset_deg': az,
                 'lens_mm': round(lens, 2), 'projected_extent': [round(v, 3) for v in ext],
                 'occlusion': 'nine ray-cast sight lines from camera to frontage; first hit must be the target building'})
    frames.append({'id': bid + '_exterior', 'title': '%s / %s exterior' % (b['brand'], b['business']),
                   'kind': 'building', 'building_id': bid,
                   'position': [round(v, 3) for v in pos], 'target': [round(v, 3) for v in target],
                   'lens_mm': round(lens, 2), 'resolution': [1920, 1080], 'samples': 14, 'exposure': 1.7})

all_objs = [o for o in scene.objects if o.type == 'MESH' and o.get('building_id') and o.get('layer') in EXTERIOR_LAYERS]
lo_all, hi_all = bbox_of(all_objs)
village_rows = []
for i, theta in enumerate((35.0, 125.0, 215.0, 305.0), start=1):
    a = math.radians(theta)
    inward = Vector((math.cos(a), math.sin(a), 0.0))
    best_v = None
    for d_try in range(60, 320, 5):
        pos = Vector((inward.x * d_try, inward.y * d_try, 0.42 * d_try))
        target = Vector((0, 0, 5.0))
        res = solve_lens(lo_all, hi_all, pos, target, margin=0.03)
        if res:
            best_v = (pos, res); break
    assert best_v, theta
    pos, (lens, ext) = best_v
    village_rows.append({'view': 'V%02d' % i, 'orbit_deg': theta, 'camera': [round(v, 2) for v in pos],
                         'height_m': round(pos.z, 2), 'distance_m': round(pos.length, 2),
                         'lens_mm': round(lens, 2), 'projected_extent': [round(v, 3) for v in ext]})
    frames.append({'id': 'V%02d' % i, 'title': 'Whole village / elevated view %d' % i, 'kind': 'village',
                   'position': [round(v, 3) for v in pos], 'target': [0, 0, 5.0],
                   'lens_mm': round(lens, 2), 'resolution': [1920, 1080], 'samples': 14, 'exposure': 1.7})

bpy.data.objects.remove(cam, do_unlink=True); bpy.data.cameras.remove(camdata)

design_path = R / 'design/production-views.json'
design = json.loads(design_path.read_text())
have = {f['id']: i for i, f in enumerate(design['frames'])}
added = []
for f in frames:
    if f['id'] in have:
        design['frames'][have[f['id']]] = f
    else:
        design['frames'].append(f); added.append(f['id'])
design['count'] = len(design['frames'])
design_path.write_text(json.dumps(design, indent=2) + '\n')
(R / 'design/production-exterior-views.json').write_text(json.dumps(
    {'buildings': rows, 'village_views': village_rows,
     'measured_whole_built_extent': {'min': [round(v, 3) for v in lo_all], 'max': [round(v, 3) for v in hi_all]},
     'method': 'candidate viewpoints inside the square, nine-ray occlusion test to the target frontage, then numerically solved lens for the measured envelope'},
    indent=2) + '\n')

t = bpy.data.texts.get('VIEW_PRESETS.json') or bpy.data.texts.new('VIEW_PRESETS.json')
t.clear(); t.write(json.dumps(design)); t.use_fake_user = True
scene['exterior_view_notice'] = 'One occlusion-checked exterior camera per building plus four measured whole-village orbit cameras; framing only, geometry/materials/lights unchanged.'
sig = geometry_uv_pose_material_signature()
out = R / '.cache/stocked-town/Winterlichtplatz-exterior-framed-UNPROMOTED.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(out), compress=True)
r = dict(base)
r.update(native=str(out.relative_to(R)), native_sha256=file_sha256(out), native_bytes=out.stat().st_size,
         geometry_uv_pose_material_signature=sig,
         parent_camera_corrected_native_sha256=base['native_sha256'],
         actual_added_view_presets=added, view_presets_total=design['count'],
         stage='EXTERIOR/VILLAGE CAMERAS FITTED TO MEASURED BOUNDS WITH OCCLUSION RAY TESTS - CANDIDATE, NOT FINAL ACCEPTANCE')
(R / 'evidence/production/R14-exterior-framed-town.json').write_text(json.dumps(r, indent=2) + '\n')
print('EXTERIOR_VILLAGE_CAMERAS_FITTED', r['native_sha256'], r['native_bytes'], sig, added, flush=True)
for row in rows:
    print('BUILDING_FIT', row['building'], 'h', row['height_m'], 'lens', row['lens_mm'], 'd', row['camera_distance_m'], 'az', row['orbit_offset_deg'], 'cam', row['camera'], 'ext', row['projected_extent'], flush=True)
for v in village_rows:
    print('VILLAGE_FIT', v['view'], v['camera'], v['lens_mm'], v['projected_extent'], flush=True)
