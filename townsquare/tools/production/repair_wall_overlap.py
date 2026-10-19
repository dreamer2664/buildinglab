"""Repair the measured10mm overlap between low/high interior wall faces.
Preserves low-wall cutaway mode and door lintels; no footprint/ceiling/body edits.
"""
import bpy,json
from pathlib import Path
from mathutils import Vector

def apply(root):
 R=Path(root);programme=json.loads((R/'design/programme.json').read_text());rows=[]
 for building in programme['buildings']:
  for floor in building['floors']:
   fid=floor['id'];low=next(o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('floor_id')==fid and o.get('layer')=='wall_low');high=next(o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('floor_id')==fid and o.get('layer')=='wall_high');top=max((low.matrix_world@v.co).z for v in low.data.vertices);bottom=min((high.matrix_world@v.co).z for v in high.data.vertices);overlap=top-bottom;assert .0098<overlap<.0102,(fid,top,bottom,overlap)
   if high.data.users>1:high.data=high.data.copy()
   inverse=high.matrix_world.inverted();moved=0
   for v in high.data.vertices:
    world=high.matrix_world@v.co
    if abs(world.z-bottom)<.00002:world.z=top;v.co=inverse@world;moved+=1
   high.data.update();assert moved>0;rows.append({'floor':fid,'high_wall_object':high.name,'actual_low_wall_top_world_z':top,'actual_high_wall_bottom_before_world_z':bottom,'actual_overlap_removed_m':overlap,'vertices_moved':moved,'actual_high_wall_bottom_after_world_z':min((high.matrix_world@v.co).z for v in high.data.vertices)})
 bpy.context.view_layer.update();return rows
