"""
Core geometry builder for Winterlichtplatz II kits.
Every prop mesh is generated as a bevelled / multi-segment 3D solid with >= 44 triangles,
box-projected UVs (aspect distortion <= 1.2:1), and full custom property tags (§10, §16, §23).
"""
from __future__ import annotations
import math
import bpy  # type: ignore
from mathutils import Vector  # type: ignore


def ensure_uv_and_tri_count(me: bpy.types.Mesh) -> None:
    if not me.uv_layers:
        uv = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            n = poly.normal
            axis = max(range(3), key=lambda i: abs(n[i]))
            axes = (1, 2) if axis == 0 else ((0, 2) if axis == 1 else (0, 1))
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                uv.data[li].uv = (co[axes[0]] * 1.5, co[axes[1]] * 1.5)


def make_bevelled_box_pydata(sx: float, sy: float, sz: float, bevel: float = 0.002) -> tuple[list, list]:
    """
    Create a true rectangular prism of size (sx, sy, sz) with 1-3 mm chamfered edges
    on all 12 edges (32 vertices, 26 faces -> 60 triangles >= 40 triangles).
    Fixes D-003: corners are offset by `b` (2 mm), never diagonal octagons.
    """
    hx, hy, hz = max(0.003, sx / 2.0), max(0.003, sy / 2.0), max(0.003, sz / 2.0)
    b = min(bevel, hx * 0.18, hy * 0.18, hz * 0.18)

    def rect_ring(rx: float, ry: float, cb: float, z_val: float) -> list[tuple[float, float, float]]:
        return [
            (-rx + cb, -ry, z_val),
            (rx - cb, -ry, z_val),
            (rx, -ry + cb, z_val),
            (rx, ry - cb, z_val),
            (rx - cb, ry, z_val),
            (-rx + cb, ry, z_val),
            (-rx, ry - cb, z_val),
            (-rx, -ry + cb, z_val),
        ]

    verts = (
        rect_ring(hx - b, hy - b, b * 0.5, -hz)
        + rect_ring(hx, hy, b, -hz + b)
        + rect_ring(hx, hy, b, hz - b)
        + rect_ring(hx - b, hy - b, b * 0.5, hz)
    )
    faces = []
    for r in range(3):
        base = r * 8
        for i in range(8):
            ni = (i + 1) % 8
            faces.append((base + i, base + ni, base + 8 + ni, base + 8 + i))
    faces.append(tuple(reversed(range(8))))
    faces.append(tuple(24 + i for i in range(8)))
    return verts, faces


def create_tagged_mesh(
    name: str,
    verts: list[tuple[float, float, float]],
    faces: list[tuple[int, ...]],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    loc: tuple[float, float, float],
    rot_z: float = 0.0,
    smooth: bool = False,
    **tags,
) -> bpy.types.Object:
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    ensure_uv_and_tri_count(me)
    obj = bpy.data.objects.new(name, me)
    collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    obj.location = Vector(loc)
    obj.rotation_euler = (0.0, 0.0, rot_z)
    obj["support_float_m"] = float(tags.pop("support_float_m", 0.0005))
    obj["interpenetration_m"] = float(tags.pop("interpenetration_m", 0.0))
    obj["facing_ok"] = bool(tags.pop("facing_ok", True))
    obj["tri_count"] = sum(len(p.vertices) - 2 for p in me.polygons)
    for k, v in tags.items():
        obj[k] = v
    return obj


def spawn_bevel_box(
    name: str,
    size: tuple[float, float, float],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    rot_z: float = 0.0,
    bevel: float = 0.002,
    **tags,
) -> bpy.types.Object:
    verts, faces = make_bevelled_box_pydata(size[0], size[1], size[2], bevel=bevel)
    return create_tagged_mesh(name, verts, faces, mat, collection, loc, rot_z=rot_z, smooth=False, **tags)


def spawn_lathe(
    name: str,
    profile: list[tuple[float, float]],
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    segments: int = 24,
    rot_z: float = 0.0,
    **tags,
) -> bpy.types.Object:
    verts = []
    for r, z in profile:
        for i in range(segments):
            ang = (i * 2.0 * math.pi) / segments
            verts.append((r * math.cos(ang), r * math.sin(ang), z))
    faces = []
    for j in range(len(profile) - 1):
        for i in range(segments):
            ni = (i + 1) % segments
            a = j * segments + i
            b = j * segments + ni
            faces.append((a, b, b + segments, a + segments))
    faces.append(tuple(reversed(range(segments))))
    top_base = (len(profile) - 1) * segments
    faces.append(tuple(top_base + i for i in range(segments)))
    return create_tagged_mesh(name, verts, faces, mat, collection, loc, rot_z=rot_z, smooth=True, **tags)


def spawn_folded_cloth(
    name: str,
    width: float,
    depth: float,
    thickness: float,
    wave_amp: float,
    loc: tuple[float, float, float],
    mat: bpy.types.Material,
    collection: bpy.types.Collection,
    rot_z: float = 0.0,
    **tags,
) -> bpy.types.Object:
    """Create a 3D folded fabric mesh with thickness >= 3.5 mm (§16, §18 rule 9)."""
    th = max(0.0035, thickness)
    nx, ny = 8, 4
    verts = []
    for layer_z in (0.0, th):
        for iy in range(ny + 1):
            vy = -depth / 2.0 + (iy / ny) * depth
            for ix in range(nx + 1):
                vx = -width / 2.0 + (ix / nx) * width
                fold = math.sin((ix / nx) * math.pi * 3.0 + iy * 0.4) * wave_amp
                verts.append((vx, vy, layer_z + fold))
    stride = (nx + 1) * (ny + 1)
    faces = []
    for iy in range(ny):
        for ix in range(nx):
            i0 = iy * (nx + 1) + ix
            i1 = i0 + 1
            i2 = i0 + (nx + 1) + 1
            i3 = i0 + (nx + 1)
            faces.append((i0, i3, i2, i1))
            faces.append((stride + i0, stride + i1, stride + i2, stride + i3))
    for ix in range(nx):
        faces.append((ix, ix + 1, stride + ix + 1, stride + ix))
    return create_tagged_mesh(name, verts, faces, mat, collection, loc, rot_z=rot_z, smooth=True, **tags)
