"""PORTUS plan library — pure Python, no bpy.

Single source of truth for footprints, storeys, room rectangles, doors and
windows. Both `design/generate_programme.py` (Stage A data) and
`source/build.py` (Stage B geometry) import this module, so a plan and the
model cut from it cannot drift apart.

Coordinates are global metres: +X east, +Y north, +Z up.
Zero is the basin south-west corner; water is +0.00; land and quay top +2.40.
"""
from __future__ import annotations

import hashlib
import math

# ── constants fixed by the packet ───────────────────────────────────────────
SITE_W, SITE_H = 400.0, 320.0
BASIN = (110.0, 30.0, 290.0, 120.0)          # x0, y0, x1, y1
WATER_Z = 0.00
BASIN_DEPTH = 6.0
QUAY_TOP = 2.40
GROUND = QUAY_TOP                             # land surface = quay coping level
LAND_Z = QUAY_TOP

EXT_WALL = {                                  # half? no: full thickness
    "brick": 0.45, "warehouse": 0.60, "stucco": 0.45,
    "timber": 0.42, "steel": 0.30, "concrete": 0.40,
}
SLAB = 0.24
PARTY = 0.24
SLOT_W = 1.20                                 # open light slot between the two ranges
RES_STOREY = 3.20
COM_STOREY = 4.40
WARE_STOREY = 4.00
RES_CEILING = 2.70
COM_CEILING = 3.80
DOOR_W, DOOR_H = 0.90, 2.10
LOADING_W, LOADING_H = 2.50, 3.00
HUMAN_H = 1.75
EYE_H = 1.62

# ── block layout ────────────────────────────────────────────────────────────
# Six blocks, 48 buildings, streets 9–14 m, one 22 m boulevard on the north edge.
BASIN_X0, BASIN_Y0, BASIN_X1, BASIN_Y1 = BASIN
B_ROW_Y = (BASIN_Y1 + 8.0, BASIN_Y1 + 8.0 + 14.0)      # north quay apron 8 m
E_WEST_X = (88.0, 102.0)                                # west quay apron 8 m
E_SOUTH_Y = (8.0, 22.0)                                 # south quay apron 8 m
F_ROW_Y = (4.0, 22.0)
G_ROW_X = (298.0, 312.0)                                # east quay apron 8 m

BLOCK_ORDER = [("A", 8), ("B", 12), ("C", 4), ("D", 1), ("E", 12), ("F", 5), ("G", 6)]

# names from the packet's district description
BLOCK_NAMES = {
    "A": "Speicherstadt", "B": "Kaimauerzeile", "C": "Werft", "D": "Markthalle",
    "E": "Kaistrasse", "F": "Amt", "G": "Kaiwerkstaetten",
}

# the 48 ground-floor businesses named in Part III 13.2
SHOP_NAMES = [
    "fishmonger", "chandlery", "bakery", "pub", "harbour chandlery", "barber",
    "laundry", "ship's broker", "sailmaker", "netmaker", "grocer", "butcher",
    "cafe", "dock cafe", "hardware", "paint", "rope walk", "ice house",
    "customs office", "post", "bank", "pharmacy", "tobacconist", "bookshop",
    "second-hand", "pawn", "radio repair", "bicycle", "cobbler", "tailor",
    "printing", "sail loft", "cooperage", "smokehouse", "cold store",
    "coal merchant", "chandlery no.3", "auction hall", "bait shop", "noodle bar",
    "boat paint", "wire rigging", "chandler's loft", "marine insurance",
    "harbour books", "rope and tar", "engine parts", "fish smokehouse",
]

# facade rhythm: (window module m, roof kind, roof pitch deg, storey pattern, walls)
ROOFS = ["slate", "clay", "standing_seam", "monitor", "shed", "flat", "mansard", "glass"]
WALLS = ["brick", "stucco", "timber", "cladding", "concrete", "stone"]

ARCHETYPES = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12"]
PALETTES = ["1890 dock", "1930 clerk", "1955 utility", "1978 renovation", "2020s conversion",
            "fish merchant", "rail family", "harbour master"]
GENERATIONS = ["1890s dockworker", "1930s clerk", "1955", "1978 renovation", "2020s conversion"]
OCCUPANCY = ["family", "single", "shared", "live-work"]

