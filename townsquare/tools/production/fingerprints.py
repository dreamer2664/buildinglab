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
