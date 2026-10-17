"""Original actual furnishing differentiation, not a programme-label substitute.
Apply only to a new candidate/unsaved study. Keeps floor shells,164rooms, all occupied floors;
replaces secondary-room programmes and bakery kitchen with distinct real geometry.
"""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
import model_lib as g
import furniture as f
from fitout_transforms import material_bounds,edit_region
SCHEMES={'B02_L02':('Baker guest bedroom','8D4137','D1BA8D'),'B04_L02':('Illustrator drawing studio','456783','D7CBB6'),'B05_L02':('Planted conservatory','527B60','DED3B4'),'B08_L02':('Child bedroom and play','558F9B','E0BD73'),'B09_L02':('Maker workroom','5B6972','B57F4E'),'B11_L02':('Cycle and outdoor gear room','46685B','BBC4B2'),'B12_L02':('Writer library and study','774449','D8CDAE')}
def apply(root,only=None):
 start=set(bpy.context.scene.objects);R=Path(root);programme=json.loads((R/'design/programme.json').read_text());plans=json.loads((R/'evidence/production/R11-plan-annotation-source.json').read_text())['plans'];g.M={}
 base=['Oak','Walnut','Steel','Porcelain','Black','Teal','OliveFabric','Glass','Terracotta','Leaf','Paper','Linen','Upholstery','Bronze','Soil','Terrazzo','Tile','Glow']
 for n in base:
  m=bpy.data.materials.get(n);assert m,'Required real native material missing: '+n;g.M[n]=m
 initial=dict(g.M);report=[]
 for fid,(theme,hue,linen)in SCHEMES.items():
  if only and fid not in only:continue
  b=next(b for b in programme['buildings']if any(x['id']==fid for x in b['floors']));floor=next(x for x in b['floors']if x['id']==fid);cx,cy=b['centre_xy_m'];angle=math.radians(b['rotation_deg']);co,si=math.cos(angle),math.sin(angle);rooms={r['room_id']:r for r in plans[fid+'_plan']['rooms']};g.M=dict(initial)
  for key,color in [('OliveFabric',hue),('Upholstery',hue),('Teal',hue),('Linen',linen),('Tile',linen)]:
   m=initial[key].copy();m.name='R12/'+fid+'/'+key;bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   for link in list(bs.inputs['Base Color'].links):m.node_tree.links.remove(link)
   bs.inputs['Base Color'].default_value=g.linear(color);m.diffuse_color=g.linear(color);g.M[key]=m
  def bounds(room):
   q=rooms[fid+'_'+room]['world_bounds'];corners=[(x,y)for x in [q[0][0],q[1][0]]for y in [q[0][1],q[1][1]]];p=[((x-cx)*co+(y-cy)*si,-(x-cx)*si+(y-cy)*co)for x,y in corners];return(min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p))
  def scope(room):return g.scope(c=bpy.data.collections[fid],origin=(cx,cy,floor['datum_m']),angle=angle,building_id=b['id'],floor_id=fid,room_id=fid+'_'+room,layer='furniture',stage='R12_REAL_DIFFERENTIATION')
  def clear(room):
   old=[o for o in list(bpy.context.scene.objects)if o.get('room_id')==fid+'_'+room and o.get('layer')=='furniture']
   for o in old:bpy.data.objects.remove(o,do_unlink=True)
   return len(old)
  # Whole-room180degree turns were REJECTED after actual26plan inspection: doors/armchairs collided.
  # Keep original primary-bed/wardrobe/plant/armchair/door relationships. Only four homes get
  # a scoped sofa+coffee-table quarter-turn in the clear central zone, preserving all UVs.
  transformed=[]
  if b['id']in ['B02','B04','B08','B09']:
   o=next(o for o in bpy.context.scene.objects if o.type=='MESH'and o.get('room_id')==fid+'_LIVING'and o.get('layer')=='furniture');lo,hi=material_bounds(o,b,floor['datum_m'],'sofa_02');sx,sy=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2
   transformed.append(edit_region(o,b,floor['datum_m'],(lo[0]-.03,sy-2.15,-.1),(hi[0]+.03,hi[1]+.05,2.4),angle=-math.pi/2,pivot=(sx,sy),tag='Sofa_and_low_table_only_clear_central_quarter_turn'))
  def turn_new(before,x,y,turn=math.pi/2):
   centre=Vector((cx+co*x-si*y,cy+si*x+co*y,0));matrix=Matrix.Translation(centre)@Matrix.Rotation(turn,4,'Z')@Matrix.Translation(-centre)
   for ob in set(bpy.context.scene.objects)-before:ob.matrix_world=matrix@ob.matrix_world
  def side_case(name,x,y,width=1.45,turn=math.pi/2):
   before=set(bpy.context.scene.objects);f.bookcase(name,x,y,width=width);turn_new(before,x,y,turn)
  deleted=clear('SECOND_ROOM');x0,y0,x1,y1=bounds('SECOND_ROOM');mx,my=(x0+x1)/2,(y0+y1)/2
  with scope('SECOND_ROOM'):
   if b['id']=='B02':
    f.bed(fid+'_SINGLE_GUEST',x0+1.20,my,angle=math.pi/2,width=.95);f.table(fid+'_RECIPE_DESK',x1-.85,y1-.55,width=1.3,depth=.6);f.chair(fid+'_DESK_CHAIR',x1-.85,y1-1.2,math.pi)
    for shelfz in [1.35,1.85]:
     g.box(fid+'_RECIPE_WALL_SHELF',(x1-.85,y1-.17,shelfz),(1.30,.30,.04),'Oak',.01)
     for j in range(6):g.box(fid+'_RECIPE_BOOK',(x1-1.37+j*.17,y1-.17,shelfz+.17),(.065,.22,.30),['Paper','Terracotta','OliveFabric'][j%3],.006)
   elif b['id']=='B04':
    f.table(fid+'_DRAFTING_DESK',mx,y1-.60,width=2.15,depth=.9,height=.83);f.chair(fid+'_DRAFTER_CHAIR',mx,y1-1.40,math.pi);side_case(fid+'_ART_REFERENCE',x0+.23,y0+1.05,width=1.55)
    ex,ey=x1-.85,my
    for dx in [-.4,.4]:g.rod(fid+'_EASEL_LEG',(ex+dx,ey,.04),(ex,ey,1.8),.035,'Oak')
    g.rod(fid+'_EASEL_REAR',(ex,ey+.60,.04),(ex,ey,1.65),.03,'Oak');g.box(fid+'_EASEL_CANVAS',(ex,ey-.04,1.35),(.75,.035,.9),'Paper',.008)
    for i in range(4):g.box(fid+'_ORIGINAL_GEOMETRIC_ART',(ex-.24+i*.16,ey-.064,1.15+i*.13),(.13,.01,.18),['Terracotta','Teal','OliveFabric','Linen'][i],.01)
    g.box(fid+'_PAPER_STACK',(mx-.45,y1-.58,.91),(.45,.32,.06),'Paper',.006)
   elif b['id']=='B05':
    # Entry is y0: no bench across the doorway. Back-wall +side-wall L arrangement.
    f.table(fid+'_POT_BENCH_BACK',mx,y1-.55,width=x1-x0-.8,depth=.65,height=.7)
    for j in range(4):f.plant(fid+'_CONSERVATORY_BACK',x0+.55+j*(x1-x0-1.1)/3,y1-.55,z=.735,size=.58+.08*(j%3))
    before=set(bpy.context.scene.objects);f.table(fid+'_POT_BENCH_SIDE',x0+.45,my,width=y1-y0-2.0,depth=.65,height=.7);turn_new(before,x0+.45,my)
    for j in range(4):f.plant(fid+'_CONSERVATORY_SIDE',x0+.45,y0+1.15+j*(y1-y0-2.3)/3,z=.735,size=.58+.08*(j%3))
    f.chair(fid+'_GARDEN_CHAIR',mx+.2,my,0);g.box(fid+'_SEED_STORAGE',(x1-.4,my,.55),(.5,.8,1.05),'Teal',.02)
   elif b['id']=='B08':
    f.bed(fid+'_CHILD_SINGLE',x0+1.20,my,angle=math.pi/2,width=.90);f.table(fid+'_CHILD_STUDY',x1-.85,y1-.55,width=1.3,depth=.6,height=.63);before_chair=set(bpy.context.scene.objects);f.chair(fid+'_STUDY_CHAIR',x1-.85,y1-1.2,math.pi)
    for child_chair in set(bpy.context.scene.objects)-before_chair:child_chair.location.z=floor['datum_m']+(child_chair.location.z-floor['datum_m'])*.75;child_chair.scale.z*=.75
    before=set(bpy.context.scene.objects);tx,ty=x1-.35,y0+1.15;g.box(fid+'_TOY_CHEST',(tx,ty,.32),(1.2,.55,.55),'Teal',.055)
    for j in range(7):
     g.box(fid+'_WOODEN_PLAY_BLOCK',(tx-.42+j*.13,ty,.650),(.11,.11,.11),['Terracotta','Linen','OliveFabric'][j%3],.018)
     if j%2:g.box(fid+'_STACKED_PLAY_BLOCK',(tx-.42+j*.13,ty,.760),(.11,.11,.11),'Linen',.018)
    turn_new(before,tx,ty)
   elif b['id']=='B09':
    f.table(fid+'_MAKER_BENCH',mx,y1-.55,width=x1-x0-.8,depth=.8,height=.91);side_case(fid+'_PARTS_STORAGE',x0+.23,y0+1.05,width=1.45);g.box(fid+'_BENCH_VISE',(mx+.45,y1-.9,1.05),(.28,.25,.23),'Steel',.025);g.rod(fid+'_VISE_HANDLE',(mx+.45,y1-1.08,.98),(mx+.45,y1-1.08,1.22),.018,'Steel')
    g.box(fid+'_REAL_TOOL_BACKBOARD',(mx,y1-.10,1.55),(x1-x0-.9,.035,.8),'Oak',.012)
    for j in range(7):g.rod(fid+'_TOOL_HOOK',(x0+.55+j*.26,y1-.12,1.65),(x0+.55+j*.26,y1-.19,1.65),.009,'Steel')
    for j in range(7):g.rod(fid+'_VISIBLE_HAND_TOOL',(x0+.55+j*.26,y1-.18,1.25),(x0+.55+j*.26,y1-.18,1.75),.015,'Steel');g.box(fid+'_TOOL_GRIP',(x0+.55+j*.26,y1-.18,1.35),(.05,.06,.20),'Oak',.01)
    f.chair(fid+'_MAKER_STOOL',mx,y1-1.35,math.pi)
   elif b['id']=='B11':
    f.wardrobe(fid+'_GEAR_LOCKER',x0+1.15,y1-.35,width=1.7);before=set(bpy.context.scene.objects);f.table(fid+'_SERVICE_BENCH',x1-.4,y0+1.05,width=1.3,depth=.7,height=.86);turn_new(before,x1-.4,y0+1.05)
    bike_start=set(bpy.context.scene.objects);bx,by=mx,my-.10
    for xx in [bx-.62,bx+.62]:
     g.torus(fid+'_BICYCLE_TYRE',(xx,by,.356),.33,.026,'Black','Y');g.torus(fid+'_BICYCLE_RIM',(xx,by,.356),.30,.012,'Steel','Y')
     for j in range(20):a=j*math.tau/20;g.rod(fid+'_BICYCLE_SPOKE',(xx,by,.356),(xx+.29*math.cos(a),by,.356+.29*math.sin(a)),.0018,'Steel',4)
    pts=[(bx-.62,by,.356),(bx-.28,by,.86),(bx+.17,by,.356),(bx+.42,by,.9),(bx+.62,by,.356)]
    for a,bp in [(0,1),(1,2),(2,0),(1,3),(3,2),(3,4)]:g.rod(fid+'_BICYCLE_FRAME',pts[a],pts[bp],.018,'Teal')
    g.box(fid+'_SADDLE',(bx-.28,by,.94),(.28,.16,.055),'Black',.025);g.rod(fid+'_HANDLE_STEM',pts[3],(bx+.38,by,1.03),.018,'Steel');g.rod(fid+'_HANDLEBAR',(bx+.38,by-.25,1.03),(bx+.38,by+.25,1.03),.016,'Steel');g.rod(fid+'_CRANK',(bx+.17,by,.356),(bx+.33,by,.27),.012,'Steel');g.box(fid+'_PEDAL',(bx+.33,by,.27),(.12,.10,.03),'Steel',.01);g.rod(fid+'_KICKSTAND',(bx+.17,by,.356),(bx+.17,by+.28,.015),.015,'Black');turn_new(bike_start,bx,by)
   else:
    f.table(fid+'_WRITING_DESK',mx,y1-.55,width=1.85,depth=.75);f.chair(fid+'_AUTHOR_CHAIR',mx,y1-1.3,math.pi)
    for xx in [x0+.23,x1-.23]:side_case(fid+'_LIBRARY',xx,y0+1.10,width=1.35,turn=math.pi/2 if xx<mx else -math.pi/2)
    for j in range(4):g.box(fid+'_MANUSCRIPT',(mx-.5+j*.2,y1-.6,.801+j*.012),(.30,.22,.012),'Paper',.002)
    g.box(fid+'_LAPTOP_BASE',(mx+.25,y1-.6,.804),(.34,.24,.018),'Steel',.008);g.box(fid+'_LAPTOP_SCREEN',(mx+.25,y1-.48,.933),(.34,.018,.24),'Black',.008)
  if b['id']=='B02':
   clear('KITCHEN');x0,y0,x1,y1=bounds('KITCHEN');mx,my=(x0+x1)/2,(y0+y1)/2
   with scope('KITCHEN'):
    f.kitchen(fid+'_BAKERS_FITTED_KITCHEN',x0+.48,y1-.48,modules=5);g.box(fid+'_BAKING_ISLAND_BASE',(mx,my+.7,.43),(1.65,.72,.81),'Teal',.025);g.box(fid+'_BAKING_ISLAND_STONE',(mx,my+.7,.89),(1.78,.84,.065),'Terrazzo',.025);f.dining(fid+'_BREAKFAST',mx,y0+1.45)
    for j in range(3):g.lathe(fid+'_MIXING_BOWL',(mx-.5+j*.48,my+.7,.923),[(.06,0),(.11,.10),(.15,.17),(.145,.18),(.10,.10),(.04,.015)],'Porcelain',24)
    g.rod(fid+'_ROLLING_PIN',(mx-.4,my+.42,.96),(mx+.2,my+.42,.96),.045,'Oak',16)
  # Floor-specific palettes on original retained furniture, not just different brand labels.
  for o in bpy.context.scene.objects:
   if o.type=='MESH' and o.get('floor_id')==fid and o.get('layer')=='furniture':
    if o.data.users>1:o.data=o.data.copy()
    for slot in o.material_slots:
     if not slot.material:continue
     name=slot.material.name.rsplit('.',1)[0]if slot.material.name.rsplit('.',1)[-1].isdigit()else slot.material.name
     if name in ['OliveFabric','Linen','Upholstery','Teal','Tile']:slot.material=g.M[name]
  report.append({'floor':fid,'actual_theme':theme,'secondary_room_old_furniture_objects_removed':deleted,'actual_scoped_sofa_low_table_edits':transformed,'primary_bed_and_existing_armchair_retained_safe_original_orientation':True,'changes':'Actual new functional room fit-out and layout, not relabel; bakery additionally receives fitted baking kitchen/island/ceramic bowls/rolling pin/breakfast. Shells,datum,stairs,room finish/ceiling kept. Conceptual, not certified.'})
 for ob in bpy.context.scene.objects:
  if ob in start or ob.type!='MESH' or ob.data.uv_layers:continue
  uv=ob.data.uv_layers.new(name='UVMap')
  for poly in ob.data.polygons:
   axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=[1,2] if axis==0 else [0,2] if axis==1 else [0,1]
   for li in poly.loop_indices:
    p=ob.data.vertices[ob.data.loops[li].vertex_index].co;uv.data[li].uv=(p[axes[0]]*.8,p[axes[1]]*.8)
 bpy.context.view_layer.update();return report