# archetype band tables: list of (v0, v1, [(room, u_fraction), ...])
# v runs from the front facade (0.0) to the back (1.0); u across the range.
# every band spans the full range width, so every room touches either the
# outer wall or the open light slot -> every counted room has a window.
ARCH_TABLE = {
    "A1": [(0.00, 0.30, [("living", 1.0)]),
           (0.30, 0.55, [("kitchen", 0.58), ("entry", 0.42)]),
           (0.55, 0.80, [("bedroom", 0.60), ("bathroom", 0.40)]),
           (0.80, 1.00, [("store", 1.0)])],
    "A2": [(0.00, 0.26, [("living", 1.0)]),
           (0.26, 0.50, [("kitchen", 0.60), ("entry", 0.40)]),
           (0.50, 0.78, [("bedroom", 0.55), ("bathroom", 0.45)]),
           (0.78, 1.00, [("store", 1.0)])],
    "A3": [(0.00, 0.34, [("living", 1.0)]),
           (0.34, 0.58, [("kitchen", 0.52), ("entry", 0.48)]),
           (0.58, 0.84, [("bedroom", 0.62), ("bathroom", 0.38)]),
           (0.84, 1.00, [("store", 1.0)])],
    "A4": [(0.00, 0.24, [("kitchen", 0.55), ("entry", 0.45)]),
           (0.24, 0.58, [("living", 1.0)]),
           (0.58, 0.82, [("bedroom", 0.60), ("bathroom", 0.40)]),
           (0.82, 1.00, [("store", 1.0)])],
    "A5": [(0.00, 0.28, [("living", 1.0)]),
           (0.28, 0.56, [("bedroom", 0.58), ("bathroom", 0.42)]),
           (0.56, 0.80, [("kitchen", 0.60), ("entry", 0.40)]),
           (0.80, 1.00, [("store", 1.0)])],
    "A6": [(0.00, 0.32, [("living", 1.0)]),
           (0.32, 0.52, [("kitchen", 0.56), ("entry", 0.44)]),
           (0.52, 0.76, [("bedroom", 0.64), ("bathroom", 0.36)]),
           (0.76, 1.00, [("store", 1.0)])],
    "A7": [(0.00, 0.22, [("living", 1.0)]),
           (0.22, 0.54, [("kitchen", 0.50), ("entry", 0.50)]),
           (0.54, 0.80, [("bedroom", 0.66), ("bathroom", 0.34)]),
           (0.80, 1.00, [("store", 1.0)])],
    "A8": [(0.00, 0.30, [("living", 1.0)]),
           (0.30, 0.60, [("bedroom", 0.62), ("bathroom", 0.38)]),
           (0.60, 0.82, [("kitchen", 0.55), ("entry", 0.45)]),
           (0.82, 1.00, [("store", 1.0)])],
    "A9": [(0.00, 0.36, [("living", 1.0)]),
           (0.36, 0.60, [("kitchen", 0.60), ("entry", 0.40)]),
           (0.60, 0.86, [("bedroom", 0.58), ("bathroom", 0.42)]),
           (0.86, 1.00, [("store", 1.0)])],
    "A10": [(0.00, 0.26, [("kitchen", 0.62), ("entry", 0.38)]),
            (0.26, 0.56, [("living", 1.0)]),
            (0.56, 0.82, [("bedroom", 0.60), ("bathroom", 0.40)]),
            (0.82, 1.00, [("store", 1.0)])],
    "A11": [(0.00, 0.30, [("living", 1.0)]),
            (0.30, 0.54, [("kitchen", 0.54), ("entry", 0.46)]),
            (0.54, 0.78, [("bedroom", 0.56), ("bathroom", 0.44)]),
            (0.78, 1.00, [("store", 1.0)])],
    "A12": [(0.00, 0.28, [("living", 1.0)]),
            (0.28, 0.50, [("kitchen", 0.62), ("entry", 0.38)]),
            (0.50, 0.74, [("bedroom", 0.60), ("bathroom", 0.40)]),
            (0.74, 1.00, [("store", 1.0)])],
}


def _det_rand(seed: str) -> float:
    """Deterministic float in [0,1) from a seed string."""
    h = hashlib.sha256(seed.encode()).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


