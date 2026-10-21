# HANDOFF — where the work stands, how to resume, what is owed

Written 2026-10-21T20:18:55Z by bazalgette on branch `agent/bazalgette/t-20261021-8511`, card `t-20261021-8511`
(lease 2026-10-22T03:56:27Z). This file is the conservative-assumption log §36 requires and the
resume procedure NO-STOP-001 requires. Read it top to bottom before touching anything.

## Live processes at the time of writing

| process | purpose | state |
| --- | --- | --- |
| beatloop (see `evidence/RUN.json` for pid) | ntfy beat every 7 min, board beat every 15 min | running; last seq in `evidence/HEARTBEATS.jsonl` |
| watchdog | urgent SILENT if no beat for 16 min | running |
| chunk pipeline (`tools/pipeline_loop.sh`, start_process id chunk-pipeline-9b5a8523) | lays, builds, verifies, records every chunk S0011→S1319; commits+pushes every 25 chunks; prunes blends to a 40-chunk rolling window | next = S000043; 31 chunks recorded, 31 ok |

If the sandbox died and you are reading this in a new one: `bash tools/beatloop.sh &` and
`bash tools/watchdog.sh &` first (silence is the unforgivable defect), then
`nohup bash tools/pipeline_loop.sh &` — it resumes from `evidence/PIPELINE_STATE.json` and skips
chunks whose census is already recorded. Everything else resumes from git.

## Conservative assumptions logged (§36: no questions, statements only)

1. **Chunk binaries are ephemeral; the ledgers are the master.** 75 GB of blends cannot live on an
   18 GB station and cannot live in git history. The clean-room reproduction (G13 rehearsal) proves
   a blend rebuilds bit-identical in census and u_hash from ledger + seed, so a rolling window of 40
   blends is kept and the rest are deleted after their census is recorded (C-018). A reviewer who
   wants chunk S0900 opens it by rebuilding it, which is also what G13 demands.
2. **The 1,284 finals of §24 exceed this station's render budget** (BUDGET.md: ≈450–550 CPU hours).
   Proofs at 1024 for every class come first; the 510 orthographic drawing views are cheap and will
   carry most of the count; the expensive classes are rendered to the count the budget allows and
   the remainder is listed here as owed, never as done.
3. **Admiralty tidal constants for London Bridge were unobtainable**; the harmonic set in TIDES.json
   is a least-squares fit to published PLA/BBC predictions (RMS 0.0244 m) and stays open-provisional
   as D-003 until the Admiralty table or a PLA booklet can be read.
4. **1,315 intra-line joins, not the packet's 1,319**: five lines of 300/270/220/280/250 chunks give
   1,315 internal joins. Both numbers are reported everywhere joins are quoted (C-015).
5. **Historical engine speed and stroke carried as history, commission values used as law**:
   14 strokes/min and 3.05 m beam stroke per the packet; the historical 11 rpm and 2.743 m stroke
   stay in `historical_*` fields (C-002, C-003).
6. **The wet line and submersion darkening are derived at lay time from the HYDRAULICS ledger**, not
   painted at render time, so the wear law remains a consequence of the ledger (R5, D-014).

## What is measured and passing now

- Validator battery: 17 PASS, 8 PENDING, 0 FAIL (`bash validate/run_all.sh`).
- Negative battery: 40 cases, 40 proven refusals (`python3 tools/negative_tests.py`).
- Gradient: 1,315 joins continuous to 0.000 mm, zero uphill metres.
- Tide: 4,032 samples, max |Δ| 0.100 m against the 0.15 m tolerance, six gauges.
- Overflows: 17 actuations in the 28-day gate window, 55 over 180 days, six of six open, zero
  scripted, every row carries its driver.
- Bricks: network census predicted 175,101,280 (2.87× the 61 M floor); the built slice passes
  census = ledger, uniqueness and mesh-link samples on every chunk.
- Reproduction: S0042 and S0000 rebuilt clean-room to identical hashes.
- Gates: G2 and G3 PASS; the other twelve PENDING with the blocking clause named in GATES.jsonl.

## PENDING validators and the stage that clears them

v_cycle, v_drawings, v_facing, v_kinematics, v_parts, v_people, v_renders, v_stations

## Open defects (never hidden, always numbered)

D-003 tidal constants provisional · D-005 90 reaches below 0.67 m/s at dry-weather flow (all clear
half-full; recorded, not fixed by fudging the gradient) · everything else closed-fixed with its fix
named in `evidence/DEFECTS.jsonl`.

## Owed work, in order

1. Finish the network lay/build (pipeline is running; ≈1.9 h of machine time).
2. Stations, engines, parts, kinematics, P-V (Stage H) per PARTS_SCHEDULE.md.
3. People, yards, embankments, lampposts (Stage G subjects still absent).
4. Drawings: 340 sections, 158 profile tiles, 12 hydraulic maps (Stage H).
5. Renders to the §24 count within the BUDGET.md envelope; proofs for every class first.
6. Blind test (G12) and G14's 40 locations: reviewer-side; prepare the packs, do not self-score.
7. Window release `best-renders-cloaca` with BEST.zip once ≥40 renders exist; superseded zips to
   storagecode first; `evidence/WINDOW.jsonl` appended at every cut.

## Secrets

The live PAT and the ntfy topic were pasted into chat earlier in this session. §2.1/§2.4.6 call for
rotation on suspected exposure. Rotation is the Director's call, not mine: it is flagged here and in
the final report, once, and not acted on unilaterally. No credential is written into any lane file;
`validate/v_secrets.py` scans every commit for credential shapes and its negative test proves it
catches one.
