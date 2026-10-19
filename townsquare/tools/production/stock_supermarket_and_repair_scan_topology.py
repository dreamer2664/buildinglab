"""Original measured supermarket merchandising + exact duplicate-face scan repair.
Additions sit on actual shelf surfaces, not arbitrary room labels/XY positions. Earlier native immutable.
"""
import bpy,json,sys,math,array,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'))
import model_lib as L
from fingerprints import file_sha256,geometry_uv_pose_material_signature
from scan_town_signatures import architecture_signature,architectural_material_photo_signature
from scan_mesh_topology_repair import repair_duplicate_faces
b=json.loads((R/'evidence/production/R13-crafted-exteriors.json').read_text());assert file_sha256(bpy.data.filepath)==b['native_sha256'];s=bpy.context.scene;anchors=json.loads((R/'evidence/production/R13-supermarket-stock-anchors.json').read_text());assert anchors['source_native_sha256']==b['native_sha256'];labels=json.loads((R/'assets/branding/products/manifest.json').read_text());assert file_sha256(R/labels['atlas'])==labels['atlas_sha256'];before=architecture_signature();materials_before=architectural_material_photo_signature();original_objects=set(s.objects)
# Fix the exact duplicate faces that glTF's own validator was silently removing.
repair=[];seen=set()
for ob in s.objects:
 if ob.type!='MESH'or not ob.name.startswith('CROWD_')or not ob.get('source_pose_id'):continue
 mesh=ob.data
 if mesh.as_pointer()in seen:continue
 seen.add(mesh.as_pointer());proof=repair_duplicate_faces(mesh);proof.update(source_pose=ob['source_pose_id'],mesh=mesh.name);repair.append(proof);print('ACTUAL_SCAN_DUPLICATE_FACE_REPAIR',ob['source_pose_id'],proof['actual_duplicate_faces_removed'],flush=True)
# Original fictional packaging; one packed self-contained atlas, no external font dependency in scene.
image=bpy.data.images.load(str(R/labels['atlas']),check_existing=False);image.name='MARKTGRUEN_PRODUCTS_original_label_atlas_1536';image.colorspace_settings.name='sRGB';image.pack();image.buffers_free();image.filepath='//packed/'+image.name+'.png';labelmat=bpy.data.materials.new('R14 original MARKTGRUEN grocery print');labelmat.use_nodes=True;node=labelmat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;bs=labelmat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.72;labelmat.node_tree.links.new(node.outputs['Color'],bs.inputs['Base Color'])
for args in [('R14 can rim steel','A5ABA4',.3,.82),('R14 carton paper edge','D6D0BD',.8),('R14 bottle glass','455F39',.24,.05,.18),('R14 cap cream','D5D1BA',.54),('R14 pricecard white','DDD7C3',.79)]:L.material(*args)
for row in labels['labels']:L.material('R14 pack hue '+str(row['id']),row['rgb_srgb'],.72)
root=next(c for c in bpy.data.collections if c.name.startswith('B01 ')and not c.name.startswith('B01 /'));collection=L.collection('B01 / R14 original stocked groceries',root,building_id='B01',floor_id='B01_L01',room_id='B01_L01_SALES');template_collection=L.collection('R14 / temporary packaging templates');templates={}
def uv_label(name,vertices,sku,price_only=False):
 row=labels['labels'][sku];x0,y0,x1,y1=row['label_cell_px'];a,bv=x0/1536,1-y1/1536;c,d=x1/1536,1-y0/1536
 if price_only:bv=1-(y0+728)/1536;d=1-(y0+674)/1536
 o=L.obj(name,vertices,[(0,1,2,3)],labelmat);uv=o.data.uv_layers.new(name='OriginalGroceryLabelUV')
 for loop,xy in zip(uv.data,[(a,bv),(c,bv),(c,d),(a,d)]):loop.uv=xy
 return o
