"""Actual native-scene mechanical gate. Not an independent visual acceptance vote.
blender -b scene/building-final.blend --python-exit-code 1 --python tools/validate_scene.py
"""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];s=bpy.context.scene;D=json.loads((R/'assets/exterior/aligned-programme.json').read_text());errors=[]
def names_of(o):return json.loads(o['component_names']) if o.get('component_names') else [o.name]
def check(q,msg):
 if not q:errors.append(msg)
mesh=[o for o in s.objects if o.type=='MESH'];palette={m.name for o in mesh for m in o.data.materials if m};check({'Limestone','Plaster','Terracotta','Teal','Oak','Walnut','Glass','Linen','Upholstery','OliveFabric','Tile','Porcelain','Steel','Glow'}.issubset(palette),'required real PBR palette on actual mesh slots');check(not [o for o in mesh if not o.data.materials or any(m is None for m in o.data.materials)],'all actual mesh material slots populated');level_names=sorted(c.name for c in bpy.data.collections if c.get('occupied_level'));check(level_names==[f'L{i:02}' for i in range(1,7)],'exactly six occupied L01–L06 collections');check(s.unit_settings.system=='METRIC' and abs(s.unit_settings.scale_length-1)<1e-8,'metric scale')
bpy.context.view_layer.update();levels=[]
for l in D['levels']:
 lid=l['id'];slabs=[o for o in mesh if o.get('level')==lid and o.get('role')=='slab'];pts=[o.matrix_world@Vector(v) for o in slabs for v in o.bound_box]
 check(bool(pts),lid+' floor slabs')
 if pts:
  b=[min(p[i] for p in pts) for i in range(3)]+[max(p[i] for p in pts) for i in range(3)];check(abs(b[3]-b[0]-26)<.01 and abs(b[4]-b[1]-20)<.01,lid+' actual slab footprint');levels.append({'id':lid,'FFL_m':l['elevation_m'],'storey_height_m':l['storey_height_m'],'slab_components':len(slabs),'actual_slab_bounds_m':b})
 for suffix in ['FACADE','PARTITIONS_LOW','PARTITIONS_HIGH','CEILING','STAIRS','LIFT','FURNITURE']:check(bpy.data.collections.get(lid+'_'+suffix) is not None,lid+' reversible '+suffix)
 check(bpy.data.objects.get('CAM_'+lid+'_AXON') is not None and bpy.data.objects.get('CAM_'+lid+'_PLAN') is not None,lid+' saved floor cameras')
homeids=sorted({o.get('home') for o in mesh if o.get('home')});homes=[]
check(len(homeids)==14,'14 actual mesh-tagged furnished homes')
for h in homeids:
 obs=[o for o in mesh if o.get('home')==h and o.get('fixture')];names=[name for o in obs for name in names_of(o)]
 for family in ['FRIDGE_DOOR','DISHWASHER_DOOR','HOOD_FILTER','INDUCTION','OVEN_GLASS','SINK_BOWL','MATTRESS','WC_BOWL','SHOWER_TRAY','BASIN','WARDROBE','SOFA']:
  check(any(family in n for n in names),h+' missing modelled '+family)
 check(any(o.get('fixture')=='kitchen' for o in obs) and any(o.get('fixture')=='bed' for o in obs),h+' actual kitchen/bed families')
 check(sum(len(o.data.vertices) for o in obs)>1000,h+' actual furnished vertex inventory')
 homes.append({'home':h,'editable_batched_meshes':len(obs),'preserved_source_components':len(names),'rooms':sorted({o.get('room_id') for o in obs if o.get('room_id')})})
import sys
sys.path.insert(0,str(R/'assets/exterior'));from circulation_checks import lift_checks
lift_report=lift_checks(s,D);errors.extend(lift_report['errors'])
recep=[o for o in mesh if o.get('room_id')=='L01_LOBBY' and o.get('fixture')=='reception'];rp=[o.matrix_world@Vector(v) for o in recep for v in o.bound_box]
reception_clearance={'scope':'nominal unobstructed bounding strips at west/north of reception furniture, not swept-path/code certification','west_strip_m':min(v.x for v in rp)-10.5,'north_strip_m':7.1-max(v.y for v in rp)}
check(reception_clearance['west_strip_m']>=1 and reception_clearance['north_strip_m']>=1,'reception west/north circulation strips at least 1 m')
empty=[];room_rows=[]
for l in D['levels']:
 for r in l['rooms']:
  if r['kind'] in ['stair','elevator'] or 'RISER_' in r['id']:continue
  obs=[o for o in mesh if o.get('room_id')==r['id'] and o.get('fixture') and o.get('fixture')!='room_lighting']
  if not obs:empty.append(r['id'])
  x,y,xx,yy=r['rect'];room_rows.append({'id':r['id'],'level':l['id'],'home':r.get('home') or '', 'name':r['name'],'kind':r['kind'],'bounds_xy_m':r['rect'],'area_m2':round((xx-x)*(yy-y),3),'furniture_batched_mesh_objects':len(obs),'preserved_source_furniture_components':sum(len(names_of(o)) for o in obs),'dimensions_m':[round(xx-x,5),round(yy-y,5)],'area_basis':'rectangular programme extent, not net lettable; common-core extent includes separately labelled shaft/risers'})
