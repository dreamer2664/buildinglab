"""Actual licensed photogrammetry mesh/UV/photo intake, packed editable native realism slice.
No generated/painted replacement, no original town mutation, no adoption from source preview alone.
"""
import bpy,os,json,sys,hashlib,array
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
from fingerprints import file_sha256
pose=os.environ.get('SQUARE_SCAN_POSE','HSR0015-Body-009');lod=os.environ.get('SQUARE_SCAN_LOD','LOD1');suffix=''if lod=='LOD1'else'-'+lod;src=json.loads((R/'evidence/production'/('R12-actual-scan-intake-'+pose+suffix+'.json')).read_text());obj=next(x for x in src['members']if x['member'].endswith('.obj'));tex=next(x for x in src['members']if x['member'].endswith('_diffuse.png'));assert file_sha256(R/obj['path'])==obj['sha256']and file_sha256(R/tex['path'])==tex['sha256'];bpy.ops.wm.read_factory_settings(use_empty=True)
lo=[float('inf')]*3;hi=[float('-inf')]*3;source_vertices=0;source_faces=0
for line in (R/obj['path']).open():
 if line.startswith('v '):
  co=tuple(map(float,line.split()[1:4]));source_vertices+=1
  for i in range(3):lo[i]=min(lo[i],co[i]);hi[i]=max(hi[i],co[i])
 elif line.startswith('f '):source_faces+=1
assert hi[2]-lo[2]>max(hi[i]-lo[i]for i in range(2))*1.5,'Source must actually be Z-up metre person';centre=((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,lo[2])
bpy.ops.wm.obj_import(filepath=str(R/obj['path']),forward_axis='Y',up_axis='Z',global_scale=1,clamp_size=0,use_split_objects=False,use_split_groups=False,import_vertex_groups=False,validate_meshes=True)
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1;human=meshes[0];me=human.data;bpy.context.view_layer.update();actual=[human.matrix_world@v.co for v in me.vertices];bounds=[[min(v[i]for v in actual)for i in range(3)],[max(v[i]for v in actual)for i in range(3)]];assert max(abs(bounds[j][i]-[lo,hi][j][i])for j in range(2)for i in range(3))<1e-5,'Native axis/scale drift';del actual;assert len(me.vertices)==source_vertices and len(me.polygons)==source_faces;assert len(me.uv_layers)==1
for v in me.vertices:v.co-=Vector(centre)
for f in me.polygons:f.use_smooth=True
me.name='SCAN / actual original '+lod+' / '+pose;human.name='SCAN|'+pose;me.materials.clear();me.update();texture_path=R/tex['path']
if os.environ.get('SQUARE_SCAN_TEXTURE_OVERRIDE'):
 texture_path=R/os.environ['SQUARE_SCAN_TEXTURE_OVERRIDE'];assert texture_path.is_file()
cleanup={}
if os.environ.get('SQUARE_SCAN_CLEAN')=='1':
 import bmesh
 # Explicitly scoped 10mm source-floor slice, not a whole-body smoothing/remesh.
 bm=bmesh.new();bm.from_mesh(me);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();original_positions=[v.co.copy()for v in bm.verts];vl=bm.verts.layers.int.new('source_vertex_index');fl=bm.faces.layers.int.new('source_face_index');ul=bm.loops.layers.uv.active
 for i,v in enumerate(bm.verts):v[vl]=i+1
 for i,f in enumerate(bm.faces):f[fl]=i+1
 def upper_uv_rows():
  import struct
  h=hashlib.sha256();count=0
  for f in bm.faces:
   if min(v.co.z for v in f.verts)<=.04:continue
   h.update(struct.pack('<i',f[fl]));a=array.array('f')
   for loop in f.loops:a.extend(loop[ul].uv)
   h.update(a.tobytes());count+=1
  return count,h.hexdigest()
 upper_before=upper_uv_rows();before=(len(bm.verts),len(bm.faces));cut=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(0,0,.01),plane_no=(0,0,1),clear_inner=True,clear_outer=False);edges=[e for e in cut['geom_cut']if isinstance(e,bmesh.types.BMEdge)and e.is_boundary];caps=bmesh.ops.holes_fill(bm,edges=edges,sides=0)if edges else {'faces':[]}
 upper_after=upper_uv_rows();assert upper_before==upper_after,'Upper-body topology or UV drift';upper_count=0;max_error=0
 for v in bm.verts:
  if v.co.z>.04 and v[vl]and original_positions[v[vl]-1].z>.04:
   error=(v.co-original_positions[v[vl]-1]).length;max_error=max(max_error,error);upper_count+=1
 assert upper_count==sum(v.z>.04 for v in original_positions)and max_error<1e-6,'Unintended upper-body source change'
 for v in bm.verts:v.co.z-=.01
 bm.to_mesh(me);bm.free();me.update();suffix+='-clean';cleanup={'method':'Trim original captured ground/sole region below10mm, close cut edge loops, translate retained scan down10mm for metric ground contact. Original upper-body geometry/UV/photo unretouched.','slice_plane_original_normalized_z_m':.01,'vertices_faces_before':before,'vertices_faces_after':[len(me.vertices),len(me.polygons)],'new_sole_cap_faces':len(caps['faces']),'actual_upper_body_vertex_count_conserved':upper_count,'actual_upper_body_max_vertex_error_m_before_documented_origin_shift':max_error,'actual_upper_body_topology_and_uv_exact_equality':True};assert abs(min(v.co.z for v in me.vertices))<1e-5
