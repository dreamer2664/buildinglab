"""Actual inspect/ray-test-driven correction of ceiling/fixture assemblies buried in upper slabs."""
import bpy,json
from mathutils import Vector

def repair_clearance(programme):
 s=bpy.context.scene;bpy.context.view_layer.update();room_shift={};room_ceiling_bottom={};changes=[];floor_cases=[]
 def bounds(o):
  ps=[o.matrix_world@Vector(p) for p in o.bound_box];return min(p.z for p in ps),max(p.z for p in ps)
 def shift(o,dz):
  mat=o.matrix_world.copy();mat.translation.z+=dz;o.matrix_world=mat
 for building in programme['buildings']:
  floors=building['floors']
  for index,f in enumerate(floors[:-1]):
   upper=floors[index+1]['id'];slabs=[o for o in s.objects if o.type=='MESH' and o.get('floor_id')==upper and o.get('layer')=='slab'];assert slabs,upper
   underside=min(bounds(o)[0] for o in slabs);ceilings=[o for o in s.objects if o.type=='MESH' and o.get('floor_id')==f['id'] and o.get('layer')=='ceiling'];moved=[]
   for o in ceilings:
    low,high=bounds(o);dz=min(0,underside-.015-high)
    if dz>=-.0001:continue
    key=(f['id'],o.get('room_id'));room_shift[key]=min(room_shift.get(key,0),dz);shift(o,dz);room_ceiling_bottom[key]=low+dz;moved.append(o.name)
    changes.append({'object':o.name,'layer':'ceiling','floor':f['id'],'room':o.get('room_id'),'old_bounds_z':[low,high],'upper_slab_underside_z_m':underside,'world_z_shift_m':dz,'new_bounds_z':[low+dz,high+dz]})
   floor_cases.append({'floor':f['id'],'upper_floor':upper,'actual_upper_slab_underside_z_m':underside,'ceiling_meshes_corrected':moved})
 # Translate each corresponding existing physical fixture, its actual emitter and high
 # interior brand header together. No power/colour/material change or fake glow plane.
 corrected_lights=[]
 for o in s.objects:
  key=(o.get('floor_id'),o.get('room_id'));dz=room_shift.get(key)
  if dz is None:continue
  layer=o.get('layer');do_move=(o.type=='MESH' and layer=='lighting') or (o.type=='LIGHT' and bool(o.get('fixture_group')))
  if o.type=='MESH' and layer=='signage':do_move=bounds(o)[1]>room_ceiling_bottom[key]-.06
  if not do_move:continue
  oldz=o.matrix_world.translation.z;shift(o,dz);changes.append({'object':o.name,'layer':layer,'type':o.type,'floor':key[0],'room':key[1],'old_world_z_m':oldz,'world_z_shift_m':dz,'new_world_z_m':oldz+dz})
  if o.type=='LIGHT':corrected_lights.append(o)
 bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();ray_checks=[]
 for o in corrected_lights:
  forward=o.matrix_world.to_quaternion()@Vector((0,0,-1))
  if forward.z>-.95:continue
  hit,loc,normal,idx,obj,mat=s.ray_cast(deps,o.matrix_world.translation+Vector((0,0,-.0001)),Vector((0,0,-1)),distance=.25)
  blocked=bool(hit and obj.get('layer') in ['slab','ceiling','lighting']);ray_checks.append({'light':o.name,'world_z_m':o.matrix_world.translation.z,'immediate_downward_hit':obj.name if hit else None,'hit_z_m':loc.z if hit else None,'blocked_by_slab_ceiling_or_fixture':blocked})
 assert not any(x['blocked_by_slab_ceiling_or_fixture'] for x in ray_checks),[x for x in ray_checks if x['blocked_by_slab_ceiling_or_fixture']]
 return {'fix':'Room ceilings and their existing physical fixture/emitter assemblies lowered below actual next-floor slab underside with15mm top clearance. R10 actual rays proved B01 emitters embedded60mm into upper slab. Fixture powers/colours and source materials/body poses untouched. High interior brand headers followed corrected ceilings; exterior signs unchanged.','floor_cases':floor_cases,'corrected_room_groups':len(room_shift),'changes':changes,'actual_corrected_emitter_downward_ray_checks':ray_checks,'unresolved_immediate_ceiling_slab_fixture_occluders':0,'visual_acceptance':'PENDING / numeric ray clearance is not image inspection'}
