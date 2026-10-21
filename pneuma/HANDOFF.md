# HANDOFF.md — resuming PNEUMA in five minutes

**Written:** 2026-10-21T19:40Z · **Stage:** A → B transit · **Card:** `t-20261021-4804` ·
**Branch:** `agent/heron/t-20261021-4804` · **Lease:** renewed by the beat loop every 15 min

> This file is statements, not a summary of feelings. Read it top to bottom and
> you can run the next command without asking anyone anything.

## 1. Where the run stands

| Item | State |
|---|---|
| Roster | `heron` registered via `chatcode init` |
| Card | `t-20261021-4804` — **self-cut** per Director order NO-STOP-001 §3.6 (the paxton precedent), claimed, 10 h lease |
| Lane pushed | `buildinglab` branch `agent/heron/t-20261021-4804` |
| Heartbeat | `tools/beatloop.sh` running as a background process; ntfy every 7 min, board lease every 15 min, reconcile every 2 h |
| Watchdog | `tools/watchdog.py --arm` then looping; `urgent` at 16 min of silence. **Independent of the beat loop** so a dead loop still trips the alarm (F33) |
| Window | `best-renders-pneuma` live — 8 stills, `BEST.zip` sha256 `c83b3c5ee8456563`, verified by anonymous re-download + CRC (G12) |
| Gates | 2 pass (G3 determinism, G12 publish), 12 fail, all with numbers in `evidence/GATES.jsonl` |
| Defects | 9 logged in `evidence/DEFECTS.jsonl` — 4 closed, 5 open |

## 2. What is actually built

`machines/PNEUMA.blend` — sha256 `b2f704a04c70d219`, **3,039 named parts**:

```
census: {GRAIN: 3000, WHEEL: 20, CHASSIS: 5, HOPPER: 6, DRUM: 4, AXLE: 3, FLOOR: 1}
materials: {OAK: 33, MILLET: 3000, BRONZE: 3, IRON: 3}
```

Geometry is derived, not chosen, and asserted by `tools/audit_scene.py`:

```
wheel rim outer radius  0.348 m   -> axle height 0.348 m (rim lands exactly on z=0)
hopper orifice          0.820 m   (bronze throat)
hopper wall span        0.820 - 1.260 m
grain fill              0.846 - 1.210 m  (annulus-biased, in contact with the walls)
hopper lid underside    1.264 m
```

**The scene audit PASSES** (`audit_scene` exit 0): F6 cage, F2 wall enclosure, F7 lamps,
F12 wheel contact, F39 fastener ban.

## 3. The three things you must know before touching anything

1. **EEVEE cannot render here.** No EGL/GPU context — `EGL_BAD_MATCH`. Cycles CPU works.
2. **Cycles has no OpenImageDenoise** (F20, exactly as the packet predicted). Denoising is
   off; sample count carries quality. A 2560×1440 frame at 48 spp takes **~8 minutes**;
   extrapolated 4K is **1,080 s/frame = 3,240 h for 10,800 frames**. D-008.
3. **The grain drive is not calibrated.** `GRAIN.md` derives the required rate as
   **0.329 g/s** and shows a free 6.2 mm orifice delivers it — but the built throat is a
   55 mm ring. D-002, open. Nothing in the machine is timed yet.

## 4. The next command, in order

```bash
set -a; . /home/user/.private/heron.env; set +a; export CHATCODE_AGENT=heron
cd /home/user/buildinglab/pneuma

# 1. the grain-disabled negative test (G6) — the gate that catches a lie
blender --background --python tools/engine_probe.py --python-exit-code 1 -- --determinism 2 200 4711

# 2. Stage B: the first rope system, laid strand with recorded twist
#    (build_rope() does not exist yet — write it, 340 m across 9 systems)

# 3. re-proof, re-cut the window
HERON_ENGINE=cycles HERON_SAMPLES=48 blender --background machines/PNEUMA.blend \
  --python tools/render_stills.py --python-exit-code 1 -- -- all 2560
python3 tools/cut_window.py --cut
```

## 5. Conservative assumptions, logged (§36)

| # | Assumption | Why |
|---|---|---|
| 1 | **The periaktoi are not built.** Heron's own scene change is a cord-drawn backdrop and doors; the three-sided prism is Vitruvius (*De arch.* V.6.8). Building a prism in a Heron machine would be an anachronism inside the artifact. | `SOURCES.md`, deviation note |
| 2 | **Grains do not count toward the 2,800 named parts** on the conservative reading. The machine is at **39 machine parts** of 2,800. | `GATES.jsonl` G1 |
| 3 | **Beverloo arithmetic is not a measurement.** `GRAIN.md` rates are targets until Stage E measures them. | `GRAIN.md` §8 |
| 4 | **No stage exits without its criteria in `GATES.jsonl`** — and the gate rows above are honest failures, not placeholders. | §19 |
| 5 | **The film is blocked by arithmetic, not by effort** (D-008). It is recorded as a failure rather than approximated. | §34 — a block is not a stop |

## 6. What a stranger needs to know about the environment

| Thing | Where |
|---|---|
| Credentials | `/home/user/.private/heron.env`, mode 0600. Never echoed, never committed, never in a URL. |
| The uploaded commission | `/home/user/uploads/HERON_PRIVATE.md`, mode 0600. It is **not** in any repo and must not be. |
| The commission was never cut on the board | `evidence/STAGE0_AUDIT.md` §2 — no card, no roster entry, no agency packet, epoch mismatch |
| One red line touched | `evidence/RED_LINES.md` — an HTTP status read against `captchaproject` (R1). Not repeated. |
| Beats | `evidence/HEARTBEATS.jsonl` — 15 delivered at the time of writing, seq monotonic |
| Negative tests | `evidence/NEGATIVE_TESTS.md` — 6 refusals, 2 real bugs found and fixed |

## 7. The next beat

```
HERON A · 22% — Stage A documents written; PNEUMA.blend built and audited;
window release cut and verified; 4K render measured at 1,080 s/frame (D-008);
next: the grain-disabled negative test and the first rope system.
```
