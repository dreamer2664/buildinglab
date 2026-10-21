#!/usr/bin/env python3
"""
hb_reconcile.py — Heartbeat reconciler for PAXTON / CRYSTAL (§1.5, §32).
Adapted from daedalus (underworks/tools/hb_reconcile.luau & reconcile.sh, Appendix A).

Compares:
  1. local:    evidence/HEARTBEATS.jsonl
  2. expected: evidence/expected_ticks.jsonl
  3. server:   live poll of NTFY_SERVER/NTFY_TOPIC/json?poll=1&since=all&scheduled=0
               with `.topic` immediately stripped in memory before writing to disk.

Checks for gaps > 12 minutes (720 s -> HB-GAP per §1.5).
Never backfills. Never fakes.
"""
from __future__ import annotations
import datetime
import json
import os
import subprocess
import sys
import urllib.request

GAP_MIN = 12
GAP_SEC = GAP_MIN * 60


def load_env(env_path: str = "/home/user/.private/paxton.env") -> None:
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def parse_iso_to_epoch(s: str) -> int:
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return int(dt.timestamp())
    except Exception:
        return 0


def read_jsonl(path: str) -> list[dict]:
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows


def poll_server(server: str, topic: str) -> list[dict]:
    url = f"{server.rstrip('/')}/{topic}/json?poll=1&since=all&scheduled=0"
    req = urllib.request.Request(url, headers={"User-Agent": "paxton-reconcile/1.0"})
    rows = []
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            # Strip secret topic immediately in memory (§2.4)
            obj.pop("topic", None)
            if obj.get("event") == "message":
                rows.append(obj)
        except Exception:
            pass
    return rows


def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    load_env()

    topic = os.environ.get("NTFY_TOPIC", "")
    server = os.environ.get("NTFY_SERVER", "https://ntfy.sh")
    if not topic:
        print("hb_reconcile: NTFY_TOPIC missing", file=sys.stderr)
        return 1

    now_dt = datetime.datetime.now(datetime.timezone.utc)
    stamp = now_dt.strftime("%Y%m%dT%H%M%SZ")
    now_iso = now_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    os.makedirs("evidence/HB_RECONCILE", exist_ok=True)
    server_msgs = poll_server(server, topic)

    snap_path = f"evidence/HB_RECONCILE/{stamp}.jsonl"
    with open(snap_path, "w", encoding="utf-8") as fh:
        for m in server_msgs:
            fh.write(json.dumps({
                "id": m.get("id"),
                "time": m.get("time"),
                "title": m.get("title"),
                "priority": m.get("priority"),
                "message": m.get("message"),
            }, sort_keys=True) + "\n")

    local_rows = read_jsonl("evidence/HEARTBEATS.jsonl")
    expected_rows = read_jsonl("evidence/expected_ticks.jsonl")

    local_rows.sort(key=lambda r: int(r.get("seq", 0)))

    # Separate server messages into agent beats vs pre-boot channel tests vs watchdog alarms
    server_beat_ids = {}
    channel_test_ids = []
    watchdog_alarm_ids = []
    for m in server_msgs:
        mid = m.get("id", "")
        title = m.get("title", "") or ""
        msg_body = m.get("message", "") or ""
        if "SILENT" in title:
            watchdog_alarm_ids.append(mid)
        elif "channel test" in title or '"ev":"channel-test"' in msg_body:
            channel_test_ids.append(mid)
        else:
            server_beat_ids[mid] = m

    found = 0
    missing = []
    local_ids = set()
    for r in local_rows:
        rid = r.get("id", "")
        local_ids.add(rid)
        if rid in server_beat_ids:
            found += 1
        else:
            missing.append(r.get("seq"))

    extra = [mid for mid in server_beat_ids if mid not in local_ids]

    gaps = []
    for i in range(1, len(local_rows)):
        t_prev = int(local_rows[i - 1].get("server_time") or parse_iso_to_epoch(local_rows[i - 1].get("local_time", "")))
        t_curr = int(local_rows[i].get("server_time") or parse_iso_to_epoch(local_rows[i].get("local_time", "")))
        delta = t_curr - t_prev
        if delta > GAP_SEC:
            gaps.append({
                "from": local_rows[i - 1].get("seq"),
                "to": local_rows[i].get("seq"),
                "secs": delta,
            })

    span = 0
    covered = 0
    if len(local_rows) >= 2:
        t0 = int(local_rows[0].get("server_time") or parse_iso_to_epoch(local_rows[0].get("local_time", "")))
        t1 = int(local_rows[-1].get("server_time") or parse_iso_to_epoch(local_rows[-1].get("local_time", "")))
        span = max(0, t1 - t0)
        for i in range(1, len(local_rows)):
            tp = int(local_rows[i - 1].get("server_time") or parse_iso_to_epoch(local_rows[i - 1].get("local_time", "")))
            tc = int(local_rows[i].get("server_time") or parse_iso_to_epoch(local_rows[i].get("local_time", "")))
            covered += min(max(0, tc - tp), 420)  # 7 min = 420 s slot
        coverage = min(100.0, (covered / span * 100.0)) if span > 0 else 100.0
    else:
        coverage = 100.0 if len(local_rows) == 1 and found == 1 else 0.0

    verdict = "PASS"
    if len(missing) > 0:
        verdict = f"FAIL — {len(missing)} local beats missing on server"
    elif len(gaps) >= 3:
        verdict = "FAIL — 3 or more HB-GAP (>12m) episodes"

    lines = [
        f"RECONCILE at {now_iso}",
        f"  local beats      {len(local_rows)}",
        f"  expected ticks   {len(expected_rows)}",
        f"  server agent bts {len(server_beat_ids)} (plus {len(channel_test_ids)} channel-test, {len(watchdog_alarm_ids)} watchdog-alarm)",
        f"  FOUND            {found}",
        f"  MISSING          {len(missing)} {missing if missing else ''}".rstrip(),
        f"  EXTRA            {len(extra)} {extra if extra else ''}".rstrip(),
        f"  GAPS >{GAP_MIN}m        {len(gaps)}",
    ]
    for g in gaps:
        lines.append(f"     HB-GAP seq {g['from']} -> {g['to']} : {g['secs'] // 60}m {g['secs'] % 60}s")
    lines.append(f"  coverage         {coverage:.1f}% (span {span}s)")
    lines.append(f"  VERDICT          {verdict}")

    report = "\n".join(lines) + "\n"
    print(report, end="")
    with open("evidence/RECONCILE.log", "a", encoding="utf-8") as fh:
        fh.write(report)

    summary = {
        "at": now_iso,
        "snapshot": snap_path,
        "local": len(local_rows),
        "expected": len(expected_rows),
        "server_beats": len(server_beat_ids),
        "channel_tests": channel_test_ids,
        "watchdog_alarms": watchdog_alarm_ids,
        "found": found,
        "missing": missing,
        "extra": extra,
        "gaps": gaps,
        "coverage": round(coverage, 1),
        "verdict": verdict,
    }
    with open("evidence/RECONCILE_LAST.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
        fh.write("\n")

    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
