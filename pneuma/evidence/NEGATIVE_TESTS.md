# NEGATIVE TESTS — the tools are refused on purpose, once each (F22)

A validator that has never failed has never been tested. These rows are the
record for the Stage 0 tooling. Full 22-validator refusal pass belongs to
Part VII and cannot be completed here: 15 of the 22 validators need a Blender
scene, and there is no Blender on this host.

| # | Test | Injected failure | Result | Verdict |
|---|---|---|---|---|
| N-01 | `beat.sh` seq arithmetic | empty `HEARTBEATS.jsonl` | `grep -c` exits 1 on a zero count, so `|| echo 0` appended a second `0` and `$(( 0 + 1 ))` became a syntax error; `SEQ` was unbound | **REFUSED — bug found, fixed.** Counting moved to python3; zero-count no longer breaks the beat |
| N-02 | `hb_reconcile.py` seq check | two consecutive beats in the ledger | flagged `HB-SEQ: duplicate seq` | **REFUSED — correct, but noisy.** Dry-run rows were being counted as beats; they are now excluded and reported as `dry_runs` |
| N-03 | `hb_reconcile.py` frame honesty | a beat claiming `frames_rendered=9000` against an empty `FRAMES.jsonl` | flagged `HB-FALSE: beat seq=9 claims frames_rendered=9000 but FRAMES.jsonl holds 0`, exit 1 | **REFUSED — correct.** This is the check that makes a lying beat impossible (§32) |
| N-04 | `watchdog.py` silent path | topic with no heartbeats, watchdog armed 17 min ago | fired `urgent HERON SILENT` with `last_seq=unknown`, `silent_minutes=17`, rc=1 | **REFUSED — correct** (F33). Run in `HERON_DRYRUN=1`: the alert path was exercised, nothing was posted |
| N-05 | `watchdog.py` state hygiene | self-test run against a live state file | the pre-test `WATCHDOG.json` was restored, file absent when there was none | **REFUSED — correct.** A self-test must not leave the watchdog armed at a lie |
| N-06 | `hb_reconcile.py` before any beats | empty ledger, watchdog unarmed | returns `NOT RUNNING YET` instead of a false `HB-GAP` | **REFUSED — correct.** Silence before the first beat is not a gap |

## Not tested, and why

* `beat.sh` live POST — not run. Posting to the live topic is an outward act on a
  commission that holds no card; the dry-run path exercises the payload and the
  ledger write.
* `hb_reconcile.py` against the live topic — the reconcile reads the local
  ledger only, by design (§1.5: the board is the record, ntfy is the doorbell).
* `watchdog.py` end-to-end against the live topic — the silent path was proven
  in dry-run (N-04); the live arm is pending.
