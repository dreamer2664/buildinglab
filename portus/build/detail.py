"""PORTUS detail library — architectural elements built as real geometry.

Everything here returns lists of axis-aligned rects ``(x0, y0, z0, x1, y1, z1)``
which the caller merges into one mesh per building. Object count stays flat
while triangle count carries the detail.

Units are metres. The brick module follows UK imperial brickwork:
215 x 65 x 102.5 mm brick, 10 mm joint, 225 mm x 75 mm module.
"""
from __future__ import annotations

import math

BRICK_L = 0.215
BRICK_H = 0.065
JOINT = 0.010
PITCH_U = BRICK_L + JOINT      # 0.225
PITCH_V = BRICK_H + JOINT      # 0.075


# ── face mapping ───────────────────────────────────────────────────────────
def face_map(side, x0, y0, x1, y1, plane, depth):
    """Return (to_world, u_range, v_is_up) for one wall face.

    ``plane`` is the outer face coordinate in the perpendicular axis;
    ``depth`` is how far the element projects outward from that plane.
    ``to_world(u, v, d0, d1)`` gives a rect spanning depth d0..d1 measured
    outward from ``plane``.
    """
    if side == "S":
        return (lambda u, v, d0, d1: (u, plane - d1, v, u, plane - d0, v)), (x0, x1)
    if side == "N":
        return (lambda u, v, d0, d1: (u, plane + d0, v, u, plane + d1, v)), (x0, x1)
    if side == "W":
        return (lambda u, v, d0, d1: (plane - d1, u, v, plane - d0, u, v)), (y0, y1)
    return (lambda u, v, d0, d1: (plane + d0, u, v, plane + d1, u, v)), (y0, y1)


def _rect(side, plane, u0, u1, v0, v1, d0, d1):
    """Build a world rect from face-local coordinates."""
    if side == "S":
        return (u0, plane - d1, v0, u1, plane - d0, v1)
    if side == "N":
        return (u0, plane + d0, v0, u1, plane + d1, v1)
    if side == "W":
        return (plane - d1, u0, v0, plane - d0, u1, v1)
    return (plane + d0, u0, v0, plane + d1, u1, v1)


def _overlaps(a0, a1, b0, b1, slack=0.0):
    return a0 < b1 - slack and a1 > b0 + slack


# ── masonry ────────────────────────────────────────────────────────────────
def brick_wall(side, plane, u0, u1, v0, v1, openings=(), out=0.03,
               brick_l=BRICK_L, brick_h=BRICK_H, joint=JOINT,
               variant_bands=(), max_bricks=None):
    """A brick face as individual bricks, running bond.

    ``out`` is how far the brick faces stand proud of the wall plane; the joint
    behind them is the shadow line that makes the wall read as masonry rather
    than a board. Bricks inside an ``openings`` rect are skipped, so the wall
    is punched, not painted.

    ``variant_bands`` is a list of ``(v_lo, v_hi, material_index)`` used by the
    caller to split headers/stretchers into different merged groups.
    """
    pu = brick_l + joint
    pv = brick_h + joint
    rects = []
    n_v = int((v1 - v0) / pv)
    for j in range(n_v):
        za = v0 + j * pv
        zb = za + brick_h
        if zb > v1 + 1e-6:
            break
        offset = (pu * 0.5) if (j % 2) else 0.0        # running bond
        u = u0 - offset
        while u < u1:
            ua = u
            ub = u + brick_l
            uc, ud = max(ua, u0), min(ub, u1)
            u = ub + joint
            if ud - uc < 0.02:                          # sliver at the end
                continue
            brk = False
            for (ou0, ou1, ov0, ov1) in openings:
                if _overlaps(uc, ud, ou0, ou1) and _overlaps(za, zb, ov0, ov1):
                    brk = True
                    break
            if brk:
                continue
            rects.append(_rect(side, plane, uc, ud, za, zb, -out, 0.0))
            if max_bricks is not None and len(rects) >= max_bricks:
                return rects
    return rects


