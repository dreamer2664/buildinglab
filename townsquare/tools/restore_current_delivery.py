"""Restore the latest durable R10 native/rig/frame checkpoint after disposable cache loss.
Run tools/bootstrap_runtime.py first for Blender. Public HTTPS only; no credentials.
This is recovery, not evidence that images were inspected.
"""
from pathlib import Path
import urllib.request,zipfile,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];E=R/'evidence/production';p=json.loads((E/'R10-public-checkpoint.json').read_text());C=R/'.cache/restored-current';C.mkdir(parents=True,exist_ok=True)
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
for row in p['archives']:
 with restore_archive(row) as z:
  for name in z.namelist():
   if name=='Master/Winterlichtplatz.blend':dest=R/'.cache/master/Winterlichtplatz-R10.blend'
   elif name=='Master/Winterlichtplatz-render-derivative.blend':dest=R/'.cache/master/Winterlichtplatz-render-R10.blend'
   elif name.startswith('People/') and name.endswith('.blend'):dest=R/'.cache/fixed-people/rigs'/Path(name).name
   elif name.startswith('provenance/'):dest=R/'.cache/recovery/master'/name
   else:continue
   dest.parent.mkdir(parents=True,exist_ok=True)
   with z.open(name) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst)
 print('CURRENT_PUBLIC_NATIVE_OR_RIGS_RESTORED',row['asset'],flush=True)
cp=E/'R10-render-checkpoints.json'
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
print('CURRENT_DELIVERY_CACHE_RECOVERY_DONE',flush=True)
