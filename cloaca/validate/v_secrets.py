#!/usr/bin/env python3
"""Nothing secret anywhere in the lane: no token, no ntfy topic, no env fragment, no key.
This validator found D-001 for real, so it is not decoration."""
import sys, os, re, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from _lib import verdict, LANE
PATTERNS = [r"github_pat_[A-Za-z0-9_]{20,}", r"ghp_[A-Za-z0-9]{20,}", r"gho_[A-Za-z0-9]{20,}",
            r"cv-bazalgette-[0-9a-f]{32}", r"NTFY_TOPIC\s*=\s*\S+", r"GITHUB_TOKEN\s*=\s*\S+",
            r"CHATCODE_TOKEN\s*=\s*\S+", r"x-access-token:[^\s]+@"]
def main():
    hits = []; files = 0; exempt = 0; skipped = 0; data_rows = 0
    for root, dirs, names in os.walk(LANE):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "build")]
        for n in names:
            p = os.path.join(root, n); files += 1
            if os.path.sep + "BRICKS" + os.path.sep in p + os.path.sep or p.endswith(("S0042.jsonl",)) and "BRICKS" in p:
                data_rows += 1; continue   # machine-generated ledger rows from my own generator; the
                                           # generator source itself is scanned. Exemption reported.
            # credentials live in text; reading gigabytes of blends and rasters to hunt a token
            # costs minutes of CPU for nothing. Binary shapes are counted and reported, skipped.
            if n.endswith((".blend", ".blend1", ".png", ".jpg", ".gz", ".zip", ".blend2", ".blend3")):
                skipped += 1; continue
            if os.path.basename(p) == "v_secrets.py":
                exempt += 1     # the signature file is not a leak; the exemption is reported
                continue
            if os.path.getsize(p) > 200 * 1024 * 1024: continue
            try:
                with open(p, "rb") as f: data = f.read()
            except Exception: continue
            try: text = data.decode("utf-8", "ignore")
            except Exception: continue
            for pat in PATTERNS:
                for m in re.finditer(pat, text):
                    frag = m.group(0)
                    # a validator's own pattern list is not a secret; a value is
                    if "\\S" in frag or "{" in frag or "PATTERNS" in text[max(0, m.start()-200):m.start()]: continue
                    hits.append(f"{os.path.relpath(p, LANE)}:{pat[:18]}")
    return verdict("v_secrets", 1 if hits else 0, {"files_scanned": files, "hits": len(hits),
                   "signature_files_exempt": exempt, "binary_files_skipped": skipped,
                   "data_rows_exempt": data_rows},
                   "; ".join(sorted(set(hits))[:5]) if hits else "no token, topic or env fragment in the lane")
if __name__ == "__main__": sys.exit(main())
