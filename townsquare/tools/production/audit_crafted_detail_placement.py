"""Actual new facade world bounds and clear-glass rectangle checks; not certified circulation."""
import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
b=json.loads((R/'evidence/production/R13-crafted-exteriors.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];schedule={x['id']:x for x in json.loads((R/'design/programme.json').read_text())['buildings']};rows=[];failures=[];glass_failures=[]
for ob in bpy.context.scene.objects:
 if ob.get('stage')!='R13_ORIGINAL_ADDITIVE_FACADE_CRAFT':continue
 e=schedule[ob['building_id']];w,d=e['footprint_m'];angle=math.radians(e['rotation_deg']);c=math.cos(angle);s=math.sin(angle);ox,oy=e['centre_xy_m'];top=e['floors'][-1]['datum_m']+e['floors'][-1]['height_m'];roof=next(x for x in b['actual_exterior_craft']if x['building']==ob['building_id'])['actual_end_roof_ridge_z_m']
 def local(v):return Vector((c*(v.x-ox)+s*(v.y-oy),-s*(v.x-ox)+c*(v.y-oy),v.z))
 ps=[local(ob.matrix_world@Vector(p))for p in ob.bound_box];lo=[min(v[i]for v in ps)for i in range(3)];hi=[max(v[i]for v in ps)for i in range(3)];issues=[]
 if lo[0]<-w/2-1.2 or hi[0]>w/2+1.2 or lo[1]<-d/2-1.2 or hi[1]>d/2+1.2:issues.append('New detail not at actual assigned building envelope')
 if lo[2]<-.02 or hi[2]>roof+.4:issues.append('New detail vertical bounds exceed measured building roof/ground')
 if ob.get('actual_glass_anchor'):
  a=json.loads(ob['actual_glass_anchor']);axis=0 if a['side']in ['front','back']else 1;h0,h1=a['horizontal_bounds'];z0,z1=a['vertical_bounds'];bad=[]
  for f in ob.data.polygons:
   points=[local(ob.matrix_world@ob.data.vertices[i].co)for i in f.vertices];a0=min(v[axis]for v in points);a1=max(v[axis]for v in points);b0=min(v.z for v in points);b1=max(v.z for v in points)
   if min(a1,h1-.015)>max(a0,h0+.015)and min(b1,z1-.015)>max(b0,z0+.015):bad.append(f.index)
  if bad:glass_failures.append({'object':ob.name,'raw_decor_faces_intruding_measured_clear_glass_rectangle':bad})
 row={'object':ob.name,'building':ob['building_id'],'actual_local_bounds':[lo,hi],'issues':issues};rows.append(row)
 if issues:failures.append(row)
r={'native_sha256':b['native_sha256'],'actual_detail_groups_checked':len(rows),'building_bound_failures':failures,'clear_glass_rectangle_failures':glass_failures,'objects':rows,'scope':'Actual transformed new detail bounds and conservative raw face bounding-box projection versus measured glass clear rectangles. Not structural/accessibility/playground/meshcollision certification or proof of individual visual inspection.'};(R/'evidence/production/R13-crafted-detail-placement-audit.json').write_text(json.dumps(r,indent=2)+'\n');assert not failures and not glass_failures,(len(failures),len(glass_failures));print('ACTUAL_CRAFTED_DETAIL_WORLD_PLACEMENT_AND_CLEAR_GLASS_PASS',len(rows),'WINDOW_PANE_INTRUSIONS0',flush=True)
