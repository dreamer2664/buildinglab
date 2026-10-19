"""Restore verified packed photographic maps; resampling is explicitly recorded."""
import bpy,json,re,hashlib,gc
from pathlib import Path

def upgrade_images(root,frame=None,full_resolution=False):
 R=Path(root);manifest=json.loads((R/'evidence/production/native-source-map-manifest.json').read_text());groups={}
 def base(n):return re.sub(r'\.\d{3}$','',n)
 for rec in manifest:groups.setdefault(base(rec['name']),[]).append(rec)
 changes=[]
 # Pixel-exact datablock deduplication avoids decoding identical photograph bytes repeatedly.
 registry={}
 for image in list(bpy.data.images):
  if not image.users or not image.packed_file or image.source!='FILE':continue
  key=(hashlib.sha256(image.packed_file.data).hexdigest(),image.colorspace_settings.name,image.alpha_mode)
  if key in registry:
   name=image.name;image.user_remap(registry[key]);bpy.data.images.remove(image);changes.append({'image':name,'pixel_exact_shared_packed_image':registry[key].name,'source_packed_sha256':key[0],'scope':'Pixel-exact packed bytes/colourspace/alpha interpretation, no resampling or material mapping change'})
  else:registry[key]=image
 for old in list(bpy.data.images):
  if old.users==0 or old.source!='FILE':continue
  if old.name.startswith('HSRD100_') and not full_resolution:
   assert old.packed_file,'Scan photo must be self-contained'
   original_manifest=R/'evidence/production/R12-render-scan-original-photos.json';original=None
   if original_manifest.exists():
    m=json.loads(original_manifest.read_text())
    if m['source_full_native_sha256']==bpy.context.scene.get('source_authoritative_full_native_sha256'):original=next((r for r in m['rows']if r['name']==old.name),None)
   raw=(R/original['file']).read_bytes()if original else old.packed_file.data;source_hash=hashlib.sha256(raw).hexdigest()
   if original:assert source_hash==original['source_packed_sha256']
   oldname=old.name;color=old.colorspace_settings.name;source=(int.from_bytes(raw[16:20],'big'),int.from_bytes(raw[20:24],'big'));cap=2048 if frame['kind']=='people' else (512 if frame['kind'] in ['town','aerial'] else 1024);factor=min(1,cap/max(source));dest=tuple(max(1,round(x*factor))for x in source)
   if dest==source:old.buffers_free();continue
   folder=R/'.cache/scan-render-source-photos';folder.mkdir(exist_ok=True);p=folder/(source_hash+'.png')
   if not p.exists():p.write_bytes(raw)
   del raw
   new=bpy.data.images.load(str(p),check_existing=False);new.colorspace_settings.name=color;new.scale(*dest);new.pack();new.buffers_free();old.user_remap(new);bpy.data.images.remove(old);new.name=oldname;changes.append({'image':oldname,'source_packed_sha256':source_hash,'source_dimensions':source,'render_dimensions':dest,'cap_px':cap,'scope':'Render-only source-photo resampling; geometry/UV unchanged and full4kpacked source retained in immutable native'});gc.collect();continue
  if old.name.startswith('MARKTGRUEN_PRODUCTS_')and not full_resolution:
   ledger=json.loads((R/'assets/branding/products/manifest.json').read_text());p=R/ledger['atlas'];assert hashlib.sha256(p.read_bytes()).hexdigest()==ledger['atlas_sha256'];name=old.name;color=old.colorspace_settings.name;cap=1536 if frame['kind']=='interior'else 1024 if frame.get('id')=='H03'else 512;new=bpy.data.images.load(str(p),check_existing=False);new.colorspace_settings.name=color;source=tuple(new.size);factor=min(1,cap/max(source));dest=tuple(round(x*factor)for x in source)
   if dest!=source:new.scale(*dest)
   new.pack();new.buffers_free();old.user_remap(new);bpy.data.images.remove(old);new.name=name;changes.append({'image':name,'source_original_graphic_sha256':ledger['atlas_sha256'],'source_dimensions':source,'render_dimensions':dest,'cap_px':cap,'scope':'Original fictional package atlas, no image generation or geometry substitution'});continue
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
   if re.match(r'^B\d\d\.png',oldname):
    target=frame.get('building_id')or {'H03':'B01','H04':'B03','H06':'B09'}.get(frame.get('id'));cap=2048 if target and base(oldname)==target+'.png'else 512
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