def coursed_relief(side, plane, u0, u1, v0, v1, openings=(), course=0.15,
                   proud=0.014, every=1, brick_l=0.45, brick_h=0.135):
    """Coarse brickwork: running bond at 0.45 x 0.135 m.

    Not a proud slab course. An earlier version of this drew projecting
    horizontal bands and read as venetian blinds on the facade — the course has
    to be *brick-shaped* to be read as masonry, and it must carry the wall
    material, not the stone. Same function, a third of the cost of full-size
    bricks at 215 mm.
    """
    return brick_wall(side, plane, u0, u1, v0, v1, openings=openings, out=proud,
                      brick_l=brick_l, brick_h=brick_h)


def plinth(side, plane, u0, u1, v0, h=0.55, out=0.05):
    """Chamfered stone base course: bed, body, weathered top."""
    return [
        _rect(side, plane, u0, u1, v0, v0 + 0.10, 0.0, out * 0.6),
        _rect(side, plane, u0, u1, v0 + 0.10, v0 + h - 0.06, 0.0, out),
        _rect(side, plane, u0, u1, v0 + h - 0.06, v0 + h, 0.0, out * 1.35),
    ]


def quoins(side, plane, u_edge, v0, v1, inward, stone_len=0.45, stone_h=0.30,
           out=0.045):
    """Alternating long/short quoin stones up a corner.

    ``inward`` is +1 or -1: the direction into the wall along u.
    """
    rects = []
    v = v0
    k = 0
    while v < v1 - 0.05:
        ln = stone_len if (k % 2 == 0) else stone_len * 0.62
        if k % 2 == 0:
            a, b = (u_edge, u_edge + inward * ln)
        else:
            a, b = (u_edge, u_edge + inward * ln)
        a, b = min(a, b), max(a, b)
        zb = min(v + stone_h - 0.012, v1)
        rects.append(_rect(side, plane, a, b, v, zb, 0.0, out))
        v += stone_h
        k += 1
    return rects


# ── horizontal mouldings ───────────────────────────────────────────────────
def string_course(side, plane, u0, u1, v, depth=0.09, h=0.16):
    """A plat band: shadow gap, weathering slope, top bead."""
    return [
        _rect(side, plane, u0, u1, v, v + 0.04, 0.0, depth * 0.35),
        _rect(side, plane, u0, u1, v + 0.04, v + h - 0.03, 0.0, depth),
        _rect(side, plane, u0, u1, v + h - 0.03, v + h, 0.0, depth * 1.12),
    ]


def cornice(side, plane, u0, u1, v, modulus=0.44, dentil=True):
    """Bed mould, dentil course, corona, cyma recta.

    A cornice is the deepest shadow on the building and does most of the work
    of making a facade read as architecture rather than extrusion.
    """
    rects = [
        _rect(side, plane, u0, u1, v, v + 0.07, 0.0, 0.05),          # bed mould
        _rect(side, plane, u0, u1, v + 0.07, v + 0.17, 0.0, 0.10),   # fascia
    ]
    v1 = v + 0.17
    if dentil:
        n = max(1, int((u1 - u0) / modulus))
        step = (u1 - u0) / n
        for i in range(n):
            a = u0 + i * step + 0.03
            b = a + step * 0.55
            rects.append(_rect(side, plane, a, b, v1, v1 + 0.11, 0.0, 0.14))
    rects.append(_rect(side, plane, u0, u1, v1 + 0.11, v1 + 0.19, 0.0, 0.11))
    rects.append(_rect(side, plane, u0, u1, v1 + 0.19, v1 + 0.29, 0.0, 0.30))  # corona
    rects.append(_rect(side, plane, u0, u1, v1 + 0.29, v1 + 0.38, 0.0, 0.24))  # cyma
    rects.append(_rect(side, plane, u0, u1, v1 + 0.38, v1 + 0.42, 0.0, 0.10))
    return rects


