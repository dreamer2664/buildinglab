"""Anonymous recovery of the latest published, unpromoted editable study after cache reset.
Uses the recorded immutable archive/member digests; does not create visual acceptance.
"""
from pathlib import Path
import urllib.request,json,zipfile,hashlib,shutil,datetime
R=Path(__file__).resolve().parents[1]
choices=[('R12-groomed-native-public-backup.json','R12-groomed-town.json'),('R12-wall-native-public-backup.json','R12-wall-corrected-interiors.json'),('R12-placement-native-public-backup.json','R12-placement-corrected-interiors.json')]
rn,bn=next((a,b)for a,b in choices if (R/'evidence/production'/a).exists());receipt=json.loads((R/'evidence/production'/rn).read_text());build=json.loads((R/'evidence/production'/bn).read_text());cache=R/'.cache/restored-placement-study';cache.mkdir(parents=True,exist_ok=True);archive=cache/receipt['asset']
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
if not archive.exists():
 with urllib.request.urlopen(receipt['url'],timeout=180)as src,archive.with_suffix('.partial').open('wb')as dst:shutil.copyfileobj(src,dst)
 archive.with_suffix('.partial').replace(archive)
assert sha(archive)==receipt['sha256'];native=R/build['native'];native.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(archive)as z:
 assert z.testzip()is None;m=json.loads(z.read('MANIFEST.json'));member=next(n for n,v in m['members'].items()if n.endswith('.blend')and v['sha256']==build['native_sha256']);assert m['members'][member]['sha256']==receipt['study_native_sha256']==build['native_sha256']
 for n,v in m['members'].items():
  with z.open(n)as f:assert hashlib.file_digest(f,'sha256').hexdigest()==v['sha256'],n
 with z.open(member)as src,native.open('wb')as dst:shutil.copyfileobj(src,dst)
assert sha(native)==build['native_sha256'];r={'stage':'ACTUAL_ANONYMOUS_STUDY_NATIVE_RECOVERY_SHA_CRC_PASS_NOT_ACCEPTANCE','archive_sha256':receipt['sha256'],'native_sha256':sha(native),'native':str(native.relative_to(R)),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};(R/'evidence/production/R12-placement-study-recovery.json').write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_PUBLISHED_PLACEMENT_STUDY_NATIVE_RESTORED',r['native_sha256'],flush=True)
