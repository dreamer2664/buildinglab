import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];out=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH' or o.get('building_id')!='B03' or o.get('floor_id') not in ['B03_L01','EXTERIOR']:continue
 if o.get('layer') not in ['wall_high','wall_low','exterior','door']:continue
 m=o.data;adj={v.index:set() for v in m.vertices}
 for e in m.edges:a,b=e.vertices;adj[a].add(b);adj[b].add(a)
 unseen=set(adj)
 while unseen:
  first=unseen.pop();part={first};stack=[first]
  while stack:
   for w in adj[stack.pop()]:
    if w in unseen:unseen.remove(w);part.add(w);stack.append(w)
  pts=[o.matrix_world@m.vertices[i].co for i in part];lo=[round(min(p[i] for p in pts),4) for i in range(3)];hi=[round(max(p[i] for p in pts),4) for i in range(3)]
  out.append({'object':o.name,'vertices':len(part),'min':lo,'max':hi})
(R/'evidence/production/B03-envelope-components.json').write_text(json.dumps(out,indent=2)+'\n')
for r in out:
 if 'wall_high' in r['object'] or 'wall_low' in r['object']:print(r)
