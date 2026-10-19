"""Independent original OBJ vertex/UV loop import check before any cleanup/material changes."""
import bpy,json,os,array
from pathlib import Path
R=Path(__file__).resolve().parents[2];pose=os.environ.get('SQUARE_SCAN_POSE','HSR0040-Body-012');r=json.loads((R/'evidence/production'/('R12-actual-scan-intake-'+pose+'.json')).read_text());path=R/next(x['path']for x in r['members']if x['member'].endswith('.obj'));vs=[];uvs=[];faces=[];source_uv=[]
for line in path.open():
 a=line.split()
 if not a:continue
 if a[0]=='v':vs.extend(map(float,a[1:4]))
 elif a[0]=='vt':uvs.append(tuple(map(float,a[1:3])))
 elif a[0]=='f':
  for i in a[1:]:
   bits=i.split('/');faces.append(int(bits[0])-1);source_uv.extend(uvs[int(bits[1])-1])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.wm.obj_import(filepath=str(path),forward_axis='Y',up_axis='Z',use_split_objects=False,use_split_groups=False,validate_meshes=True);mesh=next(o.data for o in bpy.context.scene.objects if o.type=='MESH');positions=array.array('f',[0])*(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',positions);loops=array.array('i',[0])*len(mesh.loops);mesh.loops.foreach_get('vertex_index',loops);native_uv=array.array('f',[0])*(len(mesh.loops)*2);mesh.uv_layers.active.data.foreach_get('uv',native_uv);assert len(positions)==len(vs)and list(loops)==faces;pe=max(abs(a-b)for a,b in zip(positions,vs));ue=max(abs(a-b)for a,b in zip(native_uv,source_uv));assert pe<1e-6 and ue<1e-6;out={'pose':pose,'original_OBJ_vertex_order_and_every_face_corner_index_match':True,'actual_original_vertex_coordinate_max_error_m':pe,'actual_original_UV_every_loop_max_error':ue,'actual_vertices':len(mesh.vertices),'actual_face_corners':len(mesh.loops),'result':'ORIGINAL_OBJ_GEOMETRY_UV_IMPORT_PASS; not a source-capture quality approval'};(R/'evidence/production'/('R12-original-OBJ-UV-import-'+pose+'.json')).write_text(json.dumps(out,indent=2)+'\n');print('ACTUAL_ORIGINAL_OBJ_VERTEX_AND_EVERY_LOOP_UV_MATCH',out)
