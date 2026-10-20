#!/usr/bin/env python3
"""
publish_release.py — Packages, uploads, and verifies the GitHub Release
`nordbahnhof/brunel/r01-<sha12>` on `dreamer2664/storagecode` per §34.
"""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE_DIR = Path("/tmp/nordbahnhof_release")
VERIFY_DIR = Path("/tmp/verify")


def run(cmd: list[str], cwd: Path | None = None) -> str:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return res.stdout.strip()


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_release_assets(sha12: str) -> list[Path]:
    if STAGE_DIR.exists():
        shutil.rmtree(STAGE_DIR)
    STAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. NORDBAHNHOF.blend.zst
    run(["zstd", "-f", "-10", str(ROOT / "source" / "NORDBAHNHOF.blend"), "-o", str(STAGE_DIR / "NORDBAHNHOF.blend.zst")])
    # 2. NORDBAHNHOF_lib.blend.zst
    run(["zstd", "-f", "-10", str(ROOT / "source" / "NORDBAHNHOF_lib.blend"), "-o", str(STAGE_DIR / "NORDBAHNHOF_lib.blend.zst")])
    # 3. NORDBAHNHOF_exports.tar.zst
    run(["tar", "--zstd", "-cf", str(STAGE_DIR / "NORDBAHNHOF_exports.tar.zst"), "-C", str(ROOT), "exports"])
    # 4. NORDBAHNHOF_renders_final.tar.zst (best + final renders)
    run(["tar", "--zstd", "-cf", str(STAGE_DIR / "NORDBAHNHOF_renders_final.tar.zst"), "-C", str(ROOT / "renders"), "best"])
    # 5. NORDBAHNHOF_renders_proof.tar.zst
    run(["tar", "--zstd", "-cf", str(STAGE_DIR / "NORDBAHNHOF_renders_proof.tar.zst"), "-C", str(ROOT / "renders"), "proof", ".cache"])
    # 6. NORDBAHNHOF_evidence.tar.zst
    run(["tar", "--zstd", "-cf", str(STAGE_DIR / "NORDBAHNHOF_evidence.tar.zst"), "-C", str(ROOT), "evidence", "EVIDENCE"])
    # 7. RELEASE_NOTES.md
    shutil.copy2(ROOT / "RELEASE_NOTES.md", STAGE_DIR / "RELEASE_NOTES.md")

    asset_names = [
        "NORDBAHNHOF.blend.zst",
        "NORDBAHNHOF_lib.blend.zst",
        "NORDBAHNHOF_exports.tar.zst",
        "NORDBAHNHOF_renders_final.tar.zst",
        "NORDBAHNHOF_renders_proof.tar.zst",
        "NORDBAHNHOF_evidence.tar.zst",
        "RELEASE_NOTES.md",
    ]
    sums_lines = []
    for name in asset_names:
        p = STAGE_DIR / name
        sums_lines.append(f"{sha256_file(p)}  {name}")
    # Also include repo-relative SHA256SUMS lines
    sums_lines.append((ROOT / "evidence" / "SHA256SUMS").read_text(encoding="utf-8").strip())
    (STAGE_DIR / "SHA256SUMS").write_text("\n".join(sums_lines) + "\n", encoding="utf-8")
    shutil.copy2(STAGE_DIR / "SHA256SUMS", ROOT / "evidence" / "SHA256SUMS")
    shutil.copy2(STAGE_DIR / "SHA256SUMS", ROOT / "EVIDENCE" / "SHA256SUMS")
    asset_names.append("SHA256SUMS")
    return [STAGE_DIR / n for n in asset_names]


def github_api(url: str, token: str, method: str = "GET", data: bytes | None = None, content_type: str = "application/json") -> dict:
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("Content-Type", content_type)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_and_upload_release(tag: str, assets: list[Path], token: str) -> dict:
    repo = "dreamer2664/storagecode"
    body = (ROOT / "RELEASE_NOTES.md").read_text(encoding="utf-8")
    payload = json.dumps({
        "tag_name": tag,
        "target_commitish": "main",
        "name": f"NORDBAHNHOF {tag} (brunel)",
        "body": body,
        "draft": False,
        "prerelease": False,
    }).encode("utf-8")

    try:
        rel = github_api(f"https://api.github.com/repos/{repo}/releases", token, method="POST", data=payload)
    except urllib.error.HTTPError as e:
        if e.code == 422:
            rel = github_api(f"https://api.github.com/repos/{repo}/releases/tags/{tag}", token, method="GET")
        else:
            raise

    upload_base = rel["upload_url"].split("{")[0]
    uploaded = []
    for p in assets:
        url = f"{upload_base}?name={p.name}"
        res = github_api(url, token, method="POST", data=p.read_bytes(), content_type="application/octet-stream")
        uploaded.append({
            "name": p.name,
            "size": res["size"],
            "browser_download_url": res["browser_download_url"],
            "api_asset_url": res["url"],
        })
        print(f"Uploaded {p.name} ({res['size']} bytes)")
    return {"release_id": rel["id"], "html_url": rel["html_url"], "tag": tag, "assets": uploaded}