for row in labels['labels']:
 sku=row['id'];kind=row['category'];paint='R14 pack hue '+str(sku);previous=set(template_collection.objects)
 with L.scope(c=template_collection,origin=(0,0,0),angle=0,stage='R14_ORIGINAL_GROCERY_TEMPLATE'):
  if kind in ['carton','milk']:
   w,d,h=(.08,.08,.23)if kind=='milk'else(.13,.105,.25);L.box('Actual printed carton body',(0,0,h/2),(w,d,h),paint)
   if kind=='milk':
    vertices=[(-w/2,-d/2,h),(w/2,-d/2,h),(w/2,d/2,h),(-w/2,d/2,h),(-w/2,0,h+.035),(w/2,0,h+.035)];L.place(L.obj('Real folded gable milk-carton top',vertices,[(0,1,5,4),(3,4,5,2),(0,4,3),(1,2,5)],paint),(0,0,0));h+=.035
   uv_label('Original printed package front',[(-w*.46,-d/2-.0008,.025),(w*.46,-d/2-.0008,.025),(w*.46,-d/2-.0008,min(h-.02,.225)),(-w*.46,-d/2-.0008,min(h-.02,.225))],sku)
  else:
   radius=.038 if kind=='can'else.043;h=.115 if kind=='can'else.255
   if kind=='can':profile=[(radius*.92,0),(radius,.004),(radius,.108),(radius*.96,.115)];L.lathe('Actual rolled-rim food tin',(0,0,0),profile,paint,n=16);L.torus('Food tin top rolled rim',(0,0,.112),r=radius,tube=.0022,mat='R14 can rim steel')
   else:
    L.lathe('Actual juice bottle tapered shoulder and neck',(0,0,0),[(radius*.9,0),(radius,.018),(radius,.17),(.022,.205),(.017,.212),(.017,.25)],'R14 bottle glass',n=16);L.cylinder('Bottle screw cap',(0,0,.253),.019,.018,'R14 cap cream',n=12)
   x0,y0,x1,y1=row['label_cell_px'];u0,u1=x0/1536,x1/1536;v0,v1=1-y1/1536,1-y0/1536;verts=[];faces=[];steps=16;z0=.012;z1=.102 if kind=='can'else.165
   for j in range(steps+1):
    t=math.tau*j/steps;verts.extend([(math.sin(t)*(radius+.0008),-math.cos(t)*(radius+.0008),z0),(math.sin(t)*(radius+.0008),-math.cos(t)*(radius+.0008),z1)])
   for j in range(steps):faces.append((2*j,2*j+2,2*j+3,2*j+1))
   band=L.obj('Original printed wrapped food label',verts,faces,labelmat);uv=band.data.uv_layers.new(name='OriginalGroceryLabelUV')
   for j,poly in enumerate(band.data.polygons):
    for li,xy in zip(poly.loop_indices,[(u0+(u1-u0)*j/steps,v0),(u0+(u1-u0)*(j+1)/steps,v0),(u0+(u1-u0)*(j+1)/steps,v1),(u0+(u1-u0)*j/steps,v1)]):uv.data[li].uv=xy
   w=d=radius*2
  bpy.ops.object.select_all(action='DESELECT');parts=[o for o in template_collection.objects if o not in previous]
  for o in parts:o.select_set(True)
  bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.view_layer.objects.active;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.name='R14 original grocery '+row['sku'];templates[sku]={'object':o,'width':w,'depth':d,'height':h,'category':kind}
