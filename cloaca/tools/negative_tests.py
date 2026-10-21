#!/usr/bin/env python3
"""Refuse each validator once, on purpose (R2 / F34: a validator that has never failed has never
been tested).

Every case builds a MIRROR of the lane - real directories, symlinked files - then breaks exactly
one thing in it and runs the validator against the mirror with CLOACA_LANE pointed at it. The real
lane is never written to: the validator's own verdict row lands in the mirror's evidence dir.

Each case also runs a CONTROL on a pristine mirror first. If the control does not reproduce the
standing of the last battery run, the harness itself is broken and the case is reported as
NOT PROVEN rather than as a pass. Expected exits: 1 = the validator caught the breakage,
3 = the validator refused to pass with no subject (which is the refusal that matters for Stages H/I).
"""
import sys, os, json, shutil, subprocess, glob, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
NT   = "/tmp/cloaca_nt"
SKIP_DIRS  = {"build", "__pycache__", ".git", "node_modules"}
SKIP_FILES = {"VALIDATORS.jsonl"}          # never let a mirror append to the real verdict ledger
VALIDATE   = os.path.join(LANE, "validate")

def mirror(dst, skip_dirs=()):
    """Real directory tree, symlinked files. os.walk does not follow directory symlinks, so a
    walking validator sees the mirror's own tree and nothing escapes it."""
    if os.path.exists(dst): shutil.rmtree(dst)
    sd = set(SKIP_DIRS) | set(skip_dirs)
    for root, dirs, names in os.walk(LANE):
        dirs[:] = [d for d in dirs if d not in sd]
        rel = os.path.relpath(root, LANE)
        tgt = dst if rel == "." else os.path.join(dst, rel)
        os.makedirs(tgt, exist_ok=True)
        for n in names:
            if n in SKIP_FILES: continue
            lp = os.path.join(tgt, n)
            if not os.path.exists(lp): os.symlink(os.path.join(root, n), lp)
    for d in ("stations", "engines", "drawings", "renders", "evidence/PV", "ledgers/BRICKS", "chunks", "tests"):
        os.makedirs(os.path.join(dst, d), exist_ok=True)
    return dst

def write(dst, rel, text):
    p = os.path.join(dst, rel)
    if os.path.islink(p): os.unlink(p)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(text if isinstance(text, str) else json.dumps(text, indent=1))
    return p

def rows_of(rel):
    with open(os.path.join(LANE, rel)) as f:
        return [json.loads(l) for l in f if l.strip()]

