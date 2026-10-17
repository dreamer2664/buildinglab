"""Restore verified packed photographic maps; resampling is explicitly recorded."""
import bpy,json,re,hashlib,gc
from pathlib import Path

def upgrade_images(root,frame=None,full_resolution=False):
 R=Path(root);manifest=json.loads((R/'evidence/production/native-source-map-manifest.json').read_text());groups={}
 def base(n):return re.sub(r'\.\d{3}$','',n)
 for rec in manifest:groups.setdefault(base(rec['name']),[]).append(rec)
 changes=[]
 for old in list(bpy.data.images):
  if old.users==0 or old.source!='FILE':continue
  choices=groups.get(base(old.name),[])
  if not choices:continue
  rec=max(choices,key=lambda x:x['bytes']);p=R/rec['file']
  if not p.exists():raise FileNotFoundError(p)
  oldname=old.name;color=old.colorspace_settings.name
  if full_resolution:
   new=bpy.data.images.load(str(p),check_existing=False);new.colorspace_settings.name=color;new.pack()
   row={'image':oldname,'source_packed_sha256':rec['sha256'],'mode':'original verified full-resolution packed bytes, no pixel resampling'}
  else:
   kind=frame['kind'];oldsize=tuple(old.size)
   cap=1024 if kind=='interior' else 512
   if kind in ['town','aerial'] and any(x in oldname for x in ['cobblestone','snow_','rough_plaster']):cap=1024
   if re.match(r'^B\d\d\.png',oldname):cap=2048
   if kind=='people' and any(x in oldname for x in ['young_','middleage_','old_']):cap=2048
   new=bpy.data.images.load(str(p),check_existing=False);new.colorspace_settings.name=color;source=tuple(new.size)
   factor=min(1,cap/max(source));dest=(max(1,round(source[0]*factor)),max(1,round(source[1]*factor)))
   if dest==oldsize:
    bpy.data.images.remove(new);old.buffers_free();continue
   if dest!=source:new.scale(*dest)
   new.pack();new.buffers_free()
   row={'image':oldname,'source_packed_sha256':rec['sha256'],'source_dimensions':source,'previous_derivative_dimensions':oldsize,'render_dimensions':dest,'cap_px':cap}
  old.user_remap(new);bpy.data.images.remove(old);new.name=oldname;changes.append(row);gc.collect()
 return changes
