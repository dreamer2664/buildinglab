"""Read-only actual native roof/window anchors, not guessed facade coordinates."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
b=json.loads((R/'evidence/production/R12-original-uv-scanned-town.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];schedule=json.loads((R/'design/programme.json').read_text());rows=[]
for entry in schedule['buildings']:
 bid=entry['id'];w,d=entry['footprint_m'];angle=math.radians(entry['rotation_deg']);c=math.cos(angle);q=math.sin(angle);ox,oy=entry['centre_xy_m']
 def local(v):return Vector((c*(v.x-ox)+q*(v.y-oy),-q*(v.x-ox)+c*(v.y-oy),v.z))
 objs=[o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('building_id')==bid];roof=[o for o in objs if o.get('layer')=='roof'];points=[local(o.matrix_world@Vector(p))for o in roof for p in o.bound_box];roof_bounds=[[min(v[i]for v in points)for i in range(3)],[max(v[i]for v in points)for i in range(3)]]if points else None;panes=[]
 for ob in objs:
  glass={i for i,m in enumerate(ob.data.materials)if m and any(x in m.name.lower()for x in ['glass','glazing'])}
  if not glass:continue
  for poly in ob.data.polygons:
   if poly.material_index not in glass:continue
   vs=[local(ob.matrix_world@ob.data.vertices[i].co)for i in poly.vertices];lo=[min(v[i]for v in vs)for i in range(3)];hi=[max(v[i]for v in vs)for i in range(3)];z=(lo[2]+hi[2])/2;floor=next((f for f in entry['floors']if f['datum_m']+.3<z<f['datum_m']+f['height_m']-.1),None)
   if not floor or floor['index']==0:continue
   for side,axis,plane in [('front',1,-d/2),('back',1,d/2),('left',0,-w/2),('right',0,w/2)]:
    if max(abs(v[axis]-plane)for v in vs)<.35 and hi[2]-lo[2]>.25:
     horizontal=1-axis;panes.append({'side':side,'floor':floor['id'],'horizontal_bounds':[lo[horizontal],hi[horizontal]],'vertical_bounds':[lo[2],hi[2]],'source_object':ob.name});break
 # Combine mullion-separated panes only; a real gap larger than180mm keeps distinct windows.
 groups=[]
 for pane in panes:
  a,z=pane['horizontal_bounds'],pane['vertical_bounds'];match=next((g for g in groups if g['side']==pane['side']and g['floor']==pane['floor']and max(a[0],g['horizontal_bounds'][0])-min(a[1],g['horizontal_bounds'][1])<.18 and max(z[0],g['vertical_bounds'][0])-min(z[1],g['vertical_bounds'][1])<.18),None)
  if match:
   match['horizontal_bounds']=[min(a[0],match['horizontal_bounds'][0]),max(a[1],match['horizontal_bounds'][1])];match['vertical_bounds']=[min(z[0],match['vertical_bounds'][0]),max(z[1],match['vertical_bounds'][1])];match['source_glass_faces']+=1
  else:groups.append(dict(pane,source_glass_faces=1))
 rows.append({'building':bid,'actual_roof_object_names':[o.name for o in roof],'actual_roof_local_bounds':roof_bounds,'actual_measured_upper_window_groups':groups,'actual_existing_mesh_objects':len(objs)});print('ACTUAL_EXTERIOR_ANCHORS',bid,'roof',roof_bounds,'upper_windows',len(groups),flush=True)
(R/'evidence/production/R13-exterior-detail-anchors.json').write_text(json.dumps({'source_native_sha256':b['native_sha256'],'buildings':rows,'method':'Actual saved-source glass polygon bounds transformed through documented building yaw; no inferred room/window labels or fabricated observations'},indent=2)+'\n')
