"""Actual reopen + structural/packing/contact audit. Not visual or independent acceptance."""
import bpy,json,hashlib,array,os
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];s=bpy.context.scene;bpy.context.view_layer.update();expected=json.loads((R/'design/programme.json').read_text());issues=[]
file=Path(bpy.data.filepath);h=hashlib.sha256()
with file.open('rb') as f:
 while b:=f.read(1024*1024):h.update(b)
floors=[];rooms=[]
for b in expected['buildings']:
 for f in b['floors']:
  fid=f['id'];meshes=[o for o in s.objects if o.type=='MESH' and o.get('floor_id')==fid];finishes=[o for o in meshes if o.get('layer')=='finish'];furniture=[o for o in meshes if o.get('layer')=='furniture'];room_ids={o.get('room_id') for o in finishes}
  missing=[rid for rid in room_ids if not any(o.get('room_id')==rid and len(o.data.polygons)>0 for o in furniture)]
  if not finishes or not furniture or missing:issues.append({'floor':fid,'missing_furnished_rooms':missing})
  floors.append({'floor_id':fid,'programme':f['programme'],'finished_room_count':len(room_ids),'furniture_batches':len(furniture),'furniture_faces':sum(len(o.data.polygons) for o in furniture),'furniture_source_component_count':sum(int(o.get('component_count',0)) for o in furniture),'rooms_missing_actual_furniture':missing})
  rooms+=sorted(room_ids)
people=[];variants={}
for o in s.objects:
 if o.type=='MESH' and o.name.startswith('CROWD_'):
  ps=[o.matrix_world@Vector(p) for p in o.bound_box];sole=min(p.z for p in ps);variant=o.get('variant_id');variants[variant]=variants.get(variant,0)+1
  people.append({'name':o.name,'variant':variant,'person_id':o.get('person_id'),'sole_z_m':round(sole,8),'height_m':round(max(p.z for p in ps)-sole,5),'pose_is_static_in_town':True})
  if abs(sole-.006)>1e-5:issues.append({'person':o.name,'sole_z_m':sole})
if len(floors)!=26 or len(people)!=36 or len(variants)!=12:issues.append('Unexpected floor/people/variant count')
images=[]
for im in bpy.data.images:
 if not im.users:continue
 rec={'name':im.name,'packed':bool(im.packed_file),'colorspace':im.colorspace_settings.name}
 if im.packed_file:rec['packed_sha256']=hashlib.sha256(im.packed_file.data).hexdigest();rec['packed_bytes']=len(im.packed_file.data)
 elif im.source=='FILE':issues.append({'missing_packed_image':im.name,'path':im.filepath})
 images.append(rec)
street=next(o for o in s.objects if o.type=='MESH' and o.get('layer')=='street_furniture' and o.get('building_id')=='PUBLIC')
points=[street.matrix_world@v.co for v in street.data.vertices]
benchpositions=[]
for x in [-25,-15,-5,5,15,25]:benchpositions += [(x,-21,0),(x,21,3.141592653589793)]
for y in [-15,-9,-3,3,9,15]:benchpositions += [(-28,y,3.141592653589793/2),(28,y,-3.141592653589793/2)]
import math
bench_tests=[]
for x,y,a in benchpositions:
 co,si=math.cos(a),math.sin(a);count=0
 for p in points:
  dx,dy=p.x-x,p.y-y;xx,yy=dx*co+dy*si,-dx*si+dy*co
  if abs(xx)<1.01 and -.28<yy<.3 and .44<p.z<.52:count+=1
 bench_tests.append({'xy_m':[x,y],'seat_slat_vertices_in_expected_band':count,'geometry_found':count>=24})
lamp_tests=[]
for i in range(24):
 if i<12:x,y=[-29,-19,-9,9,19,29][i%6],[-23,23][i//6]
 else:x,y=[-30,30][(i-12)//6],[-17,-10,-3,3,10,17][i%6]
 count=sum(abs(p.x-x)<.31 and abs(p.y-y)<.31 and 3.9<p.z<4.7 for p in points);lamp_tests.append({'xy_m':[x,y],'lantern_cap_diffuser_vertices':count,'geometry_found':count>=24})
public={'benches':sum(t['geometry_found'] for t in bench_tests),'lamps':sum(t['geometry_found'] for t in lamp_tests),'market_stalls':len([o for o in s.objects if o.type=='MESH' and 'MARKET_' in o.name]),'deciduous_trees':len([o for o in s.objects if o.type=='MESH' and 'LINDEN_' in o.name])}
for name,count in [('benches',24),('lamps',24),('market_stalls',8),('deciduous_trees',12)]:
 if public[name]!=count:issues.append({'public_count_mismatch':name,'actual':public[name],'expected':count})
trunks=[]
for o in s.objects:
 if o.type=='MESH' and 'LINDEN_' in o.name:
  low=[o.matrix_world@v.co for v in o.data.vertices if (o.matrix_world@v.co).z<1]
  if low:
   x=(min(p.x for p in low)+max(p.x for p in low))/2;y=(min(p.y for p in low)+max(p.y for p in low))/2;trunks.append({'tree':o.name,'base_centre_xy_m':[x,y]})
   if 14.8<x<27.2 and -4.2<y<10.2:issues.append({'tree_base_overlaps_equipment_envelope':o.name,'centre':[x,y]})
brands=[]
for i in range(1,13):
 name=f'B{i:02}.png';used=any(im.name.startswith(name) and im.users>0 and im.packed_file for im in bpy.data.images);brands.append({'building':f'B{i:02}','packed_original_mark_connected':used})
 if not used:issues.append({'missing_brand_image':name})
result={'native_file':str(file),'native_sha256':h.hexdigest(),'reopened_with_blender':bpy.app.version_string,'status':'PASS' if not issues else 'FAIL','issues':issues,'objects':len(s.objects),'occupied_floors':floors,'finished_rooms':len(set(rooms)),'people':people,'variant_instance_counts':variants,'public_counts':public,'bench_geometry_tests':bench_tests,'lamp_geometry_tests':lamp_tests,'public_count_method':'Actual slat and lantern geometry at expected centres in the combined editable street-furniture mesh; not obsolete pre-batch object names','tree_bases':trunks,'connected_brand_images':brands,'used_images':images,'camera_presets':len([o for o in s.objects if o.type=='CAMERA' and o.get('view_id')]),'embedded_self_contained_view_tools':all(bpy.data.texts.get(n) for n in ['VIEW_PRESETS.json','VIEW_TOOLS.py','READ_ME.txt']),'visual_acceptance':'NOT asserted by structural/packing/contact tests','regulatory_certification':'NOT asserted','independent_acceptance':'NOT GRANTED'}
out=R/'evidence/production'/os.environ.get('SQUARE_VALIDATION_REPORT','R11-full-native-reopen.json');out.write_text(json.dumps(result,indent=2)+'\n');print('ACTUAL_NATIVE_REOPEN_GATE',result['status'],'rooms',result['finished_rooms'],'people',len(people),'issues',issues,flush=True)
if issues:raise RuntimeError('Structural/packing/contact gate failed')
