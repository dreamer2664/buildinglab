"""Restore disposable runtime from immutable public sources. No credentials or renderer secrets."""
from pathlib import Path
import urllib.request,hashlib,zipfile,tarfile,json,concurrent.futures,shutil
R=Path(__file__).resolve().parents[1];C=R/'.cache';C.mkdir(exist_ok=True);H=Path('/home/user/.cache');H.mkdir(exist_ok=True)
pub=json.loads((R/'evidence/production/public-package-recovery.json').read_text());people=next(x for x in pub if x['package']=='People-rigs')
items=[('R7-Master.zip','https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-d5ea619e187b/Winterlichtplatz-R7-Master-d5ea619e187b.zip','ff53b77b114784dd262d7f3d8e2e482e47180511e2d759622360222976e17e11'),('recovery/Winterlichtplatz-People-rigs-4bf44a021c3d.zip',people['url'],people['archive_sha256']),('blender.tar.xz','https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz?townsquare=production','4da1c956673c0485e63054e563ee69198cc8f80d8157dd7592dffc8a6a5592e6')]
def get(row):
 name,url,expected=row;p=C/name;p.parent.mkdir(parents=True,exist_ok=True)
 if not p.exists():
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  with urllib.request.urlopen(request,timeout=180) as src,p.with_suffix('.partial').open('wb') as dst:
   while b:=src.read(1024*1024):dst.write(b)
  p.with_suffix('.partial').replace(p)
 h=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
 if expected:assert h==expected,(name,h,expected)
 print('RESTORED_PUBLIC_BYTES',name,p.stat().st_size,h,flush=True);return p
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:paths=list(pool.map(get,items))
for p in paths[:2]:
 with zipfile.ZipFile(p) as z:
  mn='MANIFEST.json' if 'MANIFEST.json' in z.namelist() else 'Package-MANIFEST.json';m=json.loads(z.read(mn))
  for name,row in m['members'].items():
   with z.open(name) as f:h=hashlib.file_digest(f,'sha256').hexdigest()
   assert h==row['sha256'],name
  assert z.testzip() is None
  if p.name=='R7-Master.zip':
   for a,b in [('Master/Winterlichtplatz.blend','.cache/master/Winterlichtplatz-R7.blend'),('Master/Winterlichtplatz-render-derivative.blend','.cache/master/Winterlichtplatz-render-R7.blend')]:
    dest=R/b;dest.parent.mkdir(parents=True,exist_ok=True)
    with z.open(a) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
   for name in z.namelist():
    if name.startswith('provenance/'):
     dest=C/'recovery/master'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(z.read(name))
 print('RESTORED_PUBLIC_EVERY_MEMBER_VERIFIED',p.name,flush=True)
if not (H/'blender-4.3.2-linux-x64/blender').exists():
 with tarfile.open(paths[2]) as t:t.extractall(H,filter='data')
print('RUNTIME_PUBLIC_SOURCES_RESTORED',flush=True)
