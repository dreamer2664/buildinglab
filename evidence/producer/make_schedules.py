"""Export readable, editable schedules from measured/programmed native gate reports."""
from pathlib import Path
import csv,json
R=Path(__file__).resolve().parents[2];out=R/'exports';out.mkdir(exist_ok=True)
rooms=json.loads((R/'evidence/producer/room-schedule.json').read_text())
fields=['level','home','room_id','name','kind','x0_m','y0_m','x1_m','y1_m','width_m','depth_m','rectangular_extent_area_m2','batched_furniture_mesh_objects','preserved_source_furniture_components','area_basis']
with (out/'room-schedule.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in rooms:
  x,y,xx,yy=r['bounds_xy_m'];w.writerow({'level':r['level'],'home':r['home'],'room_id':r['id'],'name':r['name'],'kind':r['kind'],'x0_m':x,'y0_m':y,'x1_m':xx,'y1_m':yy,'width_m':round(xx-x,5),'depth_m':round(yy-y,5),'rectangular_extent_area_m2':r['area_m2'],'batched_furniture_mesh_objects':r['furniture_batched_mesh_objects'],'preserved_source_furniture_components':r['preserved_source_furniture_components'],'area_basis':r['area_basis']})
homes=json.loads((R/'assets/interiors/furnishing-schedule.json').read_text());gate=json.loads((R/'evidence/producer/scene-validation.json').read_text());assert gate['status']=='PASS'
fields=['level','home','living_room','kitchen_placement','native_batched_furniture_meshes','preserved_source_furniture_components','required_families_checked','scope']
with (out/'furnishing-schedule.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in homes:
  g=next(g for g in gate['homes'] if g['home']==r['home']);w.writerow({'level':r['level'],'home':r['home'],'living_room':r['room'],'kitchen_placement':r['kitchen'],'native_batched_furniture_meshes':g['editable_batched_meshes'],'preserved_source_furniture_components':g['preserved_source_components'],'required_families_checked':'fridge; dishwasher; hood; hob; oven; sink; bed/mattress; wardrobe; sofa; WC; shower; basin','scope':'actual native-name/geometry inventory, not appliance quantities or compliance certification'})
print('SCHEDULES_EXPORTED',len(rooms),'room extents and',len(homes),'furnished homes')
