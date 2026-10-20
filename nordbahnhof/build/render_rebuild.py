import bpy,sys
from pathlib import Path
for o in bpy.data.objects:
 for m in o.modifiers:
  if m.type=='SUBSURF':m.render_levels=1
sys.path.insert(0,str(Path(__file__).resolve().parent))
import render_batch
render_batch.main()
