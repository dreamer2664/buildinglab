"""geo.py — meshes, materials and measurement helpers for the PORTUS build.

No texture maps. Every surface is a Principled BSDF fed by procedural noise, or
real geometry (the setts are modelled stones, not a paving image). That is a
deliberate limit of this stage and it is written down in evidence/RIGHTS.md.
"""
from __future__ import annotations

import math

import bmesh
import bpy
from mathutils import Vector

# ── materials ───────────────────────────────────────────────────────────────
# name: (base colour sRGB, roughness, metallic, extra kwargs)
PALETTE = {
    "brick":       ((0.255, 0.108, 0.078), 0.88, 0.0),
    "brick_dark":  ((0.185, 0.078, 0.058), 0.90, 0.0),
    "brick_yellow": ((0.470, 0.330, 0.180), 0.86, 0.0),
    "stucco":      ((0.640, 0.580, 0.470), 0.82, 0.0),
    "stucco_pale": ((0.720, 0.690, 0.610), 0.84, 0.0),
    "stone":       ((0.520, 0.490, 0.440), 0.75, 0.0),
    "concrete":    ((0.430, 0.420, 0.400), 0.80, 0.0),
    "cladding":    ((0.390, 0.420, 0.400), 0.60, 0.35),
    "steel":       ((0.290, 0.300, 0.310), 0.45, 0.85),
    "steel_dark":  ((0.120, 0.125, 0.130), 0.50, 0.80),
    "iron":        ((0.075, 0.078, 0.080), 0.55, 0.75),
    "rust":        ((0.330, 0.140, 0.070), 0.90, 0.20),
    "brass":       ((0.610, 0.440, 0.160), 0.32, 0.95),
    "timber":      ((0.330, 0.210, 0.120), 0.70, 0.0),
    "timber_pale": ((0.520, 0.390, 0.240), 0.72, 0.0),
    "timber_dark": ((0.170, 0.105, 0.062), 0.66, 0.0),
    "slate":       ((0.145, 0.155, 0.170), 0.72, 0.0),
    "clay":        ((0.420, 0.180, 0.110), 0.78, 0.0),
    "sett":        ((0.165, 0.158, 0.150), 0.86, 0.0),
    "sett_warm":   ((0.345, 0.312, 0.278), 0.84, 0.0),
    "paving":      ((0.205, 0.192, 0.175), 0.90, 0.0),
    "asphalt":     ((0.098, 0.098, 0.102), 0.92, 0.0),
    "ballast":     ((0.230, 0.215, 0.195), 0.95, 0.0),
    "sand":        ((0.230, 0.198, 0.150), 0.94, 0.0),
    "mud":         ((0.120, 0.105, 0.085), 0.95, 0.0),
    "glass":       ((0.330, 0.380, 0.400), 0.06, 0.0, dict(transmission=0.92, ior=1.45)),
    "glass_dirty": ((0.280, 0.300, 0.300), 0.20, 0.0, dict(transmission=0.72, ior=1.45)),
    "water":       ((0.035, 0.070, 0.075), 0.045, 0.0, dict(transmission=0.86, ior=1.333)),
    "ice":         ((0.620, 0.720, 0.780), 0.22, 0.0, dict(transmission=0.45, ior=1.31)),
    "foam":        ((0.780, 0.800, 0.800), 0.55, 0.0, dict(alpha=0.75)),
    "plaster":     ((0.700, 0.665, 0.600), 0.88, 0.0),
    "plaster_cool": ((0.640, 0.650, 0.620), 0.90, 0.0),
    "wood_floor":  ((0.290, 0.180, 0.098), 0.62, 0.0),
    "tile":        ((0.660, 0.660, 0.640), 0.30, 0.0),
    "tile_dark":   ((0.180, 0.200, 0.210), 0.35, 0.0),
    "fabric_red":  ((0.330, 0.090, 0.080), 0.92, 0.0),
    "fabric_green": ((0.110, 0.180, 0.130), 0.92, 0.0),
    "fabric_blue": ((0.110, 0.140, 0.230), 0.92, 0.0),
    "fabric_ochre": ((0.520, 0.360, 0.120), 0.92, 0.0),
    "fabric_grey": ((0.330, 0.330, 0.340), 0.94, 0.0),
    "paper":       ((0.780, 0.755, 0.700), 0.85, 0.0),
    "ceramic":     ((0.820, 0.820, 0.800), 0.20, 0.0),
    "enamel":      ((0.760, 0.760, 0.740), 0.24, 0.0),
    "copper_pot":  ((0.430, 0.220, 0.120), 0.38, 0.75),
    "rope":        ((0.430, 0.360, 0.230), 0.90, 0.0),
    "canvas":      ((0.680, 0.620, 0.480), 0.90, 0.0),
    "leaf":        ((0.090, 0.180, 0.080), 0.78, 0.0),
    "terracotta":  ((0.430, 0.200, 0.120), 0.85, 0.0),
    "skin":        ((0.520, 0.330, 0.240), 0.62, 0.0),
    "hair":        ((0.070, 0.055, 0.045), 0.72, 0.0),
    "cloth_navy":  ((0.075, 0.095, 0.150), 0.93, 0.0),
    "cloth_grey":  ((0.190, 0.190, 0.190), 0.93, 0.0),
    "cloth_olive": ((0.180, 0.170, 0.110), 0.93, 0.0),
    "boot":        ((0.085, 0.065, 0.055), 0.80, 0.0),
    "paint_red":   ((0.420, 0.120, 0.090), 0.45, 0.10),
    "paint_blue":  ((0.090, 0.150, 0.300), 0.45, 0.10),
    "paint_green": ((0.090, 0.220, 0.140), 0.45, 0.10),
    "paint_white": ((0.760, 0.760, 0.740), 0.42, 0.05),
    "lamp_warm":   ((0.900, 0.720, 0.480), 0.40, 0.0, dict(emission=1.00, emit_color=(1.0, 0.72, 0.44))),
    "lamp_cool":   ((0.780, 0.860, 0.980), 0.40, 0.0, dict(emission=1.00, emit_color=(0.86, 0.93, 1.0))),
    "hull":        ((0.115, 0.130, 0.140), 0.55, 0.25),
    "hull_red":    ((0.320, 0.085, 0.070), 0.62, 0.10),
    "deck":        ((0.240, 0.235, 0.220), 0.80, 0.10),
    "hatch":       ((0.180, 0.190, 0.195), 0.70, 0.30),
    "crane_yellow": ((0.560, 0.420, 0.090), 0.45, 0.25),
    "signal":      ((0.700, 0.120, 0.090), 0.35, 0.0, dict(emission=2.5, emit_color=(1.0, 0.16, 0.10))),
}


