#!/usr/bin/env python3
"""tools/hb_reconcile.py — every 2 hours: does the ledger agree with the doorbell?

The board is the record, ntfy is the doorbell (§1.5). This compares what was
delivered against what was expected, and reports:

  HB-GAP      a gap > 12 minutes with no beat            (three unexplained => review fails)
  HB-QUOTA    beats mirrored locally because of 429
  HB-FALSE    a beat whose frames_rendered exceeds ledgers/FRAMES.jsonl
  HB-SEQ      a non-monotonic or duplicated seq

Exit 0 when clean, 1 when a gap or a false beat is found. A reconciliation that
finds nothing but cannot see the ledger is not a reconciliation: if
evidence/HEARTBEATS.jsonl is missing it says so and exits 1.

Usage: python3 tools/hb_reconcile.py [--since-minutes 120] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HB = ROOT / "evidence" / "HEARTBEATS.jsonl"
FRAMES = ROOT / "ledgers" / "FRAMES.jsonl"
STATE = ROOT / "evidence" / "WATCHDOG.json"
GAP = timedelta(minutes=12)
BEAT_EVERY = timedelta(minutes=7)


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"_parse_error": True, "_line": i})
    return rows


def ts(v: str | None) -> datetime | None:
    if not v:
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-minutes", type=int, default=120)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    problems: list[dict] = []
    notes: list[str] = []

    if not HB.exists():
        print("reconcile: evidence/HEARTBEATS.jsonl is missing — nothing to reconcile", file=sys.stderr)
        return 1

    rows = read_jsonl(HB)
    delivered = [r for r in rows if r.get("delivered") is True]
    mirrored = [r for r in rows if r.get("delivered") is False and r.get("hb_quota")]
    failed = [r for r in rows if r.get("delivered") is False and not r.get("hb_quota") and not r.get("dry_run")]
    dry = [r for r in rows if r.get("dry_run") is True]

    # --- seq monotonicity -----------------------------------------------------
    # Only real beats carry a seq. A dry run is a rehearsal: it holds the seq it
    # *would* take, and is excluded here so a test never reads as a duplicate.
    real = [r for r in rows if r.get("dry_run") is not True]
    seqs = [r.get("seq") for r in real if isinstance(r.get("seq"), int)]
    if seqs != sorted(seqs):
        problems.append({"code": "HB-SEQ", "detail": "seq is not monotonic in HEARTBEATS.jsonl"})
    if len(seqs) != len(set(seqs)):
        problems.append({"code": "HB-SEQ", "detail": f"duplicate seq present ({len(seqs)} rows, {len(set(seqs))} unique)"})

    # --- frame honesty --------------------------------------------------------
    frame_rows = 0
    if FRAMES.exists():
        frame_rows = sum(1 for l in FRAMES.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip())
    else:
        notes.append("ledgers/FRAMES.jsonl absent — frame honesty check skipped (expected before stage E)")
    for r in real:
        fr = r.get("frames_rendered")
        if isinstance(fr, int) and fr > frame_rows:
            problems.append({
                "code": "HB-FALSE",
                "detail": f"beat seq={r.get('seq')} claims frames_rendered={fr} but FRAMES.jsonl holds {frame_rows}",
            })

    # --- gaps -----------------------------------------------------------------
    # A gap is only a gap once beats have actually begun. Before the first beat
    # (watchdog unarmed, empty ledger) there is no silence to report — reporting
    # one would be a defect that describes nothing.
    armed = STATE.exists() and load_state().get("armed_utc") is not None
    if not rows and not armed:
        result["notes"].append("no beats recorded and the watchdog is not armed — "
                               "heartbeat has not begun; nothing to reconcile yet")
        result["verdict"] = "NOT RUNNING YET"
        if a.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"reconcile @ {result['t']} · 0 rows · watchdog not armed")
            for n in result["notes"]:
                print(f"  note: {n}")
            print("  verdict: NOT RUNNING YET — arm the watchdog when beats begin")
        return 0

    times = sorted(t for t in (ts(r.get("t")) for r in real) if t)
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=a.since_minutes)
    recent = [t for t in times if t >= window_start]

    expected_beats = max(0, int((a.since_minutes * 60) / (BEAT_EVERY.total_seconds())) )
    if len(recent) + len([r for r in mirrored if window_start <= (ts(r.get("t")) or now) <= now]) < max(0, expected_beats - 1):
        problems.append({
            "code": "HB-GAP",
            "detail": f"{len(recent)} beat(s) in the last {a.since_minutes} min, expected ~{expected_beats} at a 7-min cadence",
        })
    for x, y in zip(times, times[1:]):
        if y - x > GAP:
            problems.append({
                "code": "HB-GAP",
                "detail": f"{int((y - x).total_seconds() // 60)} min of silence between {x.isoformat()} and {y.isoformat()}",
            })
    if times and now - times[-1] > GAP:
        problems.append({
            "code": "HB-GAP",
            "detail": f"last beat {int((now - times[-1]).total_seconds() // 60)} min ago (>12 min)",
        })

    if mirrored:
        notes.append(f"HB-QUOTA: {len(mirrored)} beat(s) mirrored locally during quota degradation")
    if dry:
        notes.append(f"{len(dry)} dry-run row(s) excluded from seq and gap checks — rehearsals, not beats")

    result = {
        "t": now.isoformat().replace("+00:00", "Z"),
        "since_minutes": a.since_minutes,
        "rows": len(rows),
        "delivered": len(delivered),
        "mirrored_quota": len(mirrored),
        "failed": len(failed),
        "dry_runs": len(dry),
        "last_beat": times[-1].isoformat().replace("+00:00", "Z") if times else None,
        "frame_rows": frame_rows,
        "problems": problems,
        "notes": notes,
        "verdict": "CLEAN" if not problems else "DEFECTS",
    }

    if a.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"reconcile @ {result['t']} · {len(rows)} rows · {len(delivered)} delivered · "
              f"{len(mirrored)} mirrored · {len(failed)} failed · frames={frame_rows}")
        print(f"  last beat: {result['last_beat'] or 'none'}")
        for n in notes:
            print(f"  note: {n}")
        if problems:
            for p in problems:
                print(f"  {p['code']}: {p['detail']}", file=sys.stderr)
            print(f"  verdict: {result['verdict']}")
        else:
            print("  verdict: CLEAN — ledger and doorbell agree")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
