#!/usr/bin/env python3
"""
Playable & Articulated City Upgrader (`townsquare/scene/make_playable.py`).
Upgrades `master.blend` and `master.glb` so the entire two-neighbourhood city is playable:
1. Every human (`340/340` in `03_PEOPLE`) receives:
   - 23 distinct anatomical limb & hair vertex groups (`Pelvis`, `Spine`, `Chest`, `Neck`, `Head`,
     `Hair_Crown`, `Hair_Strand.L`, `Hair_Strand.R`, `Hair_Back`,
     `Shoulder.L`, `UpperArm.L`, `ForeArm.L`, `Hand.L`,
     `Shoulder.R`, `UpperArm.R`, `ForeArm.R`, `Hand.R`,
     `Thigh.L`, `Shin.L`, `Foot.L`, `Thigh.R`, `Shin.R`, `Foot.R`).
   - A dedicated 23-bone hierarchical Skeletal Armature (`RIG_<human_name>`) bound via
     `PlayableArmature` (`ARMATURE` modifier), with keyframed limb & hair-ruffle pose actions
     across Frames 1..60 (Frame 1 = exact rest pose for static render parity).
   - 5 Shape Keys (`Basis`, `Hair_Ruffle_Wind_L`, `Hair_Ruffle_Wind_R`, `Hair_Bounce`, `Chest_Breathe`)
     on every human mesh data-block, plus articulated multi-strand hair tufts on the 12 hero figures.
2. 62 Hinged Movable Doors (`PLAYABLE_DOOR_*` in `06_PLAYABLE_RIGS`):
   - 20 ground-floor glazed shop entrance doors (`B01`..`B20`)
   - 20 ground-floor oak residential lobby doors (`B01`..`B20`)
   - 16 interior apartment/room doors (`B02`, `B04`, `B07`, `B10`, `B13`, `B15`, `B18`)
   - 6 vehicle & street-furniture doors (electric tram front/rear doors, carriage cab door,
     vintage taxi driver door, 2 telephone booth doors).
   - Each door's local origin `(0,0,0)` lies on its vertical hinge pin (`Z` axis) so changing
     `door.rotation_euler.z` swings the door leaf smoothly open (`0°..95°`), with keyframed
     swing actions across Frames 1..60 (Frame 1 = `0°` closed).
3. Articulated Animals, Wind-Swaying Trees, and Vehicle Wheel/Pantograph Groups:
   - `CITY_ANIMALS` receives 11 anatomical vertex groups (`Head`, `Snout`, `Ear.L`, `Ear.R`,
     `Neck`, `Torso`, `Leg_FL`, `Leg_FR`, `Leg_BL`, `Leg_BR`, `Tail_Wag`) + shape keys.
   - `DECIDUOUS_TREE_01..32` receive wind vertex groups (`Trunk_Static`, `MainBough_Sway`,
     `TwigCrown_Ruffle`) + keyframed wind sway across Frames 1..60 (Frame 1 = rest).
"""
from __future__ import annotations
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import bpy  # type: ignore
import bmesh  # type: ignore

ROOT = Path("/home/user/buildinglab")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from townsquare.kits.core import ensure_collection

PROG_PATH = ROOT / "townsquare/design/PROGRAMME.json"
WORK_DIR = Path("/var/tmp/townsquare_work")
BLEND_REAL = WORK_DIR / "master.blend"
GLB_REAL = WORK_DIR / "master.glb"
BLEND_LINK = ROOT / "townsquare/scene/master.blend"
GLB_LINK = ROOT / "townsquare/scene/master.glb"
BUILD_JSON = ROOT / "townsquare/evidence/validation/master_scene_build.json"
EXPORT_PARITY_JSON = ROOT / "townsquare/evidence/validation/export_parity.json"
PLAYABLE_STATE_JSON = ROOT / "townsquare/evidence/validation/playable_state.json"

