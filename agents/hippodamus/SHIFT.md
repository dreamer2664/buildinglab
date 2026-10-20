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

## 2026-10-20 — Stage B close-out (commit 58c7949)
- Build: 5,173 objects / 1,189,892 tris / 2,519 props in B05.
- PASS: v_programme, v_export 5/5, v_rail 16/16, v_water 15/15, v_plant 11/11.
- OPEN: v_contact 3/5 (D-216 interpenetration depth), v_clearance 8/9 (D-217
  door approaches), v_density 5/7 (15 rooms short; 8/208 apartments, D-201).
- Next: fix D-217 in the shop/warehouse builders (place fixtures in room-local
  coordinates inside the keep-out frame), then bring the 15 short rooms to their
  class floor, then a full 24-view 1024 pass, then v_light --images.
- Machine note: 1.9 GiB RAM is the binding constraint. A background render pass
  saturates the shell (load >12, free <100 MB) and bash calls time out at 240 s;
  two concurrent Blender processes OOM. Render one view per bash call.
