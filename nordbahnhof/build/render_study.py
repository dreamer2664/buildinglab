"""Render WIP study separately from the rejected r01 gallery."""
import bpy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_batch as renderer
root=Path(__file__).resolve().parents[1]/'renders/rebuild'
for name,subdir in [('PROOF_DIR','proof'),('FINAL_DIR','native'),('CACHE_DIR','.cache')]:
 p=root/subdir;p.mkdir(parents=True,exist_ok=True);setattr(renderer,name,p)
for ob in bpy.data.objects:
 for m in ob.modifiers:
  if m.type=='SUBSURF':m.render_levels=1
renderer.main()
