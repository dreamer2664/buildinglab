"""Actual saved editable bakery-home differentiation pilot, not final/current native promotion."""
import bpy,sys,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from differentiate_interiors import apply
from view_tools import apply_view,prune_for_render
from image_tools import upgrade_images
assert file_sha256(bpy.data.filepath)=='7fb9ce64d02030beac15b2adb8df32831e885acfabca51ca26a28a0f2d5a77b1'
report=apply(R,only=['B02_L02']);out=R/'.cache/differentiated-home-study';out.mkdir(exist_ok=True);native=out/'B02-differentiated-full-scene-STUDY.blend';bpy.context.scene['study_only']='Unpromoted actual furnished-layout differentiation of B02_L02; R11frozen untouched';bpy.ops.wm.save_as_mainfile(filepath=str(native));r={'stage':'ACTUAL_SAVED_NATIVE_DIFFERENTIATION_STUDY_NOT_PROMOTED','source_frozen_native_sha256':'7fb9ce64d02030beac15b2adb8df32831e885acfabca51ca26a28a0f2d5a77b1','study_native':str(native.relative_to(R)),'study_native_sha256':file_sha256(native),'actual_changes':report,'images':[],'inspection':'PENDING, no uniqueness/realism acceptance from authoring success'}
for id in ['B02_L02_plan','B02_L02_cutaway','B02_L02_interior']:
 bpy.ops.wm.open_mainfile(filepath=str(native));f=apply_view(id);prune_for_render(f);upgrade_images(R,f);s=bpy.context.scene;s.render.resolution_x=1024;s.render.resolution_y=576;s.cycles.samples=8;s.cycles.use_denoising=False;s.use_nodes=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.filepath=str(out/(id+'.png'));bpy.ops.render.render(write_still=True);r['images'].append({'id':id,'path':str(Path(s.render.filepath).relative_to(R)),'dimensions':[1024,576],'samples':8,'raw_sha256':file_sha256(s.render.filepath)});print('DISTINCT_HOME_PILOT_ORIGINAL_RENDERED',id,flush=True)
(R/'evidence/production/R12-distinct-home-first-study.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_DIFFERENTIATED_HOME_NATIVE_AND_THREE_RAW_PILOTS_DONE / original opens pending',flush=True)
