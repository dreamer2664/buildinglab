import bpy,math,sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent));import build_bay as b
ROOT=Path(__file__).resolve().parents[1];col=b.make_collection('REBUILD_DETAILS')
def mat(name,c,metal=0,rough=.6):return b.make_pbr_mat(name,c,metal,rough,.025,30)
iron=mat('Detail blackened iron',(.018,.027,.027),.65,.38);wood=mat('Detail aged oak',(.19,.085,.028),0,.4);brass=mat('Detail brass',(.46,.28,.08),.8,.3);white=mat('Detail enamel ivory',(.8,.73,.56),0,.35);navy=mat('Detail enamel navy',(.008,.021,.035),.15,.28)
cache={}
def box(name,loc,sz,ma):
 key=(tuple(sz),ma.name)
 if key not in cache:cache[key]=b.create_box_mesh(name,*sz,bevel_m=.004)
 return b.add_mesh_obj(name,cache[key],loc,mat=ma,col=col)
def line(name,p,q,r,ma):
 p,q=Vector(p),Vector(q);curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.bevel_depth=r;curve.bevel_resolution=1;sp=curve.splines.new('POLY');sp.points.add(1)
 for v,co in zip(sp.points,(p,q)):v.co=(*co,1)
 curve.materials.append(ma);ob=bpy.data.objects.new(name,curve);col.objects.link(ob);return ob
def label(name,text,loc,size,ma,rot=(math.pi/2,0,math.pi)):
 cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.size=size;cu.align_x='CENTER';cu.extrude=.0015;cu.materials.append(ma);ob=bpy.data.objects.new(name,cu);col.objects.link(ob);ob.location=loc;ob.rotation_euler=rot;return ob
# World-metric brick shader: no downloaded texture needed; physical mortar relief.
def masonry(ma,axis,width,height,c1,c2):
 nt=ma.node_tree;nodes=nt.nodes;links=nt.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
 geom=nodes.new('ShaderNodeNewGeometry');sep=nodes.new('ShaderNodeSeparateXYZ');comb=nodes.new('ShaderNodeCombineXYZ');links.new(geom.outputs['Position'],sep.inputs[0]);links.new(sep.outputs[axis],comb.inputs['X']);links.new(sep.outputs['Z'],comb.inputs['Y'])
 tex=nodes.new('ShaderNodeTexBrick');tex.inputs['Scale'].default_value=1;tex.inputs['Brick Width'].default_value=width;tex.inputs['Row Height'].default_value=height;tex.inputs['Mortar Size'].default_value=.009;tex.inputs['Mortar Smooth'].default_value=.004;tex.inputs['Color1'].default_value=(*c1,1);tex.inputs['Color2'].default_value=(*c2,1);tex.inputs['Mortar'].default_value=(.12,.105,.085,1)
 links.new(comb.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Color'],bs.inputs['Base Color']);bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.35;bump.inputs['Distance'].default_value=.008;links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs[0],bs.inputs['Normal'])
brick=bpy.data.materials.get('Rebuild soot brown brick')
if brick:masonry(brick,'Y',.32,.105,(.17,.082,.035),(.29,.15,.07))
stone=bpy.data.materials.get('Rebuild limestone ashlar')
if stone:masonry(stone,'X',.95,.44,(.42,.36,.27),(.51,.44,.33))
# Replace monolithic bench backs with real slatted platform benches.
for ob in list(bpy.data.objects):
 if ob.name.startswith('PLT_07_Bench'):bpy.data.objects.remove(ob,do_unlink=True)
for k in range(12):
 x=-61+k*12;y=99.2;z=.76
 for j in range(6):box('Bench seat slat',(x,y-.3+j*.11,z+.45),(2.5,.085,.035),wood)
 for j in range(5):box('Bench back slat',(x,y+.31,z+.66+j*.105),(2.5,.035,.075),wood)
 for dx in (-1,1):
  box('Bench pedestal',(x+dx,y,z+.23),(.06,.6,.45),iron)
  box('Bench upright',(x+dx,y+.31,z+.72),(.055,.055,.9),iron)
  box('Bench armrest',(x+dx,y,z+.7),(.065,.68,.035),wood)
# Suspended platform boards with clearly legible lettering.
for x in (-52,0,52):
 for yy,number in [(96,7),(84,6),(72,5)]:
  for dx in (-1.5,1.5):line('Sign suspension',(x+dx,yy,13.8),(x+dx,yy,5),.012,iron)
  box('Platform sign',(x,yy,4.5),(4,.12,1),navy)
  for zz in (4.02,4.98):box('Sign brass edging',(x,yy,zz),(4.04,.14,.035),brass)
  label('Platform numeral',f'GLEIS  {number}',(x,yy-.075,4.22),.55,white,rot=(math.pi/2,0,0))
# Platform paving joints, actual inlaid joints every 1.5 m rather than featureless slabs.
for x in [-89+i*1.5 for i in range(120)]:box('Platform stone joint',(x,99,.763),(.012,8.8,.0015),iron)
for y in (96.4,97.8,99.2,100.6,102):box('Platform longitudinal joint',(0,y,.763),(180,.009,.0015),iron)
# Tall clock: two-sided dial with ticks, radial hands and pendulum housing.
x,y,z=-36,97,4.9
line('Clock support',(x,y,.76),(x,y,4.9),.055,iron)
for side in (-1,1):
 me=b.create_cyl_mesh('Clock surround',.62,.10,verts=64,axis='Y');b.add_mesh_obj('Clock surround',me,(x,y,z),mat=brass,col=col)
 me=b.create_cyl_mesh('Clock dial',.57,.012,verts=64,axis='Y');b.add_mesh_obj('Clock dial',me,(x,y+side*.06,z),mat=white,col=col)
 for j in range(60):
  a=j*math.pi/30;r=.49;ob=box('Clock tick',(x+math.sin(a)*r,y+side*.075,z+math.cos(a)*r),(.014,.01,.065 if j%5==0 else .028),iron);ob.rotation_euler.y=a
 for a,length in [(math.radians(140),.31),(math.radians(240),.46)]:line('Clock hand',(x,y+side*.09,z),(x+math.sin(a)*length,y+side*.09,z+math.cos(a)*length),.014,iron)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_REBUILD.blend'),compress=True)
print('Detailing WIP saved; not accepted')
