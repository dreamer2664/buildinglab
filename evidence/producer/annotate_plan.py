"""Lossless, explicitly disclosed technical overlays on actual Blender plan PNGs.
Original render is preserved in memory-bounded noisy-cache; no geometry/image synthesis.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2];FONT=ROOT/'evidence/producer/fonts/DejaVuSans.ttf'
def annotate(view):
 p=ROOT/'renders/final'/(view+'.png');meta=json.loads((ROOT/'evidence/producer'/('render-'+view+'.json')).read_text());im=Image.open(p).convert('RGB');d=ImageDraw.Draw(im);W,H=im.size
 def ft(n):return ImageFont.truetype(str(FONT),n)
 col='#153e3a';white='#faf7ef'
 for sw in meta['door_swings']:
  d.line([tuple(x) for x in sw['arc']],fill=col,width=2);d.line([tuple(sw['hinge']),tuple(sw['end'])],fill=col,width=3)
 for point in meta.get('lighting_points',[]):
  px,py=point['xy'];d.ellipse((px-7,py-7,px+7,py+7),fill='#faf7df',outline='#985c30',width=2);d.line([(px-3,py),(px+3,py)],fill='#985c30',width=1);d.line([(px,py-3),(px,py+3)],fill='#985c30',width=1)
 for label in meta['labels']:
  width=max(42,label['max_width']);n=17 if width>150 else 14;f=ft(n);lines=[]
  for src in label['text'].split('\n'):
   line=''
   for word in src.split():
    if line and d.textlength(line+' '+word,font=f)>width:lines.append(line);line=word
    else:line=(line+' '+word).strip()
   lines.append(line)
  text='\n'.join(lines);lx,ly=label['xy'];ly+=(64 if label['text'].startswith('COMMON') else 24) if label.get('kind')=='corridor' else 42;d.multiline_text((lx,ly),text,font=f,anchor='mm',align='center',spacing=3,fill=col,stroke_width=2,stroke_fill=white)
 # Header and overall footprint dimensions are derived from saved camera projection.
 d.text((58,48),'CASA DEI COLORI',font=ft(30),fill=col);d.text((58,94),meta['level']+' / FURNISHED PLAN',font=ft(22),fill=col)
 d.text((58,128),f"FFL +{meta['elevation']:.2f} m",font=ft(20),fill=col)
 d.text((58,280),'○ Native lighting points\n(symbols; not a circuit design)',font=ft(15),fill=col,spacing=7)
 d.text((58,173),'Concept design\nNot a code / permit drawing\nNorth up; dimensions in metres',font=ft(15),fill=col,spacing=7)
 c0,c1,c2,c3=meta['dimension_corners'];yy=c0[1]+30;xx=c0[0]-32
 d.line([(c0[0],c0[1]),(c0[0],yy+8),(c0[0],yy),(c1[0],yy),(c1[0],c1[1])],fill=col,width=2)
 for x in [c0[0],c1[0]]:d.line([(x-6,yy+6),(x+6,yy-6)],fill=col,width=2)
 d.text(((c0[0]+c1[0])/2,yy-5),'26.00 m',font=ft(19),fill=col,anchor='ms',stroke_width=3,stroke_fill=white)
 d.line([(c0[0],c0[1]),(xx-8,c0[1]),(xx,c0[1]),(xx,c2[1]),(c2[0],c2[1])],fill=col,width=2)
 d.text((xx-12,(c0[1]+c2[1])/2),'20.00 m',font=ft(19),fill=col,anchor='rm',stroke_width=3,stroke_fill=white)
 for y in [c0[1],c2[1]]:d.line([(xx-6,y+6),(xx+6,y-6)],fill=col,width=2)
 x,y=W-135,150;d.line([(x,y+110),(x,y)],fill=col,width=4);d.polygon([(x,y-18),(x-13,y+16),(x+13,y+16)],fill=col);d.text((x,y-40),'N',font=ft(28),fill=col,anchor='mm')
 x,y=60,H-110;step=meta['scale_pixels_per_metre'];d.text((x,y-40),'METRIC SCALE',font=ft(16),fill=col)
 for i in range(5):
  d.rectangle((x+i*step,y,x+(i+1)*step,y+12),fill=col if i%2==0 else white,outline=col,width=1);d.text((x+i*step,y+20),str(i),font=ft(14),fill=col)
 d.text((x+5*step,y+20),'5 m',font=ft(14),fill=col)
 im.save(p,optimize=True);meta['annotation']='Pillow overlay: actual programme room labels, actual luminaire-position symbols, door swings, measured footprint dimensions, north arrow and camera-derived metric scale. Bundled DejaVu Sans licence.';(ROOT/'evidence/producer'/('render-'+view+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
if __name__=='__main__':annotate(sys.argv[1])