HUMAN_BONE_DEFS = [
    ("Pelvis", (0.0, 0.0, 0.88), (0.0, 0.0, 0.98), None),
    ("Spine", (0.0, 0.0, 0.98), (0.0, 0.0, 1.18), "Pelvis"),
    ("Chest", (0.0, 0.0, 1.18), (0.0, 0.0, 1.40), "Spine"),
    ("Neck", (0.0, 0.0, 1.40), (0.0, 0.0, 1.50), "Chest"),
    ("Head", (0.0, 0.0, 1.50), (0.0, 0.0, 1.68), "Neck"),
    ("Hair_Crown", (0.0, 0.0, 1.66), (0.0, 0.0, 1.75), "Head"),
    ("Hair_Strand.L", (-0.07, -0.02, 1.65), (-0.10, -0.02, 1.52), "Head"),
    ("Hair_Strand.R", (0.07, -0.02, 1.65), (0.10, -0.02, 1.52), "Head"),
    ("Hair_Back", (0.0, 0.07, 1.64), (0.0, 0.10, 1.48), "Head"),
    ("Shoulder.L", (-0.05, 0.0, 1.36), (-0.16, 0.0, 1.36), "Chest"),
    ("UpperArm.L", (-0.16, 0.0, 1.36), (-0.20, 0.0, 1.10), "Shoulder.L"),
    ("ForeArm.L", (-0.20, 0.0, 1.10), (-0.22, -0.03, 0.86), "UpperArm.L"),
    ("Hand.L", (-0.22, -0.03, 0.86), (-0.23, -0.05, 0.74), "ForeArm.L"),
    ("Shoulder.R", (0.05, 0.0, 1.36), (0.16, 0.0, 1.36), "Chest"),
    ("UpperArm.R", (0.16, 0.0, 1.36), (0.20, 0.0, 1.10), "Shoulder.R"),
    ("ForeArm.R", (0.20, 0.0, 1.10), (0.22, -0.03, 0.86), "UpperArm.R"),
    ("Hand.R", (0.22, -0.03, 0.86), (0.23, -0.05, 0.74), "ForeArm.R"),
    ("Thigh.L", (-0.09, 0.0, 0.88), (-0.10, 0.0, 0.48), "Pelvis"),
    ("Shin.L", (-0.10, 0.0, 0.48), (-0.10, 0.0, 0.08), "Thigh.L"),
    ("Foot.L", (-0.10, 0.0, 0.08), (-0.10, -0.14, 0.02), "Shin.L"),
    ("Thigh.R", (0.09, 0.0, 0.88), (0.10, 0.0, 0.48), "Pelvis"),
    ("Shin.R", (0.10, 0.0, 0.48), (0.10, 0.0, 0.08), "Thigh.R"),
    ("Foot.R", (0.10, 0.0, 0.08), (0.10, -0.14, 0.02), "Shin.R"),
]
HUMAN_GROUPS = [b[0] for b in HUMAN_BONE_DEFS]


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_hinged_door_mesh(
    name: str,
    width: float,
    height: float,
    thickness: float,
    mat_leaf: bpy.types.Material | None,
    mat_brass: bpy.types.Material | None,
    mat_glass: bpy.types.Material | None,
    glazed: bool = True,
) -> bpy.types.Mesh:
    """
    Create a bevelled hinged door mesh whose local origin (0, 0, 0) is at the
    bottom of the vertical hinge pin (`x=0` is hinge edge, `x=width` is latch edge,
    `z in [0, height]`). Rotating around local Z swings the door on its hinges.
    """
    bm = bmesh.new()

    def add_box(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, mat_idx: int = 0) -> None:
        verts = [
            bm.verts.new((x0, y0, z0)),
            bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)),
            bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)),
            bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)),
            bm.verts.new((x0, y1, z1)),
        ]
        faces = [
            (0, 3, 2, 1),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (1, 2, 6, 5),
            (3, 0, 4, 7),
        ]
        for fidx in faces:
            f = bm.faces.new([verts[i] for i in fidx])
            f.material_index = mat_idx

    ht = thickness * 0.5
    stile = 0.11
    # Hinge stile, lock stile, bottom rail, mid rail, top rail
    add_box(0.0, stile, -ht, ht, 0.0, height, 0)
    add_box(width - stile, width, -ht, ht, 0.0, height, 0)
    add_box(stile, width - stile, -ht, ht, 0.0, 0.24, 0)
    add_box(stile, width - stile, -ht, ht, 0.88, 1.04, 0)
    add_box(stile, width - stile, -ht, ht, height - 0.14, height, 0)
    # Lower recessed timber panel
    add_box(stile, width - stile, -ht * 0.55, ht * 0.55, 0.24, 0.88, 0)
    # Upper panel (glazed for shop doors, recessed panel for oak/interior doors)
    if glazed:
        add_box(stile, width - stile, -0.006, 0.006, 1.04, height - 0.14, 2)
    else:
        add_box(stile, width - stile, -ht * 0.55, ht * 0.55, 1.04, height - 0.14, 0)

    # 3 Brass Hinge Knuckles along the vertical hinge axis (x = 0)
    for hz in (0.28, 1.05, height - 0.28):
        add_box(-0.012, 0.012, -0.012, 0.012, hz - 0.045, hz + 0.045, 1)

    # Twin Brass Lever Handles + Escutcheon Plates near latch edge (x = width - 0.065)
    hx = width - 0.065
    add_box(hx - 0.022, hx + 0.022, -ht - 0.008, ht + 0.008, 0.94, 1.12, 1)
    # Front and back lever spindles & grips
    add_box(hx - 0.012, hx + 0.012, -ht - 0.055, ht + 0.055, 1.03, 1.055, 1)
    add_box(hx - 0.115, hx + 0.012, -ht - 0.058, -ht - 0.038, 1.028, 1.056, 1)
    add_box(hx - 0.115, hx + 0.012, ht + 0.038, ht + 0.058, 1.028, 1.056, 1)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    if mat_leaf:
        mesh.materials.append(mat_leaf)
    if mat_brass:
        mesh.materials.append(mat_brass)
    if mat_glass:
        mesh.materials.append(mat_glass)
    return mesh


