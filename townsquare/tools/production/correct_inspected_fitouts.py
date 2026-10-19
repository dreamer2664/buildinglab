"""Original, actual corrections from26individual draft-plan opens.
Fixes recovered cafe/hotel/read-lounge issues and adds use-specific staff/atelier geometry.
Not an acceptance claim: save, fresh reopen, render and individually inspect afterwards.
"""
import bpy,json,math
import numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
import model_lib as g
import furniture as f
from fitout_transforms import local_vertices,material_bounds,edit_region

def apply(root):
 R=Path(root);programme=json.loads((R/'design/programme.json').read_text());plans=json.loads((R/'evidence/production/R11-plan-annotation-source.json').read_text())['plans'];start=set(bpy.context.scene.objects);report=[]
 keys=['Oak','Walnut','Steel','Porcelain','Black','Teal','OliveFabric','Glass','Terracotta','Leaf','Paper','Linen','Upholstery','Bronze','Soil','Terrazzo','Tile','Glow'];base={k:bpy.data.materials[k]for k in keys};g.M=dict(base)
 def frame(fid):
  b=next(b for b in programme['buildings']if any(x['id']==fid for x in b['floors']));floor=next(x for x in b['floors']if x['id']==fid);return b,floor
 def bounds(fid,room):
  b,floor=frame(fid);q=next(r for r in plans[fid+'_plan']['rooms']if r['room_id']==fid+'_'+room)['world_bounds'];c,s=math.cos(math.radians(b['rotation_deg'])),math.sin(math.radians(b['rotation_deg']));cx,cy=b['centre_xy_m'];pts=[((x-cx)*c+(y-cy)*s,-(x-cx)*s+(y-cy)*c)for x in [q[0][0],q[1][0]]for y in [q[0][1],q[1][1]]];return min(x for x,y in pts),min(y for x,y in pts),max(x for x,y in pts),max(y for x,y in pts)
 def scope(fid,room):
  b,floor=frame(fid);return g.scope(c=bpy.data.collections[fid],origin=(*b['centre_xy_m'],floor['datum_m']),angle=math.radians(b['rotation_deg']),building_id=b['id'],floor_id=fid,room_id=fid+'_'+room,layer='furniture',stage='R12_ACTUAL_INSPECTION_CORRECTION')
 def furniture(fid,room):return next(o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('room_id')==fid+'_'+room and o.get('layer')=='furniture')
 def clear(fid,room):
  obs=[o for o in bpy.context.scene.objects if o.get('room_id')==fid+'_'+room and o.get('layer')=='furniture']
  for o in obs:bpy.data.objects.remove(o,do_unlink=True)
  return len(obs)
 # Derive ACTUAL existing cafe table centres from broad horizontal oak tabletop faces.
 fid='B03_L01';b,fl=frame(fid);o=furniture(fid,'SALES');raw,a,*_=local_vertices(o,b,fl['datum_m']);centres=set()
 for p in o.data.polygons:
  m=o.data.materials[p.material_index]
  if not m or not m.name.startswith('Oak'):continue
  v=a[list(p.vertices)];lo,hi=v.min(axis=0),v.max(axis=0)
  if hi[2]-lo[2]<.002 and .70<lo[2]<.86 and hi[0]-lo[0]>.65 and hi[1]-lo[1]>.45:centres.add((round((lo[0]+hi[0])/2,2),round((lo[1]+hi[1])/2,2)))
 xs=sorted({x for x,y in centres});assert len(xs)==3,('Actual cafe column expectation failed, no guessed edit',sorted(centres));print('ACTUAL_CAFE_ORIGINAL_TABLE_CENTRES',sorted(centres),flush=True)
 for old,new in zip(xs,[-6.8,-2.3,2.2]):report.append(edit_region(o,b,0,(old-1.3,-6,-.1),(old+1.3,-1.4,1.1),delta=(new-old,0,0),tag='Original_cafe_complete_seating_column_away_from_bar'))
 extra=bpy.data.objects['B03_L01__R3_ORIGINAL_FURNITURE']
 for old,new in [(1.1,-4.55),(4.0,-.05)]:report.append(edit_region(extra,b,0,(old-.61,-5.7,-.1),(old+.61,-.65,1.0),delta=(new-old,0,0),tag='Additional_cafe_two_seat_columns_into_actual_intercolumn_aisles'))
 # Existing reading sofa was directly below its hall doorway; move SOFA only, not wall books/rug.
 fid='B03_L02';b,fl=frame(fid);o=furniture(fid,'FRONT_A');lo,hi=material_bounds(o,b,fl['datum_m'],'sofa_02');report.append(edit_region(o,b,fl['datum_m'],lo-.002,hi+.002,delta=(0,-1.05,0),tag='Reading_sofa_clear_of_hall_entry'))
 # Existing left hotel bedroom bed group is too close to actual hall entry.
 fid='B07_L02';b,fl=frame(fid);o=furniture(fid,'SUITE_-1_SLEEP');report.append(edit_region(o,b,fl['datum_m'],(-6.1,-2.55,-.05),(-2.65,1.30,1.7),delta=(0,-1.0,0),tag='Hotel_left_bed_rug_nightstands_clear_of_hall_entry'))
 # L03 was visually a duplicate of L02 despite different numeric hashes. Real twin/family refit.
 fid='B07_L03'
 for key,color in [('OliveFabric','476579'),('Linen','E5DAC3'),('Teal','466579')]:
  m=base[key].copy();m.name='R12/HOTEL_FAMILY/'+key;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
  for link in list(bs.inputs['Base Color'].links):m.node_tree.links.remove(link)
  bs.inputs['Base Color'].default_value=g.linear(color);g.M[key]=m
 for room in ['SUITE_-1_SLEEP','SUITE_1_SLEEP']:
  removed=clear(fid,room);x0,y0,x1,y1=bounds(fid,room);mx,my=(x0+x1)/2,(y0+y1)/2
  with scope(fid,room):
   if room=='SUITE_-1_SLEEP':
    for yy in [y0+1.25,y1-1.25]:f.bed(fid+'_TWIN',x0+1.20,yy,width=1.05,angle=math.pi/2)
    f.wardrobe(fid+'_FAMILY_WARDROBE',x1-1.4,y0+.36,width=2.0)
   else:
    f.bed(fid+'_QUEEN',mx,y0+1.35,width=1.85,angle=math.pi);f.wardrobe(fid+'_QUEEN_WARDROBE',x1-.35,my,width=2.0,angle=-math.pi/2)
    g.box(fid+'_LUGGAGE_BENCH',(x0+.6,y0+1.6,.45),(.6,1.3,.15),'Oak',.025)
    for yy in [y0+1.1,y0+2.1]:g.rod(fid+'_BENCH_LEG',(x0+.4,yy,.02),(x0+.4,yy,.4),.03,'Steel');g.rod(fid+'_BENCH_LEG',(x0+.8,yy,.02),(x0+.8,yy,.4),.03,'Steel')
   f.table(fid+'_GUEST_WORK_DESK',x1-1.45,y1-.55,width=1.9,depth=.7);f.chair(fid+'_GUEST_DESK_SEAT',x1-1.45,y1-1.35,math.pi);g.box(fid+'_GUEST_NOTEBOOK',(x1-1.65,y1-.57,.805),(.30,.22,.02),'Paper',.005);f.plant(fid+'_GUEST_PLANT',x1-.5 if room=='SUITE_-1_SLEEP'else x0+.5,my if room=='SUITE_-1_SLEEP'else y1-.5,size=.7)
  report.append({'floor':fid,'room':room,'old_furniture_batches_actually_removed':removed,'actual_replacement':'Two side-wall twin beds/shared bedside lamp/luggage wardrobe OR south-facing queen/luggage bench/side-wall wardrobe; each with work desk, seat, guest notebook and plant. Real fit-out difference; hall/salon door approaches to be individually checked.'})
 g.M=dict(base)
 card=base['Paper'].copy();card.name='R12_ORIGINAL_CARDBOARD';bs=next(n for n in card.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
 for link in list(bs.inputs['Base Color'].links):card.node_tree.links.remove(link)
 bs.inputs['Base Color'].default_value=g.linear('B58A61');bs.inputs['Roughness'].default_value=.88;g.M['Cardboard']=card
 # Original staff stock floor was minimally furnished. Add real carton racking and team workspace.
 fid='B01_L02';room='WAREHOUSE';x0,y0,x1,y1=bounds(fid,room);mx,my=(x0+x1)/2,(y0+y1)/2
 with scope(fid,room):
  for xx in [x0+2.0,x1-2.0]:
   yy=my-.6
   for dx in [-.32,.32]:
    for dy in [-1.5,1.5]:g.rod(fid+'_STOCK_UPRIGHT',(xx+dx,yy+dy,.016),(xx+dx,yy+dy,2.25),.028,'Steel')
   for zz in [.24,.94,1.64]:
    g.box(fid+'_STOCK_SHELF',(xx,yy,zz),(.72,3.1,.045),'Steel',.012)
    for j in range(5):
     cy=yy-1.2+j*.6;g.box(fid+'_REAL_PACKED_CARTON',(xx,cy,zz+.2475),(.54,.49,.45),'Cardboard',.018);g.box(fid+'_CARTON_TAPE',(xx,cy,zz+.474),(.055,.49,.003),'Paper',.001);g.box(fid+'_CARTON_SHIPPING_LABEL',(xx-.273,cy,zz+.26),(.004,.27,.15),'Paper',.001)
     for k in range(11):g.box(fid+'_ORIGINAL_CARTON_BARCODE',(xx-.276,cy-.10+k*.018,zz+.25),(.002,.004+(k%3)*.001,.08),'Black',0)
 room='PURCHASING';x0,y0,x1,y1=bounds(fid,room);tx,ty=x0+1.6,y0+1.8
 with scope(fid,room):
  f.table(fid+'_TEAM_TABLE',tx,ty,width=1.6,depth=.85)
  for dx in [-.48,.48]:f.chair(fid+'_TEAM_SEAT',tx+dx,ty+.8,0);f.chair(fid+'_TEAM_SEAT',tx+dx,ty-.8,math.pi)
  for j in range(3):g.box(fid+'_PURCHASE_ORDERS',(tx-.4+j*.35,ty,.802),(.27,.35,.014),'Paper',.003)
  g.box(fid+'_TEAM_WHITEBOARD_FRAME',(x0+.06,ty,1.55),(.06,1.9,1.1),'Steel',.015);g.box(fid+'_TEAM_WHITEBOARD',(x0+.095,ty,1.55),(.015,1.8,1.0),'Porcelain',.006)
  for j in range(5):g.box(fid+'_ORIGINAL_DELIVERY_SCHEDULE',(x0+.106,ty-.48+j*.19,1.62),(.004,.09,.45-j*.05),'Teal',.002)
 report.append({'floor':fid,'actual_addition':'Two3.1m steel carton racks with30closed taped/shipping-labelled cartons and original geometric barcodes; staff four-seat team table/purchase orders/physical wall schedule board. Door-side zones reserved.'})
 # Tailor upper atelier: real sewing station and a separate pattern/cutting workstation.
 fid='B06_L02';room='FRONT_A';x0,y0,x1,y1=bounds(fid,room);tx,ty=x0+1.35,y0+1.8
 with scope(fid,room):
  f.table(fid+'_SEWING_WORKBENCH',tx,ty,width=1.65,depth=.75,height=.80);f.chair(fid+'_SEWING_SEAT',tx,ty-.85,math.pi)
  g.box(fid+'_SEWING_MACHINE_BASE',(tx,ty,.86),(.60,.30,.05),'Porcelain',.025);g.box(fid+'_MACHINE_COLUMN',(tx+.22,ty+.03,1.05),(.14,.20,.38),'Porcelain',.06);g.box(fid+'_MACHINE_CURVED_ARM',(tx+.02,ty+.03,1.23),(.48,.20,.14),'Porcelain',.055);g.rod(fid+'_MACHINE_NEEDLE',(tx-.17,ty,1.17),(tx-.17,ty,.891),.003,'Steel',8);g.box(fid+'_PRESSER_FOOT',(tx-.17,ty,.895),(.07,.06,.015),'Steel',.006);g.torus(fid+'_MACHINE_HANDWHEEL',(tx+.31,ty+.03,1.17),.07,.015,'Black','X');g.cylinder(fid+'_THREAD_SPOOL',(tx+.15,ty+.02,1.35),.035,.10,'Linen',20);g.box(fid+'_STITCHED_FABRIC',(tx-.13,ty-.04,.890),(.4,.30,.009),'OliveFabric',.005)
 room='FRONT_B';x0,y0,x1,y1=bounds(fid,room);tx,ty=x0+1.35,y0+1.8
 with scope(fid,room):
  f.table(fid+'_PATTERN_CUTTING_TABLE',tx,ty,width=1.85,depth=.95,height=.84);g.box(fid+'_CUTTING_MAT',(tx,ty,.877),(1.55,.77,.004),'Teal',.004)
  for j in range(15):g.box(fid+'_MAT_GRID_X',(tx-.7+j*.1,ty,.880),(.002,.70,.001),'Linen',0)
  for j in range(7):g.box(fid+'_MAT_GRID_Y',(tx,ty-.3+j*.1,.880),(1.45,.002,.001),'Linen',0)
  g.box(fid+'_GARMENT_PATTERN',(tx-.25,ty,.884),(.45,.6,.005),'Paper',.003);g.box(fid+'_MEASURING_RULE',(tx+.2,ty+.25,.886),(.75,.025,.008),'Steel',.003)
  for j in range(25):g.box(fid+'_RULE_MARK',(tx-.15+j*.028,ty+.25,.891),(.002,.018,.001),'Black',0)
  for dx in [-.06,.06]:g.torus(fid+'_SCISSOR_HANDLE',(tx+.45+dx,ty-.18,.9),.05,.009,'Black')
  g.rod(fid+'_SCISSOR_BLADE',(tx+.45,ty-.14,.895),(tx+.34,ty+.10,.895),.008,'Steel',6);g.rod(fid+'_SCISSOR_BLADE',(tx+.45,ty-.14,.897),(tx+.58,ty+.1,.897),.008,'Steel',6)
 report.append({'floor':fid,'actual_addition':'Separate usable sewing bench with real3Dmachine chassis/curved arm/needle/presser/handwheel/spool/fabric and pattern table with real cutting-mat grid/paper/rule/ticks/scissor handles/blades. Not name-only atelier.'})
 for o in bpy.context.scene.objects:
  if o in start or o.type!='MESH'or o.data.uv_layers:continue
  uv=o.data.uv_layers.new(name='UVMap')
  for p in o.data.polygons:
   axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[1,2]if axis==0 else[0,2]if axis==1 else[0,1]
   for li in p.loop_indices:v=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(v[axes[0]]*.8,v[axes[1]]*.8)
 bpy.context.view_layer.update();return report