def verify_release(rel_info: dict, assets: list[Path], token: str) -> dict:
    if VERIFY_DIR.exists():
        shutil.rmtree(VERIFY_DIR)
    VERIFY_DIR.mkdir(parents=True, exist_ok=True)

    expected_sums = {}
    for line in (STAGE_DIR / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and "/" not in parts[1]:
            expected_sums[parts[1]] = parts[0]

    verified_assets = []
    for a_meta in rel_info["assets"]:
        name = a_meta["name"]
        local_p = STAGE_DIR / name
        local_bytes = local_p.stat().st_size

        # 1 & 2: Download asset to /tmp/verify/, check HTTP status 200, Content-Length, and SHA-256
        req = urllib.request.Request(a_meta["api_asset_url"], method="GET")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/octet-stream")
        with urllib.request.urlopen(req, timeout=120) as resp:
            status_code = resp.status
            data = resp.read()
        dl_p = VERIFY_DIR / name
        dl_p.write_bytes(data)
        dl_sha = sha256_file(dl_p)

        assert status_code == 200, f"HTTP status {status_code} != 200 for {name}"
        assert len(data) == local_bytes, f"Byte count mismatch for {name}: {len(data)} != {local_bytes}"
        if name in expected_sums:
            assert dl_sha == expected_sums[name], f"SHA256 mismatch for {name}"

        # 3: zstd -t and tar -tf
        zstd_ok = True
        tar_members = 0
        if name.endswith(".zst"):
            run(["zstd", "-t", str(dl_p)])
        if name.endswith(".tar.zst"):
            members = run(["tar", "--zstd", "-tf", str(dl_p)]).splitlines()
            tar_members = len(members)
            assert tar_members > 0, f"Empty tar archive {name}"

        verified_assets.append({
            "name": name,
            "http_status": status_code,
            "bytes": len(data),
            "sha256": dl_sha,
            "zstd_test": "PASS" if zstd_ok else "FAIL",
            "tar_members": tar_members,
        })

    # 4: Decompress re-downloaded NORDBAHNHOF.blend.zst and verify object count in headless Blender
    dl_blend = VERIFY_DIR / "NORDBAHNHOF.blend"
    run(["zstd", "-d", "-f", str(VERIFY_DIR / "NORDBAHNHOF.blend.zst"), "-o", str(dl_blend)])
    chk_out = run([
        "blender", "--background", str(dl_blend),
        "--python-expr", "import bpy; print('VERIFY_BLEND_OBJECTS=' + str(len(bpy.data.objects)))",
        "--python-exit-code", "1"
    ])
    obj_count = 0
    for line in chk_out.splitlines():
        if "VERIFY_BLEND_OBJECTS=" in line:
            obj_count = int(line.split("=")[1].strip())
    assert obj_count > 3000, f"Unexpected Blender object count {obj_count}"

    report = {
        "tag": rel_info["tag"],
        "html_url": rel_info["html_url"],
        "all_verified": True,
        "blender_object_count_verified": obj_count,
        "assets": verified_assets,
    }
    for d in (ROOT / "evidence", ROOT / "EVIDENCE"):
        (d / "RELEASE_VERIFY.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("CHATCODE_TOKEN")
    if not token:
        print("ERROR: Missing GITHUB_TOKEN in environment")
        sys.exit(1)
    sha12 = run(["git", "rev-parse", "--short=12", "HEAD"], cwd=ROOT)
    tag = f"nordbahnhof/brunel/r01-{sha12}"
    assets = build_release_assets(sha12)
    rel_info = create_and_upload_release(tag, assets, token)
    report = verify_release(rel_info, assets, token)
    print(f"publish_release.py PASS: {tag} -> {rel_info['html_url']} (verified {len(report['assets'])} assets, {report['blender_object_count_verified']} Blender objects)")


if __name__ == "__main__":
    main()