# Place products directly on each measured shelf rectangle; checkout conveyor is deliberately excluded.
products=[];shelves=[a for a in anchors['actual_measured_shelf_top_faces']if min(a['surface_dimensions_m'])<.56]
for shelf_index,anchor in enumerate(shelves):
 lo,hi=anchor['world_bounds'];longaxis=0 if hi[0]-lo[0]>hi[1]-lo[1]else 1;shortaxis=1-longaxis;length=hi[longaxis]-lo[longaxis];positions=max(1,int((length-.16)/.17));basez=anchor['surface_z_m'];sku=(shelf_index//3+shelf_index%3)%6;source=templates[sku];mesh=source['object'].data
 for row in range(2):
  for j in range(positions):
   if (j+3*row+shelf_index)%17==0:continue
   xyz=[0,0,basez+.001];xyz[longaxis]=lo[longaxis]+.10+(j+.5)*(length-.20)/positions;xyz[shortaxis]=(lo[shortaxis]+hi[shortaxis])/2+(-.11 if row==0 else .11);o=bpy.data.objects.new('R14|'+labels['labels'][sku]['sku']+'|shelf'+str(shelf_index)+'|'+str(row)+'-'+str(j),mesh);collection.objects.link(o);o.location=xyz;o.rotation_euler.z=0 if longaxis==0 else(-math.pi/2 if row==0 else math.pi/2)
   for k,v in {'building_id':'B01','floor_id':'B01_L01','room_id':'B01_L01_SALES','layer':'furniture','stage':'R14_MEASURED_ORIGINAL_GROCERY_STOCK','original_fictional_sku':labels['labels'][sku]['sku'],'source_measured_shelf_index':shelf_index}.items():o[k]=v
   products.append({'object':o,'shelf_index':shelf_index,'anchor':anchor,'sku':sku})
 # Original concept-price tickets are real small cards on the actual shelf lip.
 with L.scope(c=collection,origin=(0,0,0),angle=0,building_id='B01',floor_id='B01_L01',room_id='B01_L01_SALES',layer='furniture',stage='R14_MEASURED_ORIGINAL_GROCERY_STOCK'):
  for j in range(3):
   u=lo[longaxis]+(.18+(length-.36)*j/2);v=lo[shortaxis]-.008;z=basez-.022
   vertices=[(u-.065,v,z-.018),(u+.065,v,z-.018),(u+.065,v,z+.018),(u-.065,v,z+.018)]if longaxis==0 else[(v,u+.065,z-.018),(v,u-.065,z-.018),(v,u-.065,z+.018),(v,u+.065,z+.018)]
   uv_label('Original shelf price ticket',vertices,sku,True)
for template in templates.values():bpy.data.objects.remove(template['object'],do_unlink=True)
bpy.data.collections.remove(template_collection);bpy.context.view_layer.update();stock_audit=[];failures=[]
for row in products:
 o=row['object'];a=row['anchor'];points=[o.matrix_world@Vector(p)for p in o.bound_box];lo=[min(p[k]for p in points)for k in range(3)];hi=[max(p[k]for p in points)for k in range(3)];slo,shi=a['world_bounds'];issues=[]
 for k in [0,1]:
  if lo[k]<slo[k]-.015 or hi[k]>shi[k]+.015:issues.append('Product outside measured shelf XY')
 if abs(lo[2]-(a['surface_z_m']+.001))>.005 or hi[2]>a['surface_z_m']+.34:issues.append('Product not resting at actual shelf height/clear shelf interval')
 audit={'object':o.name,'shelf_index':row['shelf_index'],'sku':labels['labels'][row['sku']]['sku'],'actual_world_bounds':[lo,hi],'issues':issues};stock_audit.append(audit)
 if issues:failures.append(audit)
assert not failures,('Actual merchandising placement failures',failures[:3]);added=[o for o in s.objects if o not in original_objects];membership={o:list(o.users_collection)for o in added}
for o in added:
 for c in list(o.users_collection):c.objects.unlink(o)
after=architecture_signature();materials_after=architectural_material_photo_signature();assert before==after,'Original noncrowd geometry changed';assert materials_before==materials_after,'Original architectural/photo material graphs changed'
for o in added:
 for c in membership[o]:c.objects.link(o)
bpy.context.view_layer.update();s['candidate_revision']='UNPROMOTED / measured original grocery stock, duplicateface-repaired originalUV photographic visitors, crafted exteriors';note=bpy.data.texts.new('R14_STOCK_AND_SCAN_TOPOLOGY_NOTICE.txt');note.write('Original supermarket merchandising placed on measured actual shelf surfaces; original SKU SVG/atlas and raster font notice in project assets. No copied product brand or proxy shelves. Only exact duplicate scan faces removed through actual Mesh.validate, unique triangle geometry exact and every retained textured triangle was in source; all source vertex positions exactly unchanged. Earlier models immutable. This is not final/independent/code/clearance acceptance.\n'+json.dumps(repair,indent=2));note.use_fake_user=True
out=R/'.cache/stocked-town';out.mkdir(exist_ok=True);path=out/'Winterlichtplatz-stocked-and-topology-repaired-UNPROMOTED.blend';signature=geometry_uv_pose_material_signature();bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True);r=dict(b);r.update(stage='NEW original-stock/valid-scan-topology working candidate; actual savedsource/freshreopen/visual/export/final92/independent acceptance pending',native=str(path.relative_to(R)),native_sha256=file_sha256(path),native_bytes=path.stat().st_size,parent_crafted_native_sha256=b['native_sha256'],geometry_uv_pose_material_signature=signature,original_noncrowd_geometry_before=before,original_noncrowd_geometry_after_without_new_stock=after,original_noncrowd_material_photo_before=materials_before,original_noncrowd_material_photo_after_without_new_stock=materials_after,actual_scan_duplicate_face_repairs=repair,actual_new_merchandising_products=len(products),actual_measured_stocked_shelf_surfaces=len(shelves),actual_added_stock_objects=len(added),actual_product_placement_audit=stock_audit,product_placement_failures=failures,original_grocery_label_atlas=labels,images=[],inspection='Actual prior isolatedB01facade source original opened: shelves visibly understocked, new physical merchandise is the correction. Current source reinspection pending.');(R/'evidence/production/R14-stocked-town.json').write_text(json.dumps(r,indent=2)+'\n');print('NEW_MEASURED_STOCKED_TOPOLOGY_VALID_TOWN_SAVED',len(products),'PRODUCTS',len(shelves),'SHELVES',r['native_bytes'],r['native_sha256'],flush=True)
