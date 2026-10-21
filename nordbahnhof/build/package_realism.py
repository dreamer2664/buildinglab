"""Package only the current realism revision and honest evidence. Run after visual review."""
from pathlib import Path
import json,hashlib,zipfile,base64,html,shutil
from PIL import Image,ImageOps,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1];D=R.parent/'deliverables';D.mkdir(exist_ok=True)
N=R/'renders/realism/native';records=[]
for p in sorted(N.glob('REALVIEW_*.json')):
 j=json.loads(p.read_text());assert j['visual_inspection']!='PENDING',p
 assert j['sha256']==hashlib.sha256((N/j['file']).read_bytes()).hexdigest()
 assert j['samples']==128 and j['resolution']==[2560,1440] and len(j['tiles'])==4
 records.append(j)
assert len(records)==6,len(records)
audit=json.loads((R/'evidence/REALISM_SCENE_AUDIT.json').read_text());assert audit['all_image_assets_packed'] and audit['vehicle_count']==34 and audit['rake_count']==6
assert audit['source_sha256']==hashlib.sha256((R/'source/NORDBAHNHOF_REALISM.blend').read_bytes()).hexdigest()
assert all(t['source_sha256']==audit['source_sha256'] for j in records for t in j['tiles'])
manifest={'status':'six native final images visually opened; full commission incomplete','views':records,'source_sha256':audit['source_sha256'],'cycles_render_seconds_total':sum(j['cycles_render_seconds'] for j in records)}
(N/'RENDER_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
titles=['Arrival after rain','Oil, steel & spokes','Winter travellers','Glass, iron & distance','Along the coaches','Electric roof gear']
images=[]
for rec,title in zip(records,titles):
 p=N/rec['file'];images.append({'title':title,'name':p.name,'src':'data:image/jpeg;base64,'+base64.b64encode(p.read_bytes()).decode()})
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NORDBAHNHOF — after the rain</title><link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2032%2032%27%3E%3Crect%20width%3D%2732%27%20height%3D%2732%27%20fill%3D%27%23111412%27%2F%3E%3Ctext%20x%3D%277%27%20y%3D%2724%27%20fill%3D%27%23d4c793%27%20font-size%3D%2724%27%3EN%3C%2Ftext%3E%3C%2Fsvg%3E">
<style>*{box-sizing:border-box}body{margin:0;background:#111412;color:#e9ece6;font:15px/1.5 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:28px}header{display:flex;justify-content:space-between;align-items:end;gap:16px}small,.meta{color:#aab5a9}.eyebrow{text-transform:uppercase;letter-spacing:.22em;color:#b5bc98;font-size:11px}h1{font-weight:450;font-size:clamp(28px,4vw,48px);letter-spacing:.07em;line-height:1.1;margin:10px 0}header p{margin:8px 0 18px}.badge{border:1px solid #3b443c;border-radius:4px;padding:8px 12px;white-space:nowrap;font-size:12px}.stage{margin-top:22px;background:#080b09;overflow:auto;border:1px solid #303a32;position:relative}.stage img{display:block;width:100%;height:auto;max-height:68vh;object-fit:contain;cursor:zoom-in}.stage.zoom img{width:2560px;max-width:none;max-height:none;cursor:zoom-out}.bar{display:flex;justify-content:space-between;align-items:center;margin:16px 0;gap:16px}button,a{background:#222b24;border:1px solid #435043;border-radius:4px;color:#e4eadd;padding:8px 14px;cursor:pointer;text-decoration:none;font:inherit}.controls{display:flex;gap:8px}.title{font-size:18px;margin-bottom:3px}.thumbs{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:24px 0}.thumbs button{padding:0;overflow:hidden;background:#1a201c;text-align:left;border:1px solid #364037}.thumbs img{width:100%;display:block;aspect-ratio:16/9;object-fit:cover}.thumbs span{display:block;padding:9px;font-size:12px}.thumbs button.active{border-color:#d4c793;box-shadow:0 0 0 1px #d4c793}footer{border-top:1px solid #344037;margin-top:28px;padding-top:18px;color:#aab5a9;font-size:12px}footer p{max-width:1100px}@media(max-width:760px){main{padding:16px}.thumbs{grid-template-columns:repeat(3,1fr)}header{display:block}.bar{align-items:start}.controls{flex-wrap:wrap}.badge{display:inline-block}}
</style><main><header><div><div class="eyebrow">A built scene · a surface & construction revision</div><h1>NORDBAHNHOF</h1><p>After the rain. Iron, damp stone and winter travellers.</p></div><div class="badge">6 native views · 2560 × 1440 · 128 spp</div></header><div class="stage" id="stage"><img id="hero" alt=""></div><div class="bar"><div><div class="title" id="title"></div><div class="meta" id="count"></div></div><div class="controls"><button id="prev" aria-label="Previous image">←</button><button id="next" aria-label="Next image">→</button><button id="zoom">Inspect 1:1</button><a id="download" download>Save image</a></div></div><div class="thumbs" id="thumbs"></div><footer><p>Actual Blender Cycles renders, externally denoised in HDR with Intel OIDN and colour-managed with AgX. No generative-image replacements, no image upscaling. Click the large image for a native-pixel inspection.</p><p>The packed source retains six rakes / 34 vehicles. These camera renders isolate the hero rake and omit closed interior fittings to fit the workstation’s RAM budget. Six modern photographic human scans are CC BY 4.0; Poly Haven surface maps and sky are CC0. Full attribution, source inventory, render records, rebuilding instructions and limitations are included with the download. The full original station commission remains incomplete.</p></footer></main><script>const images=IMAGES;let index=0;const hero=document.getElementById('hero'),stage=document.getElementById('stage');function select(i){index=(i+images.length)%images.length;const im=images[index];hero.src=im.src;hero.alt=im.title;document.getElementById('title').textContent=im.title;document.getElementById('count').textContent=String(index+1).padStart(2,'0')+' / 06 · Native Cycles image';const d=document.getElementById('download');d.href=im.src;d.download=im.name;document.querySelectorAll('.thumbs button').forEach((b,j)=>b.classList.toggle('active',j===index));stage.classList.remove('zoom');document.getElementById('zoom').textContent='Inspect 1:1'}function zoom(){stage.classList.toggle('zoom');document.getElementById('zoom').textContent=stage.classList.contains('zoom')?'Fit image':'Inspect 1:1'}images.forEach((im,i)=>{const b=document.createElement('button');b.innerHTML='<img alt=""><span></span>';b.querySelector('img').src=im.src;b.querySelector('span').textContent=String(i+1).padStart(2,'0')+' '+im.title;b.onclick=()=>select(i);document.getElementById('thumbs').appendChild(b)});document.getElementById('prev').onclick=()=>select(index-1);document.getElementById('next').onclick=()=>select(index+1);document.getElementById('zoom').onclick=zoom;hero.onclick=zoom;document.addEventListener('keydown',e=>{if(e.key==='ArrowLeft')select(index-1);if(e.key==='ArrowRight')select(index+1)});select(0);</script></html>'''.replace('IMAGES',json.dumps(images,separators=(',',':')))
gallery=D/'NORDBAHNHOF-realism-gallery.html';gallery.write_text(page);shutil.copy2(gallery,R/gallery.name)
fontpath='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';f1=ImageFont.truetype(fontpath,36);f2=ImageFont.truetype(fontpath,18);f3=ImageFont.truetype(fontpath,15)
canvas=Image.new('RGB',(2400,1576),(16,21,18));draw=ImageDraw.Draw(canvas)
draw.text((38,25),'NORDBAHNHOF  /  AFTER THE RAIN',font=f1,fill=(224,228,215));draw.text((40,75),'BUILT GEOMETRY · PHOTOGRAPHIC SURFACES · NATIVE CYCLES RENDERS',font=f3,fill=(160,176,158))
# Four inspected hero views; image assets are ordinary renderer output, not generated montage art.
for cell,i in enumerate([0,1,2,3]):
 x=24+(cell%2)*1192;y=116+(cell//2)*710
 im=Image.open(N/records[i]['file']).convert('RGB');im=ImageOps.fit(im,(1168,657),method=Image.Resampling.LANCZOS)
 canvas.paste(im,(x,y));draw.text((x+6,y+670),f'0{i+1}  {titles[i]}',font=f2,fill=(208,215,202))
preview=D/'NORDBAHNHOF-realism-preview.jpg';canvas.save(preview,quality=94,optimize=True)
readme=R/'REALISM_README.md';files=[readme,R/'source/NORDBAHNHOF_REALISM.blend',R/'source/NORDBAHNHOF_REBUILD.blend',R/gallery.name,R/'assets/ASSET_LICENSES.md']
for name in ['build_bay.py','rebuild_trains.py','realism_materials.py','realism_scene.py','realism_hardware.py','render_realism_raw.py','finish_realism.py','realism_agx.py','render_realism_final.py','package_realism.py']:files.append(R/'build'/name)
for folder in ['assets/realism','assets/scans']:
 files += [p for p in (R/folder).rglob('*') if p.is_file()]
for name in ['REALISM_SCENE_AUDIT.json','REALISM_VISUAL_REVIEW.md','REALISM_GALLERY_QA.md','TRAIN_BUILD_MANIFEST.json']:files.append(R/'evidence'/name)
files += sorted(N.glob('*.jpg'))+sorted(N.glob('*.json'))
# Only render records and current inspection. No old validators or inflated acceptance scores.
checksum=[]
for p in files:
 assert p.exists(),p
 checksum.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  nordbahnhof/'+str(p.relative_to(R)))
(R/'evidence/REALISM_SHA256SUMS').write_text('\n'.join(checksum)+'\n');files.append(R/'evidence/REALISM_SHA256SUMS')
full=D/'NORDBAHNHOF-realism-complete.zip'
with zipfile.ZipFile(full,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in files:z.write(p,'nordbahnhof/'+str(p.relative_to(R)))
 z.write(preview,'NORDBAHNHOF-realism-preview.jpg')
renderzip=D/'NORDBAHNHOF-realism-renders.zip'
with zipfile.ZipFile(renderzip,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(N.glob('*.jpg'))+sorted(N.glob('*.json')):z.write(p,p.name)
 z.write(gallery,gallery.name);z.write(preview,preview.name);z.write(readme,'README.md')
for p in [full,renderzip]:
 with zipfile.ZipFile(p) as z:assert z.testzip() is None
output={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [full,renderzip,preview,gallery]}
(D/'REALISM_PACKAGE.json').write_text(json.dumps(output,indent=2));print(json.dumps(output,indent=2))
