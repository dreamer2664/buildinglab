"""Restore missing immutable assets from the actual public checkpoint receipt.
No credentials. Never overwrites a changed existing regular file. A compressed raw
GLB is retained for workspace snapshot limits; public downloads remain authoritative.
"""
from pathlib import Path
import gzip,hashlib,json,shutil,urllib.request
R=Path(__file__).resolve().parents[2]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
r=json.loads((R/'exports/checkpoint-receipt.json').read_text())
for name,row in r['assets'].items():
 p=R/name;assert p.resolve(strict=False).is_relative_to(R)
 if p.exists():
  assert sha(p)==row['sha256'],'Changed local file; refusing overwrite: '+name
  continue
 if p.is_symlink():p.unlink()
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.restore.tmp')
 z=p.with_suffix(p.suffix+'.gz')
 if z.exists():
  with gzip.open(z,'rb') as a,tmp.open('wb') as b:shutil.copyfileobj(a,b)
 else:
  assert row['url'].startswith('https://github.com/dreamer2664/storagecode/releases/download/')
  with urllib.request.urlopen(row['url'],timeout=180) as a,tmp.open('wb') as b:shutil.copyfileobj(a,b)
 assert tmp.stat().st_size==row['bytes'] and sha(tmp)==row['sha256'],'Public asset integrity failure'
 tmp.replace(p);print('RESTORED_VERIFIED',name)
print('Available checkpoint assets match recorded public SHA-256; no inspection inferred.')
