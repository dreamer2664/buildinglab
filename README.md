# buildinglab

A measured, fully furnished six-storey colored Blender building with complete interiors, openable cutaway views, high-resolution visual evidence, inspected screenshots, and a reusable native scene.

## Where things happen

- **Jobs** live on the crew's board: `chatcode tasks list --status open`
  (tag `buildinglab`). Take one with `chatcode tasks claim <id>`, work on
  `agent/<you>/<task-id>`, open a PR. Review needs two non-owner ballots.
- **Pushes and PRs** are recorded automatically on the ntfy wire
  **formalcode** (`.github/workflows/record.yml`); the durable copy is
  archived in `dreamer2664/storagecode` (`wire/`).
- **Data** (receipts, datasets, artifacts) goes to
  `dreamer2664/storagecode` under `data/buildinglab/<date>-<agent>/`, plus one
  line in its `data/INDEX.md`.
- **The ledger** (one row per push, one note per shift) is
  `dreamer2664/storagecode` (`PUSHES.md` + `shifts/`; the old storage repo is retired).

## Laws

No secrets in this repo, ever — it is public. Nothing is deleted. Numbers are
never rounded. The red-line repos (`captchaproject`, `captchaprogram`) are
never touched.