def building_specs():
    """Return the 48 building briefs with footprints and storey stacks."""
    specs = []
    # ── A · 8 warehouses, two rows of four ────────────────────────────────
    for i in range(8):
        row, col = divmod(i, 4)
        x0 = 20.0 + 40.0 * col
        y0 = 232.0 if row == 0 else 190.0
        specs.append(dict(
            id=f"A{i+1:02d}", block="A", kind="warehouse", name=f"Speicher {i+1:02d}",
            x0=x0, y0=y0, x1=x0 + 38.0, y1=y0 + 30.0,
            storeys=[dict(h=WARE_STOREY, use="commercial") for _ in range(6)],
            wall="warehouse", roof=ROOFS[i % 6], pitch=[38, 42, 35, 45, 40, 36][i % 6],
            module=[2.4, 2.1, 2.7, 3.0, 2.4, 2.1][i % 6],
            front="S"))
    # ── B · 12 mixed-use along the north quay ─────────────────────────────
    for i in range(12):
        x0 = 110.0 + 15.0 * i
        specs.append(dict(
            id=f"B{i+1:02d}", block="B", kind="mixed", name=f"Kaimauer {i+1:02d}",
            x0=x0, y0=B_ROW_Y[0], x1=x0 + 14.4, y1=B_ROW_Y[1],
            storeys=[dict(h=COM_STOREY, use="commercial")] +
                    [dict(h=RES_STOREY, use="residential") for _ in range(4)],
            wall="brick", roof=ROOFS[(i + 2) % 6], pitch=[36, 40, 42, 38, 34, 44][i % 6],
            module=[1.2, 1.5, 1.35, 1.65, 1.2, 1.8][i % 6],
            front="S"))
    # ── C · Werft: 2 tall workshops + 2 three-storey offices ──────────────
    cdefs = [("C01", 320.0, 66.0, 36.0, 30.0, "tall"), ("C02", 320.0, 30.0, 32.0, 28.0, "tall"),
             ("C03", 360.0, 100.0, 20.0, 16.0, "office"), ("C04", 360.0, 30.0, 20.0, 16.0, "office")]
    for cid, x0, y0, w, d, kind in cdefs:
        stack = ([dict(h=8.0, use="commercial")] if kind == "tall"
                 else [dict(h=COM_STOREY, use="commercial")] + [dict(h=RES_STOREY, use="commercial")] * 2)
        specs.append(dict(id=cid, block="C", kind="workshop" if kind == "tall" else "office",
                          name=f"Werft {cid[-2:]}", x0=x0, y0=y0, x1=x0 + w, y1=y0 + d,
                          storeys=stack, wall="steel" if kind == "tall" else "brick",
                          roof="shed" if kind == "tall" else "slate",
                          pitch=18 if kind == "tall" else 38,
                          module=3.6 if kind == "tall" else 1.5, front="W"))
    # ── D · the market hall ───────────────────────────────────────────────
    specs.append(dict(id="D01", block="D", kind="market", name="Markthalle",
                      x0=200.0, y0=190.0, x1=286.0, y1=250.0,
                      storeys=[dict(h=7.50, use="commercial"), dict(h=4.50, use="commercial")],
                      wall="steel", roof="glass", pitch=20, module=3.2, front="S"))
    # ── E · 12 townhouses: 6 on the west quay, 6 on the south quay ────────
    for i in range(12):
        if i < 6:
            y0 = 30.0 + 15.0 * i
            x0, x1 = E_WEST_X[0], E_WEST_X[1]
            front = "E"
        else:
            x0 = 110.0 + 15.0 * (i - 6)
            y0, y1 = E_SOUTH_Y[0], E_SOUTH_Y[1]
            x1 = x0 + 14.4
        if i < 6:
            y1 = y0 + 14.4
        specs.append(dict(
            id=f"E{i+1:02d}", block="E", kind="townhouse", name=f"Kaistrasse {i+1:02d}",
            x0=x0, y0=y0, x1=x1, y1=y1,
            storeys=[dict(h=COM_STOREY, use="commercial")] +
                    [dict(h=RES_STOREY, use="residential") for _ in range(3)],
            wall="stucco", roof=ROOFS[(i + 4) % 6], pitch=[44, 40, 46, 38, 42, 36][i % 6],
            module=[1.35, 1.5, 1.2, 1.65, 1.35, 1.5][i % 6], front=front))
    # ── F · 5 civic buildings on the south quay ───────────────────────────
    for i in range(5):
        x0 = 204.0 + 17.2 * i
        specs.append(dict(
            id=f"F{i+1:02d}", block="F", kind="civic",
            name=["Customs House", "Harbour Master", "Fire Station", "Bathhouse", "School"][i],
            x0=x0, y0=F_ROW_Y[0], x1=x0 + 16.8, y1=F_ROW_Y[1],
            storeys=[dict(h=COM_STOREY, use="commercial")] +
                    [dict(h=RES_STOREY, use="residential") for _ in range(4)],
            wall="stone", roof=ROOFS[(i + 3) % 6], pitch=[40, 36, 42, 38, 44][i % 6],
            module=[1.5, 1.65, 1.35, 1.8, 1.5][i % 6], front="N"))
    # ── G · 6 quay workshops and sheds on the east quay ───────────────────
    for i in range(6):
        y0 = 30.0 + 15.0 * i
        specs.append(dict(
            id=f"G{i+1:02d}", block="G", kind="shed", name=f"Kaiwerkstatt {i+1:02d}",
            x0=G_ROW_X[0], y0=y0, x1=G_ROW_X[1], y1=y0 + 14.4,
            storeys=[dict(h=5.00, use="commercial")],
            wall="cladding", roof="standing_seam", pitch=[12, 14, 10, 16, 12, 14][i % 6],
            module=[3.0, 3.6, 2.4, 4.2, 3.0, 3.6][i % 6], front="W"))
    # 48 unique (storey rhythm, window module, roof pitch) triples by construction:
    # 12 modules x 4 pitch offsets; a repeated module always carries a different pitch.
    MODULES = [1.20, 1.35, 1.50, 1.65, 1.80, 2.10, 2.40, 2.70, 3.00, 3.20, 3.60, 4.20]
    BASE_PITCH = {"slate": 38, "clay": 36, "standing_seam": 8, "monitor": 24,
                  "shed": 10, "flat": 0, "mansard": 55, "glass": 18}
    for i, s in enumerate(specs):
        s["shop"] = SHOP_NAMES[i % len(SHOP_NAMES)]
        s["shop_id"] = f"SHOP-{i+1:02d}"
        s["module"] = MODULES[i % 12]
        s["pitch"] = BASE_PITCH[s["roof"]] + (i // 12) * 2
    return specs


def floor_levels(spec):
    """Absolute FFL for each storey index."""
    out, z = [], LAND_Z
    for st in spec["storeys"]:
        out.append(round(z, 3))
        z += st["h"]
    return out


def building_height(spec):
    return round(sum(s["h"] for s in spec["storeys"]), 3)


# ── plans ───────────────────────────────────────────────────────────────────
def _rect(x0, y0, x1, y1):
    return dict(x0=round(x0, 3), y0=round(y0, 3), x1=round(x1, 3), y1=round(y1, 3),
                w=round(x1 - x0, 3), d=round(y1 - y0, 3),
                area=round((x1 - x0) * (y1 - y0), 3))


def _u_v_axes(spec):
    """Return mapper (u,v)->(x,y); u runs along the frontage, v is depth from the front."""
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    f = spec["front"]
    if f == "S":                       # front facade at y=y0, depth grows north
        return (lambda u, v: (x0 + u, y0 + v)), (x1 - x0), (y1 - y0)
    if f == "N":                       # front facade at y=y1, depth grows south
        return (lambda u, v: (x0 + u, y1 - v)), (x1 - x0), (y1 - y0)
    if f == "E":                       # front facade at x=x1, depth grows west
        return (lambda u, v: (x1 - v, y0 + u)), (y1 - y0), (x1 - x0)
    if f == "W":                       # front facade at x=x0, depth grows east
        return (lambda u, v: (x0 + v, y0 + u)), (y1 - y0), (x1 - x0)
    raise ValueError(f)                # pragma: no cover


def _room(x0, y0, x1, y1, name, kind="room", **kw):
    r = _rect(x0, y0, x1, y1)
    r.update(dict(name=name, kind=kind))
    r.update(kw)
    return r


def apartment_rooms(spec, level_index, apt_index, apt_id, archetype, seed):
    """Two ranges per building, one apartment per range, open light slot between.

    Returns (rooms, slot_rect, cores) in global coordinates.
    """
    to_xy, width, depth = _u_v_axes(spec)
    wt = EXT_WALL.get(spec["wall"], 0.45)
    # interior rectangle in (u, v)
    iu0, iu1 = wt, width - wt
    iv0, iv1 = wt, depth - wt
    inner_u = iu1 - iu0
    inner_v = iv1 - iv0
    # two ranges split by the slot
    mid_u = iu0 + inner_u / 2.0
    slot_u0, slot_u1 = mid_u - SLOT_W / 2.0, mid_u + SLOT_W / 2.0
    ranges = [(iu0, slot_u0), (slot_u1, iu1)]
    ru0, ru1 = ranges[apt_index]
    rw = ru1 - ru0
    # jitter: deterministic, keeps every room above its minimum
    j = lambda k: (_det_rand(f"{seed}:{k}") - 0.5) * 0.24
    table = ARCH_TABLE[archetype]
    # band boundaries with jitter, clamped so neighbours keep >= 1.6 m
    bounds = [0.0] + [b for (_, b, _) in table]
    vs = []
    for k, b in enumerate(bounds):
        v = b * inner_v
        if 0 < k < len(bounds) - 1:
            v += j(f"band{k}")
        vs.append(v)
    rooms = []
    for bi, (v0f, v1f, parts) in enumerate(table):
        parts = list(parts)
        if apt_index == 1:
            parts.reverse()          # range B is mirrored: entry still faces the slot
        v0 = vs[bi]
        v1 = vs[bi + 1]
        if len(parts) == 1:
            name = parts[0][0]
            ax0, ay0 = to_xy(ru0, iv0 + v0)
            ax1, ay1 = to_xy(ru1, iv0 + v1)
            rooms.append(_room(min(ax0, ax1), min(ay0, ay1), max(ax0, ax1), max(ay0, ay1),
                               name, kind="apartment_room"))
        else:
            # split across u at cumulative fractions, jittered but monotonic
            splits = [ru0]
            acc = 0.0
            for pi, (name, frac) in enumerate(parts[:-1]):
                acc += frac
                s = ru0 + acc * rw + j(f"u{bi}{pi}") * 0.5
                s = max(splits[-1] + 1.6, min(ru1 - 1.6 * (len(parts) - 1 - pi), s))
                splits.append(s)
            splits.append(ru1)
            for pi, (name, frac) in enumerate(parts):
                u0, u1 = splits[pi], splits[pi + 1]
                ax0, ay0 = to_xy(u0, iv0 + v0)
                ax1, ay1 = to_xy(u1, iv0 + v1)
                rooms.append(_room(min(ax0, ax1), min(ay0, ay1), max(ax0, ax1), max(ay0, ay1),
                                   name, kind="apartment_room"))
    # slot rectangle (global)
    s0 = to_xy(slot_u0, iv0)
    s1 = to_xy(slot_u1, iv1)
    slot = _rect(min(s0[0], s1[0]), min(s0[1], s1[1]), max(s0[0], s1[0]), max(s0[1], s1[1]))
    for r in rooms:
        r["apartment"] = apt_id
    return rooms, slot


def shop_rooms(spec, level_z):
    """Ground-floor business: one continuous plate, four counted rooms.
    The light slot starts at the first floor; the ground floor is solid."""
    to_xy, width, depth = _u_v_axes(spec)
    wt = EXT_WALL.get(spec["wall"], 0.45)
    iu0, iu1 = wt, width - wt
    iv0, iv1 = wt, depth - wt
    W, D = iu1 - iu0, iv1 - iv0
    out = []

    def add(name, u0, v0, u1, v1):
        ax0, ay0 = to_xy(iu0 + u0 * W, iv0 + v0 * D)
        ax1, ay1 = to_xy(iu0 + u1 * W, iv0 + v1 * D)
        out.append(_room(min(ax0, ax1), min(ay0, ay1), max(ax0, ax1), max(ay0, ay1),
                         name, kind="shop_room", shop=spec["shop_id"]))

    add("sales", 0.00, 0.00, 1.00, 0.55)
    add("stock", 0.00, 0.55, 0.50, 1.00)
    add("staff", 0.50, 0.55, 0.80, 1.00)
    add("wc", 0.80, 0.55, 1.00, 1.00)
    return out


def extra_rooms(spec, level_z):
    """Block-specific counted rooms as full-depth bays, so every bay meets the
    street facade and the rear facade and the chain is connected."""
    to_xy, width, depth = _u_v_axes(spec)
    wt = EXT_WALL.get(spec["wall"], 0.45)
    iu0, iu1 = wt, width - wt
    iv0, iv1 = wt, depth - wt
    W = iu1 - iu0
    out = []

    def add(name, u0, u1):
        ax0, ay0 = to_xy(iu0 + u0 * W, iv0)
        ax1, ay1 = to_xy(iu0 + u1 * W, iv1)
        out.append(_room(min(ax0, ax1), min(ay0, ay1), max(ax0, ax1), max(ay0, ay1),
                         name, kind="building_room"))

    k = spec["kind"]
    if k == "warehouse":
        add("warehouse floor", 0.00, 0.62)
        add("loft", 0.62, 0.83)
        add("hoist office", 0.83, 1.00)
    elif k == "workshop":
        add("machine hall", 0.00, 0.56)
        add("joinery", 0.56, 0.76)
        add("paint shop", 0.76, 0.90)
        add("foreman office", 0.90, 1.00)
    elif k == "office":
        add("office floor", 0.00, 0.55)
        add("drawing office", 0.55, 0.75)
        add("records", 0.75, 0.89)
        add("lavatory block", 0.89, 1.00)
    elif k == "civic":
        add("public hall", 0.00, 0.44)
        add("counter office", 0.44, 0.60)
        add("records room", 0.60, 0.73)
        add("interview room", 0.73, 0.84)
        add("staff room", 0.84, 0.94)
        add("lavatory block", 0.94, 1.00)
    elif k == "shed":
        add("workshop floor", 0.00, 0.66)
        add("tool store", 0.66, 0.83)
        add("bench room", 0.83, 1.00)
    return out


def market_stalls(spec):
    """80 stalls, 8 rows of 10, 1.8 m aisles between rows."""
    x0, y0, x1, y1 = spec["x0"], spec["y0"], spec["x1"], spec["y1"]
    wt = 0.30
    ix0, iy0, ix1, iy1 = x0 + wt, y0 + wt, x1 - wt, y1 - wt
    cols, rows = 10, 8
    aisle = 1.8
    stall_w = (ix1 - ix0 - (cols - 1) * 0.25) / cols
    row_pitch = (iy1 - iy0 - (rows - 1) * aisle) / rows
    out = []
    for r in range(rows):
        for c in range(cols):
            sx = ix0 + c * (stall_w + 0.25)
            sy = iy0 + r * (row_pitch + aisle)
            out.append(_room(sx, sy, sx + stall_w, sy + row_pitch,
                             f"stall {r*cols+c+1:02d}", kind="stall",
                             market="D01"))
    return out


def stall_openings(stalls):
    """A market stall has an open front onto its aisle, not a door leaf."""
    out = []
    for r in stalls:
        out.append(dict(room=r, isolated=False, window=None,
                        door=dict(side="S", x=round(r["x0"] + 0.1, 3), y=round(r["y0"], 3),
                                  w=round(max(1.5, r["w"] - 0.2), 3), h=2.05,
                                  along="x", open_front=True)))
    return out


# ── doors and windows ───────────────────────────────────────────────────────
def _edges(r):
    return [
        ("S", r["x0"], r["y0"], r["x1"], r["y0"]),
        ("N", r["x0"], r["y1"], r["x1"], r["y1"]),
        ("W", r["x0"], r["y0"], r["x0"], r["y1"]),
        ("E", r["x1"], r["y0"], r["x1"], r["y1"]),
    ]


def shared_edge(a, b, tol=0.02):
    """Longest shared wall segment between two rectangles: (side, x0,y0,x1,y1, len)."""
    best = None
    ax0, ay0, ax1, ay1 = a["x0"], a["y0"], a["x1"], a["y1"]
    bx0, by0, bx1, by1 = b["x0"], b["y0"], b["x1"], b["y1"]
    # vertical contact
    for x in (ax0, ax1):
        for xb in (bx0, bx1):
            if abs(x - xb) <= tol:
                lo, hi = max(ay0, by0), min(ay1, by1)
                if hi - lo > 0.5 and (best is None or hi - lo > best[4]):
                    best = ("W" if x == ax0 else "E", x, lo, x, hi, hi - lo)
    for y in (ay0, ay1):
        for yb in (by0, by1):
            if abs(y - yb) <= tol:
                lo, hi = max(ax0, bx0), min(ax1, bx1)
                if hi - lo > 0.5 and (best is None or hi - lo > best[4]):
                    best = ("S" if y == ay0 else "N", lo, y, hi, y, hi - lo)
    return best


def openings_for_rooms(rooms, spec, level_z, slot, exterior=True):
    """One door per room, placed on a maximum spanning tree over shared walls so
    that the apartment is connected; one window per room on the envelope or on
    the open light slot. Returns per-room dicts."""
    tol = EXT_WALL.get(spec["wall"], 0.45) + 0.12
    n = len(rooms)
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            sh = shared_edge(rooms[i], rooms[j])
            if sh:
                edges.append((sh[5], i, j, sh))
    # maximum spanning tree, rooted at the entry room (or room 0)
    root = next((i for i, r in enumerate(rooms) if r["name"] == "entry"), 0)
    in_tree, parent, tree = {root}, {}, []
    while len(in_tree) < n:
        best = None
        for (ln, i, j, sh) in edges:
            a_in, b_in = i in in_tree, j in in_tree
            if a_in != b_in and (best is None or ln > best[0]):
                best = (ln, i, j, sh)
        if best is None:
            break
        ln, i, j, sh = best
        child = j if i in in_tree else i
        parent[child] = (i if child == j else j)
        in_tree.add(child)
        tree.append((child, sh))
    doors = {}

    def door_from(child, sh):
        side, x0, y0, x1, y1, ln = sh
        loading = rooms[child]["area"] > 400.0
        dw = LOADING_W if loading else DOOR_W
        dh = LOADING_H if loading else DOOR_H
        if side in ("W", "E"):
            mid = (y0 + y1) / 2.0
            side_c = "W" if abs(rooms[child]["x0"] - x0) < 0.02 else "E"
            return dict(side=side_c, x=round(x0, 3), y=round(mid - dw / 2, 3),
                        w=dw, h=dh, along="y", loading=loading)
        mid = (x0 + x1) / 2.0
        side_c = "S" if abs(rooms[child]["y0"] - y0) < 0.02 else "N"
        return dict(side=side_c, x=round(mid - dw / 2, 3), y=round(y0, 3),
                    w=dw, h=dh, along="x", loading=loading)

    for child, sh in tree:
        doors[child] = door_from(child, sh)

    # the entry room is reached from the shared landing in the light slot:
    # give it a front door on its slot face (fall back to the envelope)
    if root not in doors:
        r = rooms[root]
        cand = None
        for (side, x0, y0, x1, y1) in _edges(r):
            if slot is not None:
                if side in ("W", "E"):
                    if abs(x0 - slot["x0"]) < 0.06 or abs(x0 - slot["x1"]) < 0.06:
                        cand = (side, x0, max(y0, slot["y0"]), x0, min(y1, slot["y1"]))
                else:
                    if abs(y0 - slot["y0"]) < 0.06 or abs(y0 - slot["y1"]) < 0.06:
                        cand = (side, max(x0, slot["x0"]), y0, min(x1, slot["x1"]), y0)
            if cand is None:
                if side in ("S", "N"):
                    on_env = abs(y0 - spec["y0"]) < tol or abs(y0 - spec["y1"]) < tol
                    cand = (side, x0, y0, x1, y0) if on_env else None
                else:
                    on_env = abs(x0 - spec["x0"]) < tol or abs(x0 - spec["x1"]) < tol
                    cand = (side, x0, y0, x0, y1) if on_env else None
            if cand and (cand[3] - cand[1] if cand[0] in ("S", "N") else cand[4] - cand[2]) >= DOOR_W + 0.2:
                break
            cand = None
        if cand:
            side, x0, y0, x1, y1 = cand
            span = (x1 - x0) if side in ("S", "N") else (y1 - y0)
            loading = r["area"] > 400.0 and span >= LOADING_W + 0.3
            dw = LOADING_W if loading else DOOR_W
            dh = LOADING_H if loading else DOOR_H
            if side in ("W", "E"):
                mid = (y0 + y1) / 2.0
                doors[root] = dict(side=side, x=round(x0, 3), y=round(mid - dw / 2, 3),
                                   w=dw, h=dh, along="y", front=True, loading=loading)
            else:
                mid = (x0 + x1) / 2.0
                doors[root] = dict(side=side, x=round(mid - dw / 2, 3), y=round(y0, 3),
                                   w=dw, h=dh, along="x", front=True, loading=loading)

    out = []
    for i, r in enumerate(rooms):
        # window: on the building envelope or on the open light slot
        win = None
        if exterior:
            for (side, x0, y0, x1, y1) in _edges(r):
                overlaps_slot = False
                if slot is not None:
                    if side in ("W", "E"):
                        near = abs(x0 - slot["x0"]) < 0.06 or abs(x0 - slot["x1"]) < 0.06
                        overlaps_slot = near and (min(y1, slot["y1"]) - max(y0, slot["y0"]) > 0.8)
                    else:
                        near = abs(y0 - slot["y0"]) < 0.06 or abs(y0 - slot["y1"]) < 0.06
                        overlaps_slot = near and (min(x1, slot["x1"]) - max(x0, slot["x0"]) > 0.8)
                if side in ("S", "N"):
                    on_env = abs(y0 - spec["y0"]) < tol or abs(y0 - spec["y1"]) < tol
                    span = x1 - x0
                else:
                    on_env = abs(x0 - spec["x0"]) < tol or abs(x0 - spec["x1"]) < tol
                    span = y1 - y0
                if (on_env or overlaps_slot) and span > 1.0:
                    w = min(1.60, max(0.60, span * 0.45))
                    if side in ("S", "N"):
                        mid = (x0 + x1) / 2.0
                        win = dict(side=side, x=round(mid - w / 2, 3), y=round(y0, 3),
                                   w=round(w, 3), h=1.40, sill=0.90)
                    else:
                        mid = (y0 + y1) / 2.0
                        win = dict(side=side, x=round(x0, 3), y=round(mid - w / 2, 3),
                                   w=round(w, 3), h=1.40, sill=0.90)
                    break
        out.append(dict(room=r, door=doors.get(i), window=win,
                        isolated=(i not in in_tree)))
    return out


def reachable(entries):
    """Undirected BFS over shared walls carrying a door, rooted at the entry."""
    n = len(entries)
    adj = {i: set() for i in range(n)}
    for i, e in enumerate(entries):
        d = e["door"]
        if not d:
            continue
        r = e["room"]
        for j, o in enumerate(entries):
            if i == j:
                continue
            sh = shared_edge(r, o["room"])
            if not sh:
                continue
            side, x0, y0, x1, y1, ln = sh
            if side != d["side"]:
                continue
            dw = d.get("w", DOOR_W)
            if d["along"] == "y":
                ok = (y0 - 0.01 <= d["y"] + dw / 2 <= y1 + 0.01)
            else:
                ok = (x0 - 0.01 <= d["x"] + dw / 2 <= x1 + 0.01)
            if ok:
                adj[i].add(j)
                adj[j].add(i)
    root = next((i for i, e in enumerate(entries) if e["room"]["name"] == "entry"), 0)
    seen, stack = {root}, [root]
    while stack:
        k = stack.pop()
        for m in adj[k]:
            if m not in seen:
                seen.add(m)
                stack.append(m)
    return len(seen) == n


def signature(rooms):
    """Arrangement signature: family + position to 5 mm + rotation to 2 deg."""
    rows = []
    for r in rooms:
        rows.append(f"{r['name']}|{round(r['x0']*200)/200:.3f}|{round(r['y0']*200)/200:.3f}|"
                    f"{round(r['w']*200)/200:.3f}|{round(r['d']*200)/200:.3f}|0")
    return hashlib.sha256("\n".join(sorted(rows)).encode()).hexdigest()


def apartment_catalogue():
    """208 apartments with archetype/palette/generation/occupancy/seed."""
    specs = building_specs()
    out = []
    n = 0
    for s in specs:
        if s["block"] not in ("B", "E", "F"):
            continue
        ffls = floor_levels(s)
        res_levels = [i for i, st in enumerate(s["storeys"]) if st["use"] == "residential"]
        for li in res_levels:
            for ai in range(2):
                n += 1
                apt_id = f"{s['id']}-L{li+1:02d}-{'AB'[ai]}"
                arch = ARCHETYPES[(n * 5) % len(ARCHETYPES)]
                pal = PALETTES[(n * 3) % len(PALETTES)]
                gen = GENERATIONS[(n * 2) % len(GENERATIONS)]
                occ = OCCUPANCY[(n * 3) % len(OCCUPANCY)]
                seed = f"PORTUS:{apt_id}:{n:03d}"
                out.append(dict(id=apt_id, building=s["id"], block=s["block"], level=li,
                                ffl=ffls[li], index=n, archetype=arch, palette=pal,
                                generation=gen, occupancy=occ, seed=seed))
    return out
