"""Declared technical PNG annotation of actual model render; no invented/interpolated geometry."""
from pathlib import Path
import json,hashlib,math,textwrap
from PIL import Image,ImageDraw,ImageFont

def annotate_plan(root,frame,path):
 R=Path(root);src=json.loads((R/'evidence/production/R11-plan-annotation-source.json').read_text());build=json.loads((R/'evidence/production/R11-native-build.json').read_text());assert src['source_native_sha256']==build['full_resolution_native_sha256'];p=src['plans'][frame['id']];programme=json.loads((R/'design/programme.json').read_text());b=next(b for b in programme['buildings'] if b['id']==frame['building_id']);floor=next(f for f in b['floors'] if f['id']==frame['floor_id'])
 before=hashlib.sha256(Path(path).read_bytes()).hexdigest();base=Image.open(path).convert('RGBA');w,h=base.size;layer=Image.new('RGBA',base.size,(0,0,0,0));d=ImageDraw.Draw(layer);ink=(22,43,45,255);accent=(33,101,91,255);font=lambda n:ImageFont.load_default(size=n);title=font(32);small=font(20);label=font(20);pxm=w/p['orthographic_scale_m']
 def xy(world):
  q=[world[k]-p['camera_origin'][k] for k in range(3)];return(w/2+sum(q[k]*p['camera_right_world'][k] for k in range(3))*pxm,h/2-sum(q[k]*p['camera_up_world'][k] for k in range(3))*pxm)
 d.rounded_rectangle((28,20,w-28,108),12,fill=(249,252,250,239));d.text((48,29),b['id']+' / L'+str(floor['index']+1).zfill(2)+'  |  '+b['brand'],font=title,fill=ink);d.text((48,73),'Actual furnished-floor model | '+textwrap.shorten(floor['programme'],width=155,placeholder='...'),font=small,fill=ink)
 for room in p['rooms']:
  rid=room['room_id'];name=(rid[len(frame['floor_id'])+1:] if rid and rid.startswith(frame['floor_id']) else str(rid)).replace('_',' ').title();name='\n'.join(textwrap.wrap(name,22));cx,cy=xy(room['world_centre']);box=d.multiline_textbbox((0,0),name,font=label,align='center',spacing=2);tw,th=box[2]-box[0],box[3]-box[1];d.rounded_rectangle((cx-tw/2-8,cy-th/2-8,cx+tw/2+8,cy+th/2+8),5,fill=(255,255,255,225),outline=(74,108,99,220));d.multiline_text((cx-tw/2,cy-th/2-box[1]),name,font=label,align='center',fill=ink,spacing=2)
 # North is projected from actual saved camera basis, not assumed image-up.
 cx,cy=w-110,195;vx=p['camera_right_world'][1];vy=-p['camera_up_world'][1];length=math.hypot(vx,vy);vx,vy=vx/length,vy/length;tip=(cx+vx*53,cy+vy*53);d.ellipse((cx-66,cy-66,cx+66,cy+66),fill=(249,252,250,235));d.line([(cx-vx*30,cy-vy*30),tip],fill=accent,width=5);d.polygon([tip,(tip[0]-vx*17-vy*9,tip[1]-vy*17+vx*9),(tip[0]-vx*17+vy*9,tip[1]-vy*17-vx*9)],fill=accent);d.text((cx+vx*73-9,cy+vy*73-10),'N',font=font(24),fill=ink)
 # Footprint dimensions are the documented model design dimensions, not a code survey.
 d.rounded_rectangle((28,h-87,w-28,h-20),10,fill=(249,252,250,241));bar=round(5*pxm);x,y=48,h-58
 for i in range(5):d.rectangle((x+round(i*bar/5),y,x+round((i+1)*bar/5),y+10),fill=ink if i%2==0 else(255,255,255,255),outline=ink)
 d.text((x,y-23),'0',font=small,fill=ink);d.text((x+bar-30,y-23),'5 m',font=small,fill=ink);note='Footprint '+str(b['footprint_m'][0])+' x '+str(b['footprint_m'][1])+' m | datum '+str(floor['datum_m'])+' m | storey '+str(floor['height_m'])+' m | conceptual, not code-certified';d.text((max(x+bar+35,620),h-62),note,font=small,fill=ink)
 Image.alpha_composite(base,layer).convert('RGB').save(path);base.close();layer.close();return {'type':'Technical room/floor/programme/metric-scale/actual-camera-north annotation, not generated geometry','source_native_sha256':src['source_native_sha256'],'annotation_source':'evidence/production/R11-plan-annotation-source.json','underlying_denoised_model_render_sha256':before,'actual_room_centres_labelled':len(p['rooms']),'footprint_dimensions_m':b['footprint_m'],'scale_bar_m':5,'font':'Pillow bundled default TrueType; no external font/network dependency'}
