"""Conservative actual open-leaf/component overlap audit, not a code certificate.
Bounding boxes can overestimate lathed/diagonal shapes: examine reported candidates.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];bpy.context.view_layer.update();fixtures={};leaves=[];rows=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bb=[o.matrix_world@Vector(v) for v in o.bound_box];lo=[min(p[i] for p in bb) for i in range(3)];hi=[max(p[i] for p in bb) for i in range(3)]
 if o.get('role')=='door' and o.name.endswith('_LEAF'):leaves.append((o,bb,lo,hi))
 elif o.get('fixture'):fixtures.setdefault(o.get('level'),[]).append((o,bb,lo,hi))
for leaf,bb,l,h in leaves:
 inv=leaf.matrix_world.inverted();lb=[Vector(v) for v in leaf.bound_box];ll=[min(p[i] for p in lb) for i in range(3)];lh=[max(p[i] for p in lb) for i in range(3)]
 for o,obb,ol,oh in fixtures.get(leaf.get('level'),[]):
  if any(min(h[i],oh[i])-max(l[i],ol[i])<.003 for i in range(3)):continue
  q=[inv@p for p in obb];ql=[min(p[i] for p in q) for i in range(3)];qh=[max(p[i] for p in q) for i in range(3)];depth=[min(lh[i],qh[i])-max(ll[i],ql[i]) for i in range(3)]
  if all(n>.003 for n in depth):rows.append({'door':leaf.get('door_id'),'leaf':leaf.name,'room':o.get('room_id'),'component':o.name,'overlap_extent_in_leaf_axes_m':depth})
report={'scope':'conservative open native door leaf vs furnishing bounds; not closed-leaf or code test','door_leaves':len(leaves),'candidates':rows};(R/'assets/interiors/clearance-audit.json').write_text(json.dumps(report,indent=2)+'\n');print('CLEARANCE_CANDIDATES',len(rows));print(*rows,sep='\n')
