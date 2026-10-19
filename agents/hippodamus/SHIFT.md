# hippodamus — shift log

## 2026-10-19

- Stage A pushed as `c985ba1` on `agent/hippodamus/t-20261019-5e10`.
- Workspace was re-provisioned mid-session and everything outside GitHub was lost
  (repo, toolchain, ~2,900 lines of Stage B builder). Stage A survived because it
  was committed; nothing else did. Rebuilt from the packet in the same session.
- Stage B branch: `agent/hippodamus/t-20261019-f3c1`.
- Two entries in `portus/DECISIONS.md` from before the loss (D-0011…D-0014) were
  lost with the workspace and are not reconstructed; the decisions they covered
  (OIDN renderer, content-hash cache, no salted `hash()`, F8 for every camera) are
  re-recorded as D-0015 onward where they still apply.
