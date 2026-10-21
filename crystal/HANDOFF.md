# HANDOFF — PAXTON / CRYSTAL

## Current Standing
- **Agent:** `paxton`
- **Task ID:** `t-20261021-3620`
- **Branch:** `agent/paxton/t-20261021-3620`
- **Stage:** `A` (entering Stage A after Stage 0 exit)
- **Zone:** `sources-and-module`
- **Percent Complete:** `2%`
- **Open Defects:** `0` (`evidence/DEFECTS.jsonl`)

## Completed Stages
- **Stage 0 (Bootstrap):** Entry tests T1–T7 passed (`boot_beat_id=yYqO2kzVeWZ1`, `flare_id=wx471Wfn9MkI`), `evidence/RUN.json`, `evidence/TOOLCHAIN.txt`, `tools/beat.sh`, `tools/hb_reconcile.py`, `tools/watchdog.sh` + kill test (`alarm_id=8c9eHQTaQZDi`), `tools/hb_daemon.sh`, `tools/secret_scan.sh`.

## Conservative Assumptions Logged (§36)
1. **Great Organ pipe count conflict (`CONFLICTS.md`):** Historical sources report 4,500 pipes (Gray & Davison Exhibition organ specification in the Official Catalogue, Class X No. 555) vs 4,000+ summary figures; adjudicated law for CRYSTAL is **4,500 pipes** across 60 stops (`>= 4,000` requirement met with exact acoustic length computation).
2. **Module grid:** 1851 pre-decimal Imperial 24 ft = `7.3152 m` exact (`7.32 m` nominal per §1.2/§15.1); all structural nodes honour the declared `7.32 m` module grid within `±10 mm` (`±0.000 m` exact in generator coordinates).

## Resume Instructions for a Stranger (5 Minutes)
1. Load credentials: `set -a; . /home/user/.private/paxton.env; set +a; export CHATCODE_AGENT=paxton`
2. Change to lane: `cd /home/user/buildinglab/crystal`
3. Check heartbeat reconciliation: `python3 tools/hb_reconcile.py`
4. Run secret scan: `bash tools/secret_scan.sh`
5. Run validators: `for v in validate/v_*.py; do python3 "$v" || exit 1; done`
6. Next action: Complete Stage A (`CONSTANTS.md`, `REFERENCES.md` >=120 rows, `CONFLICTS.md`, `BUDGET.md`, `EPHEMERIS.json`, `FLOORPLAN.md`, `STRATA.md`, `DENSITY.md`, `FAKES.md`).
