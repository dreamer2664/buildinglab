"""props.py — furniture and clutter.

Rules this file keeps:

* every prop is **one object** (the density gate counts objects, not pieces);
* every prop carries **real geometry**: parts are bevelled cubes (44+ triangles
  each) and cylinders, never a single flat quad pretending to be a chair;
* nothing is placed in a doorway: the room's door rectangle plus a 1.05 m
  approach is a keep-out zone handed to the placer, and a post-pass translates
  any straggler along the inward normal (defect D-107);
* placement is deterministic: one RNG seeded from the apartment signature.
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy

from . import geo


# ── one object from many bevelled boxes ────────────────────────────────────
def item(name, parts, mat, collection, bevel=0.008):
    """parts: [(x0,y0,z0,x1,y1,z1), ...] merged, then every edge bevelled once.

    A bevel turns a 12-triangle box into 44 triangles and a highlight; that is
    what keeps a bookshelf shelf from reading as a plane.
    """
    bm = bmesh.new()
    for (x0, y0, z0, x1, y1, z1) in parts:
        xa, xb = min(x0, x1), max(x0, x1)
        ya, yb = min(y0, y1), max(y0, y1)
        za, zb = min(z0, z1), max(z0, z1)
        vs = [bm.verts.new(v) for v in (
            (xa, ya, za), (xb, ya, za), (xb, yb, za), (xa, yb, za),
            (xa, ya, zb), (xb, ya, zb), (xb, yb, zb), (xa, yb, zb))]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                  (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            try:
                bm.faces.new([vs[i] for i in f])
            except ValueError:
                pass
    bm.normal_update()
    if bevel > 0:
        # a 8 mm bevel on a 10 mm plate collapses it into zero-area faces.
        # Cap the offset at a quarter of the thinnest dimension of the item.
        thin = min(min(abs(p[3] - p[0]), abs(p[4] - p[1]), abs(p[5] - p[2])) for p in parts)
        off = min(bevel, max(0.0008, thin * 0.25))
        geom = list(bm.edges)
        try:
            bmesh.ops.bevel(bm, geom=geom, offset=off, segments=1,
                            affect="EDGES", clamp_overlap=True, profile=0.5)
        except TypeError:                       # older signature
            bmesh.ops.bevel(bm, geom=geom, offset=off, segments=1, profile=0.5)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate(verbose=False)
    ob = bpy.data.objects.new(name, me)
    if mat is not None:
        ob.data.materials.append(mat)
    collection.objects.link(ob)
    return ob


def cylinder(name, cx, cy, z0, r, h, mat, collection, seg=12, r_top=None):
    return geo.cyl(name, cx, cy, z0, r, h, mat, collection, seg=seg, r_top=r_top)


# ── a room and its keep-out rules ──────────────────────────────────────────
class Room:
    """Local coordinates: (0,0) is the room's south-west corner, metres."""

    def __init__(self, room, level_z, collection, mats, rng, prefix="ROOM"):
        self.r = room
        self.id = room["id"] if "id" in room else room.get("name", "room")
        self.w = room["w"]
        self.d = room["d"]
        self.x0 = room["x0"]
        self.y0 = room["y0"]
        self.z = level_z
        self.coll = collection
        self.M = mats
        self.rng = rng
        self.prefix = f"{prefix}_{self.id}"
        self.n = 0
        self.taken = []          # (x0, y0, x1, y1) in local metres
        self.surfaces = []       # (x0, y0, x1, y1, z) tops that can carry clutter
        self.used_surface = []   # (x0, y0, x1, y1, z)
        self.keepout = []        # door approach zones
        self.names = []

    # -- keep-out from the doorway ------------------------------------------
    def add_door(self, door):
        if not door:
            return
        w = door.get("w", 0.9)
        depth = 1.05
        if door["along"] == "y":                     # door in an E/W wall
            x = self.x0 + (door["x"] - self.x0)
            lx = x - self.x0
            ly = door["y"] - self.y0
            if door["side"] == "W":
                self.keepout.append(dict(rect=(-0.2, ly - w / 2 - 0.1, depth, ly + w / 2 + 0.1),
                                         dir=(1.0, 0.0)))
            else:
                self.keepout.append(dict(rect=(self.w - depth, ly - w / 2 - 0.1, self.w + 0.2,
                                               ly + w / 2 + 0.1), dir=(-1.0, 0.0)))
        else:
            lx = door["x"] - self.x0
            ly = door["y"] - self.y0
            if door["side"] == "S":
                self.keepout.append(dict(rect=(lx - w / 2 - 0.1, -0.2, lx + w / 2 + 0.1, depth),
                                         dir=(0.0, 1.0)))
            else:
                self.keepout.append(dict(rect=(lx - w / 2 - 0.1, self.d - depth, lx + w / 2 + 0.1,
                                               self.d + 0.2), dir=(0.0, -1.0)))

    def blocked(self, x0, y0, x1, y1):
        for k in self.keepout:
            a, b, c, d = k["rect"]
            if x0 < c and x1 > a and y0 < d and y1 > b:
                return True
        for (a, b, c, d) in self.taken:
            if x0 < c and x1 > a and y0 < d and y1 > b:
                return True
        return False

    def fits(self, x0, y0, x1, y1, wall_gap=0.04):
        if x0 < wall_gap or y0 < wall_gap or x1 > self.w - wall_gap or y1 > self.d - wall_gap:
            return False
        return not self.blocked(x0, y0, x1, y1)

    def take(self, x0, y0, x1, y1):
        self.taken.append((x0, y0, x1, y1))

    def surface(self, x0, y0, x1, y1, z):
        """Register a top surface that clutter may stand on."""
        self.surfaces.append((x0, y0, x1, y1, z))

    def surface_spot(self, sx, sy, pitch=0.17):
        """First free patch on any registered surface, packed by a fine grid."""
        for (a, b, c, d, z) in self.surfaces:
            y = b + 0.02
            while y + sy <= d - 0.01:
                x = a + 0.02
                while x + sx <= c - 0.01:
                    cell = (x, y, x + sx, y + sy, z)
                    if not any(cell[0] < u[2] and cell[2] > u[0] and cell[1] < u[3]
                               and cell[3] > u[1] and abs(cell[4] - u[4]) < 0.02
                               for u in self.used_surface):
                        self.used_surface.append(cell)
                        return (x, y, z)
                    x += pitch
                y += pitch
        return None

    # -- placement ----------------------------------------------------------
    def spot(self, sx, sy, tries=90, margin=0.10):
        """Random free rectangle for a footprint sx × sy, or None."""
        for _ in range(tries):
            x = self.rng.uniform(margin, max(margin, self.w - sx - margin))
            y = self.rng.uniform(margin, max(margin, self.d - sy - margin))
            if self.fits(x, y, x + sx, y + sy):
                self.take(x, y, x + sx, y + sy)
                return (x, y)
        return None

    def place_against(self, side, sx, sy, along=None, offset=None):
        """Free slot against a wall: side in S,N,W,E."""
        spans = {"S": self.w, "N": self.w, "W": self.d, "E": self.d}[side]
        step = 0.14 if side in ("S", "N") else 0.12
        starts = [offset] if offset is not None else [
            (self.w if side in ("S", "N") else self.d) * k / 7.0 for k in range(8)]
        for s in starts:
            if s is None:
                continue
            for off in (0.0, 0.2, -0.2, 0.4, -0.4, 0.7, -0.7, 1.0):
                a = s + off
                if a < 0.06 or a + (sx if side in ("S", "N") else sy) > spans - 0.06:
                    continue
                if side == "S":
                    x, y = a, 0.06
                elif side == "N":
                    x, y = a, self.d - sy - 0.06
                elif side == "W":
                    x, y = 0.06, a
                else:
                    x, y = self.w - sx - 0.06, a
                if self.fits(x, y, x + sx, y + sy):
                    self.take(x, y, x + sx, y + sy)
                    return (x, y)
        return self.spot(sx, sy)

    # -- object constructors ------------------------------------------------
    def name(self, base):
        self.n += 1
        nm = f"{self.prefix}_{base}_{self.n:03d}"
        self.names.append(nm)
        return nm

    def add(self, base, parts, mat, at=(0.0, 0.0), z=None):
        """Create one prop from local part rectangles, offset to `at`, then to the
        room's **world** origin. Forgetting the last step stacks every room's
        furniture at (0,0) — which is exactly what happened before this fix."""
        ox, oy = at[0] + self.x0, at[1] + self.y0
        z = self.z if z is None else z
        moved = [(px0 + ox, py0 + oy, pz0 + z, px1 + ox, py1 + oy, pz1 + z)
                 for (px0, py0, pz0, px1, py1, pz1) in parts]
        return item(self.name(base), moved, self.M[mat], self.coll)

    def add_cyl(self, base, cx, cy, z0, r, h, mat, seg=12, r_top=None):
        return cylinder(self.name(base), self.x0 + cx, self.y0 + cy, self.z + z0,
                        r, h, self.M[mat], self.coll, seg=seg, r_top=r_top)

    def world(self, lx, ly):
        return (self.x0 + lx, self.y0 + ly)

    def settle_keepout(self, margin=0.0):
        """Translate any prop that still overlaps a doorway approach.

        The placer already refuses those rectangles (D-107); this is the second
        line of defence for props built at fixed offsets by a room builder. Each
        offender moves along the keep-out's inward normal, just far enough.
        """
        moved = 0
        pref = self.prefix + "_"
        for ob in bpy.data.objects:
            if ob.type != "MESH" or not ob.name.startswith(pref):
                continue
            b = geo.world_bounds(ob)
            lx0, ly0, lx1, ly1 = b[0] - self.x0, b[1] - self.y0, b[3] - self.x0, b[4] - self.y0
            for k in self.keepout:
                a, c, e, f = k["rect"]
                if not (lx0 < e and lx1 > a and ly0 < f and ly1 > c):
                    continue
                dx, dy = k["dir"]
                if dx > 0:
                    push = (e + margin) - lx0
                elif dx < 0:
                    push = lx1 - (a - margin)
                elif dy > 0:
                    push = (f + margin) - ly0
                else:
                    push = ly1 - (c - margin)
                if push <= 0:
                    continue
                ob.location.x += dx * push
                ob.location.y += dy * push
                moved += 1
        return moved


