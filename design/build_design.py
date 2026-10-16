"""Original Casa dei Colori schematic. Python stdlib; writes programme + six SVG plans.
Run python3 design/build_design.py, then Blender --background --python design/build_blockout.py.
Dimensions in metres; X east, Y north, Z up. No external assets.
"""
from pathlib import Path
import json, math, html
ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'design'; D.mkdir(exist_ok=True)
COLORS={'public':'#ead8b7','living':'#f1d3b1','kitchen':'#d0b995','bedroom':'#a4beb3','bathroom':'#b6d1d5','storage':'#c8bda9','corridor':'#eee6d5','stair':'#c77f62','elevator':'#6b8d91','service':'#c4c7bd','garden':'#acc49b'}
levels=[]
def room(l,id,name,kind,box,home=None):
 r={'id':l['id']+'_'+id,'name':name,'kind':kind,'rect':box,'home':home,'area_m2':round((box[2]-box[0])*(box[3]-box[1]),2)};l['rooms'].append(r);return r

def door(l,id,a,b,orientation,x,y,width=0.9,external=False):
 l['doors'].append(dict(id=l['id']+'_'+id,a=a,b=b,orientation=orientation,x=x,y=y,width=width,external=external))

def add_home(l,id,bounds,style):
 h={'id':id,'bounds':bounds,'layout':style};l['homes'].append(h)
 x0,y0,x1,y1=bounds
 if style.startswith('north'):
  # left-to-right: open living/kitchen; entry gallery; wet/bedroom strip.
  mirror=style.endswith('east'); width=x1-x0
  living=6.4+(int(l['id'][1:])%3)*.2; hall=1.4; split=y0+2.55+(int(l['id'][1:])%2)*.25
  def rect(a,b,c,d):
   return [x1-c,b,x1-a,d] if mirror else [x0+a,b,x0+c,d]
  def xp(v):return x1-v if mirror else x0+v
  room(l,id+'_live','Living / kitchen','living',rect(0,y0,living,y1),id)
  room(l,id+'_hall','Entry / storage','corridor',rect(living+.2,y0,living+.2+hall,y1),id)
  q=living+.4+hall
  room(l,id+'_bath','Bathroom','bathroom',rect(q,y0,width,split),id)
  room(l,id+'_bed','Bedroom','bedroom',rect(q,split+.2,width,y1),id)
  hx=xp(living+.2+hall/2)
  door(l,id+'_entry','CORE',l['id']+'_'+id+'_hall','H',hx,y0)
  door(l,id+'_living',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_live','V',xp(living+.1),y0+1.25)
  door(l,id+'_bathdoor',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_bath','V',xp(q-.1),y0+1.25,.8)
  door(l,id+'_beddoor',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_bed','V',xp(q-.1),split+1.4)
  h['kitchen_zone']=rect(.3,y1-2.3,3.8,y1-.25)
 elif style=='south_family' or style=='penthouse_south':
  hall_y=y1-1.4; live_w=8.6 if style=='south_family' else 10.8
  room(l,id+'_live','Living / dining / kitchen','living',[x0,y0,x0+live_w,hall_y-.2],id)
  room(l,id+'_hall','Entry gallery / storage','corridor',[x0,hall_y,x1,y1],id)
  avail=x1-(x0+live_w+.2);bedw=avail*.32
  pos=x0+live_w+.2
  for j in range(2):
   room(l,id+f'_bed{j+1}',f'Bedroom {j+1}','bedroom',[pos,y0,pos+bedw,hall_y-.2],id)
   door(l,id+f'_beddoor{j+1}',l['id']+'_'+id+'_hall',l['id']+'_'+id+f'_bed{j+1}','H',pos+bedw/2,hall_y-.1)
   pos+=bedw+.2
  remaining=x1-pos;storew=1.0
  room(l,id+'_store','Wardrobe','storage',[pos,y0,pos+storew,hall_y-.2],id)
  room(l,id+'_bath','Bathroom','bathroom',[pos+storew+.2,y0,x1,hall_y-.2],id)
  door(l,id+'_entry','CORE',l['id']+'_'+id+'_hall','H',13,y1,1.0)
  door(l,id+'_living',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_live','H',x0+live_w/2,hall_y-.1,1.1)
  door(l,id+'_storedoor',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_store','H',pos+.5,hall_y-.1,.8)
  door(l,id+'_bathdoor',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_bath','H',pos+storew+.2+(remaining-storew-.2)/2,hall_y-.1,.8)
  h['kitchen_zone']=[x0+.3,y0+.3,x0+4,y0+2.7]
 else:
  # Larger north penthouse: two furnished zones, central entry gallery.
  a=x0+4.7;b=a+1.6
  room(l,id+'_bed','Bedroom','bedroom',[x0,y0+2.9,a-.2,y1],id)
  room(l,id+'_bath','Bathroom','bathroom',[x0,y0,a-.2,y0+2.7],id)
  room(l,id+'_hall','Entry / wardrobes','corridor',[a,y0,b,y1],id)
  room(l,id+'_live','Living / kitchen / study','living',[b+.2,y0,x1,y1],id)
  door(l,id+'_entry','CORE',l['id']+'_'+id+'_hall','H',(a+b)/2,y0,1)
  for suffix,yy in [('bed',y0+4.4),('bath',y0+1.35)]:
   door(l,id+'_'+suffix+'door',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_'+suffix,'V',a-.1,yy,.9)
  door(l,id+'_living',l['id']+'_'+id+'_hall',l['id']+'_'+id+'_live','V',b+.1,y0+1.3,1.1)
  h['kitchen_zone']=[b+.5,y1-2.4,b+4.6,y1-.25]

for i in range(1,7):
 l={'id':f'L{i:02}','elevation_m':0 if i==1 else 3.8+(i-2)*3.2,'storey_height_m':3.8 if i==1 else 3.2,'rooms':[],'homes':[],'doors':[]}
 levels.append(l)
 room(l,'CORE','Common corridor','corridor',[4.7,6.8,21.3,11.2])
 # Elevator occupies a hole in the circulation polygon, not usable corridor area.
 room(l,'LIFT','Lift shaft / cab','elevator',[11.8,8.8,14.2,11.2])
 room(l,'RISER_W','Water / power riser','service',[10.5,9.6,11.6,11.2])
 room(l,'RISER_E','Ventilation riser','service',[14.4,9.6,15.5,11.2])
 door(l,'lift_door','CORE',l['id']+'_LIFT','H',13,8.8,1.0)
 for s,x0,x1 in [('A',.3,4.7),('B',21.3,25.7)]:
  room(l,'STAIR_'+s,'Exit stair '+s,'stair',[x0,6.8,x1,11.2])
  door(l,'stair_'+s,'CORE',l['id']+'_STAIR_'+s,'V',x1 if s=='A' else x0,7.6,1.0)
 if i==1:
  specs=[('CAFE','Neighbourhood cafe','public',[.3,.3,7.5,6.8]),('PREP','Cafe prep / counter','kitchen',[7.7,.3,10.3,3.7]),('CAFE_PASS','Cafe public passage','public',[7.7,3.9,10.3,6.8]),('VESTIBULE','Public vestibule','public',[10.5,.3,15.5,2.8]),('LOBBY','Reception / mail','public',[10.5,3,15.5,6.8]),('BIKES','Bicycle / storage','storage',[15.7,.3,20.5,6.8]),('WASTE','Waste / service','service',[20.7,.3,25.7,6.8]),('NEIGHBOUR','Neighbourhood room','public',[.3,11.2,8.5,17.7]),('WC','Accessible public WC','bathroom',[8.7,11.2,11.7,14.2]),('CLEANER','Cleaner / supplies','storage',[8.7,14.4,11.7,17.7]),('PLANT','Building plant','service',[11.9,11.2,18,17.7]),('PARCEL','Parcel / community store','storage',[18.2,11.2,25.7,17.7])]
  for id,name,k,b in specs:room(l,id,name,k,b)
  for id,x,y in [('LOBBY',13,6.8),('BIKES',18,6.8),('WASTE',23,6.8),('NEIGHBOUR',7.4,11.2),('WC',10,11.2),('PLANT',16.5,11.2),('PARCEL',20,11.2)]:
   if id=='WASTE':door(l,id+'_external','OUTSIDE',l['id']+'_'+id,'V',25.7,3.5,1.2,True)
   else:door(l,id+'_entry','CORE',l['id']+'_'+id,'H',x,y,1)
  door(l,'cafe','L01_LOBBY','L01_CAFE','V',10.4,4.8,1.1) # through prep entrance, then counter opening
  l['doors'][-1]['b']='L01_CAFE_PASS'
  door(l,'cafe_prep','L01_CAFE_PASS','L01_CAFE','V',7.6,4.8,1.3)
  door(l,'prep_service','L01_CAFE_PASS','L01_PREP','H',9,3.8,.9)
  door(l,'vestibule','L01_VESTIBULE','L01_LOBBY','H',13,2.9,1.5)
  door(l,'entrance','OUTSIDE','L01_VESTIBULE','H',13,.3,1.8,True)
  door(l,'cleaner','L01_NEIGHBOUR','L01_CLEANER','V',8.6,16,.8)
  for s,x in [('A',.3),('B',25.7)]:door(l,'exit_'+s,'OUTSIDE','L01_STAIR_'+s,'V',x,7.6,1.1,True)
 elif i<6:
  add_home(l,f'{i}A',[.3,11.2,12.9,17.7],'north_west')
  add_home(l,f'{i}B',[13.1,11.2,25.7,17.7],'north_east')
  add_home(l,f'{i}C',[6.5,.3,25.7,6.8],'south_family')
  room(l,'READING','Shared reading room','garden',[.3,.3,6.3,6.8])
  door(l,'reading','CORE',l['id']+'_READING','H',5.5,6.8,1.0)
 else:
  add_home(l,'6A',[.3,.3,25.7,6.8],'penthouse_south')
  add_home(l,'6B',[10.5,11.2,25.7,17.7],'penthouse_north')
  room(l,'WINTER_GARDEN','Shared winter garden','garden',[.3,11.2,10.3,17.7])
  door(l,'garden','CORE',l['id']+'_WINTER_GARDEN','H',7.8,11.2,1.2)

# Pass A design correction: enlarge the core to fit real 1.2 m landings,
# 0.28 m treads and 22 risers at ground storey; footprint increases to 26 x 20 m.
def stretch_y(y):
 if y <= 6.8:return y*7.2/6.8
 if y <= 11.2:return 7.2+(y-6.8)*5.6/4.4
 return 12.8+(y-11.2)*7.2/6.8
for l in levels:
 for r in l['rooms']:
  r['rect'][1]=round(stretch_y(r['rect'][1]),5);r['rect'][3]=round(stretch_y(r['rect'][3]),5)
  x,y,xx,yy=r['rect'];r['area_m2']=round((xx-x)*(yy-y),2)
 for h in l['homes']:
  for key in ['bounds','kitchen_zone']:
   h[key][1]=round(stretch_y(h[key][1]),5);h[key][3]=round(stretch_y(h[key][3]),5)
 for d in l['doors']:d['y']=round(stretch_y(d['y']),5)

model={'name':'Casa dei Colori','stage':'schematic blockout — not furnished release','units':'metres','orientation':'+Y north; entrance on south','footprint_m':[26,20],'slab_m':.22,'external_wall_m':.3,'internal_wall_m':.2,'parapet_m':1.1,'roof_slab_top_m':20.02,'overall_height_m':21.12,'levels':levels,'palette':COLORS,'structural_strategy':'RC floor plates on perimeter columns and two shear stair cores plus lift core; 6.4 m conceptual bay spacing. Not engineered or code-approved.'}
(D/'programme.json').write_text(json.dumps(model,indent=2)+'\n')

# vector plans: 36 px per metre, scale bar is measured in same coordinates.
for l in levels:
 scale=43;ox=122;oy=155
 def sx(x):return ox+x*scale
 def sy(y):return oy+(20-y)*scale
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1240" viewBox="0 0 1600 1240"><rect width="1600" height="1240" fill="#faf7ef"/>',f'<text x="70" y="57" font-family="sans-serif" font-size="32" fill="#203d3b">CASA DEI COLORI / {l["id"]}</text>',f'<text x="70" y="92" font-family="sans-serif" font-size="17" fill="#57635c">SCHEMATIC PLAN · {l["elevation_m"]:.2f} m FFL · storey {l["storey_height_m"]:.2f} m · not code-approved</text>']
 parts.append(f'<rect x="{sx(0)}" y="{sy(20)}" width="{26*scale}" height="{20*scale}" fill="#203d3b"/>')
 for r in l['rooms']:
  x,y,xx,yy=r['rect'];w=(xx-x)*scale;h=(yy-y)*scale
  parts.append(f'<rect x="{sx(x)}" y="{sy(yy)}" width="{w}" height="{h}" fill="{COLORS[r["kind"]]}" stroke="#64716b" stroke-width="1"/>')
  label=(r['home']+' · ' if r['home'] else '')+r['name']
  # compact wrapped text without external fonts
  import textwrap
  lines=textwrap.wrap(label,max(9,int(w/7)))
  if h<95:lines=lines[:3]
  tx=sx((x+xx)/2);ty=sy((y+yy)/2)-7*len(lines)
  if r['kind']=='living' and y<1:ty=sy(y+(yy-y)*.73)-7*len(lines)
  for j,line in enumerate(lines):parts.append(f'<text x="{tx}" y="{ty+j*15}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#243a36">{html.escape(line)}</text>')
  if w>130 and h>65:parts.append(f'<text x="{tx}" y="{ty+len(lines)*15}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#4d5e55">{xx-x:.1f} × {yy-y:.1f} m</text>')
 for h in l['homes']:
  x,y,xx,yy=h['kitchen_zone'];parts.append(f'<rect x="{sx(x)}" y="{sy(yy)}" width="{(xx-x)*scale}" height="{(yy-y)*scale}" fill="none" stroke="#9e633e" stroke-dasharray="4 3"/><text x="{sx(x)+5}" y="{sy(yy)+15}" font-family="sans-serif" font-size="11" fill="#8d5435">KITCHEN</text>')
 for d in l['doors']:
  x,y,w=d['x'],d['y'],d['width']
  if d['orientation']=='H':
   parts.append(f'<path d="M {sx(x-w/2)} {sy(y)} h {w*scale}" stroke="#fffaf0" stroke-width="12"/><path d="M {sx(x-w/2)} {sy(y)} v {-w*scale} Q {sx(x+w/2)} {sy(y)-w*scale} {sx(x+w/2)} {sy(y)}" fill="none" stroke="#705442" stroke-width="1.4"/>')
  else:parts.append(f'<path d="M {sx(x)} {sy(y-w/2)} v {-w*scale}" stroke="#fffaf0" stroke-width="12"/><path d="M {sx(x)} {sy(y-w/2)} h {w*scale}" stroke="#705442" stroke-width="1.5"/>')
 # dimension perimeter
 parts += [f'<path d="M {sx(0)} 128 H {sx(26)} M {sx(0)} 121 V 137 M {sx(26)} 121 V 137" stroke="#244a43" fill="none"/><text x="{sx(13)}" y="121" text-anchor="middle" font-family="sans-serif" font-size="17">26.00 m</text>',f'<path d="M 97 {sy(0)} V {sy(20)} M 90 {sy(0)} H 104 M 90 {sy(20)} H 104" stroke="#244a43"/><text x="79" y="550" transform="rotate(-90 79 550)" font-family="sans-serif" font-size="17">20.00 m</text>']
 parts += ['<path d="M 1400 210 V 140 l -8 17 m 8 -17 l 8 17" fill="none" stroke="#244a43" stroke-width="3"/><text x="1400" y="125" text-anchor="middle" font-family="sans-serif" font-size="22">N</text>']
 for k,(kind,color) in enumerate(COLORS.items()):parts.append(f'<rect x="1290" y="{300+k*36}" width="16" height="16" fill="{color}"/><text x="1318" y="{313+k*36}" font-family="sans-serif" font-size="14">{kind}</text>')
 parts.append(f'<text x="1290" y="760" font-family="sans-serif" font-size="15">{len(l["homes"])} homes on level</text>')
 for j in range(6):parts.append(f'<text x="{sx(j)}" y="1135" text-anchor="middle" font-family="sans-serif" font-size="15">{j}</text>')
 for j in range(5):parts.append(f'<rect x="{sx(j)}" y="1100" width="43" height="10" fill="{"#244a43" if j%2==0 else "#faf7ef"}" stroke="#244a43"/>')
 parts.append(f'<text x="{sx(6.1)}" y="1135" font-family="sans-serif" font-size="16">Scale bar: 0–5 m</text><text x="70" y="1200" font-family="sans-serif" font-size="14" fill="#65746a">43 SVG units = 1 m · print scale depends on output size · wall thickness 0.30 / 0.20 m · conceptual door swings</text></svg>')
 (D/f'plan-{l["id"]}.svg').write_text('\n'.join(parts))
print('Wrote programme and six dimensioned SVG plans.')
