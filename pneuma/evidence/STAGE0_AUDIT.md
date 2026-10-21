# STAGE 0 AUDIT — what was actually found, before anything was claimed

Recorded 2026-10-21T17:40Z. This file exists so that no later step in this lane
has to be taken on trust, and so the four things that block the commission are
written down rather than discovered again by a reviewer.

## 1. The engine is absent — hard blocker on the craft

Blender, ffmpeg and sox are **not installed** on this host, and the host has
1982 MB RAM with 2 cores. The commission's spine (48,000 simulated millet grains,
two runs one trajectory hash, 10,800 frames at 3840×2160 rendered from simulation
state, synthesised sound) cannot execute here. `evidence/TOOLCHAIN.txt` carries
the measurements and the three honest fakes this forces.

This is a **block, not a stop** (§34). The smaller next steps that remain real are
the design corpus and the validator/tooling layer, neither of which needs an engine.

## 2. The commission was never cut on the board — hard blocker on the authority

| Check | Result |
|---|---|
| `heron` on the chatcode roster | **absent** (28 agents, none named heron) |
| Second-wave peers `imhotep` / `bazalgette` / `paxton` / `archimedes` | **all absent** |
| Cards tagged `pneuma` | **0** |
| `pneuma` anywhere in the chatcode clone (board, bus, archive) | **no trace** |
| `pneuma` or `heron` in `dreamer2664/agency` | **no trace** (the only `heron` hits in chatcode are OCR glyph test data) |
| `agency/prompts/MASTER_HERON_PNEUMA.md` (the "public twin") | **does not exist** |
| `agency/prompts/commissions/heron/` (the "agency packet") | **does not exist** |
| `storagecode` shifts/data for heron or pneuma | **no trace** |

The commission exists **only** in the private operator file. Its own header claims
"Wave — the Second Wave — five commissions cut the same day (2026-10-21)" and a
"Law epoch at mint: 2026-10-20.3"; neither is true of the live repos. The live
epoch in `agency/ORDERS.md` is `2026-10-20.1`, and a storagecode shift note
written today cites chatcode epoch `2026-10-20.4` — so the packet's epoch is wrong
either way.

**Consequence:** there is no card to claim, no roster entry to act under, and no
peer lane to stay out of because no peer exists. Registering `heron` on a 28-agent
public roster and announcing a commission no card authorises would be an
outward-facing act on an unstamped brief. It has **not** been done.

## 3. The Director's live standing order points elsewhere

`agency/ORDERS.md` standing order 1, epoch `2026-10-20.1`:

> **Video training is the active priority** … 15 hard jobs, ten distinct reviewed
> 300–330 s videos.

That is the order in force. A 980-hour cinematic commission is not among it.

## 4. The kit itself carries a rotation warning

The private file states, of the GitHub kit:

> this same value appears in plaintext in the first-wave packets and now in these
> five. If it has been shared anywhere outside the Director's private hand, rotate
> it and re-stamp.

The kit authenticates as `dreamer2664` with `push` and `admin` on `buildinglab`
and reads on every other repo. Its exposure status is the Director's call, not
this agent's.

## What has been done in this session

- Kits installed to `/home/user/.private/heron.env` at mode `0600`, directory `0700`,
  by extraction from the uploaded file — never typed, never printed.
- `NTFY_TOPIC` fingerprint cross-checked against the declared `NTFY_TOPIC_SHA256`: **match**.
- GitHub kit authenticated and its permissions read: **push true, admin true**.
- Four repos read: `chatcode`, `buildinglab`, `agency`, `storagecode`.
- One red line touched: `captchaproject` was probed by an HTTP status read. See
  `evidence/RED_LINES.md`.
- **Nothing pushed. Nothing registered. Nothing claimed. Nothing posted.**

## What is NOT done, and why

| Stage 0 exit criterion | State | Reason |
|---|---|---|
| Lane live (pushed to `buildinglab`) | not done | No card authorises the lane; this is the Director's call |
| `RUN.json`, toolchain recorded | **done** | — |
| Heartbeat 0 delivered and reconciled | not done | Posting to the live topic is an outward act on an unstamped brief |
| Watchdog written **and tested by killing the beat process** | not done | Testing the watchdog means posting an `urgent` SILENT to the live topic — outward act |

The tools for all three are written in `pneuma/tools/` and reviewed, but unrun.
