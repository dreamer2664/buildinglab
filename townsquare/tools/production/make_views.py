import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];programme=json.loads((R/'design/programme.json').read_text());inventory=json.loads((R/'evidence/production/render-master-inventory.json').read_text());frames=[]
heroes=[
 ('H01','Entire square / aerial', (90,-112,100),(0,0,1),43,'aerial'),
 ('H02','Christmas tree and winter market',(13,-12,2.4),(-7,23,4.8),26,'town'),
 ('H03','MARKTGRUEN supermarket / original shop identity',(-30,17,2.1),(-20,28,2.7),27,'town'),
 ('H04','KESSEL & KAKAO / cafe and north frontage',(17,19,1.85),(20,29,2.7),26,'town'),
 ('H05','Playground / actual equipment and public realm',(16,-7,2.2),(25,1,1.6),28,'town'),
 ('H06','HAUS ABENDROT / southern evening frontage',(10,-18,2.0),(20,-28,3.2),30,'town')]
for id,title,pos,target,lens,kind in heroes:frames.append(dict(id=id,title=title,kind=kind,position=pos,target=target,lens_mm=lens,resolution=[3840,2160],samples=32,exposure=1.2))
for b in programme['buildings']:
 cx,cy=b['centre_xy_m'];ang=math.radians(b['rotation_deg']);w,d=b['footprint_m']
 def world(x,y,z):return [cx+x*math.cos(ang)-y*math.sin(ang),cy+x*math.sin(ang)+y*math.cos(ang),z]
 def local(p):
  dx,dy=p[0]-cx,p[1]-cy;return (dx*math.cos(ang)+dy*math.sin(ang),-dx*math.sin(ang)+dy*math.cos(ang),p[2])
 for floor in b['floors']:
  fid=floor['id'];z=floor['datum_m']
  for kind in ['plan','cutaway']:
   pos=world(0,-.001,z+34) if kind=='plan' else world(-w*.95,-d*1.25,z+18)
   frames.append(dict(id=fid+'_'+kind,title=b['brand']+' / '+fid+' / '+kind,programme=floor['programme'],kind=kind,building_id=b['id'],floor_id=fid,position=pos,target=world(0,0,z+.35),orthographic=True,ortho_scale=max(w,d*16/9)*1.20,lens_mm=45,resolution=[2560,1440],samples=16 if kind=='plan' else 24,exposure=.4))
  rooms=[o for o in inventory['objects'] if o['props'].get('floor_id')==fid and o['props'].get('layer')=='finish']
  preferred=['LIVING','SALES','WAREHOUSE','FRONT_A','PURCHASING','PRIMARY_BED']
  def rank(o):
   rid=o['props']['room_id'];area=(o['bounds_max'][0]-o['bounds_min'][0])*(o['bounds_max'][1]-o['bounds_min'][1]);return ((len(preferred)-next((i for i,x in enumerate(preferred) if rid.endswith('_'+x)),len(preferred)))*10000+area)
  room=max(rooms,key=rank);a=local(room['bounds_min']);c=local(room['bounds_max']);xmin,xmax=sorted([a[0],c[0]]);ymin,ymax=sorted([a[1],c[1]])
  pos=world(xmax-.95,ymin+1.0,z+1.62);target=world(xmin+(xmax-xmin)*.35,ymin+(ymax-ymin)*.65,z+1.25)
  if fid=='B03_L01':pos=[12.7,28.6,1.65];target=[24.2,33.4,1.25]
  frames.append(dict(id=fid+'_interior',title=b['brand']+' / '+fid+' / occupied interior',programme=floor['programme'],kind='interior',building_id=b['id'],floor_id=fid,room_id=room['props']['room_id'],room_bounds_world=[room['bounds_min'],room['bounds_max']],position=pos,target=target,lens_mm=22,resolution=[2560,1440],samples=32,exposure=.35))
crowd=json.loads((R/'.cache/recovery/master/provenance/master-build.json').read_text())['crowd']
for pair in range(6):
 people=crowd[pair*2:pair*2+2];center=[sum(p['xy_m'][i] for p in people)/2 for i in range(2)];dx=sum(math.sin(p['rotation_rad']) for p in people);dy=-sum(math.cos(p['rotation_rad']) for p in people);n=math.hypot(dx,dy);dx/=n;dy/=n
 frames.append(dict(id=f'D{pair+1:02}',title='Studio asset inspection / '+people[0]['variant']+' and '+people[1]['variant'],kind='people',variants=[p['variant'] for p in people],person_ids=[p['person_id'] for p in people],position=[center[0]+dx*3.9,center[1]+dy*3.9,1.55],target=[*center,1.39],lens_mm=57,resolution=[2560,1440],samples=48,exposure=.7,studio_key=True))
frames.append(dict(id='D07',title='P01 / full-body fit and ground contact',kind='people',variants=['P01'],person_ids=[1],position=[-3.5,-14.7,1.45],target=[-3,-9,.94],lens_mm=48,resolution=[2560,1440],samples=48,exposure=.7,studio_key=True))
frames.append(dict(id='D08',title='P06 / face and fabric detail',kind='people',variants=['P06'],person_ids=[6],position=[-12.7,-9.1,1.55],target=[-11.8,-7.5,1.47],lens_mm=66,resolution=[2560,1440],samples=64,exposure=.4,studio_key=True))
(R/'design/production-views.json').write_text(json.dumps({'count':len(frames),'source_production_checkpoint':'4bf44a021c3d','frames':frames},indent=2)+'\n');print('PRODUCTION_VIEW_PLAN',len(frames))
