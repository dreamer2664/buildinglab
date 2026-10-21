import bpy,sys,math,json,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'build'))
from district_core import District,palette
from district_architecture import streets,exit_canopy,blocks
from district_life import objects,crowds
start=time.time();bpy.ops.wm.open_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_REALISM.blend'))
d=District();p=palette()
print('STREETS',flush=True);streets(d,p);d.flush()
print('EXIT',flush=True);exit_canopy(d,p);d.flush()
print('BLOCKS',flush=True);blocks(d,p);d.flush()
print('LIFE',flush=True);objects(d,p);d.flush()
bpy.data.orphans_purge(do_recursive=True)
import gc,ctypes
gc.collect()
try:ctypes.CDLL('libc.so.6').malloc_trim(0)
except (OSError,AttributeError):pass
print('CROWDS',flush=True);crowds(d,p);d.flush()
scene=bpy.context.scene
for ob in bpy.data.objects:
 if ob.type=='LIGHT':ob.hide_render=True
sun_data=bpy.data.lights.new('District late afternoon sun','SUN');sun_data.energy=2.0;sun_data.angle=.065;sun_data.color=(1,.85,.66);sun=bpy.data.objects.new('District late afternoon sun',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(math.radians(36),math.radians(-24),math.radians(-38))
# Neutral packed sky from the existing source; moderate strength preserves shaded street detail.
if scene.world and scene.world.use_nodes:
 for n in scene.world.node_tree.nodes:
  if n.type=='BACKGROUND':
   sky=scene.world.node_tree.nodes.new('ShaderNodeTexSky');sky.sky_type='NISHITA';sky.sun_elevation=math.radians(28);sky.sun_rotation=math.radians(-38);sky.sun_disc=False;sky.altitude=.15;sky.air_density=1.0;sky.dust_density=1.0
   scene.world.node_tree.links.new(sky.outputs['Color'],n.inputs['Color']);n.inputs['Strength'].default_value=.35
views=[
 ('01_station_square',(64,-39,12),(1,22,4),32),
 ('02_exit_threshold',(23,16,2.05),(9,33,2.7),28),
 ('03_market_morning',(-51,-24,1.85),(-37,-33,1.65),35),
 ('04_cafe_and_tram',(45,-38,2.1),(29,-53,2.1),32),
 ('05_neighborhood_street',(11,-146,2.0),(10,-72,4),35),
 ('06_roofscape',(117,-186,64),(-7,-59,8),42),
 ('07_cafe_detail',(-29,-61,1.6),(-32,-65,1.2),36),
 ('08_exit_to_city',(11,37,2.0),(10,-28,1.9),28),
]
for name,loc,target,lens in views:
 ca=bpy.data.cameras.new('DISTVIEW_'+name);ca.lens=lens;ca.clip_start=.05;ca.clip_end=650;ob=bpy.data.objects.new(ca.name,ca);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects['DISTVIEW_01_station_square'];scene.render.engine='CYCLES';scene.render.resolution_x=1920;scene.render.resolution_y=1080;scene.render.resolution_percentage=100;scene.render.threads_mode='FIXED';scene.render.threads=2
scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.cycles.max_bounces=6;scene.cycles.diffuse_bounces=3;scene.cycles.glossy_bounces=3;scene.cycles.transmission_bounces=8;scene.cycles.use_light_tree=True
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.3;scene.use_nodes=False;scene.render.use_compositing=False
scene['district_status']='WIP: original masonry district, exit, shops, tram street and repeated photographic human scans. Not a certified historic reconstruction.'
bpy.data.orphans_purge(do_recursive=True)
report={'generated_at_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'build_seconds':time.time()-start,'component_counts':dict(d.count),'buildings_and_crowds':d.records,'scene_objects':len(bpy.data.objects),'scene_polygons_shared_once':sum(len(m.polygons) for m in bpy.data.meshes),'views':[v[0] for v in views]}
(ROOT/'docs').mkdir(exist_ok=True);(ROOT/'docs/DISTRICT_INVENTORY.json').write_text(json.dumps(report,indent=2))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_DISTRICT.blend'),compress=True)
print('DISTRICT SAVED',json.dumps({k:v for k,v in report.items() if k not in ('buildings_and_crowds','component_counts')}),flush=True)