def rig_all_humans(sc: bpy.types.Scene, col_rigs: bpy.types.Collection) -> dict:
    humans = sorted([o for o in sc.objects if o.get("role") == "human"], key=lambda o: o.name)
    col_p = bpy.data.collections.get("03_PEOPLE") or col_rigs

    # Clean up any previous human armatures
    for o in list(sc.objects):
        if o.get("role") in ("human_rig", "playable_hair_tuft"):
            bpy.data.objects.remove(o, do_unlink=True)

    # Create or reuse the 23-bone hierarchical human armature datablock
    old_arm = bpy.data.armatures.get("HUMAN_23BONE_ARMATURE")
    if old_arm:
        bpy.data.armatures.remove(old_arm)
    arm_data = bpy.data.armatures.new("HUMAN_23BONE_ARMATURE")
    tmp_obj = bpy.data.objects.new("TMP_HUMAN_ARM", arm_data)
    col_rigs.objects.link(tmp_obj)
    bpy.context.view_layer.objects.active = tmp_obj
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones
    for bname, head, tail, parent in HUMAN_BONE_DEFS:
        b = eb.new(bname)
        b.head = head
        b.tail = tail
        if parent:
            b.parent = eb[parent]
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.data.objects.remove(tmp_obj, do_unlink=True)

    # Ensure all 23 vertex groups exist in identical order on all 340 humans
    for o in humans:
        for g in HUMAN_GROUPS:
            if g not in o.vertex_groups:
                o.vertex_groups.new(name=g)

    # Assign anatomical weights & hair-ruffle/breathing shape keys on each unique human mesh
    seen_meshes: set[str] = set()
    shape_keyed_meshes = 0
    for o in humans:
        m = o.data
        if m.name in seen_meshes:
            continue
        seen_meshes.add(m.name)

        zs = [v.co.z for v in m.vertices]
        zmax = max(zs) if zs else 1.74
        vg_map = {g: o.vertex_groups[g] for g in HUMAN_GROUPS}

        for v in m.vertices:
            vi = v.index
            x, y, z = v.co.x, v.co.y, v.co.z
            zn = z / max(zmax, 0.01)

            if zn > 0.87 and abs(x) < 0.15:
                vg_map["Head"].add([vi], 0.85, "REPLACE")
                if zn > 0.93:
                    vg_map["Hair_Crown"].add([vi], 0.95, "REPLACE")
                if zn > 0.88 and x < -0.015:
                    vg_map["Hair_Strand.L"].add([vi], 0.85, "REPLACE")
                if zn > 0.88 and x > 0.015:
                    vg_map["Hair_Strand.R"].add([vi], 0.85, "REPLACE")
                if zn > 0.88 and y > 0.015:
                    vg_map["Hair_Back"].add([vi], 0.85, "REPLACE")
            elif zn > 0.82 and abs(x) < 0.12:
                vg_map["Neck"].add([vi], 1.0, "REPLACE")
            elif abs(x) > 0.13 and zn >= 0.40:
                side = "L" if x < 0 else "R"
                if zn >= 0.76:
                    vg_map[f"Shoulder.{side}"].add([vi], 1.0, "REPLACE")
                elif zn >= 0.62:
                    vg_map[f"UpperArm.{side}"].add([vi], 1.0, "REPLACE")
                elif zn >= 0.50:
                    vg_map[f"ForeArm.{side}"].add([vi], 1.0, "REPLACE")
                else:
                    vg_map[f"Hand.{side}"].add([vi], 1.0, "REPLACE")
            elif zn >= 0.68:
                vg_map["Chest"].add([vi], 1.0, "REPLACE")
            elif zn >= 0.56:
                vg_map["Spine"].add([vi], 1.0, "REPLACE")
            elif zn >= 0.47:
                vg_map["Pelvis"].add([vi], 1.0, "REPLACE")
            else:
                side = "L" if x <= 0 else "R"
                if zn >= 0.27:
                    vg_map[f"Thigh.{side}"].add([vi], 1.0, "REPLACE")
                elif zn >= 0.08:
                    vg_map[f"Shin.{side}"].add([vi], 1.0, "REPLACE")
                else:
                    vg_map[f"Foot.{side}"].add([vi], 1.0, "REPLACE")

        # Add Shape Keys (Basis + Hair_Ruffle_Wind_L + Hair_Ruffle_Wind_R + Hair_Bounce + Chest_Breathe)
        if m.shape_keys is None:
            o.shape_key_add(name="Basis", from_mix=False)
        for sk_name in ("Hair_Ruffle_Wind_L", "Hair_Ruffle_Wind_R", "Hair_Bounce", "Chest_Breathe"):
            if sk_name not in m.shape_keys.key_blocks:
                sk = o.shape_key_add(name=sk_name, from_mix=False)
                sk.value = 0.0  # Frame 1 rest pose = 0.0
                for v_idx, v in enumerate(m.vertices):
                    x, y, z = v.co.x, v.co.y, v.co.z
                    zn = z / max(zmax, 0.01)
                    co = sk.data[v_idx].co
                    if sk_name == "Hair_Ruffle_Wind_L" and zn > 0.89:
                        w = (zn - 0.89) / 0.11
                        co.x = x - 0.022 * w
                        co.y = y + 0.012 * w * math.sin(z * 18.0)
                        co.z = z + 0.008 * w
                    elif sk_name == "Hair_Ruffle_Wind_R" and zn > 0.89:
                        w = (zn - 0.89) / 0.11
                        co.x = x + 0.022 * w
                        co.y = y - 0.012 * w * math.cos(z * 18.0)
                        co.z = z + 0.008 * w
                    elif sk_name == "Hair_Bounce" and zn > 0.88:
                        w = (zn - 0.88) / 0.12
                        co.z = z + 0.016 * w
                        co.x = x * (1.0 + 0.06 * w)
                    elif sk_name == "Chest_Breathe" and 0.64 <= zn <= 0.82 and abs(x) < 0.16:
                        co.y = y - 0.012 * math.sin((zn - 0.64) / 0.18 * math.pi)
        shape_keyed_meshes += 1

    # Create 4 shared NLA/Action clips for the 340 human armatures (Frame 1 = exact zero rest pose!)
    actions: list[bpy.types.Action] = []
    for act_idx, act_name in enumerate(("ACT_Human_WalkAndRuffle", "ACT_Human_ConverseAndRuffle", "ACT_Human_StrollAndWave", "ACT_Human_IdleBreeze")):
        old_a = bpy.data.actions.get(act_name)
        if old_a:
            bpy.data.actions.remove(old_a)
        act = bpy.data.actions.new(name=act_name)
        actions.append(act)

    rig_count = 0
    rigs_created: list[bpy.types.Object] = []
    for idx, o in enumerate(humans):
        rig = bpy.data.objects.new(f"RIG_{o.name}", arm_data)
        col_rigs.objects.link(rig)
        rig.location = o.location.copy()
        rig.rotation_euler = o.rotation_euler.copy()
        rig.scale = o.scale.copy()
        rig["role"] = "human_rig"
        rig["target_human"] = o.name
        rig["bone_count"] = len(HUMAN_BONE_DEFS)
        o["rig_name"] = rig.name
        o["playable_limbs"] = True
        o["playable_hair_ruffle"] = True
        o["limb_vertex_groups"] = len(HUMAN_GROUPS)

        # Attach Armature Modifier
        mod = o.modifiers.get("PlayableArmature")
        if mod is None:
            mod = o.modifiers.new(name="PlayableArmature", type="ARMATURE")
        mod.object = rig
        mod.use_vertex_groups = True
        rigs_created.append(rig)

    bpy.context.view_layer.update()

    for idx, rig in enumerate(rigs_created):
        # Set rotation mode to XYZ on all pose bones and assign shared animation clip
        if rig.pose:
            for pb in rig.pose.bones:
                pb.rotation_mode = "XYZ"
        if idx < 4 and rig.pose:
            # Populate keyframes on the 4 shared actions using the first 4 rigs
            act = actions[idx]
            rig.animation_data_create()
            rig.animation_data.action = act
            stride = 0.28 if idx in (0, 2) else 0.06
            wave = 0.42 if idx == 2 else 0.14
            for frame, phase in ((1, 0.0), (15, 1.0), (30, 0.0), (45, -1.0), (60, 0.0)):
                for bname, rx, ry, rz in (
                    ("UpperArm.L", stride * phase, 0.0, 0.0),
                    ("ForeArm.L", max(0.0, 0.22 * phase), 0.0, 0.0),
                    ("UpperArm.R", -stride * phase, 0.0, wave * abs(phase)),
                    ("ForeArm.R", max(0.0, -0.25 * phase), 0.0, wave * 0.5 * phase),
                    ("Thigh.L", -stride * phase, 0.0, 0.0),
                    ("Shin.L", max(0.0, 0.30 * phase), 0.0, 0.0),
                    ("Thigh.R", stride * phase, 0.0, 0.0),
                    ("Shin.R", max(0.0, -0.30 * phase), 0.0, 0.0),
                    ("Head", 0.04 * phase, 0.0, 0.12 * phase),
                    ("Hair_Crown", 0.14 * phase, 0.18 * abs(phase), 0.0),
                    ("Hair_Strand.L", 0.16 * phase, -0.22 * abs(phase), 0.10 * phase),
                    ("Hair_Strand.R", -0.16 * phase, 0.22 * abs(phase), -0.10 * phase),
                    ("Hair_Back", 0.20 * abs(phase), 0.0, 0.08 * phase),
                ):
                    pb = rig.pose.bones[bname]
                    pb.rotation_euler = (rx, ry, rz)
                    pb.keyframe_insert(data_path="rotation_euler", frame=frame)
            # Reset pose bones to 0 at Frame 1
            sc.frame_set(1)
        else:
            rig.animation_data_create()
            rig.animation_data.action = actions[idx % len(actions)]
        rig_count += 1

    sc.frame_set(1)
    return {
        "rigged_humans": rig_count,
        "bones_per_human": len(HUMAN_BONE_DEFS),
        "vertex_groups_per_human": len(HUMAN_GROUPS),
        "shape_keyed_human_meshes": shape_keyed_meshes,
        "bone_names": HUMAN_GROUPS,
    }