# ── furniture catalogues ───────────────────────────────────────────────────
def _clip(v, lo, hi):
    return max(lo, min(hi, v))


def chair(room, x, y, rot=0.0, mat="timber"):
    """Seat, back, four legs, two stretchers: 8 boxes."""
    w, d = 0.46, 0.46
    parts = [(0, 0, 0.42, w, d, 0.47),                       # seat
             (0, d - 0.05, 0.47, w, d, 0.94),                # back panel
             (0.02, 0.02, 0.00, 0.07, 0.07, 0.42),           # legs
             (w - 0.07, 0.02, 0.00, w - 0.02, 0.07, 0.42),
             (0.02, d - 0.07, 0.00, 0.07, d - 0.02, 0.42),
             (w - 0.07, d - 0.07, 0.00, w - 0.02, d - 0.02, 0.42),
             (0.02, 0.02, 0.14, w - 0.02, 0.05, 0.18),       # stretchers
             (0.02, 0.02, 0.14, 0.05, d - 0.02, 0.18)]
    return room.add("chair", parts, mat, at=(x, y))


def table(room, x, y, w, d, h=0.74, mat="timber_pale"):
    parts = [(0, 0, h - 0.04, w, d, h),
             (0.04, 0.04, 0.0, 0.10, 0.10, h - 0.04),
             (w - 0.10, 0.04, 0.0, w - 0.04, 0.10, h - 0.04),
             (0.04, d - 0.10, 0.0, 0.10, d - 0.04, h - 0.04),
             (w - 0.10, d - 0.10, 0.0, w - 0.04, d - 0.04, h - 0.04),
             (0.05, 0.05, h - 0.10, w - 0.05, 0.08, h - 0.05),
             (0.05, d - 0.08, h - 0.10, w - 0.05, d - 0.05, h - 0.05)]
    room.surface(x + 0.03, y + 0.03, x + w - 0.03, y + d - 0.03, h)
    return room.add("table", parts, mat, at=(x, y))


