"""Third inspection-driven study. Actual scoped furniture edits; no frozen-source overwrite."""
import bpy,sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from fitout_transforms import edit_region,material_bounds
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
SOURCE='05d17ebaaf0b11aa9c8b5fe4acc9e785abcf0ca4965316719fd8011165118705'
assert file_sha256(bpy.data.filepath)==SOURCE
programme=json.loads((R/'design/programme.json').read_text());plans=json.loads((R/'evidence/production/R11-plan-annotation-source.json').read_text())['plans'];changes=[]
def frame(fid):
 b=next(b for b in programme['buildings']if any(f['id']==fid for f in b['floors']));return b,next(f for f in b['floors']if f['id']==fid)
def furniture(fid,room):return next(o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('room_id')==fid+'_'+room and o.get('layer')=='furniture')
fid='B05_L02';b,f=frame(fid);o=furniture(fid,'LIVING');lo,hi=material_bounds(o,b,f['datum_m'],'modern_arm_chair_01')
changes.append(edit_region(o,b,f['datum_m'],lo-.002,hi+.002,delta=(.8,-1.7,0),tag='Florist_armchair_separated_from_existing_plant',material_prefixes=['modern_arm_chair_01']))
# Use actual living-room finish extent in the building-local frame, not guessed world axes.
q=next(r for r in plans[fid+'_plan']['rooms']if r['room_id']==fid+'_LIVING')['world_bounds'];c,s=math.cos(math.radians(b['rotation_deg'])),math.sin(math.radians(b['rotation_deg']));cx,cy=b['centre_xy_m'];pts=[((x-cx)*c+(y-cy)*s,-(x-cx)*s+(y-cy)*c)for x in [q[0][0],q[1][0]]for y in [q[0][1],q[1][1]]];x1=max(x for x,y in pts);my=(min(y for x,y in pts)+max(y for x,y in pts))/2
changes.append(edit_region(o,b,f['datum_m'],(x1-1.5,my-.85,-.05),(x1+.3,my+.85,1.6),delta=(0,-1.45,0),tag='Florist_plant_moved_sideways_off_kitchen_door_approach',material_prefixes=['Terracotta','Soil','Leaf']))
for fid in ['B07_L02','B07_L03']:
 b,f=frame(fid)
 for room in ['SUITE_-1_LOUNGE','SUITE_1_LOUNGE']:
  o=furniture(fid,room);lo,hi=material_bounds(o,b,f['datum_m'],'sofa_02');changes.append(edit_region(o,b,f['datum_m'],lo-.002,hi+.002,delta=(0,-.60,0),tag='Hotel_salon_sofa_back_clear_of_bedroom_door',material_prefixes=['sofa_02']))
# The other original L02 bed also receives a clear north-side approach.
fid='B07_L02';b,f=frame(fid);o=furniture(fid,'SUITE_1_SLEEP');changes.append(edit_region(o,b,f['datum_m'],(2.65,-2.55,-.05),(6.1,1.30,1.7),delta=(0,-1.0,0),tag='Hotel_right_bed_rug_nightstands_north_approach'))
bpy.context.view_layer.update();out=R/'.cache/distinct-interiors-followup-study';out.mkdir(exist_ok=True);native=out/'Winterlichtplatz-interior-followup-STUDY-NOT-PROMOTED.blend';bpy.context.scene['study_only']='Third interior clearance study; not final production or realism acceptance.';bpy.ops.wm.save_as_mainfile(filepath=str(native))
r={'stage':'SAVED_FOLLOWUP_STUDY_NOT_PROMOTED','source_study_sha256':SOURCE,'study_native':str(native.relative_to(R)),'study_native_sha256':file_sha256(native),'actual_changes':changes,'images':[],'inspection':'PENDING individual image opens; render success does not establish clearances.'};report=R/'evidence/production/R12-interiors-followup-study.json';report.write_text(json.dumps(r,indent=2)+'\n')
for b in programme['buildings']:
 for floor in b['floors']:
  view=floor['id']+'_plan';bpy.ops.wm.open_mainfile(filepath=str(native));f=apply_view(view);prune_for_render(f);upgrade_images(R,f);scene=bpy.context.scene;scene.render.resolution_x=1024;scene.render.resolution_y=576;scene.cycles.samples=8;scene.cycles.use_denoising=True;scene.use_nodes=False;scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.filepath=str(out/(view+'.png'));bpy.ops.render.render(write_still=True);r['images'].append({'id':view,'path':str(Path(scene.render.filepath).relative_to(R)),'dimensions':[1024,576],'samples':8,'sha256':file_sha256(scene.render.filepath)});report.write_text(json.dumps(r,indent=2)+'\n');print('FOLLOWUP_PLAN_RENDERED',view,flush=True)
print('FOLLOWUP_26_PLANS_COMPLETE_INSPECTION_PENDING',flush=True)
