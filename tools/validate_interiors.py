"""Audits actual furnished mesh families and required rooms, not a scene counter claim.
Blender -b scene/interiors.blend --python-exit-code 1 --python tools/validate_interiors.py
"""
import bpy,hashlib,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'assets/exterior/aligned-programme.json').read_text());s=bpy.context.scene;errors=[];rows=[];bounds=[]
def check(q,m):
 if not q:errors.append(m)
levels=sorted(c.name for c in bpy.data.collections if c.get('occupied_level'));check(levels==[f'L{i:02}' for i in range(1,7)],'six occupied levels')
homes=[h for l in d['levels'] for h in l['homes']];check(len(homes)==14,'14 homes in programme')
for h in homes:
 obs=[o for o in s.objects if o.get('home')==h['id']];meshes=[o for o in obs if o.type=='MESH' and o.get('fixture')];names=[o.name for o in meshes]
 for part in ['KITCHEN','FRIDGE_DOOR','SINK_BOWL','INDUCTION','OVEN_GLASS','MATTRESS','WC_BOWL','SHOWER_TRAY','BASIN','WARDROBE','SOFA','SEAT_CUSHION']:
  check(any(part in n for n in names),h['id']+' missing '+part)
 check(len(meshes)>100,h['id']+' detailed furnishing mesh count');check(sum(o.type=='LIGHT' for o in obs)>=4,h['id']+' practical lighting')
 check(any(o.get('fixture')=='kitchen' for o in meshes) and any(o.get('fixture')=='bed' for o in meshes),h['id']+' actual primary mesh families')
 rows.append({'home':h['id'],'furnishing_mesh_components':len(meshes),'lights':sum(o.type=='LIGHT' for o in obs),'room_ids':sorted(set(o.get('room_id') for o in obs if o.get('room_id')))})
for l in d['levels']:
 for r in l['rooms']:
  if r['kind'] in ['stair','elevator'] or 'RISER_' in r['id']:continue
  furniture=[o for o in s.objects if o.get('room_id')==r['id'] and o.type=='MESH' and o.get('fixture')]
  check(bool(furniture),r['id']+' empty required room')
  for o in furniture:
   if any(k in o.name for k in ['ART','LEAF','STEM','PLANT','PENDANT','PRACTICAL','CORD','DIFFUSER','CEILING','LIGHT','MIRROR','TOWEL','KNOB']):continue
   p=[o.matrix_world@Vector(v) for v in o.bound_box];x,y,xx,yy=r['rect'];margin=.15
   if min(v.x for v in p)<x-margin or max(v.x for v in p)>xx+margin or min(v.y for v in p)<y-margin or max(v.y for v in p)>yy+margin:bounds.append({'room':r['id'],'object':o.name,'xy_bounds':[min(v.x for v in p),min(v.y for v in p),max(v.x for v in p),max(v.y for v in p)],'room_bounds':r['rect']})
# Actual component positions, not a builder-angle/string assertion. South-wall
# storage in north homes must present its door panels toward the room (+Y).
wardrobe_faces=[]
for l in d['levels']:
 for r in l['rooms']:
  if r['kind']!='bedroom' or r['rect'][1]<=10:continue
  prefix=r['id']+'_WARDROBE';car=[o for o in s.objects if o.type=='MESH' and o.name.startswith(prefix+'_CARCASS')];pan=[o for o in s.objects if o.type=='MESH' and o.name.startswith(prefix+'_PANEL')]
  check(len(car)==1 and len(pan)==2,r['id']+' real wardrobe carcass/two door panels')
  if car and pan:
   cy=sum((o.matrix_world@Vector((0,0,0))).y for o in car)/len(car);py=sum((o.matrix_world@Vector((0,0,0))).y for o in pan)/len(pan);delta=py-cy
   wardrobe_faces.append({'room':r['id'],'carcass_y_m':cy,'panel_y_m':py,'inward_panel_offset_m':delta,'required_direction':'+Y into bedroom, away from south wall'})
   check(delta>.27,r['id']+' wardrobe door panels face wall instead of bedroom')
camera_obstructions=[]
for cam in [o for o in s.objects if o.type=='CAMERA' and (o.name.endswith('_INTERIOR') or o.name.endswith('_DETAIL')) and o.name.startswith('CAM_L')]:
 lid=cam.name[4:7];level=next(l for l in d['levels'] if l['id']==lid)
 check(abs(cam.location.z-level['elevation_m']-1.62)<.01,cam.name+' eye height')
 for o in s.objects:
  if o.type!='MESH' or not o.get('fixture') or o.get('level')!=lid:continue
  p=o.matrix_world.inverted()@cam.location;bb=[Vector(v) for v in o.bound_box]
  if all(min(v[i] for v in bb)+.001<p[i]<max(v[i] for v in bb)-.001 for i in range(3)):camera_obstructions.append({'camera':cam.name,'inside_component_bounds':o.name})
check(not camera_obstructions,'eye-level camera intersects furnishing bounds')
for suffix in ['CAFE','PREP','CAFE_PASS','VESTIBULE','LOBBY','WC','BIKES','WASTE','PLANT','PARCEL','NEIGHBOUR','CLEANER']:
 check(any(o.get('room_id')=='L01_'+suffix and o.get('fixture') for o in s.objects),'L01 required '+suffix)
check(any(o.get('room_id')=='L06_WINTER_GARDEN' and o.get('fixture') for o in s.objects),'L06 winter garden furnishings')
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()];check(not missing and not bpy.data.libraries,'external dependencies')
check(not bounds,'furnishing components exceed room boundary (see report)')
report={'native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'wardrobe_door_face_checks':wardrobe_faces,'stage':'mechanical inventory/bounds/orientation checks, not visual acceptance','blender':bpy.app.version_string,'homes':rows,'camera_obstructions':camera_obstructions,'out_of_room_components':bounds,'missing_external':missing,'errors':errors}
(R/'assets/interiors/validation.json').write_text(json.dumps(report,indent=2)+'\n')
for row in rows:print(row)
if errors:raise RuntimeError('\n'.join(errors))
print('PASS — 14 homes with actual detailed kitchens, bedrooms, bathrooms, living furniture, storage and lights; all required public/shared rooms nonempty; six levels; zero out-of-room primary components or missing assets. Visual collisions and independent acceptance remain separate checks.')
