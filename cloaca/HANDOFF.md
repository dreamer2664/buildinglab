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

## Addendum 2026-10-22T05:51Z — sandbox restart, recovery, and what it changed

The station restarted the sandbox at a turn boundary. The working tree came back from a
capped snapshot: every uncommitted binary was gone (chunk, engine, station, yard,
embankment and people blends, drawing rasters, proof pngs, build logs), installed packages
(blender, rsvg-convert, ffmpeg) were gone, and the local .git had rolled back to a
pre-cloaca commit. R3 decided the outcome: everything committed and pushed survived,
including the pipeline's own batch pushes to S0861.

Recovery order, as executed (this is the standing procedure, C-022):
1. beats first — beatloop and watchdog relaunched before anything else;
2. git fetch + reset to the remote head (45a8787), branch reattached, credential helper
   repointed at /home/user/.private/git-credentials (a global helper that expanded
   the token variable at call time was sending an empty password to pushes — D-017 records
   the token-in-config slip made and unmade during this);
3. packages reinstalled (apt: blender, librsvg2-bin, ffmpeg);
4. ignored artifacts regenerated from committed tools: 510 drawing sheets + rasters at
   class pixels, 28 tide charts, 22 engines built and animated, 4 stations, 6 overflows,
   3 yards, 3 embankment reaches, 120 figures;
5. loops relaunched from their state files: compress_shards, pipeline (resumed at S0862),
   render loop (resumed at 546 registered views);
6. battery re-run: 24 PASS · 1 PENDING (v_renders) · 0 FAIL; GATES refreshed by the new
   tools/gates.py.

Losses that mattered and their fixes:
- build/raster.sh existed only as a heredoc in a dead shell — tools/make_raster_sh.sh now
  carries its content committed, and the raster path bug it hid (pngs landing beside the
  svgs, HM class at the wrong pixel size) is fixed in the committed copy;
- tools/state.py was gz-blind: with plain shards pruned it reported a 72,106-brick census
  against a 117 M-brick mesh — the beats would have been false (§32). It now counts gz
  masters with a stat-validated cache, compares census to ledger per settled chunk instead
  of in raw totals (a mid-batch race is reported as racing, never as a mismatch), and gauges
  pct against the C-001 predicted 175,101,280 rather than the 61 M floor, which no longer
  reports >100 % while chunks remain unplaced;
- the GATES one-off was replaced by tools/gates.py, rerunnable after any battery.

Standing conclusion: the working tree is a cache. Only pushes survive. Any artifact that
cannot be pushed must be regenerable from something that was.
- 2026-10-22 window note: station fabric v3 (true-scale brick courses 230x75 with 20 mm mortar and bump, stone-flag floors at 0.8 m, desaturated stock brick, daylight hero at world 0.25 / sun 3.0); engine_house interior camera moved to gallery height (z 7.4, y = -D/2+4.2 derived from HOUSE/FLOOR-001, lens 30) after the aisle camera sat inside the colonnade row on narrow houses; interior proofs acceptable on all four stations (scanned colonnade + keystone arcade + gilt capitals + pedestal row + timber trusses).
- disk_guard.sh launched as its own daemon: prunes chunk blends to a 16 window (6 at >92 % volume) only when the brick gz shard is git-tracked and the census exists (C-018 rebuild guarantee); the 25 GB volume filled once at chunk ~1169 (51 blends pruned by hand, 5.0 GB recovered) before the guard existed.
- G12 blind battery prepared: tools/blind_test.py prepare wrote evidence/BLIND/trials.jsonl (24 trials, 6 classes: light, palette, bond, glazing, tide, dress) and key.jsonl; 24 control views (ids BL-*) appended to RENDER_SCHEDULE (780 rows); render_batch grows blind_<class> control arms that break exactly one law each; control proof verified by eye (cold electric wash vs warm gas). Scoring ignores any runner id of this agent: the gate stays PENDING until an independent runner records answers.
- D-020 open: hero views show over-bright cornice/string lines at raking sun and one unidentified pale ground slab east of the house; final-stage polish queued.
- RECOVERY 4 (2026-10-22 ~11:26Z): sandbox rollback again. Symptoms: .git replaced by a fresh clone of main (no origin remote, SSH-less), /home/user/.private/git-credentials deleted, all daemons killed, apt Blender gone, gitignored dirs (build/, stations/scans, stations/scan_lib_build, people/scans?) wiped. Working tree files survived. Recovery executed: ntfy beat first; creds regenerated from GITHUB_TOKEN (store file, x-access-token form); remote re-added over HTTPS; branch fetched (tip 93746a0 carried every commit incl. the schedule scale-up - the loop's pushes had landed before the rollback); checkout -f -B onto the branch; uncommitted evidence (census S1300+, RENDERS, schedule, INDEX, hearts) restored from /tmp/rc4 and committed (c1a74ae); swap re-ensured (4 GB); six daemons relaunched (pipeline, render, disk_guard, beatloop, watchdog, hb_reconcile); Blender reinstall via sudo apt in flight; PIPELINE_STATE next to be reset to 1300 so chunks 1300-1319 rebuild once Blender returns (their lays already verified deterministic: S1318 census 174,450 = predicted).
- Scan libraries under gitignored paths must be treated as EPHEMERAL: stations/scan_lib_build and people/scans may need re-preparation after any future rollback; the download URLs live in evidence/BUILD_SCAN_SOURCES.jsonl and evidence/SCAN_SOURCES.jsonl so re-acquisition is mechanical.
- COMPLETION (2026-10-22 12:20Z): network 1320/1320 chunks built and indexed; census = ledger = 173,131,158 brick rows (mesh objects 175,105,806); completion sweep 24/24 validators PASS; gates G1-G11 PASS. G12 awaits an independent blind runner (harness + 24 trials committed, controls rendering); G13 awaits stranger verification; G14 belongs to the reviewer. Render register 730/1,284 and climbing in the gap loop. Completion window cut published to release 420137576 (WINDOW-COMPLETION-20261022.zip, sha logged).