def book(room, x, y, z, w=0.14, d=0.19, t=0.032, mat="fabric_red", lean=True):
    parts = [(0, 0, 0, w, d, t),                       # boards
             (0.004, 0.006, 0.002, w - 0.004, d - 0.006, t * 0.5),
             (0, 0, 0.001, 0.012, d, t - 0.001),       # spine
             (w - 0.01, 0.01, 0.004, w, d - 0.01, t - 0.004),
             (0.02, 0.02, t * 0.5, w - 0.02, d - 0.02, t * 0.58)]
    return room.add("book", parts, mat, at=(x, y), z=z)


def jar(room, x, y, z, h=0.13, r=0.045, mat="glass_dirty"):
    body = room.add_cyl("jar", x + r, y + r, z, r, h * 0.74, mat, seg=12)
    room.add_cyl("jarlid", x + r, y + r, z + h * 0.74, r * 1.04, h * 0.26, "brass", seg=12)
    return body


def crate(room, x, y, w=0.6, d=0.5, h=0.42, mat="timber_pale"):
    parts = [(0, 0, 0, w, 0.02, h), (0, d - 0.02, 0, w, d, h),
             (0, 0, 0, 0.02, d, h), (w - 0.02, 0, 0, w, d, h),
             (0, 0, 0, w, d, 0.02), (0, 0, h - 0.02, w, d, h),
             (0.02, 0.02, 0.02, 0.05, d - 0.02, h - 0.02),
             (w - 0.05, 0.02, 0.02, w - 0.02, d - 0.02, h - 0.02)]
    return room.add("crate", parts, mat, at=(x, y))


def shelf_unit(room, x, y, w, h=1.80, d=0.30, mat="timber", shelves=5):
    """Carcass + shelves + back: a real bookcase, not a slab."""
    parts = [(0, 0, 0, 0.03, d, h), (w - 0.03, 0, 0, w, d, h),
             (0, 0, 0, w, d, 0.03), (0, 0, h - 0.03, w, d, h),
             (0, 0, 0, w, 0.02, h)]
    for k in range(shelves):
        z = 0.03 + (h - 0.06) * k / (shelves - 1)
        parts.append((0.03, 0.02, z - 0.015, w - 0.03, d - 0.02, z + 0.015))
        room.surface(x + 0.03, y + 0.02, x + w - 0.03, y + d - 0.02, z + 0.015)
    return room.add("shelf", parts, mat, at=(x, y))


# ── room builders ──────────────────────────────────────────────────────────
def living(room, palette, density=70):
    r = room
    r.take(0.06, 0.06, 2.2, 0.95)
    sofa_w = min(2.1, r.w * 0.42)
    sofa_x, sofa_y = 0.15, r.d - 0.95
    parts = [(0, 0, 0.14, sofa_w, 0.82, 0.44),                 # base
             (0, 0, 0.44, sofa_w * 0.18, 0.82, 0.90),          # arms
             (sofa_w * 0.82, 0, 0.44, sofa_w, 0.82, 0.90),
             (0, 0.62, 0.44, sofa_w, 0.82, 0.92),              # back
             (0.02, 0.02, 0.04, sofa_w * 0.18, 0.60, 0.16),    # feet
             (sofa_w * 0.82, 0.02, 0.04, sofa_w - 0.02, 0.60, 0.16)]
    for k in range(3):
        parts.append((sofa_w * 0.19 + k * (sofa_w * 0.62 / 3), 0.04, 0.44,
                      sofa_w * 0.19 + (k + 1) * (sofa_w * 0.62 / 3) - 0.01, 0.62, 0.58))
    r.add("sofa", parts, palette.get("sofa", "fabric_red"), at=(sofa_x, sofa_y))
    r.take(sofa_x, sofa_y, sofa_x + sofa_w, sofa_y + 0.82)
    # coffee table
    table(r, sofa_x + 0.25, sofa_y - 0.75, 1.05, 0.55, h=0.40, mat="timber_dark")
    r.take(sofa_x + 0.25, sofa_y - 0.75, sofa_x + 1.30, sofa_y - 0.20)
    # armchair
    _s = r.spot(0.72, 0.78)
    ax, ay = (_s if _s else (None, None))
    if ax is not None:
        chair(r, ax, ay, mat="timber")
    # rug
    _s = r.spot(1.8, 1.2)
    rx, ry = (_s if _s else (None, None))
    if rx is not None:
        r.add("rug", [(0, 0, 0.024, 1.8, 1.2, 0.030), (0.05, 0.05, 0.030, 1.75, 1.15, 0.034)],
              palette.get("rug", "fabric_ochre"), at=(rx, ry))
    # bookcase + books
    bsx = r.place_against("E", 1.05, 0.32)
    if bsx:
        shelf_unit(r, bsx[0], bsx[1], 1.05, h=1.8, d=0.30)
        z0 = 0.05
        for k in range(4):
            for b in range(5):
                book(r, bsx[0] + 0.05 + b * 0.19, bsx[1] + 0.06, r.z + z0 + k * 0.44,
                     w=0.15, d=0.20, t=0.030,
                     mat=["fabric_red", "fabric_green", "fabric_blue", "paper", "fabric_grey"][(k + b) % 5])
    # dining table with four chairs
    _s = r.spot(1.5, 0.95)
    dx, dy = (_s if _s else (None, None))
    if dx is not None:
        table(r, dx, dy, 1.1, 0.75)
        for (cx, cy) in ((dx - 0.55, dy + 0.12), (dx + 1.12, dy + 0.12),
                         (dx + 0.12, dy - 0.55), (dx + 0.62, dy + 0.78)):
            if r.fits(cx, cy, cx + 0.46, cy + 0.46):
                chair(r, cx, cy)
                r.take(cx, cy, cx + 0.46, cy + 0.46)
    # lamps: floor lamp with a shade
    _p = r.place_against("W", 0.34, 0.34)
    lx, ly = (_p if _p else (None, None))
    if lx:
        r.add("lampbase", [(0.10, 0.10, 0.0, 0.24, 0.24, 0.03), (0.155, 0.155, 0.03, 0.185, 0.185, 1.45)],
              "iron", at=(lx, ly))
        r.add("lampshade", [(0.04, 0.04, 1.36, 0.30, 0.30, 1.42), (0.09, 0.09, 1.42, 0.25, 0.25, 1.58)],
              "canvas", at=(lx, ly))
    # pictures on the wall (frames + canvas)
    for k in range(3):
        px = 0.2 + k * 0.55
        if px + 0.4 < r.w - 0.1:
            r.add("picture", [(px, 0.035, 1.35, px + 0.38, 0.055, 1.82),
                              (px + 0.03, 0.055, 1.38, px + 0.35, 0.060, 1.79)],
                  "timber_dark" if k % 2 else "brass")
    # plant
    _p = r.place_against("S", 0.6, 0.6)
    plx, ply = (_p if _p else (None, None))
    if plx:
        r.add("plantpot", [(0.12, 0.12, 0, 0.48, 0.48, 0.34), (0.10, 0.10, 0.34, 0.50, 0.50, 0.40)],
              "terracotta", at=(plx, ply))
        for k in range(6):
            a = k * math.pi / 3
            r.add("plantleaf", [(0.28 + 0.16 * math.cos(a), 0.28 + 0.16 * math.sin(a), 0.40,
                                 0.34 + 0.16 * math.cos(a), 0.34 + 0.16 * math.sin(a), 0.78)],
                  "leaf", at=(plx, ply))
    # curtains at the window
    r.add("curtain_l", [(0.04, 0.02, 0.9, 0.30, 0.10, 2.45), (0.06, 0.10, 0.85, 0.28, 0.13, 2.4)],
          palette.get("curtain", "fabric_grey"))
    # cups and plates on the coffee table
    for k in range(4):
        r.add_cyl("cup", sofa_x + 0.35 + k * 0.22, sofa_y - 0.55, 0.40, 0.035, 0.075, "ceramic", seg=14)
        r.add_cyl("cupbase", sofa_x + 0.35 + k * 0.22, sofa_y - 0.55, 0.40, 0.05, 0.012, "ceramic", seg=14)
    _top_up(r, density, kinds=("book", "crate", "jar", "box"))


