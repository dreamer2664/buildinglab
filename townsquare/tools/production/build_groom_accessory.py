"""Create editable UNPROMOTED hair-only native accessory and explicit portable tube-mesh LOD.
Fresh Blender per variant; exact full-town source remains unchanged. Not a realism approval.
"""
import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
from prototype_scalp_groom import apply
pid=os.environ['SQUARE_GROOM_PID'];b=json.loads((R/'evidence/production/R12-wall-corrected-interiors.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];actors=sorted((o for o in bpy.context.scene.objects if o.type=='MESH'and o.name.endswith('_'+pid)),key=lambda o:o.name);assert actors;actor=actors[0];original_actor=actor.name
for o in list(bpy.context.scene.objects):
 if o!=actor:bpy.data.objects.remove(o,do_unlink=True)
actor.matrix_world=Matrix.Identity(4);rows=apply();assert len(rows)==1,('Expected original braid01 source',pid,[m.name for m in actor.data.materials if m]);hair=next(o for o in bpy.context.scene.objects if o.type=='CURVES');cap=next(o for o in bpy.context.scene.objects if o!=actor and o.type=='MESH')
# Vertex colour+alpha is a portable representation of the same6mm root fade, not a painted texture.
me=cap.data;col=me.color_attributes.new(name='GROOM_ROOT_RGBA',type='FLOAT_COLOR',domain='POINT');fade=me.attributes['groom_edge_fade']
for i,c in enumerate(col.data):c.color=(.006,.0028,.0013,fade.data[i].value)
mat=me.materials[0];bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');vc=mat.node_tree.nodes.new('ShaderNodeVertexColor');vc.layer_name=col.name
for socket in ['Base Color','Alpha']:
 for link in list(bs.inputs[socket].links):mat.node_tree.links.remove(link)
mat.node_tree.links.new(vc.outputs['Color'],bs.inputs['Base Color']);mat.node_tree.links.new(vc.outputs['Alpha'],bs.inputs['Alpha'])
#6k sparse physical tube strands; deliberately separate PBR approximation, never the100k native hair BSDF.
verts=[];faces=[];target=6000;curves=hair.data;step=max(1,len(curves.curves)//target);chosen=list(range(0,len(curves.curves),step))[:target]
for ci in chosen:
 points=curves.curves[ci].points;path=[p.position.copy()for p in points];base=len(verts)
 for j,p in enumerate(path):
  tangent=(path[min(len(path)-1,j+1)]-path[max(0,j-1)]).normalized();ref=Vector((1,0,0))if abs(tangent.x)<.95 else Vector((0,1,0));side=tangent.cross(ref).normalized();up=tangent.cross(side).normalized();radius=max(.000003,points[j].radius*2.5)
  for k in range(3):v=p+(side*math.cos(k*math.tau/3)+up*math.sin(k*math.tau/3))*radius;verts.append(tuple(v))
 for j in range(len(path)-1):
  for k in range(3):a=base+j*3+k;bb=base+j*3+(k+1)%3;c=base+(j+1)*3+(k+1)%3;d=base+(j+1)*3+k;faces.extend([(a,bb,c),(a,c,d)])
me=bpy.data.meshes.new('PORTABLE / '+pid+' / 6000 strand tube LOD');me.from_pydata(verts,[],faces);me.update()
for p in me.polygons:p.use_smooth=True
mat=bpy.data.materials.new('PORTABLE / brown fibre PBR approximation');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.014,.006,.0025,1);bs.inputs['Roughness'].default_value=.5;bs.inputs['Anisotropic'].default_value=.6;me.materials.append(mat);lod=bpy.data.objects.new('PORTABLE_HAIR_LOD|'+pid,me);bpy.context.scene.collection.objects.link(lod);lod['portable_hair_lod']=True;lod.hide_render=True
for o in [hair,cap,lod]:o['person_id']=actor['person_id'];o['variant_id']=pid;o['layer']='people_hair';o['scope']='UNPROMOTED physical groom accessory / technical rebuild study';o.matrix_world=Matrix.Identity(4)
hair.name='PEOPLE_HAIR_CURVES|'+pid;cap.name='PEOPLE_HAIR_ROOTS|'+pid
# Sparse UV correspondences allow actual measured alignment to the separately preserved editable rig.
skin={i for i,m in enumerate(actor.data.materials)if m and(m.name.endswith('.body')or'.body.'in m.name)};uv=actor.data.uv_layers.active;sample={};top=max(v.co.z for v in actor.data.vertices)
for p in actor.data.polygons:
 if p.material_index not in skin:continue
 for li in p.loop_indices:
  v=actor.data.vertices[actor.data.loops[li].vertex_index];t=uv.data[li].uv
  if v.co.z>top-.25:sample.setdefault((round(t.x,7),round(t.y,7)),tuple(v.co))
keys=sorted(sample);keys=keys[::max(1,len(keys)//1600)];out=R/'.cache/groom-accessories';out.mkdir(parents=True,exist_ok=True);path=out/(pid+'-physical-groom-UNPROMOTED.blend');report={'person_id':pid,'source_native_sha256':b['native_sha256'],'source_actor':original_actor,'generator_sha256':file_sha256(R/'tools/production/prototype_scalp_groom.py'),'actual_groom_generation':rows,'native_curves':len(curves.curves),'portable_lod_strands':len(chosen),'portable_lod_triangles':len(faces),'portable_lod_root_radius_scale':2.5,'head_skin_uv_correspondences':[{'uv':k,'co':sample[k]}for k in keys],'scope':'Saved UNPROMOTED editable hair-only accessory, body-local metres; real100kcurves and separate6ktube PBR LOD. Original full town untouched; no acceptance/adoption/final human claim.'};t=bpy.data.texts.new('GROOM_SOURCE_AND_LIMITATIONS.json');t.write(json.dumps(report,indent=2));t.use_fake_user=True;bpy.data.libraries.write(str(path),{hair,cap,lod,t},fake_user=True,compress=True);report.update(native=str(path.relative_to(R)),native_sha256=file_sha256(path),native_bytes=path.stat().st_size);(R/'evidence/production'/('R12-groom-accessory-'+pid+'.json')).write_text(json.dumps(report,indent=2)+'\n');print('EDITABLE_GROOM_ACCESSORY_SAVED',pid,report['native_bytes'],report['native_sha256'],flush=True)
