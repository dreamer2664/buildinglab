"""Measured camera-only correction: H03 was INSIDE a real street-lamp iron shaft.
No geometry deletion/cropping to conceal defects. Model/UV/material-index signature unchanged.
"""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256,geometry_uv_pose_material_signature
b=json.loads((R/'evidence/production/R14-stocked-town.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];before=geometry_uv_pose_material_signature();s=bpy.context.scene;frames=json.loads(bpy.data.texts['VIEW_PRESETS.json'].as_string());camera=bpy.data.objects['VIEW|H03'];old=list(camera.location);f=next(x for x in frames['frames']if x['id']=='H03');f['position']=[-28.8,16.8,2.1];camera.location=f['position'];camera.rotation_euler=(Vector(f['target'])-camera.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();checks=[]
for frame in frames['frames']:
 if not frame['id'].startswith('H'):continue
 cam=bpy.data.objects['VIEW|'+frame['id']];origin=cam.matrix_world.translation.copy();rays=[('centre',Vector((0,0,-1)))]+[(str(i),v.normalized())for i,v in enumerate(cam.data.view_frame(scene=s))]
 for label,d in rays:
  direction=cam.matrix_world.to_3x3()@d;hit,p,normal,face,o,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=1000);row={'view':frame['id'],'ray':label,'hit':hit,'distance_m':(p-origin).length if hit else None,'object':o.name if hit else None};checks.append(row)
  if frame['id']=='H03':assert not hit or row['distance_m']>.30,('Corrected camera still intersects near geometry',row)
t=bpy.data.texts['VIEW_PRESETS.json'];t.clear();t.write(json.dumps(frames));external=R/'design/production-views.json';data=json.loads(external.read_text());next(x for x in data['frames']if x['id']=='H03')['position']=f['position'];external.write_text(json.dumps(data,indent=2)+'\n');assert geometry_uv_pose_material_signature()==before==b['geometry_uv_pose_material_signature'];note=bpy.data.texts.new('H03_CAMERA_COLLISION_CORRECTION.txt');note.write('Actual prior H03camera[-30,17,2.1] was inside the blackenediron street-furniture lamp shaft; all5rays hit at52-56mm. Corrected camera moves1.2m to[-28.8,16.8,2.1], same target/lens. No source geometry, lights, materials or product/crowd placement changed. Actual centre/corner near-clearance tested; source image reinspection remains separate.');note.use_fake_user=True
out=R/'.cache/stocked-town/Winterlichtplatz-stocked-camera-corrected-UNPROMOTED.blend';bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True);r=dict(b);r.update(native=str(out.relative_to(R)),native_sha256=file_sha256(out),native_bytes=out.stat().st_size,parent_uncorrected_camera_native_sha256=b['native_sha256'],actual_camera_correction={'view':'H03','old_position':old,'new_position':list(camera.location),'same_target':f['target'],'same_lens_mm':camera.data.lens,'actual_primary_ray_checks':checks,'geometry_signature_exactly_preserved':before},stage='CAMERA_ONLY_COLLISION_CORRECTED_STOCKED_CANDIDATE_NOT_FINAL_ACCEPTANCE');(R/'evidence/production/R14-camera-corrected-stocked-town.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_H03_LAMP_COLLISION_CAMERA_CORRECTION_SAVED',r['native_sha256'],r['native_bytes'],flush=True)
