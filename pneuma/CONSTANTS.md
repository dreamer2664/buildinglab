# CONSTANTS.md — the numbers this lane is built on

Fixed by the commission (§36: the runtime, frame count, gates, lane and silence
are not the agent's to change). Everything else here is derived and labelled.

## 1. The film — fixed

| Constant | Value |
|---|---|
| Runtime | **7 min 30 s** exactly |
| Frame rate | 24 fps |
| Frames | **10,800** |
| Resolution | **3840 × 2160** |
| Frame uniqueness | 10,800 distinct sha256; zero duplicates, zero interpolations, zero upscales |
| Shot structure | 15 shots × 30 s, seeded boundary states |
| Scene changes | 4 (between 5 scenes), each ±0.4 s of `TIMING.md` |

## 2. The machine — fixed

| Constant | Value |
|---|---|
| Named parts, cart-theatre | **≥ 2,800** |
| Mechanisms | **34**, each cited (see `SOURCES.md`) |
| Grains | **48,000** rigid bodies |
| Ropes | **9 systems**, **340 m** ±1 %, twist recorded per system |
| Rope tension samples | 240 frames → `ROPES.jsonl` |
| Rope penetration checks | every 5th frame = **2,160**, zero failures |
| Figures | **8**, ≥18 joints each |
| Keyframed machine parts | **0** (cameras and lights may be keyframed) |
| Parenting inside a mechanism | **0** — constraints only |
| Screws anywhere | **0** (G10, F39) |

## 3. The other artifacts — fixed

| Artifact | Requirement |
|---|---|
| Temple doors | open ≤90 s from first flame; close ≤120 s from extinction |
| Aeolipile | rotation emerges from jet reaction; **no motor object in the file** |
| Dispenser | 100-coin trial ledger; per-coin dispense variance ≤3 % |
| Sound | 450 provenance rows (one per second); re-synthesis ±3 dB RMS; zero library/uploaded/AI audio |
| Thunder | 14 stone drops into a hidden drum → `THUNDER.jsonl` |
| Views | **594** required, across 12 classes |
| Drawings | **34**, one per mechanism, citation on the sheet |
| Proof sheets | 45 × 240 frames at 256 px, every one opened |
| Blind test | 24 trials / 6 classes; ≥18/24 "could work"; ≤6/10 photo-confusion |

## 4. Derived constants — this lane's arithmetic

| Constant | Value | Derivation |
|---|---|---|
| Millet grain mass | **3.1 mg** | 2.36 mm³ × 1.30 g/cm³ |
| Millet bulk density | 790 kg/m³ | poured test weight |
| Grain supply mass | **148 g** | 48,000 × 3.1 mg |
| Grain supply volume | 187 cm³ | 148 g / 790 kg/m³ |
| **Required discharge rate** | **0.329 g/s** | 148 g / 450 s (`GRAIN.md` §3) |
| Beverloo orifice for that rate | 6.2 mm | `Q = C ρ_b √g (D_o − kd)^2.5`, k=2 |
| Sim grain scale | **4×** (8 mm) | solver contact margin; see `GRAIN.md` §2 |
| Sim time scale | **2×** (Froude, t ∝ √(L/g)) | the correction |
| Timing band | ±0.4 s per scene change | fixed; ±140 s at 1σ is the *uncalibrated* band |

## 5. The stage ladder — fixed hours

| Stage | Hours | Exit |
|---|---|---|
| 0 bootstrap | 0–4 | lane live, toolchain recorded, heartbeat 0, watchdog tested |
| A sources + design | 4–60 | `SOURCES.md`, `MECHANISMS.md`, `CONSTANTS.md`, `DRIVERS.md`, `GRAIN.md`, `BUDGET.md` |
| B chassis + first rope | 60–160 | cart, axle, drum, first rope; two runs one hash |
| C theatre + periaktoi | 160–280 | stage, six prisms, flats; scene change 1 at ±0.4 s |
| D the eight figures | 280–400 | 8 automata, 18+ joints, drive chains documented |
| E grain + timing | 400–480 | 48,000 grains live; full dry run at ±0.4 s |
| F the other machines | 480–600 | temple doors, aeolipile, dispenser |
| G sound | 600–700 | event ledgers → synthesis → 450-row map → ±3 dB |
| H the film | 700–900 | 15 shots: sim → proof → inspect → 4K |
| I package | 900–980 | 594 views, drawings, blind test, publication, reproduction |

**Budget: 980 h.** At 24 h/day of wall clock that is 41 days; the honest position
of this lane against it is in `evidence/BUDGET.md`.

## 6. Measured on this host — not fixed, and not ours

| Measurement | Value | Where |
|---|---|---|
| Blender | 4.3.2, headless boots at 261 MB RSS | `evidence/ENGINE_PROBE.json` |
| EEVEE_NEXT | **cannot render** — no EGL/GPU context | `evidence/TOOLCHAIN.txt` |
| Cycles CPU | renders; **no OpenImageDenoise** (F20) | `evidence/ENGINE_PROBE.json` |
| Rigid-body determinism | **reproduces** — 2 runs, 1 trajectory hash | `evidence/TRAJECTORY_HASHES.jsonl` |
| RAM ceiling | 1982 MB total | `evidence/BENCH.json` |
| Grain bake rate | see `evidence/BENCH.json` | measured |
| 4K render rate | see `evidence/BENCH.json` | measured |

## 7. The silence constants

| Constant | Value |
|---|---|
| ntfy beat | every **7 min** |
| Board heartbeat | every **15 min** |
| Reconcile | every **2 h** |
| `HB-GAP` | >12 min |
| Watchdog urgent | **16 min** |
| Beats per day | ≤210 (shared free tier, 250/day across the wave) |
| Degraded cadence on 429 | 21 min, logged `HB-QUOTA` |
