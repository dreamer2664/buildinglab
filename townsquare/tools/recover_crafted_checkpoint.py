"""Anonymous pinned recovery of actual latest preserved R13, including missing source receipts."""
from pathlib import Path
import urllib.request,hashlib,zipfile,json,shutil
R=Path(__file__).resolve().parents[1];folder=R/'.cache/recovered-crafted';folder.mkdir(parents=True,exist_ok=True);name='Winterlichtplatz-UNPROMOTED-rebuilt-editable-b8ea5ed69e0a-8bd26279c1b8.zip';url='https://github.com/dreamer2664/storagecode/releases/download/townsquare/blender/candidate-20261017-7fb9ce64d020/'+name;expected='b5dfc99472995638ba08b441dcb05970f164cd6766b64e33bfbca21a8691f8be';p=folder/name
if not p.exists():
 with urllib.request.urlopen(url,timeout=180)as src,p.open('wb')as dst:shutil.copyfileobj(src,dst)
with p.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected
native_sha='b8ea5ed69e0af9436a6b9fa80be9409ec506ef4a233f10b4e2ddea4c02fd23fb';native=R/'.cache/crafted-exteriors/Winterlichtplatz-crafted-exteriors-UNPROMOTED.blend';native.parent.mkdir(parents=True,exist_ok=True);restored=[]
with zipfile.ZipFile(p)as z:
 assert z.testzip()is None;m=json.loads(z.read('MANIFEST.json'))
 for n,row in m['members'].items():
  with z.open(n)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],n
  if n.endswith('.blend')and row['sha256']==native_sha:dest=native
  elif n.startswith(('evidence/production/','assets/','design/','tools/production/'))and Path(n).suffix in ['.json','.md','.svg','.txt','.py','.png','.jpg']:
   dest=(R/n).resolve();assert dest.is_relative_to(R)
   if dest.exists():continue
  else:continue
  dest.parent.mkdir(parents=True,exist_ok=True)
  with z.open(n)as src,dest.open('wb')as dst:shutil.copyfileobj(src,dst)
  restored.append(str(dest.relative_to(R)))
with native.open('rb')as f:assert hashlib.file_digest(f,'sha256').hexdigest()==native_sha
receipt={'asset':name,'url':url,'bytes':p.stat().st_size,'sha256':expected,'study_native_sha256':native_sha,'study_native_bytes':native.stat().st_size,'archive_CRC_and_every_member_SHA_bytes':'ACTUAL_ANONYMOUS_PASS','storage_ledger_commit':'9a919bf0344f4123fa7708ab9803bdcd3d6718c9','restored_missing_files':restored};(R/'evidence/production/R13-crafted-exteriors-native-public-backup.json').write_text(json.dumps(receipt,indent=2)+'\n');print('ACTUAL_CRAFTED_NATIVE_AND_MISSING_RECEIPTS_RECOVERED',native_sha,len(restored),flush=True)
