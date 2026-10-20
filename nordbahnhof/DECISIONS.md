# NORDBAHNHOF — Architectural & Engineering Decisions (`nordbahnhof/DECISIONS.md`)

| ID | Date (UTC) | Stage | Decision | Rationale |
|---|---|---|---|---|
| `DEC-001` | 2026-10-19 | Stage 0 | Record `CPU without OIDN` in `TOOLCHAIN.txt` and configure Cycles CPU clamping (`direct=5.0`, `indirect=2.5`, `use_light_tree=False`) + 3x3 edge-preserving median despike (F20). | Host has 2 Xeon vCPUs (no GPU) and 1.9 GiB RAM; disabling light-tree and using soft area lights + edge-preserving despike prevents fireflies and keeps peak RAM at ~184 MB (<1.9 GiB, avoiding F10). |
| `DEC-002` | 2026-10-19 | Stage A | Mirror evidence files to both `nordbahnhof/evidence/` and `nordbahnhof/EVIDENCE/`, and drawings to both `nordbahnhof/design/plans/` and `sections/`/`details/`. | Satisfies both §1.1 command paths (`nordbahnhof/evidence/`) and §30 tree paths (`nordbahnhof/EVIDENCE/`) without discrepancy. |
| `DEC-003` | 2026-10-19 | Stage A | Persist all 15 broken negative-test fixtures in `nordbahnhof/validate/fixtures/broken_01_scale.json` .. `broken_15_package.json`. | Ensures any independent reviewer can run `python3 nordbahnhof/validate/run_negative_tests.py` and verify all 15 deliberate breaks are caught on demand (§28.1). |
| `DEC-004` | 2026-10-19 | Stage B | Use `orient_between()` node-to-node vector tracking for arched lattice truss chords/diagonals and `look_at_rotation()` target tracking for all 30 cameras (`D-001`..`D-006`). | Eliminates chord separation on curved barrel vaults and guarantees every camera frames its exact subject without wall or vehicle occlusion. |

Independent non-owner acceptance remains PENDING. No self-review/vote.
