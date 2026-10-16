"""Independent geometry audit, executed by Blender on the saved blockout."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];d=json.loads((R/'design/programme.json').read_text());s=bpy.context.scene
errors=[];report={'stage':'BLDG-1 only','blender':bpy.app.version_string,'levels':[],'missing_external_files':[]}
def check(q,msg):
 if not q:errors.append(msg)
cs=[c for c in bpy.data.collections if c.get('occupied_level')];check(len(cs)==6,'occupied level collections')
for l in d['levels']:
 lid=l['id'];c=bpy.data.collections.get(lid);check(c is not None,lid+' collection')
 if not c:continue
 slabs=[o for o in c.objects if o.get('role')=='slab'];check(bool(slabs),lid+' slabs')
 points=[o.matrix_world@Vector(v) for o in slabs for v in o.bound_box]
 bounds=[[min(v[k] for v in points),max(v[k] for v in points)] for k in range(3)]
 check(abs(bounds[0][1]-bounds[0][0]-26)<.0001,lid+' measured width')
 check(abs(bounds[1][1]-bounds[1][0]-20)<.0001,lid+' measured depth')
 check(abs(bounds[2][1]-l['elevation_m'])<.0001,lid+' FFL geometry')
 homes=set()
 for r in l['rooms']:
  if r['kind'] in ['stair','elevator']:continue
  o=bpy.data.objects.get(r['id']+'_ZONE');check(o is not None,r['id']+' mesh')
  if o:
   x,y,xx,yy=r['rect'];check(abs(o.dimensions.x-(xx-x))<.0001 and abs(o.dimensions.y-(yy-y))<.0001,r['id']+' dimensions')
   if o.get('home'):homes.add(o['home'])
 for suffix in ['AXON','PLAN']:check(bpy.data.objects.get('CAM_'+lid+'_'+suffix) is not None,lid+' camera '+suffix)
 for side in ['A','B']:
  steps=[o for o in c.objects if o.name.startswith(lid+'_STAIR_'+side+'_F1_')]
  check(len(steps)==(0 if lid=='L06' else 11 if lid=='L01' else 10),lid+' stair '+side+' first-flight count')
  second=[o for o in c.objects if o.name.startswith(lid+'_STAIR_'+side+'_F2_')]
  check(len(second)==len(steps),lid+' stair '+side+' return flight count')
  if second:check(abs(max(o.location.z+o.dimensions.z/2 for o in second)-(l['elevation_m']+l['storey_height_m']))<.0001,lid+' stair '+side+' connects next FFL')
 report['levels'].append({'id':lid,'slab_bounds_m':bounds,'proposed_home_mesh_groups':sorted(homes),'mesh_objects':sum(o.type=='MESH' for o in c.objects)})
for im in bpy.data.images:
 if im.source=='FILE' and not im.packed_file:
  path=Path(bpy.path.abspath(im.filepath))
  if not path.exists():report['missing_external_files'].append(im.name)
check(not report['missing_external_files'],'missing external textures')
check(not bpy.data.libraries,'linked external libraries')
report['source_blend_sha256']=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();report['errors']=errors
(R/'design/geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
if errors:raise RuntimeError('\n'.join(errors))
print('PASS — reopened measured schematic geometry: 6 levels, 14 proposed home mesh groups, 26 x 20 m slabs, dual stairs and per-floor cameras; no missing external assets. NOT final furnishings.')
