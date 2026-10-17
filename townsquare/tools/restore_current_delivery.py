"""Restore the latest durable R11 native/rig/frame checkpoint after disposable cache loss.
Run tools/bootstrap_runtime.py first for Blender. Public HTTPS only; no credentials.
This is recovery, not evidence that images were inspected.
"""
from pathlib import Path
import urllib.request,zipfile,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];E=R/'evidence/production';p=json.loads((E/'R11-public-checkpoint.json').read_text());C=R/'.cache/restored-current';C.mkdir(parents=True,exist_ok=True)
def restore_archive(row):
 dest=C/row['asset']
 if not dest.exists():
  with urllib.request.urlopen(row['url'],timeout=180) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
 with dest.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
 z=zipfile.ZipFile(dest);assert z.testzip() is None;m=json.loads(z.read('MANIFEST.json'))
 for n,r in m['members'].items():
  with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256'],n
  assert z.getinfo(n).file_size==r['bytes']
 return z
for row in p['archives']+([p['unchanged_editable_people_archive']] if p.get('unchanged_editable_people_archive') else []):
 with restore_archive(row) as z:
  for name in z.namelist():
   if name=='Master/Winterlichtplatz.blend':dest=R/'.cache/master/Winterlichtplatz-R11.blend'
   elif name=='Master/Winterlichtplatz-render-derivative.blend':dest=R/'.cache/master/Winterlichtplatz-render-R11.blend'
   elif name.startswith('People/') and name.endswith('.blend'):dest=R/'.cache/fixed-people/rigs'/Path(name).name
   elif name.startswith('provenance/'):dest=R/'.cache/recovery/master'/name
   else:continue
   dest.parent.mkdir(parents=True,exist_ok=True)
   with z.open(name) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
 print('CURRENT_PUBLIC_NATIVE_OR_RIGS_RESTORED',row['asset'],flush=True)
additional=E/'R11-additional-public-packages.json'
if additional.exists():
 for row in json.loads(additional.read_text())['archives']:
  if not any(t in row['asset'] for t in ['Buildings-','Public-realm','Portable-town']):continue
  with restore_archive(row) as z:
   for name in z.namelist():
    if name.startswith('Buildings/') and name.endswith('.blend'):dest=R/'.cache/final-components/Native'/Path(name).name
    elif name.startswith('GLB/') and name.endswith('.glb'):dest=R/'.cache/final-components/GLB'/Path(name).name
    elif name=='Public/PUBLIC.blend':dest=R/'.cache/final-components/Native/PUBLIC.blend'
    elif name=='Public/PUBLIC.glb':dest=R/'.cache/final-components/GLB/PUBLIC.glb'
    elif name=='Portable/Winterlichtplatz.glb':dest=R/'.cache/final-components/Winterlichtplatz-R11.glb'
    elif name=='Portable/Actual-clean-reimport.blend':dest=R/'.cache/final-components/Winterlichtplatz-GLB-clean-reimport.blend'
    elif name.startswith('Portable/Variants/') and name.endswith('.glb'):dest=R/'.cache/final-components/GLB'/Path(name).name
    else:continue
    dest.parent.mkdir(parents=True,exist_ok=True)
    with z.open(name) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
  print('CURRENT_PUBLIC_COMPONENT_OR_PORTABLE_ARCHIVE_RESTORED',row['asset'],flush=True)
cp=E/'R11-render-checkpoints.json'
if cp.exists():
 row=next((r for r in reversed(json.loads(cp.read_text())) if r['native_sha256']==p['full_resolution_native_sha256']),None)
 if row:
  with restore_archive(row) as z:
   paths=json.loads(z.read('Evidence/RESTORE.json'))
   for name,relative in paths.items():
    dest=(R/relative).resolve();assert dest.is_relative_to(R) and '.cache/final-renders/' in str(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with z.open(name) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
  print('CURRENT_PUBLIC_RENDER_CHECKPOINT_RESTORED',len(row['views']),'completed views; inspection only from existing actual manual ledger',flush=True)
model=R/'.cache/final-components/Winterlichtplatz-R11.glb'
if model.exists():
 link=R/'viewer/model.glb';link.unlink(missing_ok=True);link.symlink_to('../.cache/final-components/Winterlichtplatz-R11.glb')
print('CURRENT_DELIVERY_CACHE_RECOVERY_DONE. For rendering run Blender factory/background with tools/production/restore_packed_source_maps.py to recover exact source-map bytes from the restored full packed native. Archive/member checks and file restore finished; separately execute native/map/smoke/browser checks and actually open their originals. See recovery receipts for what was really tested.',flush=True)