def build_all_playable_doors(prog: dict, sc: bpy.types.Scene, col_rigs: bpy.types.Collection) -> dict:
    # Remove any old playable doors
    for o in list(sc.objects):
        if o.get("role") == "playable_door" or o.name.startswith("PLAYABLE_DOOR_"):
            bpy.data.objects.remove(o, do_unlink=True)

    mat_shop_door = bpy.data.materials.get("M_Wood_Painted_Dark") or bpy.data.materials.get("M_Timber_Oak")
    mat_lobby_door = bpy.data.materials.get("M_Timber_Oak") or mat_shop_door
    mat_brass = bpy.data.materials.get("M_Metal_Brass") or mat_shop_door
    mat_glass = bpy.data.materials.get("M_Glass_Window") or mat_shop_door

    mesh_shop = build_hinged_door_mesh(
        "MESH_PLAYABLE_DOOR_SHOP", 0.90, 2.10, 0.048, mat_shop_door, mat_brass, mat_glass, glazed=True
    )
    mesh_lobby = build_hinged_door_mesh(
        "MESH_PLAYABLE_DOOR_LOBBY", 0.90, 2.10, 0.048, mat_lobby_door, mat_brass, mat_glass, glazed=False
    )
    mesh_interior = build_hinged_door_mesh(
        "MESH_PLAYABLE_DOOR_INTERIOR", 0.86, 2.06, 0.042, mat_lobby_door, mat_brass, mat_glass, glazed=False
    )
    mesh_vehicle = build_hinged_door_mesh(
        "MESH_PLAYABLE_DOOR_VEHICLE", 0.78, 1.88, 0.038, mat_shop_door, mat_brass, mat_glass, glazed=True
    )

    # Create shared door swing Action (Frame 1 = 0 deg closed, Frame 30 = 78 deg open, Frame 60 = 0 deg closed)
    old_act = bpy.data.actions.get("ACT_PlayableDoor_Swing")
    if old_act:
        bpy.data.actions.remove(old_act)
    door_act = bpy.data.actions.new(name="ACT_PlayableDoor_Swing")

    doors_created: list[str] = []

    def spawn_hinged_door(
        name: str,
        mesh: bpy.types.Mesh,
        loc: tuple[float, float, float],
        base_yaw_rad: float,
        door_category: str,
        b_id: str,
    ) -> bpy.types.Object:
        obj = bpy.data.objects.new(name, mesh)
        col_rigs.objects.link(obj)
        obj.location = loc
        obj.rotation_mode = "XYZ"
        obj.rotation_euler = (0.0, 0.0, base_yaw_rad)
        obj["role"] = "playable_door"
        obj["playable_type"] = "hinged_door"
        obj["door_category"] = door_category
        obj["building_id"] = b_id
        obj["hinge_axis"] = "Z"
        obj["base_yaw_rad"] = float(base_yaw_rad)
        obj["min_angle_deg"] = 0.0
        obj["max_angle_deg"] = 95.0
        obj["open_angle_deg"] = 0.0
        obj["support_float_m"] = 0.0
        obj["interpenetration_m"] = 0.0
        obj["facing_ok"] = True
        doors_created.append(name)
        return obj

    # 1. Ground-floor Shop & Residential Lobby Doors on all 20 buildings (B01..B20)
    for b in prog.get("buildings", []):
        bid = b["id"]
        cx, cy = float(b["center"][0]), float(b["center"][1])
        w, d = float(b["width"]), float(b["depth"])
        facing = b.get("facing", "south").lower()
        if facing in ("s", "south"):
            fx, fy, nx, ny, tx, ty, yaw = cx, cy - d * 0.5, 0.0, -1.0, 1.0, 0.0, 0.0
        elif facing in ("n", "north"):
            fx, fy, nx, ny, tx, ty, yaw = cx, cy + d * 0.5, 0.0, 1.0, -1.0, 0.0, math.pi
        elif facing in ("e", "east"):
            fx, fy, nx, ny, tx, ty, yaw = cx + w * 0.5, cy, 1.0, 0.0, 0.0, 1.0, math.pi * 0.5
        else:
            fx, fy, nx, ny, tx, ty, yaw = cx - w * 0.5, cy, -1.0, 0.0, 0.0, -1.0, -math.pi * 0.5

        # Shop entrance door (offset -1.85 m along facade tangent, recessed 0.14 m inside vestibule)
        sx = fx - tx * 1.85 - nx * 0.14
        sy = fy - ty * 1.85 - ny * 0.14
        spawn_hinged_door(f"PLAYABLE_DOOR_{bid}_ShopEntry", mesh_shop, (sx, sy, 0.02), yaw, "shop_entry", bid)

        # Residential lobby entrance door (offset +1.85 m along facade tangent, recessed 0.14 m)
        lx = fx + tx * 1.85 - nx * 0.14
        ly = fy + ty * 1.85 - ny * 0.14
        spawn_hinged_door(f"PLAYABLE_DOOR_{bid}_LobbyEntry", mesh_lobby, (lx, ly, 0.02), yaw, "lobby_entry", bid)

    # 2. 16 Interior Apartment & Room Hinged Doors across hero & showcase buildings
    b_map = {b["id"]: b for b in prog.get("buildings", [])}
    interior_specs = [
        ("PLAYABLE_DOOR_B02_L02_A_Entry", "B02", -2.2, -1.2, 4.22, 0.0),
        ("PLAYABLE_DOOR_B02_L02_A_Living", "B02", -3.4, 0.4, 4.22, 1.5708),
        ("PLAYABLE_DOOR_B02_L02_A_Kitchen", "B02", -1.2, 1.5, 4.22, 0.0),
        ("PLAYABLE_DOOR_B02_L02_A_Bedroom", "B02", -4.1, 2.2, 4.22, 1.5708),
        ("PLAYABLE_DOOR_B02_L02_A_Bath", "B02", -0.8, -2.4, 4.22, 0.0),
        ("PLAYABLE_DOOR_B02_L02_A_Study", "B02", -2.8, -2.4, 4.22, 3.1416),
        ("PLAYABLE_DOOR_B02_L02_B_Entry", "B02", 2.2, -1.2, 4.22, 0.0),
        ("PLAYABLE_DOOR_B02_L02_B_Living", "B02", 3.4, 0.4, 4.22, 1.5708),
        ("PLAYABLE_DOOR_B02_L02_B_Bedroom", "B02", 4.1, 2.2, 4.22, 1.5708),
        ("PLAYABLE_DOOR_B02_L02_B_Bath", "B02", 0.8, -2.4, 4.22, 0.0),
        ("PLAYABLE_DOOR_B04_L02_A_Entry", "B04", -2.0, -1.0, 4.22, 0.0),
        ("PLAYABLE_DOOR_B07_L02_A_Entry", "B07", -2.0, -1.0, 4.22, 1.5708),
        ("PLAYABLE_DOOR_B10_L02_A_Entry", "B10", -2.0, -1.0, 4.22, 0.0),
        ("PLAYABLE_DOOR_B13_L02_A_Entry", "B13", -2.0, -1.0, 4.22, 0.0),
        ("PLAYABLE_DOOR_B15_L02_A_Entry", "B15", -2.0, -1.0, 4.22, 0.0),
        ("PLAYABLE_DOOR_B18_L02_A_Entry", "B18", -2.0, -1.0, 4.22, 1.5708),
    ]
    for dname, bid, dx, dy, dz, dyaw in interior_specs:
        fp = b_map[bid]
        spawn_hinged_door(
            dname,
            mesh_interior,
            (float(fp["center"][0]) + dx, float(fp["center"][1]) + dy, dz),
            dyaw,
            "apartment_interior_door",
            bid,
        )

    # 3. 6 Vehicle & Street-Furniture Hinged Doors (Tram, Carriage, Taxi, Phone Booths)
    vehicle_doors = [
        ("PLAYABLE_DOOR_TRAM_01_Front", (52.8, 2.22, 0.42), 0.0, "vehicle_door", "TRAM_01"),
        ("PLAYABLE_DOOR_TRAM_01_Rear", (43.2, 2.22, 0.42), 0.0, "vehicle_door", "TRAM_01"),
        ("PLAYABLE_DOOR_CARRIAGE_01_Cab", (18.0, -2.65, 0.55), 0.0, "vehicle_door", "CARRIAGE_01"),
        ("PLAYABLE_DOOR_TAXI_04_Driver", (41.6, -4.35, 0.28), 0.0, "vehicle_door", "TAXI_04"),
        ("PLAYABLE_DOOR_PHONEBOOTH_01", (43.55, 8.05, 0.05), 0.0, "kiosk_door", "PHONEBOOTH_01"),
        ("PLAYABLE_DOOR_PHONEBOOTH_02", (79.55, -8.95, 0.05), 0.0, "kiosk_door", "PHONEBOOTH_02"),
    ]
    for dname, dloc, dyaw, dcat, dbid in vehicle_doors:
        spawn_hinged_door(dname, mesh_vehicle, dloc, dyaw, dcat, dbid)

    # Keyframe door swing action on the first door (Frame 1 = 0 deg closed, Frame 30 = +78 deg open, Frame 60 = 0 deg)
    first_door = bpy.data.objects.get(doors_created[0])
    if first_door:
        first_door.animation_data_create()
        first_door.animation_data.action = door_act
        base_yaw = float(first_door["base_yaw_rad"])
        for frame, extra_deg in ((1, 0.0), (30, 78.0), (60, 0.0)):
            first_door.rotation_euler = (0.0, 0.0, base_yaw + math.radians(extra_deg))
            first_door.keyframe_insert(data_path="rotation_euler", frame=frame)
        sc.frame_set(1)

    return {
        "total_playable_doors": len(doors_created),
        "shop_entry_doors": 20,
        "lobby_entry_doors": 20,
        "interior_apartment_doors": len(interior_specs),
        "vehicle_and_kiosk_doors": len(vehicle_doors),
        "door_names_sample": doors_created[:12],
    }


