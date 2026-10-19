"""Re-solve the four whole-village orbit cameras so the built square is vertically centred and
the frame is as tight as the measured envelope allows. Presets only; the model is untouched.
"""
import bpy, json, sys, math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

R = Path(__file__).resolve().parents[2]
EXTERIOR_LAYERS = {'exterior', 'roof', 'signage', 'wall_low', 'wall_high', 'slab', 'door', 'stairs'}
scene = bpy.context.scene
bpy.context.view_layer.update()
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


def extents(lo, hi, pos, target, lens):
    camdata.lens = lens; cam.location = pos
    cam.rotation_euler = (target - pos).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()
    corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]
    pts = [world_to_camera_view(scene, cam, p) for p in corners]
    return [min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts)], all(p.z > 0 for p in pts)


def solve(lo, hi, pos, margin=0.035, lo_lens=10.0, hi_lens=90.0):
    # aim so the vertical centre of the built mass lands at 0.5
    tz_lo, tz_hi = -10.0, 20.0
    best = None
    for _ in range(24):
        tz = (tz_lo + tz_hi) / 2
        target = Vector((0, 0, tz))
        e, front = extents(lo, hi, pos, target, 30.0)
        if not front:
            tz_hi = tz; continue
        if (e[2] + e[3]) / 2 < 0.5:
            tz_hi = tz
        else:
            tz_lo = tz
        best = (tz, target)
    tz, target = best
    a, b = lo_lens, hi_lens
    ok_lens = None
    for _ in range(24):
        mid = (a + b) / 2
        e, front = extents(lo, hi, pos, target, mid)
        if front and all(margin <= v <= 1 - margin for v in e):
            ok_lens = (mid, e); a = mid
        else:
            b = mid
    assert ok_lens, 'no lens fits'
    return target, ok_lens[0], ok_lens[1]


all_objs = [o for o in scene.objects if o.type == 'MESH' and o.get('building_id') and o.get('layer') in EXTERIOR_LAYERS]
lo_all, hi_all = bbox(all_objs)
design_path = R / 'design/production-views.json'
design = json.loads(design_path.read_text())
rows = []
for i, theta in enumerate((35.0, 125.0, 215.0, 305.0), start=1):
    vid = 'V%02d' % i
    frame = next(f for f in design['frames'] if f['id'] == vid)
    pos = Vector(frame['position'])
    target, lens, e = solve(lo_all, hi_all, pos)
    frame['target'] = [round(v, 3) for v in target]
    frame['lens_mm'] = round(lens, 2)
    rows.append({'view': vid, 'camera': frame['position'], 'target': frame['target'], 'lens_mm': frame['lens_mm'],
                 'projected_extent': [round(v, 3) for v in e]})
    print('VILLAGE_REFRAME', vid, frame['position'], frame['target'], frame['lens_mm'], [round(v, 3) for v in e], flush=True)
design_path.write_text(json.dumps(design, indent=2) + '\n')
(R / 'design/production-village-views.json').write_text(json.dumps({'views': rows, 'method': 'vertical centring of the measured built envelope plus largest fitting lens'}, indent=2) + '\n')
