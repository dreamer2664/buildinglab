#!/usr/bin/env python3
"""
playable_controller.py — Interactive CLI & Blender Pose/Door/Wind Controller
for the playable Winterlichtplatz & Schlosspark-Viertel city (`master.blend`).

Usage examples (inside Blender or standalone):
  blender --background townsquare/scene/master.blend --python-exit-code 1 \
    --python townsquare/tools/playable_controller.py -- \
    --pose-human HERO_H01_HSR0015-Body-009 --bone UpperArm.R --angles -45,10,25 \
    --set-door PLAYABLE_DOOR_B01_ShopEntry --angle 82 \
    --ruffle-hair 0.85
"""
from __future__ import annotations
import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "evidence" / "validation" / "playable_state.json"


def get_cli_argv() -> list[str]:
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    if "blender" in Path(sys.argv[0]).name.lower():
        return []
    return sys.argv[1:]


def pose_human_limb(human_name: str, bone_name: str, angles_deg: tuple[float, float, float]) -> dict:
    import bpy  # type: ignore
    rig = bpy.data.objects.get(f"RIG_{human_name}") or bpy.data.objects.get(human_name)
    if rig is None or rig.type != "ARMATURE":
        raise ValueError(f"Human rig not found for {human_name!r}")
    if bone_name not in rig.pose.bones:
        raise ValueError(f"Bone {bone_name!r} not in {rig.name} (available: {[b.name for b in rig.pose.bones]})")
    pb = rig.pose.bones[bone_name]
    pb.rotation_mode = "XYZ"
    pb.rotation_euler = tuple(math.radians(a) for a in angles_deg)
    bpy.context.view_layer.update()
    return {
        "rig": rig.name,
        "bone": bone_name,
        "angles_deg": list(angles_deg),
    }


def set_door_angle(door_name: str, angle_deg: float) -> dict:
    import bpy  # type: ignore
    door = bpy.data.objects.get(door_name)
    if door is None or door.get("role") != "playable_door":
        raise ValueError(f"Playable door not found: {door_name!r}")
    lo = float(door.get("min_angle_deg", 0.0))
    hi = float(door.get("max_angle_deg", 95.0))
    clamped = max(lo, min(hi, float(angle_deg)))
    base_yaw = float(door.get("base_yaw_rad", 0.0))
    door.rotation_mode = "XYZ"
    door.rotation_euler = (0.0, 0.0, base_yaw + math.radians(clamped))
    door["open_angle_deg"] = clamped
    bpy.context.view_layer.update()
    return {
        "door": door.name,
        "open_angle_deg": clamped,
        "rotation_z_rad": door.rotation_euler.z,
    }


def set_hair_ruffle(strength: float) -> dict:
    import bpy  # type: ignore
    s = max(0.0, min(1.0, float(strength)))
    humans = [o for o in bpy.context.scene.objects if o.get("role") == "human"]
    seen_meshes: set[str] = set()
    for o in humans:
        m = o.data
        if m.name not in seen_meshes and m.shape_keys:
            seen_meshes.add(m.name)
            for kname, factor in (
                ("Hair_Ruffle_Wind_L", s),
                ("Hair_Ruffle_Wind_R", s * 0.65),
                ("Hair_Bounce", s * 0.5),
            ):
                if kname in m.shape_keys.key_blocks:
                    m.shape_keys.key_blocks[kname].value = factor
        rig = bpy.data.objects.get(o.get("rig_name", f"RIG_{o.name}"))
        if rig and rig.pose:
            for bname, rx, ry, rz in (
                ("Hair_Crown", 0.18 * s, 0.22 * s, 0.0),
                ("Hair_Strand.L", 0.20 * s, -0.28 * s, 0.12 * s),
                ("Hair_Strand.R", -0.18 * s, 0.26 * s, -0.12 * s),
                ("Hair_Back", 0.24 * s, 0.0, 0.10 * s),
            ):
                if bname in rig.pose.bones:
                    rig.pose.bones[bname].rotation_euler = (rx, ry, rz)
    bpy.context.view_layer.update()
    return {"hair_ruffle_strength": s, "humans_updated": len(humans)}


def main() -> int:
    p = argparse.ArgumentParser(description="Playable City Pose, Door & Hair-Ruffle Controller")
    p.add_argument("--list", action="store_true", help="Print playable summary")
    p.add_argument("--pose-human", type=str, default=None, help="Human object or rig name")
    p.add_argument("--bone", type=str, default="UpperArm.R", help="Limb or hair bone name")
    p.add_argument("--angles", type=str, default="0,0,0", help="Comma-separated XYZ degrees")
    p.add_argument("--set-door", type=str, default=None, help="Playable door object name")
    p.add_argument("--angle", type=float, default=75.0, help="Door opening angle in degrees (0..95)")
    p.add_argument("--ruffle-hair", type=float, default=None, help="Wind hair ruffle strength (0.0..1.0)")
    p.add_argument("--save", action="store_true", help="Save modified pose back to blend file")
    args = p.parse_args(get_cli_argv())

    out: dict = {}
    if args.list and STATE_PATH.exists():
        out["summary"] = json.loads(STATE_PATH.read_text(encoding="utf-8"))

    try:
        import bpy  # type: ignore
        if bpy.context and bpy.context.scene:
            if args.pose_human:
                ang = tuple(float(x) for x in args.angles.split(","))
                out["posed_human"] = pose_human_limb(args.pose_human, args.bone, (ang[0], ang[1], ang[2]))
            if args.set_door:
                out["door_state"] = set_door_angle(args.set_door, args.angle)
            if args.ruffle_hair is not None:
                out["hair_ruffle"] = set_hair_ruffle(args.ruffle_hair)
            if args.save:
                bpy.ops.wm.save_mainfile(compress=True)
    except ImportError:
        pass

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