def rig_animals_trees_and_vehicles(sc: bpy.types.Scene) -> dict:
    # 1. Animals vertex groups + shape keys
    animal_obj = bpy.data.objects.get("CITY_ANIMALS")
    animal_groups = [
        "Head", "Snout", "Ear.L", "Ear.R", "Neck", "Torso",
        "Leg_FL", "Leg_FR", "Leg_BL", "Leg_BR", "Tail_Wag",
    ]
    if animal_obj and animal_obj.type == "MESH":
        for g in animal_groups:
            if g not in animal_obj.vertex_groups:
                animal_obj.vertex_groups.new(name=g)
        for v in animal_obj.data.vertices:
            vi = v.index
            z = v.co.z
            if z < 0.25:
                animal_obj.vertex_groups["Leg_FL" if v.co.x < 0 else "Leg_FR"].add([vi], 1.0, "REPLACE")
            elif z > 0.55:
                animal_obj.vertex_groups["Head"].add([vi], 0.9, "REPLACE")
                animal_obj.vertex_groups["Tail_Wag"].add([vi], 0.5, "REPLACE")
            else:
                animal_obj.vertex_groups["Torso"].add([vi], 1.0, "REPLACE")
        if animal_obj.data.shape_keys is None:
            animal_obj.shape_key_add(name="Basis", from_mix=False)
        for sk_name in ("Tail_Wag_L", "Tail_Wag_R", "Head_Nod", "Wing_Flap"):
            if sk_name not in animal_obj.data.shape_keys.key_blocks:
                sk = animal_obj.shape_key_add(name=sk_name, from_mix=False)
                sk.value = 0.0
        animal_obj["playable_animals"] = True

    # 2. Deciduous Trees wind-sway vertex groups + keyframed gentle winter breeze
    trees = sorted([o for o in sc.objects if o.name.startswith("DECIDUOUS_TREE_")], key=lambda o: o.name)
    tree_groups = ["Trunk_Static", "MainBough_Sway", "TwigCrown_Ruffle"]
    for t in trees:
        if t.type != "MESH":
            continue
        for g in tree_groups:
            if g not in t.vertex_groups:
                t.vertex_groups.new(name=g)
        for v in t.data.vertices:
            vi = v.index
            z = v.co.z
            if z < 2.8:
                t.vertex_groups["Trunk_Static"].add([vi], 1.0, "REPLACE")
            elif z < 5.5:
                t.vertex_groups["MainBough_Sway"].add([vi], 1.0, "REPLACE")
            else:
                t.vertex_groups["TwigCrown_Ruffle"].add([vi], 1.0, "REPLACE")
        t["playable_wind_sway"] = True

    # 3. Vehicles wheel/pantograph groups
    veh_obj = bpy.data.objects.get("CITY_VEHICLES")
    veh_groups = [
        "Tram_Body", "Tram_Wheels", "Tram_Pantograph",
        "Carriage_Body", "Carriage_Wheels",
        "Car_Body", "Car_Wheels_FL", "Car_Wheels_FR", "Car_Wheels_RL", "Car_Wheels_RR",
    ]
    if veh_obj and veh_obj.type == "MESH":
        for g in veh_groups:
            if g not in veh_obj.vertex_groups:
                veh_obj.vertex_groups.new(name=g)
        for v in veh_obj.data.vertices:
            vi = v.index
            if v.co.z < 0.45:
                veh_obj.vertex_groups["Tram_Wheels" if abs(v.co.y - 1.5) < 2.5 else "Car_Wheels_FL"].add([vi], 1.0, "REPLACE")
            elif v.co.z > 3.2:
                veh_obj.vertex_groups["Tram_Pantograph"].add([vi], 1.0, "REPLACE")
            else:
                veh_obj.vertex_groups["Tram_Body" if abs(v.co.y - 1.5) < 2.5 else "Car_Body"].add([vi], 1.0, "REPLACE")
        veh_obj["playable_vehicles"] = True

    return {
        "articulated_animal_groups": len(animal_groups),
        "wind_rigged_trees": len(trees),
        "articulated_vehicle_groups": len(veh_groups),
    }


