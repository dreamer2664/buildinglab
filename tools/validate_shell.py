"""Mechanical shell validator. Run Blender -b scene/shell.blend --python-exit-code 1 --python tools/validate_shell.py."""
import bpy,json,math,hashlib
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'assets/exterior/aligned-programme.json').read_text());s=bpy.context.scene;errors=[];rows=[]
def check(q,m):
 if not q:errors.append(m)
levels=[c for c in bpy.data.collections if c.get('occupied_level')];check(sorted(c.name for c in levels)==[f'L{i:02}' for i in range(1,7)],'six occupied levels')
for l in D['levels']:
 lid=l['id'];obs=[o for o in s.objects if o.get('level')==lid];slabs=[o for o in obs if o.get('role')=='slab'];p=[o.matrix_world@Vector(v) for o in slabs for v in o.bound_box]
 check(bool(p),lid+' slab mesh')
 if p:check(abs(max(v.x for v in p)-min(v.x for v in p)-26)<.001 and abs(max(v.y for v in p)-min(v.y for v in p)-20)<.001,lid+' measured slab 26x20')
 for side in ['A','B']:
  flights=[o for o in obs if o.get('role')=='stair_flight' and o.get('route')==side];check(len(flights)==(0 if lid=='L06' else 2),lid+' route '+side+' paired flights')
  if flights:
   highest=max(max((o.matrix_world@v.co).z for v in o.data.vertices) for o in flights);check(abs(highest-(l['elevation_m']+l['storey_height_m']+.04))<.001,lid+' route '+side+' meets next finished floor')
  check(any('_STAIR_'+side+'_LANDING' in o.name for o in obs),lid+' route '+side+' landing')
 check(any('_LIFT_DOOR' in o.name for o in obs),lid+' lift doors')
 check(all(bpy.data.collections.get(lid+'_'+suffix) is not None for suffix in ['FACADE','PARTITIONS_LOW','PARTITIONS_HIGH','CEILING']),lid+' reversible cutaway groups')
 windows=[o for o in obs if '_GLAZING' in o.name];check(len(windows)>=6,lid+' actual glazing meshes');check(any('_WINDOW_REVEAL' in o.name for o in obs),lid+' modeled reveals')
 rows.append({'level':lid,'slab_objects':len(slabs),'glazing_meshes':len(windows),'objects':len(obs),'floor_m':l['elevation_m']})
check(bpy.data.objects.get('ROOF_STRUCTURAL_SLAB') is not None,'roof slab');check(any(o.name.startswith('ROOF_PARAPET') for o in s.objects),'roof parapet');check(bpy.data.objects.get('L01_LIFT_CAB_FLOOR') is not None,'one actual elevator cab')
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()];check(not missing and not bpy.data.libraries,'no missing external images or linked libraries')
import sys
sys.path.insert(0,str(R/'assets/exterior'));from circulation_checks import lift_checks
bpy.context.view_layer.update();lift_report=lift_checks(s,D);errors.extend(lift_report['errors'])
ceiling_checks=[]
for l in D['levels']:
 for r in l['rooms']:
  if r['kind'] in ['stair','elevator']:continue
  obs=[o for o in s.objects if o.type=='MESH' and o.name.startswith(r['id']+'_CEILING')];check(bool(obs),r['id']+' actual ceiling finish')
  if not obs:continue
  pts=[o.matrix_world@Vector(v) for o in obs for v in o.bound_box];x,y,xx,yy=r['rect'];bb=[min(p.x for p in pts),min(p.y for p in pts),max(p.x for p in pts),max(p.y for p in pts)]
  ok=bb[0]<=x-.025 and bb[1]<=y-.025 and bb[2]>=xx+.025 and bb[3]>=yy+.025
  check(ok,r['id']+' ceiling finish does not overlap enclosing wall edges');ceiling_checks.append({'room':r['id'],'actual_xy_bounds':bb,'room_bounds':r['rect'],'at_least_25mm_overlap':ok})
report={'native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'ceiling_edge_checks':ceiling_checks,'actual_lift_geometry_checks':lift_report,'stage':'mechanical shell only, not code/visual/independent acceptance','levels':rows,'missing_external':missing,'errors':errors,'blender':bpy.app.version_string}
(R/'assets/exterior/validation.json').write_text(json.dumps(report,indent=2)+'\n')
for x in rows:print(x)
if errors:raise RuntimeError('\n'.join(errors))
print('PASS — six measured floor plates, ten paired-flight connections across two continuous routes, six elevator portals, one cab, roof/parapet, real glazing/reveals and cutaway collections. No external file dependency. Visual/engineering acceptance is separate.')
