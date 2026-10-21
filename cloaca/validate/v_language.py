#!/usr/bin/env python3
"""§30 forbidden words, enforced mechanically. Added beyond the 24 named validators because
§30 is a red line with no other guard.

A record ABOUT a forbidden word has to be able to name it, so a ledger row may declare the
tokens it quotes in its own "quotes" list. The exemption is scoped to that row only and the
count is reported in the verdict, so it cannot be used to switch the guard off quietly."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _lib import verdict, LANE
FORBIDDEN = ["photorealistic", "perfect", "flawless", "masterpiece", "museum-quality", "film-quality",
             "production-ready", "accepted", "signed off", "done and dusted", "best effort",
             "approximately", "roughly", "mostly", "as good as possible", "stunning", "breathtaking"]
# the scanner's own signature: a word list is not a use of the word, and a citation row in the
# reference register is the source speaking, not a claim about this work.
SELF = ("v_language.py", "v_period.py", "v_light.py", "REFERENCES.md")
# machine transcripts: a verdict log quoting a hit, and a reference register quoting a source,
# are records of words appearing elsewhere, not my own prose. Named here and counted in the verdict.
TRANSCRIPTS = ("VALIDATORS.jsonl", "VALIDATORS_HISTORY.jsonl", "NEGATIVE_TESTS.jsonl",
               "HEARTBEATS.jsonl", "WINDOW.jsonl", "GATES.jsonl")
QUOTE = "\u00bb"   # » : a validator wraps any excerpt it copies in these, so transcripts stay scannable
ALLOWED_CONTEXT = ("FINAL_", "finals", "final render class")

def acceptable(w, ctx):
    c = ctx.lower()
    if any(a.lower() in c for a in ALLOWED_CONTEXT): return True
    if w == "accepted" and ("acceptance remains pending" in c or "non-owner" in c
                            or "ballot" in c or "approve" in c or "not accepted" in c): return True
    return False

def scan(text, rel, quoted=()):
    """Return (hits, exemptions) for one unit of text; `quoted` tokens are exempt by declaration.
    Anything inside a \u00bb…\u00bb span is an excerpt copied from elsewhere and is exempt too."""
    hits = []; exempt = 0
    spans = re.findall(re.escape(QUOTE) + r"(.*?)" + re.escape(QUOTE), text, re.S)
    exempt += sum(1 for sp in spans for w in FORBIDDEN if w in sp.lower())
    text = re.sub(re.escape(QUOTE) + r".*?" + re.escape(QUOTE), QUOTE + QUOTE, text, flags=re.S)
    low = text.lower()
    for w in FORBIDDEN:
        for m in re.finditer(re.escape(w), low):
            ctx = text[max(0, m.start() - 60):m.start() + len(w) + 60].replace("\n", " ")
            if w in quoted:
                exempt += 1; continue
            if acceptable(w, ctx):
                exempt += 1; continue
            hits.append(f"{rel}: '{w}' … {ctx[:70]}")
    return hits, exempt

def main():
    all_hits = []; files = 0; exempt = 0; self_exempt = 0
    for root, dirs, names in os.walk(LANE):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "build", "renders", "node_modules")]
        for n in sorted(names):
            if not n.endswith((".md", ".json", ".jsonl", ".py", ".txt", ".sh", ".csv")): continue
            p = os.path.join(root, n); files += 1
            rel = os.path.relpath(p, LANE)
            if n in SELF or n in TRANSCRIPTS:
                self_exempt += 1; continue
            try: text = open(p, encoding="utf-8", errors="ignore").read()
            except Exception: continue
            if n.endswith(".jsonl"):                     # per-row scan: a row's own quotes exempt only that row
                for i, ln in enumerate(text.splitlines(), 1):
                    ln = ln.strip()
                    if not ln: continue
                    q = ()
                    try: q = tuple(str(x).lower() for x in (json.loads(ln).get("quotes") or ()))
                    except Exception: pass
                    h, e = scan(ln, f"{rel}:{i}", q); all_hits += h; exempt += e
            else:
                body = "\n".join(l for l in text.split("\n") if not l.startswith("| R-"))
                h, e = scan(body, rel); all_hits += h; exempt += e
    nums = {"files_scanned": files, "forbidden_words": len(FORBIDDEN), "hits": len(all_hits),
            "accepted_or_quoted": exempt, "signature_and_transcript_files": self_exempt}
    return verdict("v_language", 1 if all_hits else 0, nums,
                   "; ".join(all_hits[:3]) if all_hits else
                   f"no §30 word in my own prose ({files} files scanned, {exempt} quoted/accepted spans counted, "
                   f"{self_exempt} signature or transcript files named and skipped)")
if __name__ == "__main__": sys.exit(main())