mat=bpy.data.materials.new('CC BY4 / Digital Reality Lab / '+pose+' / photo diffuse');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.65;bs.inputs['Specular IOR Level'].default_value=.25;im=bpy.data.images.load(str(texture_path),check_existing=False);im.name='HSRD100_'+pose+'_8k_diffuse';im.colorspace_settings.name='sRGB';im.pack();im.buffers_free();node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im;mat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color']);me.materials.append(mat);human['license']='CC BY4.0';human['source']=src['source_url'];human['author']='Digital Reality Lab';human['source_archive_sha256']=src['source_archive_sha256'];human['license_url']='https://creativecommons.org/licenses/by/4.0/';human['attribution']='HSRD-100 (2025), Digital Reality Lab; original photographic human scan. Unit/origin normalization; any sole-slice and texture resampling are recorded in THIRD_PARTY_ASSET_NOTICE. No endorsement.'
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=False;s.render.resolution_x=1280;s.render.resolution_y=960;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0
world=bpy.data.worlds.new('Neutral actual scan intake studio');world.use_nodes=True;world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.5,.54,.6,1);world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.3;s.world=world
from view_tools import _area
_area('Scan intake key',(-2,-3,4),(0,0,1.2),500,3,(1,.96,.9));_area('Scan intake fill',(3,-1,2),(0,0,1.3),180,3,(.8,.88,1));_area('Scan intake rim',(1,2,3),(0,0,1.3),260,2)
cam=bpy.data.objects.new('STUDY / actual source scan camera',bpy.data.cameras.new('STUDY / scan camera'));s.collection.objects.link(cam);s.camera=cam;cam.location=(2,-4,1.8);target=Vector((0,0,.9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=58;cam.data.clip_start=.02
notice=src['attribution']+'\nActual changes: '+json.dumps(cleanup)+'; texture used '+str(texture_path.relative_to(R))+' SHA256 '+file_sha256(texture_path)+'; source original remains unchanged.\n'+'\nDataset pinned revision '+src['revision']+'; source ZIP SHA256 '+src['source_archive_sha256']+'.\nSource mesh and photo diffuse mapped/packed without image generation, retouching or inferred identity. Source publisher asserts informed collection consent and commercial modification/redistribution under CC BY4.0. No biometric/medical/surveillance use. This is an UNPROMOTED native intake study, not final scene/rig/realism approval.\n';t=bpy.data.texts.new('THIRD_PARTY_ASSET_NOTICE.txt');t.write(notice);t.use_fake_user=True
out=R/'.cache/scan-intake/native';out.mkdir(parents=True,exist_ok=True);path=out/(pose+suffix+'-native-study.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);r={'stage':'Actual imported packed editable licensed scan native; image/render/adoption PENDING','pose_asset_id':pose,'source_dataset_revision':src['revision'],'source_archive_sha256':src['source_archive_sha256'],'cleanup':cleanup,'lod':lod,'texture_actually_used_sha256':file_sha256(texture_path),'texture_actually_used_path':str(texture_path.relative_to(R)),'source_obj_sha256':obj['sha256'],'source_texture_sha256':tex['sha256'],'original_source_bounds':[lo,hi],'actual_origin_translation':centre,'mesh_vertices':len(me.vertices),'mesh_polygons':len(me.polygons),'mesh_uv_layers':len(me.uv_layers),'packed_diffuse_dimensions':list(im.size),'native':str(path.relative_to(R)),'native_sha256':file_sha256(path),'native_bytes':path.stat().st_size,'attribution':notice,'limitations':'Static real3Dphoto scan, not a rigged scan/automatic body animation. Source photo may contain captured shading; single rough dielectric approximate material, not separate scanned BRDF. No person identification inferred or required.'};(R/'evidence/production'/('R12-native-scan-asset-'+pose+suffix+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_LICENSED_SCAN_NATIVE_SAVED',pose,r['mesh_vertices'],r['mesh_polygons'],r['native_bytes'],r['native_sha256'],flush=True)