def dump(dst, rel, rows): write(dst, rel, "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows))

def patch(dst, rel, fn):
    rows = rows_of(rel); fn(rows); dump(dst, rel, rows)

def patchj(dst, rel, fn):
    d = json.load(open(os.path.join(LANE, rel))); fn(d); write(dst, rel, d)

# ---- synthetic chunk lane (brick-level cases stay small so the battery runs in minutes) --------
def synth(dst, ledger_rows, predicted=None, bounds=None, chunk="S0000", profile="ovoid-675",
          u_match=True, peak_mb=400.0, build_s=1.5, extra_index=None, chunks_dir=True):
    mirror(dst, skip_dirs=("chunks", "ledgers"))
    os.makedirs(os.path.join(dst, "ledgers/BRICKS"), exist_ok=True)
    if chunks_dir: os.makedirs(os.path.join(dst, "chunks"), exist_ok=True)
    n = predicted if predicted is not None else len(ledger_rows)
    b = bounds or [[-0.002, -0.913, -0.253], [99.992, 0.913, 2.945]]
    row = {"chunk": chunk, "row": 0, "line": "N-high", "idx": 0, "profile": profile, "state": "built",
           "key": "a" * 64, "bricks_predicted": n, "census": len(ledger_rows),
           "census_hash": "b" * 64, "build_u_hash": "c" * 64, "chunk_file": f"chunks/{chunk}.blend",
           "built_ts": "2026-10-21T00:00:00Z", "file_bytes": 1000, "faces": 6 * len(ledger_rows),
           "bounds_m": b, "station_m": 0.0, "invert_in_m": 42.6, "invert_out_m": 42.486}
    idx = [row] + (extra_index or [])
    dump(dst, "ledgers/INDEX.jsonl", idx)
    dump(dst, "ledgers/INVERTS.jsonl", [{"chunk": chunk, "line": "N-high", "idx": 0, "profile": profile,
        "invert_in_m": 42.6, "invert_out_m": 42.486, "fall_m": 0.114, "fall_m_per_km": 1.14, "station_m": 0.0,
        "courses": 1163, "wythes": 2, "ring_thickness_m": 0.228, "bricks_predicted": n,
        "overflow": None, "station_name": None}])
    write(dst, f"evidence/CENSUS/{chunk}.json", {"chunk": chunk, "brick_objects": len(ledger_rows),
        "bricks_laid": len(ledger_rows), "census_hash": "b" * 64, "build_u_hash": "c" * 64,
        "u_hash_match": u_match, "peak_mb": peak_mb, "build_s": build_s, "bounds_m": b,
        "faces": 6 * len(ledger_rows), "file_bytes": 1000})
    dump(dst, f"ledgers/BRICKS/{chunk}.jsonl", ledger_rows)
    if chunks_dir: write(dst, f"chunks/{chunk}.blend", "synthetic")
    return dst

def brick(u, w, c, j, x, y, z, l=239, d=(0, 0, 1), r=0, g=154):
    return {"u": u, "w": w, "c": c, "j": j, "x": x, "y": y, "z": z, "r": r, "d": list(d), "l": l,
            "g": g, "k": 0, "z_": "wall"}

def ring(chunk, courses=3, per=12, r=675, y0=0):
    """A few honest courses on the ovoid wall: distinct positions, 239 mm apart, joint intact."""
    out = []
    for c in range(courses):
        for j in range(per):
            ang = 2 * 3.141592653589793 * j / per
            out.append(brick(f"{chunk[:2]}{c:03d}{j:03d}aaaa", 0, c, j, int(round(c * 85.9845 + 38)),
                             int(round(r * 1.0 * __import__("math").cos(ang) * 1000)),
                             int(round((r + r * __import__("math").sin(ang)) * 1000))))
    return out

def run(v, lane):
    env = dict(os.environ, CLOACA_LANE=lane)
    p = subprocess.run([sys.executable, os.path.join(VALIDATE, f"{v}.py")], env=env,
                       capture_output=True, text=True, cwd=LANE)
    line = (p.stdout.strip().splitlines() or [""])[-1]
    return p.returncode, line[:200]

STANDING = {}
for r in rows_of("evidence/VALIDATORS.jsonl") if os.path.exists(os.path.join(LANE, "evidence/VALIDATORS.jsonl")) else []:
    if "validator" in r: STANDING[r["validator"]] = r["exit"]

CASES = []
def case(cid, v, what, expect, setup, skip=(), control=None):
    CASES.append(dict(id=cid, v=v, what=what, expect=expect, setup=setup, skip=skip, control=control))

# ---------------- A. ledger-level breakage on a mirror of the real lane ------------------------
def drop_rows(n):
    def f(dst): patch(dst, "ledgers/INDEX.jsonl", lambda rs: rs.__delitem__(slice(0, n)))
    return f
case("NT-01", "v_index", "3 INDEX rows deleted (1,317 left)", 1, drop_rows(3))
def rename_id(dst): patch(dst, "ledgers/INDEX.jsonl", lambda rs: rs[7].__setitem__("chunk", "X0007"))
case("NT-02", "v_index", "one chunk id renamed S0007 -> X0007", 1, rename_id)
def uphill(dst): patch(dst, "ledgers/INVERTS.jsonl", lambda rs: [r.__setitem__("fall_m", -0.20) for r in rs if r["chunk"] == "S0500"])
case("NT-03", "v_gradient", "S0500 given a 0.20 m rise (uphill metres)", 1, uphill)
def join_gap(dst): patch(dst, "ledgers/INVERTS.jsonl", lambda rs: [r.__setitem__("invert_in_m", r["invert_in_m"] + 0.05) for r in rs if r["chunk"] == "S0501"])
case("NT-04", "v_gradient", "S0501 invert shifted 50 mm (join tolerance is +/-10 mm)", 1, join_gap)
def wythe(dst): patchj(dst, "PROFILE.json", lambda d: d["profiles"]["ovoid-675"].__setitem__("wythes", 3))
case("NT-05", "v_profile", "ovoid-675 declared 3 wythes instead of 2 (census no longer follows the profile)", 1, wythe)
def twin(dst):
    rows = rows_of("ledgers/DEVIATIONS.jsonl")
    rows[1] = dict(rows[0]); rows[1]["chunk"] = "S0001"
    dump(dst, "ledgers/DEVIATIONS.jsonl", rows)
case("NT-06", "v_distinct", "S0001 given S0000's deviation signature (twin chunks)", 1, twin)
def dupkey(dst): patch(dst, "ledgers/INDEX.jsonl", lambda rs: rs[9].__setitem__("key", rs[8]["key"]))
case("NT-07", "v_distinct", "two INDEX rows share one geometry key", 1, dupkey)
def tide_delta(dst): patchj(dst, "evidence/TIDE_VALIDATION.json", lambda d: d.__setitem__("max_abs_delta_m", 0.9))
case("NT-08", "v_tide", "sim declared 0.90 m against published levels (tolerance 0.15 m)", 1, tide_delta)
def tide_gauge(dst): patchj(dst, "evidence/TIDE_VALIDATION.json", lambda d: d["per_gauge"]["G3"].__setitem__("within_0p15", False))
case("NT-09", "v_tide", "one gauge out of tolerance", 1, tide_gauge)
def depth(dst): patch(dst, "ledgers/HYDRAULICS.jsonl", lambda rs: [ (r.__setitem__("depth_m", -0.4), r.__setitem__("water_surface_m", r["invert_in_m"] - 0.4)) for r in rs if r["chunk"] == "S0700"])
case("NT-10", "v_flow", "S0700 given a negative flow depth", 1, depth)
def nodriver(dst): patch(dst, "evidence/OVERFLOWS.jsonl", lambda rs: [r.pop("driver", None) for r in rs])
case("NT-11", "v_overflow", "driver stripped from every actuation (scripted overflow)", 1, nodriver)
def five_of(dst): patchj(dst, "TIDES.json", lambda d: d.__setitem__("overflows", d["overflows"][:5]))
case("NT-12", "v_overflow", "only 5 overflows declared where 6 are specified", 1, five_of)
def no_of(dst): patchj(dst, "TIDES.json", lambda d: d.__setitem__("overflows", []))
case("NT-13", "v_facing", "no overflow declared at all", 3, no_of)
BAD_WORDS = ("photo" + "realistic", "per" + "fect", "ap" + "proximately")   # assembled at runtime:
# the harness source must not contain a §30 word, or the control mirror fails on the harness itself.
def word(dst): write(dst, "NOTES_BAD.md", f"The interior is {BAD_WORDS[0]} and the bond is {BAD_WORDS[1]}.\n")
case("NT-14", "v_language", "a note carrying two words from the §30 list", 1, word)
TOK = ("GITHUB_" + "TO" + "KEN", "gh" + "p_")     # assembled at runtime, same reason as BAD_WORDS
def secret(dst): write(dst, "oops.txt", f"export {TOK[0]}={TOK[1]}" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8\n")
case("NT-15", "v_secrets", "a token-shaped credential pasted into a lane file", 1, secret)
def electric(dst): dump(dst, "evidence/RENDERS.jsonl", [{"id": "R-BAD-1", "class": "sewer_interior", "kind": "final",
    "width": 2560, "height": 1440, "light_sources": ["electric arc lamp"], "hydraulics_row": "S0000"}])
case("NT-16", "v_period", "a render lit by an electric arc lamp (period is 1858-1875)", 1, electric)
def area(dst): dump(dst, "evidence/RENDERS.jsonl", [{"id": "R-BAD-2", "class": "brick_macro", "kind": "final",
    "width": 2560, "height": 1440, "light_sources": ["area light"], "hydraulics_row": "S0000"}])
case("NT-17", "v_light", "a render lit by a studio area light", 1, area)
def lowres(dst): dump(dst, "evidence/RENDERS.jsonl", [{"id": "R-BAD-3", "class": "sewer_interior", "kind": "final",
    "width": 640, "height": 360, "light_sources": ["gas flame"], "hydraulics_row": "S0000"}])
case("NT-18", "v_renders", "a final view at 640x360 where the class requires 2560x1440", 1, lowres)
def upscaled(dst): dump(dst, "evidence/RENDERS.jsonl", [{"id": "R-BAD-4", "class": "brick_macro", "kind": "final",
    "width": 2560, "height": 1440, "upscaled": True, "light_sources": ["gas flame"], "hydraulics_row": "S0000"}])
case("NT-19", "v_renders", "a view flagged as upscaled (F10 automatic fail)", 1, upscaled)

# ---------------- B. brick-level breakage on a small synthetic lane ---------------------------
def b_units(dst):
    synth(dst, ring("S0000", 4, 14), bounds=[[-0.002, -0.913, -0.253], [49.9, 0.913, 2.945]])
case("NT-20", "v_units", "chunk bounds 50 m long where a chunk is 100 m", 1, b_units)
def b_census(dst):
    r = ring("S0000", 4, 14); synth(dst, r, predicted=len(r) + 1)
case("NT-21", "v_chunk", "ledger carries one brick the geometry does not (census != predicted)", 1, b_census)
def b_mem(dst):
    r = ring("S0000", 4, 14); synth(dst, r, peak_mb=1400.0)
case("NT-22", "v_chunk", "build peaked at 1,400 MB against the 1,200 MB ceiling", 1, b_mem)
def b_uhash(dst):
    r = ring("S0000", 4, 14); synth(dst, r, u_match=False)
case("NT-23", "v_chunk", "mesh u_hash does not match the ledger order (F42)", 1, b_uhash)
def b_floor(dst):
    r = ring("S0000", 4, 14); synth(dst, r); patch(dst, "ledgers/INDEX.jsonl", lambda rs: rs[0].__setitem__("bricks_predicted", 1))
case("NT-24", "v_bricks", "network predicted census cut below the 61,000,000 floor", 1, b_floor)
def b_dupbrick(dst):
    r = ring("S0000", 4, 14); r[5] = dict(r[4]); synth(dst, r)
case("NT-25", "v_bricks", "two ledger rows identical (a brick laid twice)", 1, b_dupbrick)
def b_zfight(dst):
    # v_zfight measures circumferential centre distance minus the brick length, so the breakage is
    # two bricks in one seat, not two at one chainage.
    r = ring("S0000", 4, 14); r[5]["y"], r[5]["z"] = r[4]["y"], r[4]["z"]; r[5]["u"] = "zzzzzzzzzzzzzzzz"
    synth(dst, r)
case("NT-26", "v_zfight", "two bricks of one course seated in the same place (faces coincident)", 1, b_zfight)
def b_void(dst):
    r = ring("S0000", 4, 14)
    for x in r[:20]: x["y"], x["z"] = 0, 675
    synth(dst, r)
case("NT-27", "v_voids", "bricks placed inside the waterway", 1, b_void)
def b_join(dst):
    r0 = ring("S0000", 4, 14)
    r1 = [dict(x) for x in r0]
    for x in r1: x["c"] += 4; x["x"] += 64      # 150 mm pitch across the head instead of 86 mm
    row1 = {"chunk": "S0001", "row": 1, "line": "N-high", "idx": 1, "profile": "ovoid-675", "state": "built",
            "key": "d" * 64, "bricks_predicted": len(r1), "census": len(r1), "census_hash": "e" * 64,
            "build_u_hash": "f" * 64, "chunk_file": "chunks/S0001.blend", "built_ts": "2026-10-21T00:00:00Z",
            "file_bytes": 1000, "faces": 6 * len(r1), "bounds_m": [[-0.002, -0.913, -0.253], [99.992, 0.913, 2.945]],
            "station_m": 100.0, "invert_in_m": 42.486, "invert_out_m": 42.372}
    synth(dst, r0, extra_index=[row1])
    dump(dst, "ledgers/BRICKS/S0001.jsonl", r1)
    write(dst, "evidence/CENSUS/S0001.json", {"chunk": "S0001", "brick_objects": len(r1), "bricks_laid": len(r1),
        "census_hash": "e" * 64, "build_u_hash": "f" * 64, "u_hash_match": True, "peak_mb": 400.0, "build_s": 1.5,
        "bounds_m": row1["bounds_m"], "faces": 6 * len(r1), "file_bytes": 1000})
    write(dst, "chunks/S0001.blend", "synthetic")
    patch(dst, "ledgers/INVERTS.jsonl", lambda rs: rs.append({"chunk": "S0001", "line": "N-high", "idx": 1,
        "profile": "ovoid-675", "invert_in_m": 42.486, "invert_out_m": 42.372, "fall_m": 0.114,
        "fall_m_per_km": 1.14, "station_m": 100.0, "courses": 1163, "wythes": 2, "ring_thickness_m": 0.228,
        "bricks_predicted": len(r1), "overflow": None, "station_name": None}))
case("NT-28", "v_joins", "course pitch across the chunk head stretched to 150 mm (D-010 reproduced)", 1, b_join)

# ---------------- C. subject absent, then subject planted but uninspected ---------------------
SUBJECTS = [("v_stations", "stations/x.blend", 4), ("v_parts", "engines/x.blend", 22),
            ("v_kinematics", "engines/x.blend", 22), ("v_cycle", "evidence/PV/x.json", 22),
            ("v_people", "ledgers/PEOPLE.jsonl", 120), ("v_drawings", "drawings/x.json", 510)]
for i, (v, path, target) in enumerate(SUBJECTS):
    case(f"NT-{29+i}", v, f"subject absent (target {target})", 3, lambda dst: None, skip=("chunks", "ledgers"))
    def plant(dst, path=path):
        write(dst, path, "[]")
    case(f"NT-{35+i}", v, f"subject planted but never inspected to the gate", 1, plant, skip=("chunks", "ledgers"))

def main():
    os.makedirs(NT, exist_ok=True)
    out = []; npass = nfail = 0
    for c in CASES:
        lane = os.path.join(NT, c["id"])
        try:
            cl = os.path.join(NT, c["id"] + "_control")
            mirror(cl, skip_dirs=tuple(c["skip"]))
            c["setup"](cl) if False else None
            crc, cline = run(c["v"], cl)
            mirror(lane, skip_dirs=tuple(c["skip"]))
            c["setup"](lane)
            rc, line = run(c["v"], lane)
            standing = STANDING.get(c["v"])
            ctrl_ok = (crc == standing) if standing is not None else True
            caught = (rc == c["expect"])
            ok = caught and ctrl_ok
            npass += ok; nfail += (not ok)
            out.append({**{k: c[k] for k in ("id", "v", "what", "expect")}, "control_exit": crc,
                        "standing": standing, "control_ok": ctrl_ok, "exit": rc, "caught": caught,
                        "proven": ok, "verdict_line": "\u00bb" + line + "\u00bb"})
            print(f"{'PROVEN ' if ok else 'NOT PROVEN'} {c['id']:6s} {c['v']:13s} expect {c['expect']} got {rc} (control {crc}/standing {standing}) · {c['what']}")
            if not ok: print(f"         {line}")
            shutil.rmtree(lane, ignore_errors=True); shutil.rmtree(cl, ignore_errors=True)
        except Exception as e:
            nfail += 1
            out.append({**{k: c[k] for k in ("id", "v", "what", "expect")}, "proven": False, "error": repr(e)})
            print(f"NOT PROVEN {c['id']} {c['v']}: harness error {e!r}")
    ev = os.path.join(LANE, "evidence/NEGATIVE_TESTS.jsonl")
    with open(ev, "a") as f:
        f.write(json.dumps({"t": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "run": {"cases": len(CASES), "proven": npass, "not_proven": nfail},
                            "cases": out}, sort_keys=True) + "\n")
    print(f"\nnegative battery: {len(CASES)} cases · {npass} proven refusals · {nfail} not proven")
    return 1 if nfail else 0

if __name__ == "__main__": sys.exit(main())
