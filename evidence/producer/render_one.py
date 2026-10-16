"""Render ONE final-resolution PNG in a fresh Blender process to bound RAM.
RENDER_VIEW=exterior-day blender -b scene/building-final.blend -t 6 --python-exit-code 1 --python evidence/producer/render_one.py
Postprocess with external OIDN after Blender exits, then annotate plans.
"""
import bpy,os,sys,json,math
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent));from view_modes import set_view
from views import VIEWS
v=next(v for v in VIEWS if v['id']==os.environ['RENDER_VIEW']);s=bpy.context.scene;set_view(v['mode'],v.get('level'));s.camera=bpy.data.objects[v['camera']]
s.cycles.use_denoising=False;s.cycles.samples=int(os.environ.get('RENDER_SAMPLES','16'));s.render.resolution_x=v['width'];s.render.resolution_y=v['height'];s.render.resolution_percentage=100
if os.environ.get('RENDER_DRAFT')=='1':s.render.resolution_percentage=50
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=35
if v.get('night'):
 bpy.data.lights['SUN'].energy=.04;s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.09;s.view_settings.exposure=.9
out=ROOT/'renders/final';out.mkdir(parents=True,exist_ok=True);s.render.filepath=str(out/(v['id']+'.png'))
meta=dict(v);meta.update({'camera_location':list(s.camera.location),'camera_lens_mm':s.camera.data.lens,'camera_type':s.camera.data.type,'samples':s.cycles.samples,'blender':bpy.app.version_string,'integrated_denoising':False,'colour_management':s.view_settings.view_transform+' / '+s.view_settings.look,'exposure':s.view_settings.exposure,'source':'scene/building-final.blend','render_percentage':s.render.resolution_percentage})
def xy(x,y,z):
 p=world_to_camera_view(s,s.camera,Vector((x,y,z)));return [p.x*v['width'],(1-p.y)*v['height']]
if v['mode']=='plan':
 data=json.loads((ROOT/'assets/exterior/aligned-programme.json').read_text());l=next(l for l in data['levels'] if l['id']==v['level']);z=l['elevation_m'];meta['elevation']=z;labels=[];doors=[]
 for r in l['rooms']:
  x,y,xx,yy=r['rect'];k=r['kind'];home=r.get('home') or '';label={'living':'LIVING / KITCHEN','bedroom':'BEDROOM','bathroom':'BATH','storage':'STORE','riser':'RISER','stair':'EXIT STAIR','elevator':'LIFT','gallery':'COMMON GALLERY','corridor':'ENTRY' if home else 'COMMON CORE'}.get(k,r['name'].upper())
  if 'RISER' in r['id']:label='RISER'
  if k=='stair':label='EXIT STAIR '+r['id'][-1]
  if k=='bedroom' and r['id'].endswith(('bed1','bed2')):label='BEDROOM '+r['id'][-1]
  cx,cy=(x+xx)/2,(y+yy)/2
  if k=='corridor' and not home:cx,cy=8.5,8.5
  if k not in ['corridor','stair','elevator','service']:label+=f'\n{xx-x:.2f} × {yy-y:.2f} m'
  labels.append({'text':((home+'\n') if home and k!='corridor' else '')+label,'xy':xy(cx,cy,z+.06),'kind':k,'max_width':(xx-x)/42*v['width']-.15/42*v['width']})
 for d in l['doors']:
  a,b=d['x'],d['y'];w=d['width'];hs=d.get('hinge_side',-1);sg=d.get('swing_sign',1);rec=d.get('hinge_recess_m',0);aa=math.radians(d.get('opening_degrees',90));rad=w*.95;pts=[]
  if d['orientation']=='H':
   hinge=(a+hs*(w/2-.03),b+sg*rec);pts=[xy(hinge[0]-hs*rad*math.cos(t*aa/30),hinge[1]+sg*rad*math.sin(t*aa/30),z+.06) for t in range(31)]
  else:
   hinge=(a-sg*rec,b+hs*(w/2-.03));pts=[xy(hinge[0]-sg*rad*math.sin(t*aa/30),hinge[1]-hs*rad*math.cos(t*aa/30),z+.06) for t in range(31)]
  doors.append({'hinge':xy(*hinge,z+.06),'end':pts[-1],'arc':pts,'id':d['id']})
 meta['lighting_points']=[{'xy':xy(o.location.x,o.location.y,z+.06),'name':o.name,'energy_w':o.data.energy} for o in s.objects if o.type=='LIGHT' and o.get('level')==v['level']]
 meta.update({'labels':labels,'door_swings':doors,'dimension_corners':[xy(0,0,z),xy(26,0,z),xy(0,20,z),xy(26,20,z)],'scale_pixels_per_metre':v['width']/42})
bpy.ops.render.render(write_still=True)
(ROOT/'evidence/producer'/('render-'+v['id']+'.json')).write_text(json.dumps(meta,indent=2)+'\n');print('RENDER_WRITTEN',v['id'],flush=True)
