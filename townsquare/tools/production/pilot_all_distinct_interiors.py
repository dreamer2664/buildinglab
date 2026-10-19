"""Actual editable seven-home draft + geometry-only duplicate audit +26separate plan studies.
Not a promoted master; numeric difference is not visual/realism acceptance.
"""
import bpy,sys,json,hashlib,math,os
import numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from differentiate_interiors import apply
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
assert file_sha256(bpy.data.filepath)=='7fb9ce64d02030beac15b2adb8df32831e885acfabca51ca26a28a0f2d5a77b1'
correction=os.environ.get('SQUARE_INTERIOR_CORRECTION_PASS')=='1';changes=apply(R)
if correction:
 from correct_inspected_fitouts import apply as correct
 changes.extend(correct(R))
report_path=R/'evidence/production'/('R12-all-interiors-clearance-study.json'if correction else'R12-all-interiors-first-study.json')
programme=json.loads((R/'design/programme.json').read_text());deps=bpy.context.evaluated_depsgraph_get();floor_rows=[]
for b in programme['buildings']:
 angle=-math.radians(b['rotation_deg']);co,si=math.cos(angle),math.sin(angle)
 for floor in b['floors']:
  arrays=[]
  for o in bpy.context.scene.objects:
   if o.type!='MESH' or o.get('floor_id')!=floor['id'] or o.get('layer')!='furniture':continue
   ev=o.evaluated_get(deps);me=ev.to_mesh();a=np.empty(len(me.vertices)*3,dtype=np.float64);me.vertices.foreach_get('co',a);a=a.reshape(-1,3);mat=np.asarray(o.matrix_world,dtype=np.float64);a=a@mat[:3,:3].T+mat[:3,3];x=a[:,0]-b['centre_xy_m'][0];y=a[:,1]-b['centre_xy_m'][1];a[:,0]=co*x-si*y;a[:,1]=si*x+co*y;a[:,2]-=floor['datum_m'];arrays.append(np.rint(a*1000).astype('<i8'));ev.to_mesh_clear()
  assert arrays,floor['id'];a=np.concatenate(arrays);a=a[np.lexsort((a[:,2],a[:,1],a[:,0]))];floor_rows.append({'floor':floor['id'],'evaluated_furniture_vertices':len(a),'normalised_1mm_geometry_positions_sha256':hashlib.sha256(a.tobytes()).hexdigest(),'scope':'Actual evaluated furnishing vertex positions normalized to building local XY/floor Z, sorted at1mm. No labels,brand names,material names,colours in hash. Not full topology/functional/aesthetic/realism acceptance.'})
groups={}
for row in floor_rows:groups.setdefault(row['normalised_1mm_geometry_positions_sha256'],[]).append(row['floor'])
duplicates=[v for v in groups.values()if len(v)>1];finishes={o.get('room_id')for o in bpy.context.scene.objects if o.type=='MESH'and o.get('layer')=='finish'and o.get('room_id')};furnished={o.get('room_id')for o in bpy.context.scene.objects if o.type=='MESH'and o.get('layer')=='furniture'and o.get('room_id')};missing=sorted(finishes-furnished);out=R/('.cache/distinct-interiors-clearance-study'if correction else'.cache/distinct-interiors-all-study');out.mkdir(exist_ok=True);native=out/('Winterlichtplatz-interior-clearance-STUDY-NOT-PROMOTED.blend'if correction else'Winterlichtplatz-interior-draft-NOT-PROMOTED.blend');bpy.context.scene['study_only']='Actual inspect-driven fit-out differentiation/door corrections study; R11hair still unchanged; not final or promoted.';bpy.ops.wm.save_as_mainfile(filepath=str(native));r={'stage':'ACTUAL_SAVED_SEVEN_HOME_DRAFT_NOT_PROMOTED','source_frozen_native_sha256':'7fb9ce64d02030beac15b2adb8df32831e885acfabca51ca26a28a0f2d5a77b1','study_native':str(native.relative_to(R)),'study_native_sha256':file_sha256(native),'actual_changes':changes,'floor_geometry_audit':floor_rows,'exact_geometry_duplicate_floor_groups':duplicates,'actual_finished_room_ids':len(finishes),'finished_rooms_without_furniture':missing,'images':[],'inspection':'PENDING, all26originals must individually open; no count/hash-based distinctness/realism acceptance'};report_path.write_text(json.dumps(r,indent=2)+'\n');assert not missing,missing
for b in programme['buildings']:
 for floor in b['floors']:
  id=floor['id']+'_plan';bpy.ops.wm.open_mainfile(filepath=str(native));f=apply_view(id);prune_for_render(f);upgrade_images(R,f);s=bpy.context.scene;s.render.resolution_x=1024;s.render.resolution_y=576;s.cycles.samples=8;s.cycles.use_denoising=False;s.use_nodes=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=str(out/(id+'.png'));bpy.ops.render.render(write_still=True);r['images'].append({'id':id,'path':str(Path(s.render.filepath).relative_to(R)),'dimensions':[1024,576],'samples':8,'raw_sha256':file_sha256(s.render.filepath)});report_path.write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_DISTINCT_INTERIOR_PLAN_STUDY_RENDERED',id,flush=True)
print('ACTUAL26_DRAFT_PLAN_STUDIES_COMPLETE_SEPARATE_INSPECTION_PENDING',flush=True)
