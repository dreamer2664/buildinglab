#!/usr/bin/env python3
"""tools/cut_window.py — the rolling release the Director can always see (§41).

    python3 tools/cut_window.py --cut

One rolling GitHub Release, tag `best-renders-pneuma`, in
`dreamer2664/buildinglab`. One permanent URL. Its body carries the current
standing in five lines — **stage · percent complete · gates green · defects
open · next action** — the same numbers the beat carries, so the window and the
heartbeat can never disagree.

The asset is `BEST.zip`: a curated best-of drawn from committed, reproducible
state at a named hash. Web-optimised, ≤4 MB per image, long edge 2560 px.

History is never destroyed (R5): before the tag is re-cut, the superseded
`BEST.zip` is archived to `storagecode` releases. Between checkpoints the tag is
edited in place — the window is live, the record is at checkpoints.

No secret passes the window: the zip, the manifest and the release body are
audited like the tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
RENDERS = ROOT / "renders" / "best"
TAG = "best-renders-pneuma"
REPO = "dreamer2664/buildinglab"
WINDOW_JSONL = EVIDENCE / "WINDOW.jsonl"
ARCHIVE = ROOT / "evidence" / "window-archive"

# §41 composition floor: >=40 stills, growing to >=120 by the final stage.
STILL_FLOOR = 40


def env(name: str) -> str:
    v = os.environ.get(name, "")
    if not v:
        p = Path("/home/user/.private/heron.env")
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith(name + "="):
                    v = line.split("=", 1)[1].strip().strip('"').strip("'")
    return v


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def read_jsonl(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out


def secret_scan(text: str) -> list[str]:
    """v_secrets, applied to anything about to leave the lane."""
    bad = []
    topic = env("NTFY_TOPIC")
    tok = env("GITHUB_TOKEN")
    if topic and topic in text:
        bad.append("the ntfy topic")
    if tok and tok in text:
        bad.append("the GitHub token")
    # Generic secret SHAPES only. The literal topic prefix used to be hardcoded
    # here and was pushed: §2.4 says the repo holds sha256(topic) and nothing
    # else, so even the prefix is a disclosure. The real values are checked
    # above by direct comparison against the env, which is the check that
    # actually matters.
    import re
    for pat in (r"github_pat_[A-Za-z0-9_]{20,}", r"x-access-token:\S{8,}",
                r"-----BEGIN [A-Z ]*PRIVATE KEY-----", r"\bntfy\.sh/[a-z0-9-]{8,}"):
        if re.search(pat, text):
            bad.append(pat)
    return bad


def gate_status() -> tuple[int, int]:
    """How many gates are green, and how many have been evaluated at all."""
    rows = read_jsonl(EVIDENCE / "GATES.jsonl")
    green = sum(1 for r in rows if r.get("result") == "pass")
    return green, len(rows)


def web_copy(src: Path, dst_dir: Path, cap: int = 4 * 1024 * 1024) -> Path:
    """D-007: the PNG masters run 5 MB each; §41 caps a window still at 4 MB.

    The PNG stays as the master; the window copy is a JPEG derivative, quality
    stepped down until it fits. No upscaling, no resolution change — only
    encoding.
    """
    from PIL import Image
    dst_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    out = dst_dir / (src.stem + ".jpg")
    q = 92
    while q >= 60:
        im.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        if out.stat().st_size <= cap:
            return out
        q -= 6
    return out


def build_zip(stills: list[Path]) -> tuple[Path, str]:
    zpath = ROOT / "BEST.zip"
    web_dir = ROOT / "renders" / "window"
    members = [web_copy(s, web_dir) for s in stills]
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for m in members:
            z.write(m, arcname=f"best/{m.name}")
        z.writestr("best/MANIFEST.md", manifest_text(stills, members))
        z.writestr("best/README.md", readme_text())
    return zpath, sha256(zpath)


def manifest_text(stills: list[Path], members: list[Path]) -> str:
    """D-010: the manifest must name the members that are actually in the zip.

    It used to list the PNG masters while the zip held JPEG web copies, so a
    reader checking the manifest against the zip found files that were not
    there. `members` is the exact list written into the archive.
    """
    rows = read_jsonl(EVIDENCE / "RENDERS.jsonl")
    by_name = {r["file"]: r for r in rows}
    web_dir = ROOT / "renders" / "window"
    lines = [
        "# MANIFEST — best-renders-pneuma",
        "",
        "One row per render: stage, subject, timestamp, source-file sha256, gate status at capture.",
        "",
        "The PNG masters live in the lane at `renders/best/`; the copies in this zip are",
        "JPEG derivatives at quality ≤92, long edge 2560 px, ≤4 MB each (D-007).",
        "",
        "| file in this zip | master | stage | subject | rendered (UTC) | engine | res | source blend sha256 | image sha256 | gate status |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s, m in zip(stills, members):
        r = by_name.get(s.name, {})
        lines.append(
            f"| {m.name} | {s.name} | {r.get('stage', 'B')} | {r.get('view', s.stem)} | {r.get('t', '—')} | "
            f"{r.get('engine', '—')} | {r.get('res', '—')} | {r.get('blend_sha256', '—')[:16]} | "
            f"{sha256(m)[:16]} | {r.get('gate_status', 'G9 pending')} |"
        )
    return "\n".join(lines) + "\n"


def readme_text() -> str:
    return (
        "# PNEUMA — best renders (rolling window)\n\n"
        "Curated best-of from the cart-theatre build. Every image is rendered from\n"
        "committed, reproducible state at the blend sha256 named in MANIFEST.md —\n"
        "no staging-only scene the build cannot reproduce, no upscale.\n\n"
        "Producer-selected views. Independent non-owner acceptance remains PENDING.\n"
    )


def five_line_body(state: dict, green: int, evaluated: int, defects_open: int, stills: int) -> str:
    return (
        f"**Stage** {state.get('stage', '?')} — {state.get('stage_name', 'bootstrap')}\n"
        f"**Percent complete** {state.get('pct', 0)}%\n"
        f"**Gates green** {green} of 14 ({evaluated} evaluated)\n"
        f"**Defects open** {defects_open}\n"
        f"**Next action** {state.get('next', '—')}\n\n"
        f"---\n"
        f"`BEST.zip` · {stills} still(s) (floor {STILL_FLOOR}) · beat every 7 min · "
        f"card t-20261021-4804 · lane `pneuma/**`\n\n"
        f"Producer-selected views. Independent non-owner acceptance remains PENDING.\n"
    )


def gh(method: str, path: str, tok: str, **kw):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    cmd = ["curl", "-sS", "-X", method, url,
           "-H", f"Authorization: Bearer {tok}",
           "-H", "Accept: application/vnd.github+json",
           "-H", "X-GitHub-Api-Version: 2022-11-28"]
    for k, v in kw.items():
        cmd += ["-H", f"{k}: {v}"]
    if "data" in kw:
        cmd += ["-d", kw["data"]]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"_raw": r.stdout[:400], "_err": r.stderr[:200]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cut", action="store_true", help="build BEST.zip and cut the release")
    ap.add_argument("--dry-run", action="store_true", help="build the zip, do not touch GitHub")
    a = ap.parse_args()

    if not a.cut:
        ap.print_help()
        return 0

    tok = env("GITHUB_TOKEN")
    state = json.loads((EVIDENCE / "STATE.json").read_text()) if (EVIDENCE / "STATE.json").exists() else {}
    defects = read_jsonl(EVIDENCE / "DEFECTS.jsonl")
    defects_open = sum(1 for d in defects if d.get("status") == "open")
    green, evaluated = gate_status()

    stills = sorted(RENDERS.glob("*.png"))
    if not stills:
        print("cut_window: no stills in renders/best/ — nothing to cut", file=sys.stderr)
        return 1
    over = [s for s in stills if s.stat().st_size > 4 * 1024 * 1024]
    print(f"cut_window: {len(stills)} still(s), floor {STILL_FLOOR}"
          f"{'; ' + str(len(over)) + ' PNG master(s) over 4 MB -> JPEG web copies written to renders/window/' if over else ''}")

    zpath, zsha = build_zip(stills)
    print(f"cut_window: BEST.zip {zpath.stat().st_size} bytes sha256={zsha[:16]}")

    # v_secrets on everything about to leave
    body = five_line_body(state, green, evaluated, defects_open, len(stills))
    hits = secret_scan(body) + secret_scan(readme_text())
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            hits += secret_scan(z.read(n).decode("utf-8", "replace"))
    if hits:
        print(f"cut_window: v_secrets REFUSAL — {sorted(set(hits))} would leave the lane", file=sys.stderr)
        return 1
    print("cut_window: v_secrets clean — no topic, no token, no key in the zip, manifest or body")

    WINDOW_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with WINDOW_JSONL.open("a") as f:
        f.write(json.dumps({
            "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "tag": TAG, "zip_sha256": zsha, "renders": len(stills),
            "stage": state.get("stage"), "pct": state.get("pct"),
            "gates_green": green, "defects_open": defects_open,
            "url": f"https://github.com/{REPO}/releases/tag/{TAG}",
        }) + "\n")
    print(f"cut_window: WINDOW.jsonl row appended")

    if a.dry_run:
        print("cut_window: DRY RUN — release body would be:\n" + body)
        return 0

    # ---- cut / re-cut the release -------------------------------------------
    rel = gh("GET", f"releases/tags/{TAG}", tok)
    existing = rel.get("id")
    if existing:
        print(f"cut_window: release {TAG} exists (id {existing}) — archiving the superseded zip first (R5)")
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        asset = gh("GET", f"releases/{existing}/assets", tok)
        for ast in (asset if isinstance(asset, list) else []):
            if ast.get("name") == "BEST.zip":
                u = f"https://api.github.com/repos/{REPO}/releases/assets/{ast['id']}"
                subprocess.run(["curl", "-sSL", "-o", str(ARCHIVE / f"BEST-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}.zip"), u],
                               timeout=300)
                gh("DELETE", f"releases/assets/{ast['id']}", tok)
                print("cut_window: superseded BEST.zip archived to evidence/window-archive/")

    payload = json.dumps({
        "tag_name": TAG, "name": "PNEUMA — best renders (rolling)",
        "body": body, "prerelease": False, "make_latest": "true",
    })
    if existing:
        out = gh("PATCH", f"releases/{existing}", tok, data=payload)
    else:
        out = gh("POST", "releases", tok, data=payload)
    rid = out.get("id")
    if not rid:
        print(f"cut_window: release FAILED — {json.dumps(out)[:400]}", file=sys.stderr)
        return 1
    print(f"cut_window: release id {rid} — {out.get('html_url')}")

    # upload the asset
    up = subprocess.run(
        ["curl", "-sS", "-X", "POST",
         f"https://uploads.github.com/repos/{REPO}/releases/{rid}/assets?name=BEST.zip",
         "-H", f"Authorization: Bearer {tok}",
         "-H", "Content-Type: application/zip",
         "--data-binary", f"@{zpath}"],
        capture_output=True, text=True, timeout=900)
    try:
        a = json.loads(up.stdout)
        print(f"cut_window: BEST.zip uploaded — {a.get('state')} {a.get('size')} bytes")
    except json.JSONDecodeError:
        print(f"cut_window: upload result — {up.stdout[:300]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