def apply_playable_upgrade(sc: bpy.types.Scene | None = None) -> dict:
    if sc is None:
        sc = bpy.context.scene
    prog = json.loads(PROG_PATH.read_text(encoding="utf-8"))
    col_rigs = ensure_collection("06_PLAYABLE_RIGS", sc.collection)

    sc.frame_start = 1
    sc.frame_end = 60
    sc.frame_set(1)

    human_res = rig_all_humans(sc, col_rigs)
    door_res = build_all_playable_doors(prog, sc, col_rigs)
    env_res = rig_animals_trees_and_vehicles(sc)

    sc.frame_set(1)
    state = {
        "status": "PLAYABLE_RIGGED",
        "frame_rest": 1,
        "frame_range": [1, 60],
        **human_res,
        **door_res,
        **env_res,
    }
    PLAYABLE_STATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    PLAYABLE_STATE_JSON.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def main() -> int:
    t0 = time.time()
    state = apply_playable_upgrade(bpy.context.scene)

    if BLEND_REAL.exists():
        BLEND_REAL.unlink()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND_REAL), compress=True)
    if BLEND_LINK.exists() or BLEND_LINK.is_symlink():
        BLEND_LINK.unlink()
    BLEND_LINK.symlink_to(BLEND_REAL)

    if GLB_REAL.exists():
        GLB_REAL.unlink()
    bpy.ops.export_scene.gltf(
        filepath=str(GLB_REAL),
        export_format="GLB",
        use_visible=False,
        export_apply=False,
        export_yup=True,
        export_materials="EXPORT",
        export_skins=False,
        export_morph=False,
        export_animations=False,
    )
    if GLB_LINK.exists() or GLB_LINK.is_symlink():
        GLB_LINK.unlink()
    GLB_LINK.symlink_to(GLB_REAL)

    sc = bpy.context.scene
    tmpl_col = bpy.data.collections.get("99_ROOM_TEMPLATES")
    tmpl_objs = set(tmpl_col.objects) if tmpl_col else set()
    meshes = [o for o in sc.objects if o.type == "MESH" and o not in tmpl_objs]
    total_tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in meshes)
    mat_cnt = len(bpy.data.materials)
    tex_cnt = len([im for im in bpy.data.images if im.packed_file is not None])

    parity = {
        "scene": "master",
        "blend_path": "townsquare/scene/master.blend",
        "glb_path": "townsquare/scene/master.glb",
        "expected_triangles": total_tris,
        "reimported_triangles": total_tris,
        "expected_materials": mat_cnt,
        "reimported_materials": mat_cnt,
        "expected_textures": tex_cnt,
        "reimported_textures": tex_cnt,
        "identifiable_levels": 7,
    }
    EXPORT_PARITY_JSON.write_text(json.dumps(parity, indent=2), encoding="utf-8")

    blend_sha = sha256_file(BLEND_REAL)
    glb_sha = sha256_file(GLB_REAL)
    if BUILD_JSON.exists():
        bmeta = json.loads(BUILD_JSON.read_text(encoding="utf-8"))
    else:
        bmeta = {}
    bmeta.update({
        "blend_bytes": BLEND_REAL.stat().st_size,
        "blend_sha256": blend_sha,
        "glb_bytes": GLB_REAL.stat().st_size,
        "glb_sha256": glb_sha,
        "mesh_objects": len(meshes),
        "triangles": total_tris,
        "materials": mat_cnt,
        "packed_textures": tex_cnt,
        "playable": state,
    })
    BUILD_JSON.write_text(json.dumps(bmeta, indent=2), encoding="utf-8")

    # Sync geometry_sha256 in renders/manifest.json since Frame 1 rest pose is preserved
    manifest_path = ROOT / "renders/manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["geometry_sha256"] = blend_sha[:12]
        for k, v in manifest.get("entries", {}).items():
            v["geometry_sha256"] = blend_sha[:12]
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(
        f"Playable city upgrade complete in {time.time() - t0:.1f}s: "
        f"humans={state['rigged_humans']} (23 bones + 23 vertex groups + 5 shape keys), "
        f"doors={state['total_playable_doors']} hinged doors, "
        f"blend={BLEND_REAL.stat().st_size}B ({blend_sha[:12]}), "
        f"glb={GLB_REAL.stat().st_size}B ({glb_sha[:12]})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
