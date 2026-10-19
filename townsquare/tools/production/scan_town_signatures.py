"""Explicit non-crowd conservation checks, separate from whole-scene historical signature."""
import bpy,hashlib,array,json

def architecture_signature():
 bpy.context.view_layer.update();h=hashlib.sha256()
 for o in sorted(bpy.context.scene.objects,key=lambda x:x.name):
  if o.type!='MESH'or o.name.startswith('CROWD_'):continue
  h.update(o.name.encode());h.update(repr(tuple(tuple(r)for r in o.matrix_world)).encode())
  for seq,field,k,typ in [(o.data.vertices,'co',3,'f'),(o.data.loops,'vertex_index',1,'i'),(o.data.polygons,'material_index',1,'i')]:
   a=array.array(typ,[0])*(len(seq)*k);seq.foreach_get(field,a);h.update(a.tobytes())
  for uv in o.data.uv_layers:
   a=array.array('f',[0])*(len(uv.data)*2);uv.data.foreach_get('uv',a);h.update(a.tobytes())
 return h.hexdigest()

def architectural_material_photo_signature():
 materials={m.name:m for o in bpy.context.scene.objects if not o.name.startswith('CROWD_')and hasattr(o.data,'materials')for m in o.data.materials if m};rows=[]
 for name,mat in sorted(materials.items()):
  nodes=[];links=[]
  if mat.use_nodes:
   for node in sorted(mat.node_tree.nodes,key=lambda n:n.name):
    values=[]
    for socket in node.inputs:
     if not hasattr(socket,'default_value'):continue
     v=socket.default_value
     if isinstance(v,(str,int,float,bool)):v=v
     else:
      try:v=list(v)
      except TypeError:v=str(v)
     values.append([socket.name,v])
    image=getattr(node,'image',None);photo=hashlib.sha256(image.packed_file.data).hexdigest()if image and image.packed_file else None;nodes.append([node.name,node.bl_idname,values,photo])
   links=sorted([l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier]for l in mat.node_tree.links)
  rows.append([name,list(mat.diffuse_color),mat.use_nodes,nodes,links])
 return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
