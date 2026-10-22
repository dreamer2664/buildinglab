#!/usr/bin/env python3
"""Next unregistered schedule item. With SKIP_CHUNK=1 in the environment, chunk scenes are skipped:
while the chunk pipeline is building, a second big Blender would push the 1.9 GiB station toward
the OOM killer, and chunk interiors are exactly the heavy ones."""
import json, os
skip = os.environ.get("SKIP_CHUNK") == "1"
reg = set()
for l in open("evidence/RENDERS.jsonl"):
    l = l.strip()
    if l: reg.add(json.loads(l)["id"])
for s in json.load(open("evidence/RENDER_SCHEDULE.json")):
    if s["id"] in reg: continue
    if skip and s["scene"].startswith("chunk:"): continue
    print(json.dumps(s)); break