# ── openings ───────────────────────────────────────────────────────────────
def window_opening(side, plane, u0, u1, v0, v1, *, reveal=None,
                   bars=True, shutters=False, box_sash=True, stone=None,
                   proportions="victorian"):
    """A complete window: reveal, stone sill with drip, lintel or flat arch,
    frame, sash meeting rail, glazing bars, and optional shutters.

    Returns ``(masonry, joinery, glass)`` — three rect lists so the caller can
    merge them into three materials. All three carry real depth: the pane sits
    at the back of a 300 mm reveal, so every opening has a genuine shadow.
    """
    w = u1 - u0
    h = v1 - v0
    if reveal is None:
        reveal = min(0.30, w * 0.16)
    masonry, joinery, glass = [], [], []

    # --- reveal: the four returns of the opening, cut back into the wall
    masonry.append(_rect(side, plane, u0, u1, v0, v0 + 0.05, -reveal, 0.02))     # cill bed
    masonry.append(_rect(side, plane, u0, u0 + 0.045, v0, v1, -reveal, 0.02))    # jamb
    masonry.append(_rect(side, plane, u1 - 0.045, u1, v0, v1, -reveal, 0.02))    # jamb
    masonry.append(_rect(side, plane, u0, u1, v1 - 0.045, v1, -reveal, 0.02))    # head

    # --- stone sill, projecting and dripped
    so = 0.055
    masonry.append(_rect(side, plane, u0 - 0.05, u1 + 0.05, v0 - 0.075, v0, 0.0, so))
    masonry.append(_rect(side, plane, u0 - 0.05, u1 + 0.05, v0 - 0.10, v0 - 0.075,
                         0.0, so * 0.55))                                       # drip
    # One stone lintel with a quirked underside. A fan of voussoirs plus a pair
    # of jamb architraves costs five times as much and disappears below 25 px,
    # so the depth they would give is given by the reveal instead.
    masonry.append(_rect(side, plane, u0 - 0.07, u1 + 0.07, v1 + 0.02, v1 + 0.24, 0.0, 0.055))
    masonry.append(_rect(side, plane, u0 - 0.09, u1 + 0.09, v1 + 0.24, v1 + 0.30, 0.0, 0.085))

    # --- frame, set back at the back of the reveal
    d0 = -reveal
    d1 = -reveal + 0.06
    f = 0.055
    joinery.append(_rect(side, plane, u0 + 0.02, u0 + 0.02 + f, v0 + 0.02, v1 - 0.02, d0, d1))
    joinery.append(_rect(side, plane, u1 - 0.02 - f, u1 - 0.02, v0 + 0.02, v1 - 0.02, d0, d1))
    joinery.append(_rect(side, plane, u0 + 0.02, u1 - 0.02, v1 - 0.02 - f, v1 - 0.02, d0, d1))
    joinery.append(_rect(side, plane, u0 + 0.02, u1 - 0.02, v0 + 0.02, v0 + 0.02 + f, d0, d1))

    gu0, gu1 = u0 + 0.02 + f, u1 - 0.02 - f
    gv0, gv1 = v0 + 0.02 + f, v1 - 0.02 - f

    # --- glass at the back of the reveal
    glass.append(_rect(side, plane, gu0, gu1, gv0, gv1, d0 + 0.015, d0 + 0.028))

    # --- glazing bars
    if bars:
        bw = 0.022
        nv = max(1, int(round((gu1 - gu0) / 0.42)))
        nh = max(1, int(round((gv1 - gv0) / 0.42)))
        for i in range(1, nv):
            a = gu0 + (gu1 - gu0) * i / nv
            joinery.append(_rect(side, plane, a - bw / 2, a + bw / 2, gv0, gv1, d0, d1 - 0.02))
        for j in range(1, nh):
            b = gv0 + (gv1 - gv0) * j / nh
            joinery.append(_rect(side, plane, gu0, gu1, b - bw / 2, b + bw / 2, d0, d1 - 0.02))

    # --- sash meeting rail: the strongest horizontal in the window
    if box_sash and h > 0.9:
        mr = (gv0 + gv1) / 2
        joinery.append(_rect(side, plane, gu0, gu1, mr - 0.035, mr + 0.035, d0, d1 - 0.01))

    # --- shutters folded back into the reveal
    if shutters:
        for (a, b) in ((u0 + 0.05, u0 + 0.05 + w * 0.22), (u1 - 0.05 - w * 0.22, u1 - 0.05)):
            joinery.append(_rect(side, plane, a, b, v0 + 0.05, v1 - 0.05, d0 - 0.03, d0))
            for k in range(3):
                zz = v0 + 0.05 + (v1 - v0 - 0.10) * (k + 0.5) / 3
                joinery.append(_rect(side, plane, a + 0.01, b - 0.01, zz - 0.012, zz + 0.012,
                                     d0 - 0.042, d0 - 0.03))
    return masonry, joinery, glass


