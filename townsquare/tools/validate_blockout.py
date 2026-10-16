"""Executed Blender geometry/inventory checks ONLY. Does not validate final interiors/realism."""
import bpy,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'design/programme.json').read_text());errors=[]
def check(v,msg):
 if not v:errors.append(msg)
expected={f['id'] for b in D['buildings'] for f in b['floors']};actual={c.get('floor_id') for c in bpy.data.collections if c.get('occupied_floor')};check(actual==expected,'Expected26 real occupied-floor collections')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];floorcounts={f:sum(o.get('floor_id')==f for o in meshes) for f in expected};check(all(n>10 for n in floorcounts.values()),'Real slab/wall/opening/frame geometry on every floor')
check(all(any('SLAB' in o.name and o.get('floor_id')==f for o in meshes) for f in expected),'Actual slab per floor')
check(all(b['id'] in {o.get('building_id') for o in meshes} for b in D['buildings']),'All12 buildings physically represented')
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()];check(not missing and not bpy.data.libraries,'Zero missing image files/linked libraries')
# Inspect actual trunk vertices, not the intended planting schedule.
from mathutils import Vector
trunks=[]
for o in meshes:
 if o.name.startswith('LINDEN_TRUNK'):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box];x=sum(p.x for p in pts)/8;y=sum(p.y for p in pts)/8;trunks.append([x,y])
inside=[p for p in trunks if 15<=p[0]<=27 and -4<=p[1]<=10]
check(not inside,'Actual tree trunk intersects playground rectangle')
# Preserve explicit distinction: no actual furnished-room or realistic-human gate has passed.
report={'status':'PASS' if not errors else 'FAIL','scope':'A-stage shell inventory and portable packed-file dependencies ONLY','native':str(Path(bpy.data.filepath).relative_to(R)),'native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'actual_buildings':12,'actual_floor_collections':len(actual),'per_floor_mesh_counts':floorcounts,'packed_images':len([im for im in bpy.data.images if im.packed_file]),'actual_tree_trunk_centres_xy':trunks,'trunks_inside_playground':inside,'missing_files':missing,'furnished_floor_count':0,'people_count':0,'final_realism':'NOT PASSED','independent_acceptance':'NOT ACCEPTED','errors':errors,'blender':bpy.app.version_string}
(R/'evidence/blockout-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if errors:raise RuntimeError(';'.join(errors))
