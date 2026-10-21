# REPRODUCE.md — Clean-Room Verification & Deterministic Rebuild Protocol (§1.1)

Every artifact in `crystal/` is deterministically reproducible from the versioned Paxton kit (`kit/`), the JSONL ledgers (`ledgers/`), and the integer seeds on a headless CPU container (`Blender 4.3.2`, `Python 3.13`, `ffmpeg 7.1`, `MEM_CEILING_MB = 1200`).

## Exact Clean-Room Commands (§1.1)

```bash
cd /home/user/buildinglab/crystal

# 1. Verify toolchain & memory ceiling
cat evidence/TOOLCHAIN.txt

# 2. Rebuild the 5 versioned Paxton kit pieces (column, girder, sash_bar, pane, gutter)
blender --background --python kit/build_kit.py --python-exit-code 1

# 3. Clean-room rebuild of Bay B042 and double-dump bit-for-bit census verification (Gate G15)
mkdir -p build
blender --background bays/B042.blend --python tools/build_bay.py --python-exit-code 1 -- --key 042
python3 tools/dump_bay.py 042 > build/b042_a.txt
python3 tools/dump_bay.py 042 > build/b042_b.txt
diff build/b042_a.txt build/b042_b.txt && echo "BAY CENSUS MATCH"
# Expected census_sha256: 333785188bcfe43be20a3c12186e55cd05bf7b1d076778df72b7c27a93cc8f95

# 4. Recompute Great Organ acoustic pipe lengths & rebuild the Three Wonders
python3 tools/compute_organ.py
blender --background --python tools/build_wonders.py --python-exit-code 1

# 5. Run the physics-driven erection simulation (2,880 frames @ 24 fps, glazing rate ledger)
python3 film/tools/sim_erection.py

# 6. Execute all 5 test suites (3,736 assertions >= 2,400 required)
for t in tests/*.py; do python3 "$t" || exit 1; done

# 7. Execute all 27 validators (each verified to refuse injected faults in evidence/NEGATIVE_TESTS.md)
for v in validate/v_*.py; do python3 "$v" || exit 1; done

# 8. Reconcile heartbeats & scan for secrets
python3 tools/hb_reconcile.py
bash tools/secret_scan.sh
```
