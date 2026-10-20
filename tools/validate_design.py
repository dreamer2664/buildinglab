#!/usr/bin/env python3
"""BLDG-1 schematic checks only. NOT a furnished-scene/release validator.
python3 tools/validate_design.py [--geometry]
--geometry independently reopens blockout in Blender and audits actual mesh bounds.
"""
from pathlib import Path
import json,sys,math,subprocess,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1];d=json.loads((R/'design/programme.json').read_text());errors=[]
def check(q,msg):
 if not q:errors.append(msg)
levels=d['levels'];check([x['id'] for x in levels]==[f'L{i:02}' for i in range(1,7)],'exactly six ordered occupied levels')
check(d['footprint_m']==[26,20],'footprint 26 x 20 m');check(abs(sum(l['storey_height_m'] for l in levels)-19.8)<1e-6,'roof bearing elevation 19.8 m')
check(abs(d['overall_height_m']-21.12)<1e-6,'overall height 21.12 m')
count=0;names=set();allroomids=[]
for l in levels:
 lid=l['id'];homes=l['homes'];count+=len(homes);rooms=l['rooms'];byid={r['id']:r for r in rooms};allroomids+=list(byid)
 check(len(homes)==(0 if lid=='L01' else 2 if lid=='L06' else 3),lid+' home count')
 for r in rooms:
  names.add(r['name']);x,y,xx,yy=r['rect'];check(0<=x<xx<=26 and 0<=y<yy<=20,r['id']+' bounds')
  check(abs((xx-x)*(yy-y)-r['area_m2'])<.015,r['id']+' measured area')
 for i,a in enumerate(rooms):
  for b in rooms[i+1:]:
   # Core rectangle intentionally includes lift/riser holes; those are excluded from net circulation.
   if a['id'].endswith('_CORE') and b['kind'] in ['elevator','service']:continue
   x,y,xx,yy=a['rect'];p,q,pp,qq=b['rect'];overlap=max(0,min(xx,pp)-max(x,p))*max(0,min(yy,qq)-max(y,q))
   check(overlap<.001,a['id']+' overlaps '+b['id'])
 graph={key:set() for key in byid};graph['OUTSIDE']=set()
 def norm(s):return lid+'_CORE' if s=='CORE' else s
 for door in l['doors']:
  a=norm(door['a']);b=norm(door['b']);check(a in graph and b in graph,door['id']+' endpoints')
  if a in graph and b in graph:graph[a].add(b);graph[b].add(a)
  check(door['width']>=.8,door['id']+' minimum schematic opening')
  for endpoint in [a,b]:
   if endpoint=='OUTSIDE':continue
   # Lift entrance is on the boundary of an explicit hole in the corridor polygon.
   if endpoint==lid+'_CORE' and (a.endswith('_LIFT') or b.endswith('_LIFT')):continue
   r=byid[endpoint];x,y,xx,yy=r['rect'];w=door['width'];px=door['x'];py=door['y']
   if door['orientation']=='H':
    check(x-.02<=px-w/2 and px+w/2<=xx+.02 and min(abs(py-y),abs(py-yy))<.16,door['id']+' fits '+endpoint)
   else:
    check(y-.02<=py-w/2 and py+w/2<=yy+.02 and min(abs(px-x),abs(px-xx))<.16,door['id']+' fits '+endpoint)
 seen=set();todo=[lid+'_CORE']
 while todo:
  s=todo.pop()
  if s not in seen:seen.add(s);todo+=list(graph[s]-seen)
 for r in rooms:
  if 'RISER_' not in r['id']:check(r['id'] in seen,r['id']+' unreachable from circulation / exterior routes')
 for h in homes:
  rr=[r for r in rooms if r['home']==h['id']];kinds={r['kind'] for r in rr}
  check({'living','bedroom','bathroom','corridor'}<=kinds,h['id']+' minimum room programme')
  check(len(rr)>=4,h['id']+' distinct spaces')
  x,y,xx,yy=h['kitchen_zone'];check(xx-x>=3 and yy-y>=2,h['id']+' kitchen zone')
  check(any(r['kind']=='living' and r['rect'][0]<=x<xx<=r['rect'][2] and r['rect'][1]<=y<yy<=r['rect'][3] for r in rr),h['id']+' kitchen inside living zone')
 for suffix in ['STAIR_A','STAIR_B','LIFT']:
  check(lid+'_'+suffix in byid,lid+' missing '+suffix)
 check(abs((byid[lid+'_STAIR_A']['rect'][3]-byid[lid+'_STAIR_A']['rect'][1])-5.6)<.001,lid+' stair depth for landings')
 plan=R/'design'/('plan-'+lid+'.svg');check(plan.exists(),lid+' plan exists')
 if plan.exists():
  svg=ET.parse(plan).getroot();texts=' '.join(svg.itertext());check(lid in texts and '26.00 m' in texts and '20.00 m' in texts and 'N' in texts and '5 m' in texts,lid+' dimensioned labelled plan / scale / north')
 print(lid, 'FFL',round(l['elevation_m'],2),'storey',l['storey_height_m'],'homes',len(homes),'rooms',len(rooms),'reachable',len(seen)-('OUTSIDE' in seen))
check(count==14,'exactly 14 proposed homes')
for s in ['Public vestibule','Reception / mail','Neighbourhood cafe','Cafe prep / counter','Accessible public WC','Bicycle / storage','Waste / service','Building plant','Shared winter garden']:
 check(s in names,'required room '+s)
if '--geometry' in sys.argv:
 result=subprocess.run(['blender','-b',str(R/'scene/blockout.blend'),'-t','8','--python-exit-code','1','--python',str(R/'design/audit_blockout.py')],cwd=R)
 check(result.returncode==0,'Blender geometry audit')
if errors:
 print('\n'.join('FAIL: '+e for e in errors));raise SystemExit(1)
print('PASS — design stage only: six levels; 26 x 20 m; 21.12 m parapet design height; 14 proposed homes; six dimensioned plans; dual stairs and lift; public/service programme. Not furnishing, structural or code approval.')
