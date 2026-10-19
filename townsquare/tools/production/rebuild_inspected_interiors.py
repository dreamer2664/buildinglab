"""Recover inspected fit-outs from public immutable R11 and saved scoped edit scripts.
Save full packed editable study BEFORE new render work, allowing immediate durable upload.
No invented continuity of lost binaries or inspection bindings.
"""
import bpy,sys,json,hashlib,math,os
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from differentiate_interiors import apply as home
from correct_inspected_fitouts import apply as commercial
from followup_fitouts import apply as followup
BASE='7fb9ce64d02030beac15b2adb8df32831e885acfabca51ca26a28a0f2d5a77b1'
assert file_sha256(bpy.data.filepath)==BASE
changes=home(R)+commercial(R)+followup(R)
finishes={o.get('room_id')for o in bpy.context.scene.objects if o.type=='MESH'and o.get('layer')=='finish'and o.get('room_id')};furnished={o.get('room_id')for o in bpy.context.scene.objects if o.type=='MESH'and o.get('layer')=='furniture'and o.get('room_id')};assert len(finishes)==164;assert not finishes-furnished,sorted(finishes-furnished)
# Embed the actual non-destructive view helper and a factual study note, not stale acceptance.
text=bpy.data.texts.get('VIEW_TOOLS.py')or bpy.data.texts.new('VIEW_TOOLS.py');text.clear();text.write((R/'tools/production/view_tools.py').read_text())
note=bpy.data.texts.get('INTERIOR_STUDY_STATUS.txt')or bpy.data.texts.new('INTERIOR_STUDY_STATUS.txt');note.clear();note.write('UNPROMOTED reconstructed editable interior study. Full R11 source + differentiated homes + actual cafe/hotel/atelier/staff corrections + florist/hotel-salon follow-up. Previous binary hashes are historical: this is a new save. No new hair adoption. Final-resolution/portable/realism/independent acceptance remain open. See external immutable publication and actual image review records.\n')
# Audit real placement, not floor_id metadata alone. Newly authored prop bounds must belong to their room/floor.
bpy.context.view_layer.update();schedule=json.loads((R/'design/programme.json').read_text());datums={f['id']:f['datum_m']for b in schedule['buildings']for f in b['floors']};annotations=json.loads((R/'evidence/production/R11-plan-annotation-source.json').read_text())['plans'];room_bounds={x['room_id']:x['world_bounds']for p in annotations.values()for x in p['rooms']};placement=[];failures=[]
for ob in bpy.context.scene.objects:
 if ob.type!='MESH'or not str(ob.get('stage','')).startswith('R12'):continue
 points=[ob.matrix_world@Vector(v)for v in ob.bound_box];lo=[min(p[i]for p in points)for i in range(3)];hi=[max(p[i]for p in points)for i in range(3)];fid=ob.get('floor_id');room=ob.get('room_id');rb=room_bounds.get(room);issues=[]
 if fid not in datums:issues.append('unknown floor')
 else:
  if lo[2]<datums[fid]-.12:issues.append('below occupied floor')
  if hi[2]>datums[fid]+2.95:issues.append('above room fitout height')
 if rb:
  for axis in [0,1]:
   if lo[axis]<rb[0][axis]-.20 or hi[axis]>rb[1][axis]+.20:issues.append('outside actual room XY bounds')
 row={'object':ob.name,'floor':fid,'room':room,'actual_world_bounds':[lo,hi],'issues':issues};placement.append(row)
 if issues:failures.append(row)
auditpath=R/'evidence/production'/os.environ.get('SQUARE_PLACEMENT_REPORT','R12-generated-prop-placement-audit.json');auditpath.write_text(json.dumps({'stage':'ACTUAL_EVALUATED_OBJECT_BOUND_PLACEMENT_AUDIT_NOT_COLLISION_CERTIFICATION','objects_checked':len(placement),'failures':failures,'objects':placement},indent=2)+'\n');assert not failures,('Actual generated props outside assigned room/floor',len(failures),failures[:3])
bpy.context.scene['study_only']='Rebuilt inspection-driven interiors, not promoted or accepted.'
label=os.environ.get('SQUARE_BUILD_LABEL','rebuilt-interiors');out=R/'.cache'/label;out.mkdir(parents=True,exist_ok=True);native=out/'Winterlichtplatz-rebuilt-interiors-UNPROMOTED.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
r={'stage':'ACTUAL_SAVED_RECONSTRUCTION_NOT_PROMOTED','base_native_sha256':BASE,'native':str(native.relative_to(R)),'native_sha256':file_sha256(native),'native_bytes':native.stat().st_size,'actual_finished_room_ids':len(finishes),'finished_rooms_without_furniture':sorted(finishes-furnished),'actual_changes':changes,'images':[],'inspection':'NOT YET INSPECTED for this exact saved native. Older actual study-image observations preserved separately; never rebound by assertion.'};report=R/'evidence/production'/os.environ.get('SQUARE_BUILD_REPORT','R12-rebuilt-interiors.json');report.write_text(json.dumps(r,indent=2)+'\n');print('REBUILT_EDITABLE_NATIVE_SAVED',r['native_sha256'],r['native_bytes'],flush=True)
# Normal/albedo-guided Cycles denoising; real saved-source renders, no image generation.
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
programme=json.loads((R/'design/programme.json').read_text());images=R/'evidence/quality-studies'/os.environ.get('SQUARE_PLAN_FOLDER','rebuilt-plans');images.mkdir(parents=True,exist_ok=True)
for b in programme['buildings']:
 for floor in b['floors']:
  if os.environ.get('SQUARE_PLAN_FLOORS')and floor['id']not in os.environ['SQUARE_PLAN_FLOORS'].split(','):continue
  view=floor['id']+'_plan';bpy.ops.wm.open_mainfile(filepath=str(native));f=apply_view(view);prune_for_render(f);upgrade_images(R,f);scene=bpy.context.scene;scene.render.resolution_x=1024;scene.render.resolution_y=576;scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.use_nodes=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.filepath=str(images/(view+'.png'));bpy.ops.render.render(write_still=True);r['images'].append({'id':view,'path':str(Path(scene.render.filepath).relative_to(R)),'dimensions':[1024,576],'samples':8,'sha256':file_sha256(scene.render.filepath),'inspection':'NOT YET OPENED'});report.write_text(json.dumps(r,indent=2)+'\n');print('REBUILT_PLAN_RENDERED',view,flush=True)
print('REBUILT_PLAN_STUDIES_COMPLETE_COUNT',len(r['images']),'INSPECTION_PENDING',flush=True)
