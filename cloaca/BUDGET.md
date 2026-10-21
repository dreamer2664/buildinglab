# BUDGET — measured costs, and what they mean for the 1,080-hour commission

Every number here is measured in this sandbox (2 CPUs, 1.9 GiB RAM, no swap, Blender 4.3.2 headless,
Cycles CPU). Nothing is declared. Where a cost makes a packet target unreachable at this station,
the shortfall is stated rather than hidden.

## Chunk pipeline (Stage B work, running network-wide now)

| quantity | measured | source |
| --- | --- | --- |
| lay one 72,106-row ledger | 2.0–2.6 s | `evidence/PIPELINE.jsonl` wall_s minus build |
| build + save one chunk | 1.5–1.7 s Blender, 402 MB peak | CENSUS build_s / peak_mb |
| whole chunk, wall clock | 5.2 s mean, 6 s max | `evidence/PIPELINE.jsonl` |
| network: 1,320 chunks | ≈ 1.9 h serial | extrapolation of the measured mean |
| open budget (§15.5) | 120 s/chunk — actual 6 s | 20× inside budget |
| memory ceiling | 1,200 MB — actual 402 MB peak | agency SANDBOX.md doctrine |

Disk: a chunk blend is 57 MB. 1,320 of them is 75 GB; this station has 18 GB free. The binaries are
reproducible from ledger + seed — `tools/reproduce.py` rebuilt S0042 and S0000 in a clean room to
identical census and u_hash — so the pipeline keeps a rolling window of 40 blends and deletes the
rest once their census is recorded in `INDEX.jsonl` and `evidence/CENSUS/`. The ledgers are the
master (1.6 GB of gzipped shards for the full network). C-018 records this doctrine.

## Renders

| view | resolution | samples | measured |
| --- | --- | --- | --- |
| proof, interior/macro | 1024 × 576 | 64 | 83–123 s |
| extrapolated final, 2560 × 1440 | ×6.25 pixels | 64 | ≈ 9–13 min |
| extrapolated final, 2560 × 1440 | ×6.25 | 128 | ≈ 18–26 min |
| extrapolated final, 3840 × 2160 | ×14 | 128 | ≈ 40–57 min |

The packet requires 1,284 views (§24). At the measured rates the full final set is ≈ 450–550 CPU
hours on this machine — weeks of wall clock at two cores. That is stated here plainly: **the 1,284
finals cannot all be rendered at this station inside the commission window.** The plan that follows
from the measurement:

1. Proofs at 1024 for every class first (R2), which is what exists now for five views of S0000.
2. Finals rendered in priority order — the 340 sections and 158 profile tiles are orthographic
   line-work and cost seconds, not minutes; the 12 hydraulic maps likewise. That is 510 of the 1,284
   views at drawing cost.
3. The expensive classes (interiors, macros, people, aerials) rendered to the count the remaining
   budget allows, each row carrying its measured cost, and the unrendered remainder listed in
   `HANDOFF.md` as work owed, not as work done.

No render is upscaled to reach a resolution (F10); a missing view is a missing view and is recorded
as one.

## Heartbeats and board

| quantity | law | measured |
| --- | --- | --- |
| ntfy beat | every 7 min, ≤210/day | beatloop pid in `evidence/RUN.json`; degrade to 21-min on 429 is lawful |
| board beat | every 15 min | chatcode post |
| hb_reconcile | every 2 h | `tools/hb_reconcile.py` |
| watchdog | urgent SILENT at 16 min without a beat | tested once on purpose, id recorded |

## GitHub API

Fine-grained PAT, 3,858/5,000 core at session start. Reads go through `--repo-dir` clones; the
pipeline commits in batches of 25 chunks, so ≈ 53 push calls for the whole network.

## What this budget refuses to pretend

- 61 M bricks is a floor, not a target: the network census is 175,101,280 predicted rows. Laying
  them all as ledger shards costs ≈ 1.6 GB gzipped and ≈ 50 min of lay time. Building all 1,320
  blends costs ≈ 1.9 h of Blender and 75 GB of disk, of which only a rolling window is kept.
- The 1,284 finals are the binding constraint on this station, and §24's blind test and G14 need a
  reviewer this station cannot supply. Both are recorded as owed in `HANDOFF.md`.
