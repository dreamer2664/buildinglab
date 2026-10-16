"""Small, disclosed view-ID captions on real render pixels; no invented geometry."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
TITLES={'L01-interior':'L01 / NEIGHBOURHOOD CAFE','L01-detail':'L01 / RECEPTION + MAIL','L02-interior':'L02 / HOME 2A — LIVING + KITCHEN','L02-detail':'L02 / HOME 2C — BATHROOM','L03-interior':'L03 / HOME 3B — LIVING + KITCHEN','L03-detail':'L03 / HOME 3C — BEDROOM 1','L04-interior':'L04 / HOME 4C — FAMILY LIVING','L04-detail':'L04 / HOME 4C — BEDROOM 2','L05-interior':'L05 / HOME 5A — LIVING + KITCHEN','L05-detail':'L05 / HOME 5B — BEDROOM','L06-interior':'L06 / SHARED WINTER GARDEN','L06-detail':'L06 / PENTHOUSE 6A — LIVING','exterior-day':'CASA DEI COLORI / DAY','exterior-dusk':'CASA DEI COLORI / DUSK','all-levels-section':'L01–L06 / FURNISHED SECTION','technical-structure-core':'L01–L06 / STRUCTURE + DUAL STAIR CORE','technical-facade-material':'FACADE / REVEALS, GLAZING + BALCONY'}
def caption(view):
 p=R/'renders/final'/(view+'.png');im=Image.open(p).convert('RGB');W,H=im.size;overlay=Image.new('RGBA',im.size);d=ImageDraw.Draw(overlay);n=25 if W>=3840 else 18;f=ImageFont.truetype(str(R/'evidence/producer/fonts/DejaVuSans.ttf'),n)
 title=TITLES.get(view,view.split('-')[0]+' / FURNISHED FLOOR CUTAWAY');x,y=48,H-72;w=d.textlength(title,font=f)+36;d.rounded_rectangle((x-16,y-12,x+w,y+n+13),radius=6,fill=(248,245,235,230));d.text((x,y),title,font=f,fill='#173f3b')
 Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB').save(p,optimize=True)
 meta_path=R/'evidence/producer'/('render-'+view+'.json');m=json.loads(meta_path.read_text());m['caption']=title;m['annotation']='View-ID caption only; actual saved-scene render; external tiled OIDN.';meta_path.write_text(json.dumps(m,indent=2)+'\n')
if __name__=='__main__':caption(sys.argv[1])
