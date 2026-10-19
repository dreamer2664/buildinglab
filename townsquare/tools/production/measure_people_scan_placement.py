"""Read-only current native actor placement and original face-facing measurement."""
import bpy,json,sys,re,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
b=json.loads((R/'evidence/production/R12-groomed-town.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];bpy.context.view_layer.update();rows=[]
for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
 if not re.fullmatch(r'CROWD_\d\d_P\d\d',o.name):continue
 mats=[m.name if m else None for m in o.data.materials];eyes={i for i,m in enumerate(mats)if m and any(x in m.lower()for x in ['eye01','eyes','eye_material'])};eyeids={v for p in o.data.polygons if p.material_index in eyes for v in p.vertices};eyeco=[o.data.vertices[i].co for i in eyeids];world=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[i]for v in world)for i in range(3)];hi=[max(v[i]for v in world)for i in range(3)];top=max(v.co.z for v in o.data.vertices);head=[v.co for v in o.data.vertices if v.co.z>top-.25];rows.append({'name':o.name,'person_id':o.get('person_id'),'variant':o.get('variant_id'),'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'bounds':[lo,hi],'actual_eye_materials':[mats[i]for i in eyes],'eye_vertex_count':len(eyeids),'eye_local_centroid':[sum(v[i]for v in eyeco)/len(eyeco)for i in range(3)]if eyeco else None,'head_local_bounds':[[min(v[i]for v in head)for i in range(3)],[max(v[i]for v in head)for i in range(3)]],'materials':mats})
r={'source_native_sha256':b['native_sha256'],'actors':rows};(R/'evidence/production/R12-before-scan-actual-actor-placements.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_ACTOR_PLACEMENTS_MEASURED',len(rows));print(json.dumps(rows[0],indent=2))
