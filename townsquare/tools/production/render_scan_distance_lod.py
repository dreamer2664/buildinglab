"""Unsaved render-only distance LOD for real photographic scan meshes.
Authoritative native/portable meshes untouched; people-detail views never use this.
A sampled source-surface error is limited to1pixel at the PLANNED FULL output resolution.
"""
import bpy,math
from mathutils.bvhtree import BVHTree
from mathutils import Vector

def apply_scan_distance_lod(frame):
 if frame['kind']not in ['aerial','town']:return {'applied':False,'reason':'Full source geometry retained for close people/interior/technical views'}
 s=bpy.context.scene;groups={};records=[]
 for o in s.objects:
  if o.type=='MESH'and o.name.startswith('CROWD_')and not o.hide_render and o.get('source_pose_id'):groups.setdefault(o.data.as_pointer(),[]).append(o)
 for objects in groups.values():
  source=objects[0].data;count=len(source.polygons);inverse=s.camera.matrix_world.inverted();depths=[-(inverse@(o.matrix_world@Vector(corner))).z for o in objects for corner in o.bound_box];closest=max(.01,min(depths))
  target=6000 if closest>50 else 12000 if closest>20 else 30000 if closest>8 else count
  if target>=count:continue
  stride=max(1,len(source.vertices)//2000);samples=[source.vertices[i].co.copy()for i in range(0,len(source.vertices),stride)];focal_pixels=s.camera.data.lens*frame['resolution'][0]/s.camera.data.sensor_width;accepted=None
  while target<count:
   probe=objects[0];proxy=source.copy();probe.data=proxy;modifier=probe.modifiers.new('UNSAVED render-only sampled1pixel scan LOD','DECIMATE');modifier.decimate_type='COLLAPSE';modifier.ratio=target/count;modifier.use_collapse_triangulate=True;bpy.context.view_layer.objects.active=probe;bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.context.view_layer.update();tree=BVHTree.FromObject(probe,bpy.context.evaluated_depsgraph_get());dist=[tree.find_nearest(p)[3]for p in samples];assert all(d is not None for d in dist);worst=max(dist);rms=math.sqrt(sum(d*d for d in dist)/len(dist));pixels=worst*focal_pixels/closest;del tree
   if pixels<=1:
    accepted=probe.data;records.append({'actors':[o.name for o in objects],'source_pose_id':probe['source_pose_id'],'actual_source_faces':count,'actual_render_LOD_faces':len(accepted.polygons),'closest_camera_distance_m':closest,'actual_samples':len(samples),'actual_sampled_source_surface_RMS_m':rms,'actual_sampled_source_surface_max_m':worst,'sampled_surface_error_pixels_at_full_planned_resolution':pixels,'full_planned_output':frame['resolution'],'source_geometry_retained_in_authoritative_native':True});break
   failed=probe.data;probe.data=source
   if failed.users==0:bpy.data.meshes.remove(failed)
   target=min(count,target*2)
  if accepted:
   for o in objects:o.data=accepted
  else:objects[0].data=source
 bpy.data.orphans_purge(do_recursive=True);bpy.context.view_layer.update();print('UNSAVED_DISTANCE_SCAN_LOD_READY',len(records),'FULL_RES_SAMPLE_ERROR_MAX_PX',max((r['sampled_surface_error_pixels_at_full_planned_resolution']for r in records),default=0),flush=True);return {'applied':True,'actual_shared_variant_lods':records,'limitation':'Sampled screen-space surface-error test, not a mathematical Hausdorff proof. Original photo UV interpolated through geometric decimation. This is declared render-only mesh LOD for distant visitors, not a replacement or mutating save of source assets. All close people evidence/native/export keep original geometry.'}
