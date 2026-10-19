"""Re-solve exterior cameras with an additional on-screen occlusion test.

Sampling only nine sight lines to the frontage lets a large near object (a market-stall roof)
still fill the bottom of the frame. This script adds a screen-coverage test: rays are cast on a
grid over the central part of the frame and the fraction that first hits a NEAR object which is
not the target building must stay below a limit.

Usage: blender -b <native> --python fix_building_occlusion.py -- B09 [B12 ...]
"""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools/production'))
from fingerprints import file_sha256, geometry_uv_pose_material_signature

EXTERIOR_LAYERS = {'exterior', 'roof', 'signage', 'wall_low', 'wall_high', 'slab', 'door', 'stairs'}
base = json.loads((R / 'evidence/production/R14-camera-corrected-stocked-town.json').read_text())
assert file_sha256(bpy.data.filepath) == base['native_sha256']
scene = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()
camdata = bpy.data.cameras.new('SOLVE'); cam = bpy.data.objects.new('SOLVE', camdata)
scene.collection.objects.link(cam); camdata.sensor_fit = 'HORIZONTAL'; camdata.sensor_width = 36.0


def bbox(objs):
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
    return lo, hi


def corners(lo, hi):
    return [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]


def project(lo, hi, pos, target, lens):
    camdata.lens = lens; cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    pts = [world_to_camera_view(scene, cam, p) for p in corners(lo, hi)]
    return [min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts)], all(p.z > 0 for p in pts)


def solve_lens(lo, hi, pos, target, margin=0.045):
    ext, front = project(lo, hi, pos, target, 14.0)
    if not front or not all(margin <= v <= 1 - margin for v in ext):
        return None
    best, hi_l = 14.0, 70.0
    for _ in range(20):
        mid = (best + hi_l) / 2
        ext, front = project(lo, hi, pos, target, mid)
        if front and all(margin <= v <= 1 - margin for v in ext):
            best = mid
        else:
            hi_l = mid
    ext, _ = project(lo, hi, pos, target, best)
    return best, ext


def coverage(pos, target, lens, bid, near=18.0):
    """Fraction of a frame grid whose first hit is a near, non-target object."""
    camdata.lens = lens; cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    total = bad = 0
    for fx in [0.06 + 0.88 * i / 12 for i in range(13)]:
        for fy in [0.06 + 0.88 * j / 8 for j in range(9)]:
            v = Vector((fx, fy, 0.5))
            d = (cam.matrix_world.to_3x3() @ (camdata.view_frame(scene=scene)[0] * 0 + Vector((0, 0, 0))))
            # build a world ray through the pixel using the camera frame
            frame = camdata.view_frame(scene=scene)  # top-right, bottom-right, bottom-left, top-left at -1
            x = frame[2].x + (frame[0].x - frame[2].x) * fx
            y = frame[2].y + (frame[0].y - frame[2].y) * fy
            local = Vector((x, y, -1.0))
            direction = (cam.matrix_world.to_3x3() @ local).normalized()
            hit, loc, nrm, idx, obj, mw = scene.ray_cast(dg, cam.location, direction)
            total += 1
            if hit and obj is not None:
                own = obj.get('building_id') == bid or obj.get('layer') in {'decorations', 'ground', 'auxiliary_background'}
                if not own and (loc - cam.location).length < near:
                    bad += 1
    return bad / total


prog = {b['id']: b for b in json.loads((R / 'design/programme.json').read_text())['buildings']}
design_path = R / 'design/production-views.json'
design = json.loads(design_path.read_text())
targets = [a for a in sys.argv[sys.argv.index('--') + 1:]] if '--' in sys.argv else []
rows = []
for bid in targets:
    b = prog[bid]
    objs = [o for o in scene.objects if o.get('building_id') == bid and o.type in {'MESH', 'CURVE', 'CURVES'} and o.get('layer') in EXTERIOR_LAYERS]
    lo, hi = bbox(objs)
    centre_xy = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, 0.0))
    inward = -centre_xy.normalized()
    half_w = (hi.x - lo.x) / 2 if abs(inward.y) > abs(inward.x) else (hi.y - lo.y) / 2
    lateral = Vector((-inward.y, inward.x, 0.0))
    sight = []
    for fx in (-0.7, 0.0, 0.7):
        for fz in (0.2, 0.5, 0.8):
            p = centre_xy + inward * min(half_w, 8.0) + lateral * (fx * half_w * 0.85)
            sight.append(Vector((p.x, p.y, lo.z + fz * (hi.z - lo.z))))
    best = None
    for az in (-40, -28, -16, -8, 0, 8, 16, 28, 40):
        for d in (16, 20, 25, 30, 36, 43):
            for height in (min(max(3.0, 0.30 * (hi.z - lo.z)), 6.0), min(max(4.5, 0.45 * (hi.z - lo.z)), 9.0), min(max(6.0, 0.60 * (hi.z - lo.z)), 12.0)):
                rot = Matrix.Rotation(math.radians(az), 3, 'Z')
                pos = centre_xy + (rot @ inward) * d
                if abs(pos.x) > 30.5 or abs(pos.y) > 25.0:
                    continue
                pos = Vector((pos.x, pos.y, height))
                target = Vector((centre_xy.x, centre_xy.y, lo.z + 0.5 * (hi.z - lo.z)))
                blocked = 0
                for tp in sight:
                    dd = tp - pos
                    hit, loc, nrm, idx, obj, mw = scene.ray_cast(dg, pos, dd.normalized(), distance=dd.length * 0.999)
                    if hit and obj is not None and obj.get('building_id') != bid and obj.get('layer') != 'decorations':
                        blocked += 1
                if blocked:
                    continue
                res = solve_lens(lo, hi, pos, target)
                if not res:
                    continue
                lens, ext = res
                cov = coverage(pos, target, lens, bid)
                if cov > 0.06:
                    continue
                score = lens * (1.0 - 2.0 * cov)
                if best is None or score > best[0]:
                    best = (score, pos, target, lens, ext, cov, az, d, height)
    assert best, bid
    _, pos, target, lens, ext, cov, az, d, height = best
    frame = next(f for f in design['frames'] if f['id'] == bid + '_exterior')
    frame['position'] = [round(v, 3) for v in pos]
    frame['target'] = [round(v, 3) for v in target]
    frame['lens_mm'] = round(lens, 2)
    rows.append({'building': bid, 'camera': frame['position'], 'target': frame['target'], 'lens_mm': frame['lens_mm'],
                 'projected_extent': [round(v, 3) for v in ext], 'near_occluder_fraction_of_frames': round(cov, 4),
                 'orbit_offset_deg': az, 'distance_m': d, 'camera_height_m': height})
    print('OCCLUSION_REFIT', bid, frame['position'], frame['lens_mm'], 'coverage', round(cov, 4), flush=True)

design_path.write_text(json.dumps(design, indent=2) + '\n')
(R / 'design/production-exterior-refits.json').write_text(json.dumps(rows, indent=2) + '\n')
p = R / 'evidence/production/R14-exterior-framed-town.json'
r = json.loads(p.read_text())
r.setdefault('actual_occlusion_refits', []).extend(rows)
r['occlusion_test'] = 'nine frontage sight lines plus a 13x9 frame-grid near-occluder coverage limit of 6 percent'
p.write_text(json.dumps(r, indent=2) + '\n')
# Camera presets are persisted by tools/production/persist_view_presets_in_native.py in a separate
# low-memory process: saving this 548 MB scene right after ray casting exceeds the 2 GB runtime.
print('OCCLUSION_REFIT_RECORDED', [(x['building'], x['camera'], x['lens_mm']) for x in rows], flush=True)