def kitchen(room, palette, density=90):
    r = room
    # counter run along one wall
    run = min(r.w - 0.2, 4.2)
    cx, cy = 0.1, 0.06
    parts = []
    n = int(run / 0.6)
    for k in range(n):
        x = cx + k * 0.6
        parts.append((x, cy, 0.0, x + 0.58, cy + 0.60, 0.86))          # carcass
        parts.append((x + 0.02, cy + 0.58, 0.10, x + 0.56, cy + 0.62, 0.78))  # door
        parts.append((x + 0.24, cy + 0.62, 0.70, x + 0.34, cy + 0.65, 0.73))  # handle
    parts.append((cx, cy, 0.86, cx + run, cy + 0.63, 0.90))            # worktop
    r.add("counter", parts, "timber_pale", at=(0, 0))
    r.surface(cx, cy + 0.05, cx + run, cy + 0.60, 0.90)
    r.take(cx, cy, cx + run, cy + 0.63)
    # sink + taps
    r.add("sink", [(cx + 0.7, cy + 0.12, 0.855, cx + 1.3, cy + 0.52, 0.885),
                   (cx + 0.74, cy + 0.16, 0.80, cx + 1.26, cy + 0.48, 0.86)], "steel")
    r.add("tap", [(cx + 0.96, cy + 0.55, 0.90, cx + 1.02, cy + 0.60, 1.22),
                  (cx + 0.96, cy + 0.30, 1.16, cx + 1.02, cy + 0.60, 1.22)], "steel")
    # hob with four burners
    r.add("hob", [(cx + 1.7, cy + 0.10, 0.90, cx + 2.3, cy + 0.55, 0.925)], "iron")
    for (bx, by) in ((1.84, 0.22), (2.14, 0.22), (1.84, 0.44), (2.14, 0.44)):
        r.add_cyl("burner", cx + bx, cy + by, 0.925, 0.075, 0.012, "steel", seg=12)
    # wall cabinets
    parts = []
    m = int(run / 0.6)
    for k in range(m):
        x = cx + k * 0.6
        parts.append((x, cy, 1.55, x + 0.58, cy + 0.34, 2.25))
        parts.append((x + 0.02, cy + 0.34, 1.57, x + 0.56, cy + 0.36, 2.23))
        parts.append((x + 0.24, cy + 0.36, 1.88, x + 0.34, cy + 0.39, 1.91))
    r.add("wallcab", parts, "timber", at=(0, 0))
    r.surface(cx + 0.06, cy + 0.02, cx + run - 0.06, cy + 0.30, 1.55)     # tops of the wall cabinets
    r.surface(cx + 0.05, cy + 0.05, cx + run - 0.05, cy + 0.58, 0.90)     # in the sink run, between items
    # fridge
    _p = r.place_against("E", 0.72, 0.70)
    fx, fy = (_p if _p else (None, None))
    if fx:
        r.add("fridge", [(0, 0, 0, 0.70, 0.68, 1.85), (0.02, 0.68, 0.02, 0.68, 0.71, 1.83),
                         (0.02, 0.68, 0.10, 0.68, 0.70, 0.13)], "enamel", at=(fx, fy))
    # table and chairs
    _s = r.spot(1.2, 0.8)
    tx, ty = (_s if _s else (None, None))
    if tx is not None:
        table(r, tx, ty, 1.0, 0.7)
        for (qx, qy) in ((tx - 0.5, ty + 0.1), (tx + 1.0, ty + 0.1), (tx + 0.28, ty + 0.75)):
            if r.fits(qx, qy, qx + 0.46, qy + 0.46):
                chair(r, qx, qy)
                r.take(qx, qy, qx + 0.46, qy + 0.46)
    # pots, pans, jars on the counter and hanging
    for k in range(6):
        jar(r, cx + 0.15 + k * 0.22, cy + 0.10, 0.90, h=0.18, r=0.05,
            mat=["glass_dirty", "ceramic", "brass"][k % 3])
    for k in range(4):
        p = [(0.0, 0.0, 0.0, 0.24, 0.24, 0.10), (0.02, 0.02, 0.10, 0.22, 0.22, 0.13)]
        r.add("pan", p, "copper_pot", at=(cx + 1.72 + k * 0.27, cy + 0.14), z=r.z + 0.93)
    for k in range(5):
        r.add("plate", [(0, 0, 0, 0.24, 0.24, 0.012), (0.03, 0.03, 0.012, 0.21, 0.21, 0.018)],
              "ceramic", at=(cx + 0.4 + k * 0.27, cy + 0.30), z=r.z + 0.90)
    # cutlery drawer pulled out, utensils in a jar, tea caddy, spice tins:
    # a working kitchen has more objects than surfaces, which is the point
    r.add("drawer", [(cx + 0.10, cy + 0.63, 0.55, cx + 0.60, cy + 0.98, 0.63),
                     (cx + 0.10, cy + 0.63, 0.48, cx + 0.60, cy + 0.66, 0.55)], "timber", at=(0, 0))
    for k in range(9):
        r.add("utensil", [(0, 0, 0, 0.03, 0.16, 0.02), (0.0, 0.14, 0.0, 0.045, 0.20, 0.03)],
              ["steel", "timber", "enamel"][k % 3], at=(cx + 0.14 + k * 0.05, cy + 0.66), z=r.z + 0.63)
    for k in range(6):
        r.add("spice", [(0, 0, 0, 0.06, 0.06, 0.10), (0.005, 0.005, 0.10, 0.055, 0.055, 0.115)],
              ["brass", "enamel", "terracotta"][k % 3], at=(cx + 0.75 + k * 0.085, cy + 0.42), z=r.z + 0.90)
    for k in range(4):
        r.add("teatowel", [(0, 0, 0, 0.22, 0.02, 0.30)], ["paper", "fabric_red"][k % 2],
              at=(cx + 2.45, cy + 0.05 + k * 0.03), z=r.z + 0.52)
    # pantry cupboard: carcass, four shelves, and the things on them
    px, py = r.place_against("N", 1.10, 0.42)
    if px is not None:
        parts = [(0, 0, 0, 1.10, 0.42, 2.10), (1.10, 0.05, 0.05, 1.13, 0.37, 2.05)]
        for k in range(4):
            zk = 0.10 + k * 0.50
            parts.append((0.03, 0.03, zk, 1.07, 0.39, zk + 0.03))
            r.surface(px + 0.03, py + 0.33, px + 1.07, py + 0.69, zk + 0.03)
        r.add("pantry", parts, "timber", at=(px, py))
        for k in range(18):
            r.add("tin", [(0, 0, 0, 0.10, 0.10, 0.13), (0.01, 0.01, 0.13, 0.09, 0.09, 0.15)],
                  ["enamel", "brass", "paint_red", "paint_green"][k % 4],
                  at=(px + 0.08 + (k % 6) * 0.16, py + 0.10), z=r.z + 0.13 + (k // 6) * 0.50)
    _top_up(r, density, kinds=("jar", "crate", "book", "box", "tin"))


def bedroom(room, palette, density=40):
    r = room
    bw, bd = min(1.65, r.w * 0.5), 2.05
    _p = r.place_against("E", bd, bw)
    bx, by = (_p if _p else (None, None))
    if bx is None:
        bx, by = 0.15, 0.15
    parts = [(0, 0, 0.12, bd, bw, 0.42),                        # frame
             (0.03, 0.03, 0.42, bd - 0.03, bw - 0.03, 0.62),    # mattress
             (0, 0, 0.44, 0.06, bw, 1.05),                      # headboard
             (0.06, 0.06, 0.62, bd * 0.62, bw * 0.48, 0.70),    # duvet
             (0.10, bw * 0.52, 0.62, 0.42, bw * 0.52 + 0.42, 0.74),   # pillows
             (0.10, bw * 0.06, 0.62, 0.42, bw * 0.06 + 0.42, 0.74),
             (0.04, 0.04, 0.0, 0.16, 0.16, 0.12),               # legs
             (bd - 0.16, 0.04, 0.0, bd - 0.04, 0.16, 0.12),
             (0.04, bw - 0.16, 0.0, 0.16, bw - 0.04, 0.12),
             (bd - 0.16, bw - 0.16, 0.0, bd - 0.04, bw - 0.04, 0.12)]
    r.add("bed", parts, palette.get("bed", "fabric_blue"), at=(bx, by))
    r.take(bx, by, bx + bd, by + bw)
    # wardrobe
    _p = r.place_against("W", 1.7, 0.60)
    wx, wy = (_p if _p else (None, None))
    if wx:
        parts = [(0, 0, 0, 0.60, 1.70, 2.30),
                 (0.60, 0.02, 0.02, 0.64, 0.84, 2.28), (0.60, 0.86, 0.02, 0.64, 1.68, 2.28),
                 (0.64, 0.78, 0.95, 0.67, 0.82, 1.25), (0.64, 0.88, 0.95, 0.67, 0.92, 1.25)]
        r.add("wardrobe", parts, "timber", at=(wx, wy))
    # bedside tables with lamps
    for k, yy in enumerate((by - 0.55, by + bw + 0.05)):
        if r.fits(bx + 0.1, yy, bx + 0.55, yy + 0.45):
            r.add("bedside", [(0, 0, 0, 0.42, 0.40, 0.55), (0.02, 0.40, 0.08, 0.40, 0.43, 0.42)],
                  "timber_dark", at=(bx + 0.12, yy))
            r.take(bx + 0.12, yy, bx + 0.54, yy + 0.40)
            r.add("bedlamp", [(0.10, 0.10, 0.55, 0.28, 0.28, 0.60), (0.14, 0.14, 0.60, 0.24, 0.24, 0.66),
                              (0.05, 0.05, 0.66, 0.33, 0.33, 0.86)], "canvas", at=(bx + 0.12, yy))
    # rug, pictures, clothes
    _s = r.spot(1.4, 1.0)
    rx, ry = (_s if _s else (None, None))
    if rx is not None:
        r.add("rug", [(0, 0, 0.024, 1.4, 1.0, 0.032)], palette.get("rug", "fabric_green"), at=(rx, ry))
    for k in range(2):
        r.add("picture", [(0.2 + k * 0.6, 0.035, 1.4, 0.62 + k * 0.6, 0.055, 1.85),
                          (0.24 + k * 0.6, 0.055, 1.44, 0.58 + k * 0.6, 0.06, 1.81)], "timber_dark")
    if wx is not None:
        r.surface(wx + 0.02, wy + 0.02, wx + 0.58, wy + 1.68, 2.30)   # wardrobe top
    for k in range(10):
        r.add("shoe", [(0, 0, 0, 0.27, 0.11, 0.09), (0.02, 0.02, 0.09, 0.23, 0.10, 0.13)],
              ["boot", "timber_dark", "fabric_grey"][k % 3], at=(0.10 + k * 0.30, r.d - 0.40))
    for k in range(6):
        r.add("folded", [(0, 0, 0, 0.30, 0.24, 0.07 * (k % 3 + 1))],
              ["fabric_blue", "fabric_grey", "paper"][k % 3], at=(0.10 + k * 0.34, 0.20))
    _top_up(r, density, kinds=("book", "jar", "box", "folded"))


def bathroom(room, palette, density=28):
    r = room
    parts = [(0, 0, 0, 1.65, 0.72, 0.55), (0.06, 0.06, 0.10, 1.59, 0.66, 0.56),
             (0.6, 0.60, 0.55, 1.05, 0.70, 0.60)]
    r.add("bath", parts, "enamel", at=(0.08, 0.08))
    r.take(0.08, 0.08, 1.73, 0.80)
    # basin + pedestal + mirror
    _p = r.place_against("W", 0.55, 0.42)
    bx, by = (_p if _p else (None, None))
    if bx:
        r.add("basin", [(0, 0, 0.78, 0.55, 0.42, 0.88), (0.06, 0.06, 0.30, 0.16, 0.16, 0.78),
                        (0.0, 0.0, 0.88, 0.55, 0.42, 0.90)], "ceramic", at=(bx, by))
        r.add("mirror", [(0.30, 0.02, 1.10, 0.58, 0.05, 1.70), (0.32, 0.05, 1.12, 0.56, 0.06, 1.68)],
              "glass", at=(bx, by))
    # wc
    _p = r.place_against("N", 0.45, 0.65)
    wx, wy = (_p if _p else (None, None))
    if wx:
        r.add("wc", [(0, 0.15, 0, 0.40, 0.65, 0.42), (0.02, 0.02, 0.42, 0.38, 0.50, 0.80),
                     (0.05, 0.20, 0.42, 0.35, 0.62, 0.45)], "ceramic", at=(wx, wy))
    # towel rail, clamped to the room's own width (a fixed 2.9 m put it through
    # the wall in every bathroom narrower than that — the invariant caught it)
    rail_x0 = max(0.20, r.w - 1.10)
    rail_x1 = min(r.w - 0.08, rail_x0 + 0.72)
    if rail_x1 - rail_x0 > 0.30:
        r.add("rail", [(rail_x0, 0.05, 1.15, rail_x1, 0.08, 1.18),
                       (rail_x0, 0.05, 1.05, rail_x1, 0.09, 1.08)], "brass")
        for k in range(3):
            tx = rail_x0 + 0.05 + k * 0.20
            if tx + 0.17 < rail_x1:
                r.add("towel", [(tx, 0.08, 0.95, tx + 0.17, 0.13, 1.15)],
                      ["fabric_grey", "fabric_blue", "paper"][k % 3])
    for k in range(5):
        jar(r, 0.2 + k * 0.12, r.d - 0.2, 0.90, h=0.10, r=0.03,
            mat=["glass_dirty", "ceramic", "brass"][k % 3])
    _top_up(r, density, kinds=("jar", "book"))


def entry(room, palette, density=18):
    r = room
    _p = r.place_against("W", 0.9, 0.30)
    hx, hy = (_p if _p else (None, None))
    if hx:
        parts = [(0, 0, 0.9, 0.30, 0.90, 0.95), (0.05, 0.05, 0.86, 0.28, 0.28, 0.90)]
        for k in range(4):
            parts.append((0.24, 0.10 + k * 0.2, 1.15, 0.28, 0.14 + k * 0.2, 1.35))
        r.add("coatrack", parts, "timber", at=(hx, hy))
    # shoes, mat, console
    for k in range(4):
        r.add("shoe", [(0, 0, 0, 0.28, 0.11, 0.09), (0.02, 0.02, 0.09, 0.24, 0.10, 0.13)],
              "boot", at=(0.15 + k * 0.32, 0.10))
    _s = r.spot(0.8, 0.5)
    mx, my = (_s if _s else (None, None))
    if mx is not None:
        r.add("mat", [(0, 0, 0.024, 0.8, 0.5, 0.032)], "cloth_olive", at=(mx, my))
    _p = r.place_against("E", 0.7, 0.32)
    cx, cy = (_p if _p else (None, None))
    if cx:
        r.add("console", [(0, 0, 0.72, 0.32, 0.70, 0.76), (0.02, 0.02, 0, 0.06, 0.06, 0.72),
                          (0.26, 0.02, 0, 0.30, 0.06, 0.72), (0.02, 0.64, 0, 0.06, 0.68, 0.72),
                          (0.26, 0.64, 0, 0.30, 0.68, 0.72)], "timber_dark", at=(cx, cy))
    _top_up(r, density, kinds=("book", "jar"))


def shop_floor(room, palette, density=150):
    """Sales floor: shelving runs, counter, products, crates, a till."""
    r = room
    # three parallel shelving runs
    run_h = 1.75
    y = 0.5
    runs = 0
    while y + 0.45 < r.d - 0.6 and runs < 4:
        w = min(r.w - 0.4, 5.0)
        x = 0.2
        if r.fits(x, y, x + w, y + 0.42):
            parts = [(0, 0, 0, w, 0.42, 0.05)]
            for k in range(4):
                parts.append((0.02, 0.02, 0.05 + k * 0.42, w - 0.02, 0.42, 0.08 + k * 0.42))
            parts += [(0, 0, 0, 0.03, 0.42, run_h), (w - 0.03, 0, 0, w, 0.42, run_h),
                      (0, 0, run_h - 0.03, w, 0.42, run_h)]
            r.add("shelving", parts, "timber_pale", at=(x, y))
            r.take(x, y, x + w, y + 0.42)
            # products on every shelf
            for k in range(4):
                for b in range(int(w / 0.17)):
                    r.add("product", [(0, 0, 0, 0.11, 0.14, 0.20), (0.01, 0.01, 0.02, 0.10, 0.13, 0.19)],
                          ["paint_red", "paint_blue", "paint_green", "paper", "terracotta"][(k + b) % 5],
                          at=(x + 0.05 + b * 0.17, y + 0.12), z=r.z + 0.05 + k * 0.42)
        runs += 1
        y += 1.15
    # counter with till and scales
    _p = r.place_against("S", 2.2, 0.70)
    cx, cy = (_p if _p else (None, None))
    if cx:
        r.add("counter", [(0, 0, 0, 2.2, 0.70, 0.95), (0.02, 0.02, 0.10, 2.18, 0.68, 0.88),
                          (0.05, 0.70, 0.20, 2.15, 0.73, 0.60)], "timber", at=(cx, cy))
        r.add("till", [(0.3, 0.15, 0.95, 0.7, 0.5, 1.15), (0.35, 0.2, 1.15, 0.65, 0.45, 1.18)], "iron",
              at=(cx, cy))
        r.add("scales", [(1.3, 0.2, 0.95, 1.7, 0.5, 1.02), (1.45, 0.25, 1.02, 1.55, 0.45, 1.20)], "brass",
              at=(cx, cy))
    _top_up(r, density, kinds=("crate", "product", "jar", "box"))


def stock_room(room, palette, density=46):
    r = room
    for k in range(6):
        _p = r.place_against(["W", "E", "N", "W", "E", "N"][k], 0.7, 0.55)
        x, y = (_p if _p else (None, None))
        if x:
            crate(r, x, y, 0.7, 0.55, 0.45)
    for k in range(4):
        _p = r.place_against(["S", "W", "N", "E"][k], 0.55, 0.4)
        x, y = (_p if _p else (None, None))
        if x:
            _sack(r, x, y)
    _top_up(r, density, kinds=("crate", "box", "sack"))


def staff_room(room, palette, density=14):
    r = room
    _s = r.spot(0.9, 0.7)
    tx, ty = (_s if _s else (None, None))
    if tx is not None:
        table(r, tx, ty, 0.8, 0.6)
        for (qx, qy) in ((tx - 0.5, ty), (tx + 0.85, ty)):
            if r.fits(qx, qy, qx + 0.46, qy + 0.46):
                chair(r, qx, qy)
                r.take(qx, qy, qx + 0.46, qy + 0.46)
    _p = r.place_against("N", 0.35, 0.30)
    lx, ly = (_p if _p else (None, None))
    if lx:
        r.add("locker", [(0, 0, 0, 0.30, 0.35, 1.75), (0.30, 0.02, 0.05, 0.33, 0.33, 1.70)], "steel",
              at=(lx, ly))
    _top_up(r, density, kinds=("jar", "book", "box"))


def wc(room, palette, density=6):
    r = room
    r.add("wcpan", [(0.10, 0.15, 0, 0.50, 0.70, 0.42), (0.12, 0.02, 0.42, 0.48, 0.25, 0.80),
                    (0.15, 0.20, 0.42, 0.45, 0.65, 0.45)], "ceramic")
    r.add("basin", [(0.65, 0.06, 0.75, 1.05, 0.34, 0.85), (0.80, 0.06, 0.30, 0.90, 0.16, 0.75)], "ceramic")
    _top_up(r, density, kinds=("jar",))


def warehouse_floor(room, palette, density=60):
    r = room
    n = 0
    for k in range(10):
        _s = r.spot(1.1, 0.9)
        x, y = (_s if _s else (None, None))
        if x is not None:
            crate(r, x, y, 1.1, 0.9, 0.75)
            n += 1
    for k in range(8):
        _s = r.spot(0.6, 0.6)
        x, y = (_s if _s else (None, None))
        if x is not None:
            _sack(r, x, y)
    for k in range(6):
        _s = r.spot(0.5, 0.5)
        x, y = (_s if _s else (None, None))
        if x is not None:
            r.add("barrel", [(0, 0, 0, 0.5, 0.5, 0.55), (0.03, 0.03, 0.10, 0.47, 0.47, 0.14),
                             (0.03, 0.03, 0.40, 0.47, 0.47, 0.44)], "timber_dark", at=(x, y))
    _top_up(r, density, kinds=("crate", "sack", "box"))


def workshop(room, palette, density=80):
    r = room
    _p = r.place_against("N", 1.8, 0.8)
    bx, by = (_p if _p else (None, None))
    if bx:
        parts = [(0, 0, 0, 1.8, 0.8, 0.86), (0.02, 0.02, 0.86, 1.78, 0.78, 0.90),
                 (0.10, 0.60, 0.90, 0.22, 0.75, 0.98)]
        r.add("bench", parts, "timber_pale", at=(bx, by))
        for k in range(8):
            r.add("tool", [(0.05 + k * 0.2, 0.1, 0.90, 0.18 + k * 0.2, 0.16, 0.94),
                           (0.08 + k * 0.2, 0.16, 0.90, 0.14 + k * 0.2, 0.42, 0.925)],
                  ["steel", "rust", "iron"][k % 3], at=(bx, by))
        r.add("vice", [(1.3, 0.25, 0.90, 1.65, 0.55, 1.10), (1.35, 0.30, 1.10, 1.60, 0.50, 1.16)], "iron",
              at=(bx, by))
    for k in range(4):
        _s = r.spot(1.6, 0.5)
        x, y = (_s if _s else (None, None))
        if x is not None:
            r.add("timberstack", [(0, 0, 0.02 * k, 1.6, 0.5, 0.10 + 0.02 * k),
                                  (0.02, 0.02, 0.10 + 0.02 * k, 1.58, 0.48, 0.14 + 0.02 * k)],
                  "timber", at=(x, y))
    _top_up(r, density, kinds=("tool", "crate", "box"))


def stall(room, palette, density=45):
    r = room
    # trestle table down the middle + awning + produce
    tw = min(r.w - 0.3, 2.4)
    r.add("trestle", [(0.15, r.d * 0.35, 0.70, 0.15 + tw, r.d * 0.35 + 0.60, 0.76),
                      (0.25, r.d * 0.35 + 0.05, 0, 0.31, r.d * 0.35 + 0.11, 0.70),
                      (0.05 + tw, r.d * 0.35 + 0.05, 0, 0.11 + tw, r.d * 0.35 + 0.11, 0.70)],
          "timber_pale")
    r.take(0.15, r.d * 0.35, 0.15 + tw, r.d * 0.35 + 0.6)
    r.add("awningpost", [(0.08, 0.08, 0, 0.14, 0.14, 2.30), (tw + 0.06, 0.08, 0, tw + 0.12, 0.14, 2.30)],
          "timber_dark")
    r.add("awning", [(0.0, 0.0, 2.30, tw + 0.2, 0.9, 2.36), (0.0, 0.9, 2.24, tw + 0.2, 1.4, 2.30)],
          "canvas")
    for k in range(6):
        r.add("basket", [(0, 0, 0.76, 0.30, 0.26, 0.90), (0.02, 0.02, 0.80, 0.28, 0.24, 0.94)],
              "timber_pale", at=(0.22 + k * (tw - 0.4) / 6, r.d * 0.35 + 0.1))
        for j in range(4):
            r.add("produce", [(0, 0, 0.90, 0.09, 0.09, 0.99)],
                  ["paint_red", "paint_green", "fabric_ochre", "paint_green"][j % 4],
                  at=(0.26 + k * (tw - 0.4) / 6 + (j % 2) * 0.10, r.d * 0.35 + 0.14 + (j // 2) * 0.10))
    _top_up(r, density, kinds=("produce", "crate", "basket"))


def _sack(room, x, y):
    parts = [(0, 0, 0, 0.38, 0.30, 0.30), (0.02, 0.02, 0.30, 0.36, 0.28, 0.52),
             (0.10, 0.10, 0.52, 0.28, 0.20, 0.56)]
    return room.add("sack", parts, "canvas", at=(x, y))


# ── top-up: clutter that is still modelled ─────────────────────────────────
_CLUTTER = {
    "book": lambda r, x, y, z: book(r, x, y, z + 0.026,
                                    mat=["fabric_red", "fabric_green", "fabric_blue",
                                         "paper", "fabric_grey", "fabric_ochre"][r.n % 6]),
    "jar": lambda r, x, y, z: jar(r, x, y, z, h=0.10 + (r.n % 4) * 0.02),
    "crate": lambda r, x, y, z: crate(r, x, y, w=0.36, d=0.30, h=0.28),
    "box": lambda r, x, y, z: r.add("box", [(0, 0, 0, 0.30, 0.24, 0.18), (0.01, 0.01, 0.18, 0.29, 0.23, 0.20),
                                            (0.10, 0.10, 0.20, 0.20, 0.14, 0.215)],
                                    ["paper", "timber_pale", "canvas"][r.n % 3], at=(x, y), z=z),
    "product": lambda r, x, y, z: r.add("product", [(0, 0, 0, 0.11, 0.14, 0.20), (0.01, 0.01, 0.02, 0.10, 0.13, 0.19)],
                                        ["paint_red", "paint_blue", "paint_green", "paper"][r.n % 4], at=(x, y), z=z),
    "sack": lambda r, x, y, z: _sack(r, x, y),
    "tool": lambda r, x, y, z: r.add("tool", [(0, 0, 0, 0.24, 0.05, 0.03), (0.02, 0.01, 0.03, 0.08, 0.04, 0.10)],
                                     "steel", at=(x, y), z=z),
    "tin": lambda r, x, y, z: r.add("tin", [(0, 0, 0, 0.09, 0.09, 0.12), (0.01, 0.01, 0.12, 0.08, 0.08, 0.14)],
                                    ["enamel", "brass", "paint_red", "paint_green"][r.n % 4], at=(x, y), z=z),
    "folded": lambda r, x, y, z: r.add("folded", [(0, 0, 0, 0.26, 0.20, 0.09), (0.01, 0.01, 0.09, 0.25, 0.19, 0.11)],
                                       ["fabric_blue", "fabric_grey", "paper"][r.n % 3], at=(x, y), z=z),
    "basket": lambda r, x, y, z: r.add("basket", [(0, 0, 0, 0.28, 0.22, 0.14), (0.01, 0.01, 0.10, 0.27, 0.21, 0.15)],
                                      "timber_pale", at=(x, y), z=z),
    "produce": lambda r, x, y, z: r.add("produce", [(0, 0, 0, 0.10, 0.10, 0.10), (0.01, 0.01, 0.02, 0.09, 0.09, 0.09)],
                                       ["paint_red", "paint_green", "fabric_ochre"][r.n % 3], at=(x, y), z=z),
}


def _top_up(room, target, kinds=("book",), max_tries=400):
    """Add clutter until the room has `target` props. Placed on the floor edge or
    on any free patch; never in the doorway, never overlapping."""
    guard = 0
    while room.n < target and guard < max_tries:
        guard += 1
        kind = kinds[room.n % len(kinds)]
        sx = sy = 0.34
        spot = room.spot(sx, sy, tries=12, margin=0.08)
        if spot is None:
            break
        _CLUTTER[kind](room, spot[0], spot[1], room.z + 0.0)
    return room.n


def furnish(room, kind, palette, collection, mats, rng, level_z, door=None, target=None):
    """Build the whole furnishing set for one room and return the Room helper."""
    R = Room(room, level_z, collection, mats, rng)
    R.add_door(door)
    fn = {"living": living, "kitchen": kitchen, "bedroom": bedroom, "bathroom": bathroom,
          "entry": entry, "sales": shop_floor, "stock": stock_room, "staff": staff_room,
          "wc": wc, "warehouse floor": warehouse_floor, "workshop floor": workshop,
          "machine hall": workshop, "joinery": workshop, "stall": stall}.get(kind)
    if fn is None:
        _top_up(R, 18, kinds=("box", "jar"))
        return R
    default = {"living": 70, "kitchen": 90, "bedroom": 40, "bathroom": 28, "entry": 18,
               "sales": 150, "stock": 46, "staff": 14, "wc": 6, "warehouse floor": 60,
               "workshop floor": 80, "machine hall": 80, "joinery": 80, "stall": 45}.get(kind, 18)
    fn(R, palette, density=target or default)
    if R.n < (target or default):
        _top_up(R, target or default, kinds=("box", "jar", "book"))
    R.settle_keepout()
    return R
