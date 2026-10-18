import bpy,hashlib,array

def geometry_uv_pose_material_signature():
 bpy.context.view_layer.update();h=hashlib.sha256()
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  if o.type!='MESH':continue
  h.update(o.name.encode());h.update(str(tuple(tuple(row) for row in o.matrix_world)).encode())
  for seq,field,k,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
   a=array.array(typ,[0])*(len(seq)*k);seq.foreach_get(field,a);h.update(a.tobytes())
  for uv in o.data.uv_layers:
   a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
 return h.hexdigest()

def file_sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 return h.hexdigest()

def hair_geometry_signature():
 """Actual native curve point/radius/partition/world poses plus scalp vertex-colour fade.
 Separate from historical mesh-only signature; does not silently invalidate frozenR11 receipts.
 """
 bpy.context.view_layer.update();h=hashlib.sha256();cache={}
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  if o.type=='CURVES':
   h.update(o.name.encode());h.update(repr(tuple(tuple(r)for r in o.matrix_world)).encode());d=o.data;key=d.as_pointer()
   if key not in cache:
    z=hashlib.sha256()
    for name,field,count,typ in [('position','vector',3,'f'),('radius','value',1,'f')]:
     a=array.array(typ,[0])*(len(d.attributes[name].data)*count);d.attributes[name].data.foreach_get(field,a);z.update(a.tobytes())
    for field in ['first_point_index','points_length']:
     a=array.array('i',[0])*len(d.curves);d.curves.foreach_get(field,a);z.update(a.tobytes())
    z.update(repr([m.name if m else None for m in d.materials]).encode());cache[key]=z.digest()
   h.update(cache[key])
  elif o.type=='MESH'and o.get('layer')=='people_hair':
   h.update(o.name.encode())
   for name,field,n in [('groom_edge_fade','value',1),('GROOM_ROOT_RGBA','color',4)]:
    if name not in o.data.attributes:continue
    a=array.array('f',[0])*(len(o.data.attributes[name].data)*n);o.data.attributes[name].data.foreach_get(field,a);h.update(name.encode());h.update(a.tobytes())
 return h.hexdigest()
