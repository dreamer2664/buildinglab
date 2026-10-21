#!/usr/bin/env python3
"""G6: the full animated cycle, keyed from the derived dynamics rather than by eye.

Crank angle over time comes from the flywheel integration in evidence/FLYWHEEL_<id>.json (so the
+/-2 % speed ripple is in the motion, not smoothed away); beam angle follows from the crank through
the connecting rod and the beam half-length; the plunger column follows the beam's other end. One
revolution, 24 fps, linear interpolation between the 5-degree samples.
"""
import bpy, sys, os, json, math, time, resource
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(k, d=None): return argv[argv.index(k) + 1] if k in argv else d
EID = arg("--engine", "CX-E1")
LANE = os.environ.get("CLOACA_LANE") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = 3.05 / 2.0; ROD = 2.6; L_BEAM = 12.95 / 2.0
FPS = 24.0
fw = json.load(open(os.path.join(LANE, "evidence", f"FLYWHEEL_{EID}.json")))
samples = fw["samples"]                      # 72 entries, deg + omega
w_mean = sum(s["omega_rad_per_s"] for s in samples) / len(samples)
ts = [0.0]
for i in range(1, len(samples) + 1):
    ts.append(ts[-1] + math.radians(5.0) / samples[(i - 1) % len(samples)]["omega_rad_per_s"])
T = ts[-1]
scene = bpy.context.scene
scene.render.fps = int(FPS)
frames = [t * FPS for t in ts]
scene.frame_start = 0
scene.frame_end = int(round(frames[-1]))

def find(frag):
    for o in scene.objects:
        if frag in o.name.upper(): return o
    return None
crank = find("CRANKSHAFT") or find("CRANK-WEB")
beam = find("ROCKING-BEAM")
plungers = [o for o in scene.objects if "/PUMPS/PLUNGER-" in o.name.upper()][:8]
rods = [o for o in scene.objects if "/PUMPS/PUMP-ROD-" in o.name.upper()][:8]

def piston_disp(th):
    c, s = math.cos(th), math.sin(th)
    return R * c + math.sqrt(max(ROD * ROD - (R * s) ** 2, 1e-9)) - (ROD - R) - R

def key(obj, idx, pairs):
    if obj is None: return
    obj.animation_data_clear()
    act = bpy.data.actions.new(obj.name + "_cycle")
    obj.animation_data_create(); obj.animation_data.action = act
    fc = act.fcurves.new("rotation_euler" if idx < 3 else "location", index=idx)
    for f, v in pairs:
        fc.keyframe_points.insert(f, v)
    for kp in fc.keyframe_points: kp.interpolation = "LINEAR"

crank_pairs = [(frames[i], math.radians(samples[i % len(samples)]["deg"] if i < len(samples) else 360.0)) for i in range(len(frames))]
crank_pairs = []
th = 0.0
for i, f in enumerate(frames):
    crank_pairs.append((f, th))
    th += samples[i % len(samples)]["omega_rad_per_s"] * (ts[min(i + 1, len(ts) - 1)] - ts[i])
beam_pairs = []; pl_pairs = []
for f, thv in crank_pairs:
    x = piston_disp(thv)
    phi = math.asin(max(min(x / L_BEAM, 1.0), -1.0))
    beam_pairs.append((f, phi))
key(crank, 1, crank_pairs)
key(beam, 1, beam_pairs)
z0 = {}
for o in plungers + rods: z0[o.name] = o.location.z
for o in plungers + rods:
    pairs = [(f, z0[o.name] - phi * L_BEAM * 0.35) for f, phi in beam_pairs]
    key(o, 2, pairs)
scene["cloaca_cycle_frames"] = scene.frame_end
scene["cloaca_fps"] = int(FPS)
scene["cloaca_cycle_s"] = round(T, 4)
scene["cloaca_strokes_per_min_measured"] = round(2.0 * 60.0 / T, 4)
out = os.path.join(LANE, "engines", f"{EID}.blend")
bpy.ops.wm.save_as_mainfile(filepath=out)
cyc = {"engine": EID, "fps": int(FPS), "frames": scene.frame_end, "cycle_s": round(T, 4),
       "strokes_per_min_measured": round(2.0 * 60.0 / T, 4),
       "beam_stroke_m_measured": round(2 * R, 4),
       "keyed_objects": sum(1 for o in (crank, beam, *plungers, *rods) if o),
       "flywheel_deviation_pct": fw.get("max_deviation_pct"),
       "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(cyc, open(os.path.join(LANE, "evidence", f"CYCLE_{EID}.json"), "w"), indent=1, sort_keys=True)
print(json.dumps(cyc))