check(not empty,'zero empty required rooms beyond a light fixture')
public={'CAFE':'cafe_seating','PREP':'kitchen','CAFE_PASS':'cafe_counter','LOBBY':'mail_parcel','VESTIBULE':'furnishing','BIKES':'bicycle','WASTE':'waste_bin','PLANT':'plant_equipment','PARCEL':'parcel_storage','WC':'accessible_public_toilet','CLEANER':'cleaning_equipment','NEIGHBOUR':'sofa'}
for room,fam in public.items():check(any(o.get('room_id')=='L01_'+room and o.get('fixture')==fam for o in mesh),'actual L01 '+room+' / '+fam)
check(any(o.get('room_id')=='L06_WINTER_GARDEN' and o.get('fixture')=='sofa' for o in mesh),'furnished shared L06 winter garden')
flights=[o for o in mesh if o.get('role')=='stair_flight'];check(len(flights)==20,'twenty real flights / two routes')
connections=[]
for route in ['A','B']:
 fs=[o for o in flights if o.get('route')==route];check(len(fs)==10,'route '+route+' spans five storeys')
 for i,l in enumerate(D['levels'][:-1]):
  lid=l['id'];parts=[o for o in fs if o.get('level')==lid];check(len(parts)==2,lid+' route '+route+' paired flights')
  if len(parts)==2:
   top=max((o.matrix_world@Vector(v)).z for o in parts for v in o.bound_box);target=D['levels'][i+1]['elevation_m']+.04;check(abs(top-target)<.003,lid+' route '+route+' meets next landing');connections.append({'from':lid,'to':D['levels'][i+1]['id'],'route':route,'actual_flight_top_m':top,'next_finish_m':target})
check(sum('LIFT_PORTAL' in n for o in mesh for n in names_of(o))>=6,'six lift portals');check(any('LIFT_CAB' in n for o in mesh for n in names_of(o)),'physical lift cab')
check(bpy.data.texts.get('VIEW_MODES.py') is not None,'embedded reversible view switcher');check(len([o for o in s.objects if o.type=='CAMERA'])>=29,'29 saved evidence cameras')
wardrobe_faces=[]
for l in D['levels']:
 for r in l['rooms']:
  if r['kind']!='bedroom' or r['rect'][1]<=10:continue
  ys={'Oak':[],'Linen':[]}
  for o in mesh:
   if o.get('room_id')!=r['id'] or o.get('fixture')!='storage':continue
   for poly in o.data.polygons:
    mat=o.data.materials[poly.material_index].name
    if mat in ys:ys[mat].append((o.matrix_world@poly.center).y)
  check(bool(ys['Oak']) and bool(ys['Linen']),r['id']+' actual storage body/panel materials')
  if all(ys.values()):
   cy=sum(ys['Oak'])/len(ys['Oak']);py=sum(ys['Linen'])/len(ys['Linen']);delta=py-cy;wardrobe_faces.append({'room':r['id'],'actual_carcass_face_mean_y':cy,'actual_panel_face_mean_y':py,'inward_panel_offset_m':delta});check(delta>.27,r['id']+' storage panels face wall')
ceiling_edges=[]
for l in D['levels']:
 for r in l['rooms']:
  if r['kind'] in ['stair','elevator']:continue
  obs=[o for o in mesh if o.get('role')=='ceiling' and o.get('room_id')==r['id']];check(bool(obs),r['id']+' actual room-tagged ceiling finish')
  x,y,xx,yy=r['rect'];z=l['elevation_m']+l['storey_height_m']-.22;clear=[]
  for px,py in [(x-.02,y-.02),(xx+.02,y-.02),(x-.02,yy+.02),(xx+.02,yy+.02)]:
   found=False
   for o in obs:
    inv=o.matrix_world.inverted();a=inv@Vector((px,py,z-.10));b=inv@Vector((px,py,z+.10));v=b-a
    if o.ray_cast(a,v.normalized(),distance=v.length)[0]:found=True;break
   clear.append(found)
  ceiling_edges.append({'room':r['id'],'actual_corner_rays_hit_ceiling_finish':clear});check(all(clear),r['id']+' ceiling edge/corner coverage')
missing=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not Path(bpy.path.abspath(im.filepath)).exists()];check(not missing and not bpy.data.libraries,'zero missing external files/libraries');check(not [o for o in s.objects if o.type=='FONT'],'native original stroke geometry, no untracked font dependency')
roof=bpy.data.collections.get('ROOF');height=max((o.matrix_world@Vector(v)).z for o in roof.objects if o.type=='MESH' for v in o.bound_box);check(abs(height-21.12)<.015,'actual roof/parapet overall height')
report={'wardrobe_door_face_checks':wardrobe_faces,'ceiling_finish_edge_checks':ceiling_edges,'status':'PASS' if not errors else 'FAIL','scope':'mechanical native geometry/inventory only, not a visual or independent acceptance certificate','native_sha256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'blender':bpy.app.version_string,'objects':len(s.objects),'mesh_objects':len(mesh),'actual_used_materials':sorted(palette),'occupied_levels':levels,'homes':homes,'required_L01_rooms':public,'empty_required_rooms':empty,'two_routes_connections':connections,'actual_lift_geometry_checks':lift_report,'reception_clearance':reception_clearance,'overall_height_m':height,'missing_external_files':missing,'errors':errors}
(R/'evidence/producer/scene-validation.json').write_text(json.dumps(report,indent=2)+'\n');(R/'evidence/producer/room-schedule.json').write_text(json.dumps(room_rows,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['status','objects','mesh_objects','overall_height_m','empty_required_rooms','missing_external_files','errors']},indent=2))
if errors:raise RuntimeError('; '.join(errors))
print('PASS — exactly 6 occupied levels, 14 mesh-furnished homes, required L01/shared rooms, two continuous plausible stair routes, lift cab/portals, reversible collections, 29 saved cameras; zero empty required rooms or missing external files. Not code approval or independent visual acceptance.')