def _set_input(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return True
    return False


def make_material(name):
    """Principled material with a small procedural break-up on the albedo."""
    spec = PALETTE[name]
    col, rough, metal = spec[0], spec[1], spec[2]
    extra = spec[3] if len(spec) > 3 else {}
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    _set_input(bsdf, ["Base Color"], (*col, 1.0))
    _set_input(bsdf, ["Roughness"], rough)
    _set_input(bsdf, ["Metallic"], metal)
    if "transmission" in extra:
        _set_input(bsdf, ["Transmission Weight", "Transmission"], extra["transmission"])
    if "ior" in extra:
        _set_input(bsdf, ["IOR"], extra["ior"])
    if "alpha" in extra:
        _set_input(bsdf, ["Alpha"], extra["alpha"])
    if "emission" in extra:
        _set_input(bsdf, ["Emission Strength"], extra["emission"])
        ec = extra.get("emit_color", col)
        _set_input(bsdf, ["Emission Color", "Emission"], (*ec, 1.0))
    # procedural mottling: Noise -> Mix, only where it can help (rough surfaces)
    if name == "paving":
        tex = nt.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = 1.0
        tex.inputs["Mortar Size"].default_value = 0.012
        tex.inputs["Brick Width"].default_value = 1.10
        tex.inputs["Row Height"].default_value = 0.75
        tex.inputs["Color1"].default_value = (*col, 1.0)
        tex.inputs["Color2"].default_value = (col[0] * 0.97, col[1] * 0.97, col[2] * 0.96, 1.0)
        tex.inputs["Mortar"].default_value = (0.20, 0.19, 0.18, 1.0)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.7
        bump.inputs["Distance"].default_value = 0.035
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        return m
    if name in ("brick", "brick_dark", "brick_yellow") and True:
        tex = nt.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = 1.0
        tex.inputs["Mortar Size"].default_value = 0.011
        tex.inputs["Brick Width"].default_value = 0.215
        tex.inputs["Row Height"].default_value = 0.075
        tex.inputs["Color1"].default_value = (*col, 1.0)
        tex.inputs["Color2"].default_value = (*(c * 0.86 for c in col), 1.0)
        tex.inputs["Mortar"].default_value = (col[0] * 0.62, col[1] * 0.60, col[2] * 0.58, 1.0)
        mapping = nt.nodes.new("ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nt.links.new(tc.outputs["Object"], mapping.inputs["Vector"])
        nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 1.0
        bump.inputs["Distance"].default_value = 0.016
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
        return m
    if name in ("stucco", "stucco_pale", "stone",
                "concrete", "sett", "sett_warm", "timber", "timber_pale", "plaster",
                "cladding", "slate", "clay", "sand", "mud", "ballast", "wood_floor"):
        tex = nt.nodes.new("ShaderNodeTexNoise")
        tex.inputs["Scale"].default_value = 55.0 if name.startswith("sett") else 18.0
        tex.inputs["Detail"].default_value = 4.0
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        dark = tuple(c * 0.72 for c in col)
        light = tuple(min(1.0, c * 1.22) for c in col)
        ramp.color_ramp.elements[0].color = (*dark, 1.0)
        ramp.color_ramp.elements[1].color = (*light, 1.0)
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12 if "sett" not in name else 0.25
        bump.inputs["Distance"].default_value = 0.004
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def build_materials():
    return {n: make_material(n) for n in PALETTE}


# ── collections ─────────────────────────────────────────────────────────────
def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


# ── mesh primitives ────────────────────────────────────────────────────────
def _new_obj(name, verts, faces, mat, collection):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.validate(verbose=False)
    me.update()
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    collection.objects.link(ob)
    return ob


def box(name, x0, y0, z0, x1, y1, z1, mat, collection, rot_z=0.0):
    """Axis-aligned box, optionally rotated about its centre in plan."""
    xa, xb = min(x0, x1), max(x0, x1)
    ya, yb = min(y0, y1), max(y0, y1)
    za, zb = min(z0, z1), max(z0, z1)
    cx, cy = (xa + xb) / 2.0, (ya + yb) / 2.0
    hx, hy = (xb - xa) / 2.0, (yb - ya) / 2.0
    v = [(-hx, -hy, 0), (hx, -hy, 0), (hx, hy, 0), (-hx, hy, 0),
         (-hx, -hy, 1), (hx, -hy, 1), (hx, hy, 1), (-hx, hy, 1)]
    c, s = math.cos(rot_z), math.sin(rot_z)
    verts = [(cx + x * c - y * s, cy + x * s + y * c, za if z == 0 else zb) for (x, y, z) in v]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return _new_obj(name, verts, faces, mat, collection)


def box_c(name, cx, cy, z0, sx, sy, sz, mat, collection, rot_z=0.0):
    return box(name, cx - sx / 2, cy - sy / 2, z0, cx + sx / 2, cy + sy / 2, z0 + sz,
               mat, collection, rot_z)


def cyl(name, cx, cy, z0, r, h, mat, collection, seg=12, r_top=None, axis="Z"):
    """Cylinder; axis Z by default, or X/Y for rails, pipes, ropes' end fittings."""
    r_top = r if r_top is None else r_top
    verts, faces = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        ca, sa = math.cos(a), math.sin(a)
        if axis == "Z":
            verts.append((cx + r * ca, cy + r * sa, z0))
            verts.append((cx + r_top * ca, cy + r_top * sa, z0 + h))
        elif axis == "X":
            verts.append((cx, cy + r * ca, z0 + r * sa))
            verts.append((cx + h, cy + r_top * ca, z0 + r_top * sa))
        else:
            verts.append((cx + r * ca, cy, z0 + r * sa))
            verts.append((cx + r_top * ca, cy + h, z0 + r_top * sa))
    for i in range(seg):
        a, b = 2 * i, 2 * i + 1
        c, d = 2 * ((i + 1) % seg), 2 * ((i + 1) % seg) + 1
        faces.append((a, c, d, b))
    faces.append(tuple(range(0, 2 * seg, 2))[::-1])
    faces.append(tuple(range(1, 2 * seg, 2)))
    return _new_obj(name, verts, faces, mat, collection)


def sphere(name, cx, cy, cz, r, mat, collection, seg=12, rings=8, scale=(1, 1, 1)):
    verts, faces = [], []
    for j in range(rings + 1):
        phi = math.pi * j / rings
        for i in range(seg):
            th = 2 * math.pi * i / seg
            verts.append((cx + r * scale[0] * math.sin(phi) * math.cos(th),
                          cy + r * scale[1] * math.sin(phi) * math.sin(th),
                          cz + r * scale[2] * math.cos(phi)))
    for j in range(rings):
        for i in range(seg):
            a = j * seg + i
            b = j * seg + (i + 1) % seg
            c = (j + 1) * seg + (i + 1) % seg
            d = (j + 1) * seg + i
            faces.append((a, b, c, d))
    return _new_obj(name, verts, faces, mat, collection)


def grid_plane(name, x0, y0, x1, y1, z, mat, collection, nx=40, ny=20, disp=None):
    verts, faces = [], []
    for j in range(ny + 1):
        y = y0 + (y1 - y0) * j / ny
        for i in range(nx + 1):
            x = x0 + (x1 - x0) * i / nx
            zz = z + (disp(x, y) if disp else 0.0)
            verts.append((x, y, zz))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    return _new_obj(name, verts, faces, mat, collection)


def merged(name, parts, mat, collection):
    """parts: list of (x0,y0,z0,x1,y1,z1). One object, many boxes."""
    verts, faces = [], []
    for (x0, y0, z0, x1, y1, z1) in parts:
        xa, xb = min(x0, x1), max(x0, x1)
        ya, yb = min(y0, y1), max(y0, y1)
        za, zb = min(z0, z1), max(z0, z1)
        o = len(verts)
        verts += [(xa, ya, za), (xb, ya, za), (xb, yb, za), (xa, yb, za),
                  (xa, ya, zb), (xb, ya, zb), (xb, yb, zb), (xa, yb, zb)]
        faces += [(o + 0, o + 3, o + 2, o + 1), (o + 4, o + 5, o + 6, o + 7),
                  (o + 0, o + 1, o + 5, o + 4), (o + 1, o + 2, o + 6, o + 5),
                  (o + 2, o + 3, o + 7, o + 6), (o + 3, o + 0, o + 4, o + 7)]
    return _new_obj(name, verts, faces, mat, collection)


def tri_count(ob):
    me = ob.data
    if ob.type != "MESH":
        return 0
    return sum(len(p.vertices) - 2 for p in me.polygons)


def world_bounds(ob):
    """Axis-aligned world bounding box (x0,y0,z0,x1,y1,z1)."""
    mw = ob.matrix_world
    xs, ys, zs = [], [], []
    for v in ob.data.vertices:
        p = mw @ v.co
        xs.append(p.x)
        ys.append(p.y)
        zs.append(p.z)
    if not xs:
        return (0, 0, 0, 0, 0, 0)
    return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))


