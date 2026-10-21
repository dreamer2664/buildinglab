# WATCHDOG_TEST — paxton / CRYSTAL (Stage 0 · §20 · F33)

Per Part V §20: *"The watchdog first: polls the topic; 16 minutes of your silence → urgent `PAXTON SILENT` with your last seq. Test it by killing your beat process; commit the test output (F33)."*

## 1. Architecture (`crystal/tools/watchdog.sh`)

- Polls `${NTFY_SERVER}/${NTFY_TOPIC}/json?poll=1&since=all&scheduled=0` every `POLL_SEC=180` seconds.
- Strips `.topic` in memory immediately (`jq -c 'del(.topic)'`) so the topic secret never touches disk or logs (§2.4).
- Filters strictly for agent beats (`title` starts with `"PAXTON"`, excluding `"SILENT"` alarms and pre-boot `"channel test"` messages) so the watchdog never treats its own alarm as proof of life (preventing Daedalus Bug 1 / F33).
- Computes beat age from the server's `time` field against current UTC epoch (`now - newest`).
- When `age_sec >= SILENCE_SEC` (production default `SILENCE_MIN=16` = `960s`), posts `Priority: urgent`, `Title: PAXTON SILENT`, `Tags: rotating_light,skull`, body `"no beat for <N> min (<S>s); last id <id>; expected seq <n>"`.
- Enforces a 30-minute (`1800s`) cooldown per silence episode so the phone rings once per episode rather than vibrating continuously.

## 2. Executed Verification Sequence (`evidence/WATCHDOG_TEST.log`)

| Step | Timestamp (UTC) | Action | Observed Result |
|---|---|---|---|
| 1 | `2026-10-21T17:35:57Z` | Production threshold negative test (`SILENCE_MIN=16`, beat `yYqO2kzVeWZ1` age `272s`) | `poll: newest beat 4m (272s) old (id=yYqO2kzVeWZ1, beats=1)` — no false alarm fired |
| 2 | `2026-10-21T17:35:58Z` | Started `hb_daemon.sh` (`pid=4486`), killed with `kill -9 4486`, polled with threshold tripped (`SILENCE_SEC=5`) | `ALARM: no beat for 4m (273s >= 5s) last_beat_id=yYqO2kzVeWZ1 expected_seq=1` → delivered ntfy message `id=8c9eHQTaQZDi` |
| 3 | `2026-10-21T17:35:59Z` | Immediate follow-up poll (`pid=4529`) to verify alarm exclusion & cooldown suppression | `poll: newest beat 4m (274s) old (id=yYqO2kzVeWZ1, beats=1)` (`8c9eHQTaQZDi` excluded from beats) + `STILL SILENT 4m (274s) — alarm suppressed (cooldown 1800s)` |

## 3. Server Receipt

- Boot beat (`seq=0`): `id=yYqO2kzVeWZ1`, `server_time=1792603885`
- Watchdog urgent alarm (`PAXTON SILENT`): `id=8c9eHQTaQZDi`, `priority=5`, verified on server via `hb_reconcile.py`.
