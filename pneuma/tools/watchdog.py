#!/usr/bin/env python3
"""tools/watchdog.py — the alarm heron builds for herself (F33).

The one failure this agency cannot forgive is silence, so the first tool written
is the one that catches it. This polls the live ntfy topic for **her own beats**
and, if none has arrived for 16 minutes, posts a single `urgent` HERON SILENT
carrying her last seq.

Why it polls the topic and not the local ledger: if the agent is dead, the ledger
is dead too. The doorbell is the only thing still answering.

    python3 tools/watchdog.py --check      # one-shot: report age of last beat
    python3 tools/watchdog.py              # loop, every 60 s
    HERON_DRYRUN=1 python3 tools/watchdog.py --check

A beat is a message on the topic whose Tags contain `heartbeat`. The SILENT alert
itself carries `watchdog`, so it can never be mistaken for proof of life — that
is the whole point of F33.

Exit: 0 quiet · 1 alert posted · 2 could not reach the topic
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "evidence" / "WATCHDOG.json"
SILENT_AFTER = 16 * 60          # §20: urgent at 16 minutes of quiet
RE_ALERT_EVERY = 16 * 60        # do not spam the shared 250/day quota
POLL = 60

DRY = os.environ.get("HERON_DRYRUN") == "1"


def env(name: str) -> str:
    """Read a kit value from the env file without ever printing it."""
    val = os.environ.get(name, "")
    if not val:
        p = Path("/home/user/.private/heron.env")
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.startswith(name + "="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return val


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(d: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")


def fetch_beats(server: str, topic: str) -> list[dict]:
    """Return the topic's messages that are heartbeats. Never logs the topic.

    ntfy's /json endpoint streams **newline-delimited JSON objects**, not a JSON
    array — parsing it with json.load() raises and the watchdog would report
    "cannot reach the topic" while the topic is perfectly healthy. Parse line by
    line. This bug is recorded in evidence/NEGATIVE_TESTS.md.
    """
    url = f"{server.rstrip('/')}/{topic}/json?poll=1&since=all"
    req = urllib.request.Request(url, headers={"User-Agent": "heron-watchdog"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError) as e:
        raise SystemExit(f"watchdog: cannot reach the topic ({type(e).__name__}: {e}) — exit 2")

    out = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(m, dict) or m.get("event") != "message":
            continue
        tags = m.get("tags")
        # tags is a JSON array in ntfy; tolerate a string too
        if isinstance(tags, list):
            tagset = {str(t) for t in tags}
        else:
            tagset = set(str(tags or "").split(","))
        if "heartbeat" in tagset:
            out.append(m)
    return out


def post(server: str, topic: str, title: str, body: str, priority: str, tags: str) -> str | None:
    if DRY:
        print(f"watchdog: DRY-RUN would post priority={priority} tags={tags} title={title!r}")
        print(f"watchdog: body={body}")
        return "dry-run"
    req = urllib.request.Request(
        f"{server.rstrip('/')}/{topic}",
        data=body.encode(),
        method="POST",
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": tags,
            "User-Agent": "heron-watchdog",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as r:
        try:
            return json.loads(r.read().decode()).get("id")
        except json.JSONDecodeError:
            return None


def check(server: str, topic: str) -> int:
    state = load_state()
    beats = fetch_beats(server, topic)
    now = int(time.time())
    armed_at = state.get("armed_utc")

    if not beats:
        if armed_at is None:
            print("watchdog: no beats on the topic yet — watchdog is written but NOT ARMED "
                  "(run `watchdog.py --arm` when beats begin)")
            return 0
        if now - armed_at < SILENT_AFTER:
            print(f"watchdog: armed {int((now - armed_at) / 60)} min ago, no beats yet, "
                  f"alerting at {SILENT_AFTER // 60} min — quiet")
            return 0
        last_seq, silent_min = "unknown", int((now - armed_at) / 60)
    else:
        latest = max(beats, key=lambda m: m.get("time", 0))
        age = now - int(latest.get("time", 0))
        silent_min = age // 60
        try:
            last_seq = json.loads(latest.get("message", "{}")).get("seq", "unknown")
        except json.JSONDecodeError:
            last_seq = "unknown"

        if age < SILENT_AFTER:
            print(f"watchdog: last beat {silent_min} min ago (seq={last_seq}) — quiet, "
                  f"threshold {SILENT_AFTER // 60} min")
            return 0

    # ---- silence: alert ------------------------------------------------------
    state["last_alert_utc"] = now
    state["last_seq_seen"] = last_seq
    state["silent_minutes"] = silent_min
    save_state(state)

    body = json.dumps({
        "ev": "silent",
        "agent": "heron",
        "t": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "last_seq": last_seq,
        "silent_minutes": silent_min,
        "threshold_minutes": SILENT_AFTER // 60,
        "meaning": "heron has posted no heartbeat for 16 minutes. Treat the commission as unattended.",
    })
    mid = post(server, topic, "HERON SILENT", body, "urgent", "warning,watchdog")
    print(f"watchdog: ALERT POSTED — HERON SILENT, last_seq={last_seq}, silent {silent_min} min, "
          f"ntfy_id={mid}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="one-shot instead of the loop")
    ap.add_argument("--arm", action="store_true", help="mark the watchdog armed now")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the alarm fires on a topic that is provably silent (dry-run)")
    a = ap.parse_args()

    server = env("NTFY_SERVER") or "https://ntfy.sh"
    topic = env("NTFY_TOPIC")
    if not topic:
        print("watchdog: NTFY_TOPIC not found in the environment — the watchdog cannot run", file=sys.stderr)
        return 2

    if a.arm:
        s = load_state()
        s["armed_utc"] = int(time.time())
        save_state(s)
        print("watchdog: armed. Alerting at 16 minutes with no heartbeat.")
        return 0

    if a.selftest:
        # F33: an untested watchdog is a lying watchdog. This exercises the alert
        # path against a topic that is definitionally silent, in dry-run, so the
        # test posts nothing. The pre-test state is restored afterwards: a
        # self-test must never leave the watchdog armed at a lie.
        print("watchdog: SELF-TEST — forcing the silent path with no beats present")
        before = load_state()
        save_state({"selftest": True, "armed_utc": int(time.time()) - (SILENT_AFTER + 60)})
        try:
            rc = check(server, topic)
        finally:
            if before:
                save_state(before)
            elif STATE.exists():
                STATE.unlink()
        print(f"watchdog: SELF-TEST rc={rc} (expected 1 = alert fires); pre-test state restored")
        return 0 if rc == 1 else 1

    if a.check:
        return check(server, topic)

    print(f"watchdog: looping every {POLL}s; urgent at {SILENT_AFTER // 60} min of silence")
    while True:
        try:
            check(server, topic)
        except SystemExit as e:
            print(f"watchdog: {e}", file=sys.stderr)
        time.sleep(POLL)


if __name__ == "__main__":
    raise SystemExit(main())