def rope(name, p0, p1, sag, r, mat, collection, seg=8, n=16):
    """Catenary-ish rope between two points, hanging by `sag` at midspan."""
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    verts, faces = [], []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = y0 + (y1 - y0) * t
        z = z0 + (z1 - z0) * t - sag * math.sin(math.pi * t)
        # local frame along the rope
        if i < n:
            t2 = (i + 1) / n
            dx = (x1 - x0) / n
            dy = (y1 - y0) / n
            dz = (z1 - z0) / n - sag * math.pi * math.cos(math.pi * t) / n
        else:
            dx, dy, dz = x - x0, y - y0, z - z0
        L = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
        ax, ay, az = dx / L, dy / L, dz / L
        # any perpendicular
        px, py, pz = (-ay, ax, 0.0) if abs(az) < 0.9 else (0.0, -az, ay)
        pl = math.sqrt(px * px + py * py + pz * pz) or 1.0
        px, py, pz = px / pl, py / pl, pz / pl
        qx = ay * pz - az * py
        qy = az * px - ax * pz
        qz = ax * py - ay * px
        for k in range(seg):
            a = 2 * math.pi * k / seg
            ca, sa = math.cos(a), math.sin(a)
            verts.append((x + r * (px * ca + qx * sa),
                          y + r * (py * ca + qy * sa),
                          z + r * (pz * ca + qz * sa)))
    for i in range(n):
        for k in range(seg):
            a = i * seg + k
            b = i * seg + (k + 1) % seg
            c = (i + 1) * seg + (k + 1) % seg
            d = (i + 1) * seg + k
            faces.append((a, b, c, d))
    return _new_obj(name, verts, faces, mat, collection)


def mirror_x(ob):
    """Mirror an object about the world YZ plane (not used for placed props)."""
    ob.scale.x *= -1
    return ob