def door_opening(side, plane, u0, u1, v0, v1, *, reveal=0.16, panels=4,
                 fanlight=True, transom=True):
    """A door: architrave, panelled leaf, fanlight with radiating bars,
    threshold, and a projecting stone surround."""
    w, h = u1 - u0, v1 - v0
    masonry, joinery, glass = [], [], []
    masonry.append(_rect(side, plane, u0, u1, v0, v0 + 0.02, -reveal, 0.02))
    masonry.append(_rect(side, plane, u0, u0 + 0.14, v0, v1, 0.0, 0.07))        # surround
    masonry.append(_rect(side, plane, u1 - 0.14, u1, v0, v1, 0.0, 0.07))
    masonry.append(_rect(side, plane, u0 - 0.10, u1 + 0.10, v1, v1 + 0.26, 0.0, 0.09))
    masonry.append(_rect(side, plane, u0 - 0.10, u1 + 0.10, v1 + 0.26, v1 + 0.30,
                         0.0, 0.12))                                            # hood

    leaf_b = v1 - (0.75 if fanlight else 0.0)
    d0, d1 = -reveal, -reveal + 0.055
    joinery.append(_rect(side, plane, u0 + 0.02, u1 - 0.02, v0 + 0.02, leaf_b, d0 - 0.012, d1))
    # raised panels
    pw = (u1 - u0 - 0.16) / 2
    ph = (leaf_b - v0 - 0.20) / max(1, panels // 2)
    for c in range(2):
        for r in range(max(1, panels // 2)):
            a = u0 + 0.08 + c * (pw + 0.01)
            b = a + pw - 0.03
            za = v0 + 0.10 + r * ph
            zb = za + ph - 0.06
            joinery.append(_rect(side, plane, a, b, za, zb, d0 - 0.030, d0 - 0.012))
    # stile, rail, meeting stile
    joinery.append(_rect(side, plane, u0 + 0.02, u1 - 0.02, leaf_b - 0.06, leaf_b, d1 - 0.02, d1 + 0.02))
    joinery.append(_rect(side, plane, (u0 + u1) / 2 - 0.03, (u0 + u1) / 2 + 0.03,
                         v0 + 0.02, leaf_b, d1 + 0.004, d1 + 0.018))
    # handle
    kh = v0 + 1.05
    joinery.append(_rect(side, plane, u1 - 0.20, u1 - 0.14, kh - 0.05, kh + 0.05, d1 + 0.02, d1 + 0.06))
    # fanlight
    if fanlight:
        glass.append(_rect(side, plane, u0 + 0.05, u1 - 0.05, leaf_b + 0.05, v1 - 0.05,
                           d0 + 0.01, d0 + 0.022))
        joinery.append(_rect(side, plane, u0 + 0.05, u1 - 0.05, leaf_b + 0.01, leaf_b + 0.05,
                             d0, d1))
        if transom:
            cx, cz = (u0 + u1) / 2, (leaf_b + 0.05 + v1 - 0.05) / 2
            for ang in (0, 45, 90, 135):
                r = math.radians(ang)
                dx, dz = math.cos(r) * (w * 0.3), math.sin(r) * (v1 - leaf_b) * 0.4
                joinery.append(_rect(side, plane, cx - abs(dx) - 0.012, cx + abs(dx) + 0.012,
                                     cz - abs(dz) - 0.012, cz + abs(dz) + 0.012,
                                     d0, d0 + 0.02))
    # threshold
    masonry.append(_rect(side, plane, u0 - 0.05, u1 + 0.05, v0 - 0.04, v0 + 0.02, 0.0, 0.10))
    return masonry, joinery, glass


# ── roof ───────────────────────────────────────────────────────────────────
def _slab(origin, ax_u, ax_w, ax_n, uc, wc, nc, su, sw, sn):
    """One oriented box -> (verts, faces). Frame axes are unit vectors."""
    verts = []
    for (du, dw, dn) in ((-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5),
                         (-0.5, 0.5, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5),
                         (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5)):
        p = [origin[k] + ax_u[k] * (uc + du * su) + ax_w[k] * (wc + dw * sw)
             + ax_n[k] * (nc + dn * sn) for k in range(3)]
        verts.append(tuple(p))
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7)]
    return verts, faces


def _norm(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / m for c in v)


def tiled_roof(x0, y0, x1, y1, z_eave, pitch_deg, along="x", *,
               tile_u=0.85, course=0.85, thick=0.028, lap=0.012,
               gutter=True):
    """Two tiled slopes as oriented slabs, plus ridge capping and eaves gutter.

    Each tile is a real solid, offset from its neighbour, so the roof has the
    stepped, shadowed surface of a slate roof instead of a flat plane.
    Returns ``(tile_verts, tile_faces, metal_verts, metal_faces)``.
    """
    tv, tf, mv, mf = [], [], [], []

    def add(dst_v, dst_f, geom):
        v, f = geom
        o = len(dst_v)
        dst_v.extend(v)
        dst_f.extend([tuple(i + o for i in face) for face in f])

    if along == "x":
        span_lo, span_hi = x0, x1
        e0, e1 = y0, y1
        ridge = (y0 + y1) / 2.0
        u_lo, u_hi = x0, x1
        u_ax = (1.0, 0.0, 0.0)
    else:
        span_lo, span_hi = y0, y1
        e0, e1 = x0, x1
        ridge = (x0 + x1) / 2.0
        u_lo, u_hi = y0, y1
        u_ax = (0.0, 1.0, 0.0)

    half = (e1 - e0) / 2.0
    rise = math.tan(math.radians(pitch_deg)) * half
    for sgn in (-1.0, 1.0):                      # the two slopes
        eave = e0 if sgn < 0 else e1
        dy = (ridge - eave)
        dz = rise
        L = math.hypot(dy, dz)
        if along == "x":
            w_ax = _norm((0.0, dy, dz))
            n_ax = _norm((0.0, -dz, dy))
            if sgn > 0:
                n_ax = _norm((0.0, dz, -dy))
            origin = (0.0, eave, z_eave)
        else:
            w_ax = _norm((dy, 0.0, dz))
            n_ax = _norm((-dz, dy, 0.0))
            if sgn > 0:
                n_ax = _norm((dz, -dy, 0.0))
            origin = (eave, 0.0, z_eave)
        n_courses = max(1, int(L / course))
        for j in range(n_courses):
            wc = (j + 0.5) * L / n_courses
            # lower courses sit a little further out: overlapping slates
            nc = thick * 0.5 + (n_courses - j) * lap * 0.06
            n_tiles = max(1, int((u_hi - u_lo) / tile_u))
            for i in range(n_tiles):
                uc = u_lo + (i + 0.5) * (u_hi - u_lo) / n_tiles
                add(tv, tf, _slab(origin, u_ax, w_ax, n_ax, uc, wc, nc,
                                  tile_u * 0.94, L / n_courses * 0.96, thick))
    # ridge capping: one slab per 0.4 m, straddling the apex
    n_ridge = max(1, int((u_hi - u_lo) / 0.40))
    w_ax = (0.0, 1.0, 0.0) if along == "x" else (1.0, 0.0, 0.0)
    n_ax = (0.0, 0.0, 1.0)
    for i in range(n_ridge):
        uc = u_lo + (i + 0.5) * (u_hi - u_lo) / n_ridge
        org = (0.0, ridge, z_eave + rise) if along == "x" else (ridge, 0.0, z_eave + rise)
        add(mv, mf, _slab(org, u_ax, w_ax, n_ax, uc, 0.0, 0.02,
                          0.39, 0.30, 0.09))
    # eaves gutter: a trough at both eaves
    if gutter:
        for sgn in (-1.0, 1.0):
            eave = e0 if sgn < 0 else e1
            org = (0.0, eave, z_eave) if along == "x" else (eave, 0.0, z_eave)
            n_g = max(1, int((u_hi - u_lo) / 1.0))
            for i in range(n_g):
                uc = u_lo + (i + 0.5) * (u_hi - u_lo) / n_g
                add(mv, mf, _slab(org, u_ax, w_ax, n_ax, uc, 0.06 * sgn, -0.05,
                                  (u_hi - u_lo) / n_g * 0.98, 0.13, 0.012))
    return tv, tf, mv, mf


def chimney_stack(cx, cy, z0, h, w=0.95, d=0.62, pots=2):
    """Brick stack with corbel, capping and chimney pots."""
    masonry = []
    # corbel
    masonry.append((cx - w / 2 - 0.09, cy - d / 2 - 0.09, z0, cx + w / 2 + 0.09,
                    cy + d / 2 + 0.09, z0 + 0.20))
    masonry.append((cx - w / 2, cy - d / 2, z0 + 0.20, cx + w / 2, cy + d / 2, z0 + h))
    # capping course
    masonry.append((cx - w / 2 - 0.07, cy - d / 2 - 0.07, z0 + h, cx + w / 2 + 0.07,
                    cy + d / 2 + 0.07, z0 + h + 0.10))
    pots_ = []
    for k in range(pots):
        px = cx - w / 2 + w * (k + 0.5) / pots
        pots_.append((px - 0.10, cy - 0.10, z0 + h + 0.10, px + 0.10, cy + 0.10, z0 + h + 0.55))
        pots_.append((px - 0.12, cy - 0.12, z0 + h + 0.55, px + 0.12, cy + 0.12, z0 + h + 0.64))
    return masonry, pots_


# ── rain goods and ironwork ────────────────────────────────────────────────
def downpipe(side, plane, u, v0, v1, out=0.10):
    """Cast-iron downpipe with brackets, shoe and hopper head."""
    metal = []
    r = 0.055
    metal.append(_rect(side, plane, u - r, u + r, v0, v1, out - r, out + r))
    n = max(2, int((v1 - v0) / 1.8))
    for k in range(n + 1):
        v = v0 + (v1 - v0) * k / n
        metal.append(_rect(side, plane, u - r - 0.02, u + r + 0.02, v - 0.025, v + 0.025,
                           out - r * 0.4, out + r + 0.03))
    metal.append(_rect(side, plane, u - 0.13, u + 0.13, v1 - 0.02, v1 + 0.26,
                       out - 0.14, out + 0.09))                     # hopper
    metal.append(_rect(side, plane, u - r - 0.03, u + r + 0.03, v0 - 0.20, v0,
                       out - r - 0.03, out + 0.02))                 # shoe
    return metal


def tie_plates(side, plane, u0, u1, v, pitch=2.35, out=0.05):
    """Wrought-iron wall ties: the small diamonds all over old brickwork."""
    metal = []
    n = max(1, int((u1 - u0) / pitch))
    for i in range(n):
        u = u0 + (i + 0.5) * (u1 - u0) / n
        metal.append(_rect(side, plane, u - 0.075, u + 0.075, v - 0.012, v + 0.012, 0.0, out))
        metal.append(_rect(side, plane, u - 0.012, u + 0.012, v - 0.075, v + 0.075, 0.0, out))
    return metal


def air_bricks(side, plane, u0, u1, v, pitch=1.6):
    """Recessed air vents — dark slots that break up a blank brick field."""
    dark = []
    n = max(1, int((u1 - u0) / pitch))
    for i in range(n):
        u = u0 + (i + 0.5) * (u1 - u0) / n
        dark.append(_rect(side, plane, u - 0.075, u + 0.075, v, v + 0.065, -0.06, 0.004))
    return dark


def balconette(side, plane, u0, u1, v, depth=0.55, rail_h=1.0):
    """Shallow iron balcony: slab, balusters, handrail, scroll brackets."""
    metal, stone = [], []
    stone.append(_rect(side, plane, u0, u1, v, v + 0.10, 0.0, depth))
    rail_out = depth - 0.05
    n = max(2, int((u1 - u0) / 0.14))
    for i in range(n + 1):
        u = u0 + (u1 - u0) * i / n
        metal.append(_rect(side, plane, u - 0.011, u + 0.011, v + 0.10, v + rail_h,
                           rail_out - 0.02, rail_out))
    metal.append(_rect(side, plane, u0, u1, v + rail_h, v + rail_h + 0.045,
                       rail_out - 0.03, rail_out + 0.01))
    for u in (u0, u1):
        metal.append(_rect(side, plane, u - 0.02, u + 0.02, v + 0.10, v + rail_h,
                           rail_out - 0.025, rail_out + 0.005))
    for u in (u0, u1):
        for zz in (v + 0.10, v + rail_h):
            metal.append(_rect(side, plane, u - 0.03, u + 0.03, zz - 0.03, zz,
                               depth * 0.35, rail_out))
    return stone, metal
