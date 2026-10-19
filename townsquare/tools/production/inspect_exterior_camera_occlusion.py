"""Actual saved-camera first-hit/volume diagnosis; no guessed inspection or scene save."""
import bpy,sys,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from view_tools import apply_view
f=apply_view('H03');s=bpy.context.scene;bpy.context.view_layer.update();camera=s.camera;origin=camera.matrix_world.translation.copy();directions=[('centre',Vector((0,0,-1)))]+[(str(i),v.normalized())for i,v in enumerate(camera.data.view_frame(scene=s))];hits=[]
for label,d in directions:
 direction=camera.matrix_world.to_3x3()@d;hit,position,normal,face,obj,matrix=s.ray_cast(bpy.context.evaluated_depsgraph_get(),origin,direction,distance=1000);row={'ray':label,'hit':hit}
 if hit:
  row.update(object=obj.name,distance_m=(position-origin).length,position=list(position),face=face,building=obj.get('building_id'),floor=obj.get('floor_id'),room=obj.get('room_id'),layer=obj.get('layer'))
  if obj.type=='MESH'and face>=0 and face<len(obj.data.polygons):
   idx=obj.data.polygons[face].material_index;row['material']=obj.data.materials[idx].name if idx<len(obj.data.materials)and obj.data.materials[idx]else None
 hits.append(row)
volumes=[]
for mat in bpy.data.materials:
 if mat.use_nodes and any(n.type in ['VOLUME_PRINCIPLED','VOLUME_ABSORPTION','VOLUME_SCATTER']for n in mat.node_tree.nodes):volumes.append(mat.name)
r={'actual_opened_native_sha256':file_sha256(bpy.data.filepath),'camera_position':list(origin),'actual_camera_matrix':[[float(x)for x in row]for row in camera.matrix_world],'preset':f,'actual_primary_ray_hits':hits,'actual_volume_materials':volumes,'stage':'Actual source camera occlusion/volume diagnosis, not a visual acceptance or source mutation'};(R/'evidence/production/R14-H03-actual-camera-ray-diagnosis.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_STREET_CAMERA_OCCLUSION_DIAGNOSIS',json.dumps(r),flush=True)
