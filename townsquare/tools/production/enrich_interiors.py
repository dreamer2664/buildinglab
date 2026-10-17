"""Original inspect-driven additions: legible business identity, cafe fit-out and real fixtures.
Reuses the same author's MIT component library, copied into this task namespace unchanged.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
import model_lib as g
import furniture as f

def enrich(root,views):
 R=Path(root);s=bpy.context.scene;start=set(s.objects);source_materials={n:bpy.data.materials.get(n) for n in ['Oak','Walnut','Steel','Porcelain','Black','Teal','OliveFabric','Glass','Terracotta','Leaf','Paper']};g.materials()
 for name,mat in source_materials.items():
  if mat:g.M[name]=mat
 programme=json.loads((R/'design/programme.json').read_text());details=[]
 for b in programme['buildings']:
  fid=b['floors'][0]['id'];view=next(v for v in views if v.get('floor_id')==fid and v['kind']=='interior');room=view['room_id'];bounds=view['room_bounds_world'];cx,cy=b['centre_xy_m'];angle=math.radians(b['rotation_deg']);co,si=math.cos(angle),math.sin(angle)
  def local(p):dx,dy=p[0]-cx,p[1]-cy;return(dx*co+dy*si,-dx*si+dy*co)
  p,q=local(bounds[0]),local(bounds[1]);xmin,xmax=sorted([p[0],q[0]]);ymin,ymax=sorted([p[1],q[1]])
  coll=bpy.data.collections[fid]
  with g.scope(c=coll,origin=(cx,cy,0),angle=angle,building_id=b['id'],floor_id=fid,room_id=room,stage='R3_INSPECT_DRIVEN_DETAIL',layer='signage',cutaway_hide=True):
   x=xmin+(xmax-xmin)*.47;y=ymax-.08;z=3.07;g.box(b['id']+'_INTERIOR_MARK_FRAME',(x,y,z),(3.72,.05,1.06),'Oak',.018)
   image=next(im for im in bpy.data.images if im.name.startswith(b['id']+'.png'));mat=bpy.data.materials.new(b['id']+' / physical interior printed mark');mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=image;mat.node_tree.links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);bsdf.inputs['Roughness'].default_value=.62
   w,h=3.60,1.0;ob=g.obj(b['id']+'_INTERIOR_ORIGINAL_MARK',[(x-w/2,y-.029,z-h/2),(x+w/2,y-.029,z-h/2),(x+w/2,y-.029,z+h/2),(x-w/2,y-.029,z+h/2)],[(0,1,2,3)],mat);g.place(ob,(0,0,0));uv=ob.data.uv_layers.new(name='UVMap')
   for li,xy in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=xy
   details.append({'building':b['id'],'floor':fid,'room':room,'addition':'Physical printed original interior identity panel on real back wall, separately hidden in technical cutaways'})
 # Pilot inspection showed the cafe seating sparse and its coffee workstation underspecified.
 b=next(b for b in programme['buildings'] if b['id']=='B03');coll=bpy.data.collections['B03_L01']
 with g.scope(c=coll,origin=(20,34,0),angle=0,building_id='B03',floor_id='B03_L01',room_id='B03_L01_SALES',layer='furniture',stage='R3_CAFE_FITOUT'):
  for i,(x,y) in enumerate([(1.1,-4.5),(4.0,-4.5),(1.1,-1.7),(4.0,-1.7)]):
   name=f'CAFE_R3_TABLE_{i+1}';f.table(name,x,y,width=.85,depth=.75)
   f.chair(name+'_SEAT_A',x,y+.72,0);f.chair(name+'_SEAT_B',x,y-.72,math.pi)
   for dx,dy in [(-.22,-.16),(.22,.16)]:
    g.cylinder(name+'_SAUCER',(x+dx,y+dy,.807),.09,.012,'Porcelain',24);g.lathe(name+'_CUP',(x+dx,y+dy,.814),[(.042,0),(.045,.075),(.038,.078),(.034,.01)],'Porcelain',24);g.torus(name+'_CUP_HANDLE',(x+dx+.052,y+dy,.852),.024,.006,'Porcelain','Y')
   g.box(name+'_FOLDED_MENU',(x,y+.16,.85),(.16,.025,.1),'Paper',.005)
  # A right-hand coffee bar joins the original rear counter without obstructing the aisle.
  g.box('CAFE_R3_BAR_PLINTH',(5.75,-1.5,.09),(.64,3.8,.15),'Black',.012);g.box('CAFE_R3_BAR_CABINET',(5.75,-1.5,.52),(.66,3.8,.84),'Teal',.025);g.box('CAFE_R3_BAR_STONE_TOP',(5.72,-1.5,.98),(.77,3.9,.065),'Porcelain',.025)
  for y in [-2.8,-1.8,-.8,.2]:g.box('CAFE_R3_CABINET_PANEL',(5.405,y,.52),(.025,.87,.70),'Oak',.012);g.rod('CAFE_R3_PULL',(5.365,y-.16,.74),(5.365,y+.16,.74),.011,'Steel')
  g.box('CAFE_R3_ESPRESSO_CHASSIS',(5.70,-.30,1.25),(.48,.98,.44),'Steel',.04);g.box('CAFE_R3_ESPRESSO_FRONT',(5.445,-.30,1.25),(.025,.87,.29),'Black',.015);g.box('CAFE_R3_DRIP_TRAY',(5.30,-.30,1.06),(.35,.92,.035),'Steel',.01)
  for y in [-.62,-.30,.02]:
   g.rod('CAFE_R3_GROUP_HEAD',(5.42,y,1.28),(5.27,y,1.28),.044,'Steel',18);g.rod('CAFE_R3_PORTAFILTER',(5.28,y,1.25),(5.11,y,1.25),.018,'Black',12);g.lathe('CAFE_R3_ESPRESSO_CUP',(5.26,y,1.08),[(.035,0),(.041,.065),(.035,.067),(.025,.01)],'Porcelain',20)
  for i in range(13):g.rod('CAFE_R3_TRAY_GRILLE',(5.16,-.72+i*.07,1.087),(5.46,-.72+i*.07,1.087),.0025,'Black',6)
  g.rod('CAFE_R3_STEAM_WAND',(5.42,.11,1.29),(5.18,.16,1.17),.008,'Steel',12);g.cylinder('CAFE_R3_GRINDER_BASE',(5.66,-1.4,1.03),.14,.065,'Black',24);g.cylinder('CAFE_R3_GRINDER_BODY',(5.66,-1.4,1.22),.115,.34,'Steel',24);g.lathe('CAFE_R3_BEAN_HOPPER',(5.66,-1.4,1.40),[(.09,0),(.15,.25),(.15,.27),(.11,.27)],'Glass',32)
  for i in range(36):
   a=i*2.4;r=.11*math.sqrt((i%12)/12);g.sphere('CAFE_R3_COFFEE_BEAN',(5.66+math.cos(a)*r,-1.4+math.sin(a)*r,1.48+(i%4)*.035),(.011,.007,.006),'Walnut',8,5)
  for i in range(5):g.lathe('CAFE_R3_STACKED_CUPS',(5.74,-2.3,1.015+i*.032),[(.052,0),(.055,.08),(.048,.082),(.04,.012)],'Porcelain',24)
  f.plant('CAFE_R3_CORNER_PLANT',-8.1,1.0,size=1.1)
 details.append({'building':'B03','floor':'B03_L01','room':'B03_L01_SALES','addition':'Four additional two-seat tables with real ceramic settings; fitted coffee bar with cabinet pulls, three-group espresso machine, tray grille, portafilters, steam wand, transparent bean hopper, beans and stacked cups'})
 # Separate auxiliary backdrop avoids a floating rectangular plinth in aerial renders.
 # It is not part of the portable town bounds and is explicitly omitted from GLB export.
 aux=bpy.data.collections.new('AUXILIARY / snow terrain backdrop');s.collection.children.link(aux)
 ground=next(o for o in s.objects if o.type=='MESH' and o.get('layer')=='ground' and o.get('building_id')=='PUBLIC');snow=next(m for m in ground.data.materials if m and 'Snow' in m.name)
 with g.scope(c=aux,origin=(0,0,0),building_id='AUXILIARY',floor_id='PUBLIC',room_id='BACKGROUND',layer='auxiliary_background',auxiliary_background=True,stage='R3_BACKGROUND'):
  plane=g.obj('AUXILIARY / extended snow, not portable model bounds',[(-250,-250,-.105),(250,-250,-.105),(250,250,-.105),(-250,250,-.105)],[(0,1,2,3)],snow)
 details.append({'addition':'Separate500m snow terrain backdrop prevents visible scene-platform edges in aerial photography; explicitly excluded from GLB bounds'})
 added=[o for o in s.objects if o not in start and not o.get('auxiliary_background')]
 # Box-project UVs on every new component that did not already receive its authored sign UV.
 for ob in added:
  if ob.type!='MESH' or ob.data.uv_layers:continue
  uv=ob.data.uv_layers.new(name='UVMap')
  for poly in ob.data.polygons:
   n=poly.normal;axis=max(range(3),key=lambda i:abs(n[i]));axes=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
   for li in poly.loop_indices:p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*.8,p[axes[1]]*.8)
 # Evaluate bevelled original details into one editable mesh batch per floor/layer.
 deps=bpy.context.evaluated_depsgraph_get();groups={}
 for ob in added:
  if ob.type=='MESH':groups.setdefault((ob.get('floor_id'),ob.get('layer')),[]).append(ob)
 batches=[]
 for (fid,layer),objects in groups.items():
  temp=[]
  for ob in objects:
   ev=ob.evaluated_get(deps);me=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps);o=bpy.data.objects.new('EVAL/'+ob.name,me);bpy.data.collections[fid].objects.link(o);o.matrix_world=ob.matrix_world.copy();temp.append(o)
  bpy.ops.object.select_all(action='DESELECT')
  for ob in temp:ob.select_set(True)
  bpy.context.view_layer.objects.active=temp[0];bpy.ops.object.join();batch=bpy.context.view_layer.objects.active;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);batch.name=f'{fid}__R3_ORIGINAL_{layer.upper()}';props=dict(objects[0].items())
  for k,v in props.items():batch[k]=v
  batch['component_count']=len(objects)
  for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
  batches.append({'floor_id':fid,'layer':layer,'component_count':len(objects),'vertices':len(batch.data.vertices),'faces':len(batch.data.polygons)})
 report={'revision':'R3','reasons':'Actual pilot found sparse cafe fit-out and inadequate interior identity legibility; original authored additions, no picture substitutes','additions':details,'batches':batches,'reuse':'Original same-author MIT furniture/model_lib components; earlier project files not modified','visual_reinspection':'PENDING'}
 (R/'evidence/production/R3-interior-enrichment.json').write_text(json.dumps(report,indent=2)+'\n');return report
