"""Expand to the actual licensed100-pose/10-person dataset, never invent identity counts."""
import requests,json,hashlib,zipfile,concurrent.futures,io
from pathlib import Path
from PIL import Image
REV='9cc5e9c138dd310dc88c95c80e5db0a3ecb7971a';ROOT=Path(__file__).resolve().parents[1]/'assets/district';ROOT.mkdir(parents=True,exist_ok=True);API='https://huggingface.co/api/datasets/digitalrealitylab/HSRD-100/tree/'+REV+'/'
response=requests.get(API+'data',params={'recursive':'false','limit':1000},timeout=60);response.raise_for_status();subjects=response.json()
def listing(x):
 rr=requests.get(API+x['path'],params={'recursive':'true','limit':1000},timeout=60);rr.raise_for_status();j=rr.json();return [z for z in j if z['path'].endswith('-Scan-LOD2.zip') and z.get('size',0)>100000 and z.get('lfs',{}).get('oid')]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:entries=[e for xs in ex.map(listing,subjects) for e in xs]
(ROOT/'DATASET_PINNED_LOD2_TREE.json').write_text(json.dumps(entries,indent=2));print('VERIFIED_TREE',len(entries),'poses',len({e['path'].split('/')[1] for e in entries}),'identities',flush=True)
assert len({e['path'].split('/')[1] for e in entries})==10
old={'HSR0015-Body-009','HSR0023-Body-017','HSR0027-Body-004','HSR0028-Body-010','HSR0040-Body-004','HSR0042-Body-002'};existing={e['pose_id']:e for e in json.loads((ROOT/'SCAN_PROVENANCE.json').read_text())} if (ROOT/'SCAN_PROVENANCE.json').exists() else {}
def download(e):
 pose=e['path'].split('/')[2];sub=e['path'].split('/')[1]
 if pose in old:return None
 if pose in existing and (ROOT/'scans'/pose/'diffuse.jpg').exists():return existing[pose]
 url='https://huggingface.co/datasets/digitalrealitylab/HSRD-100/resolve/'+REV+'/'+e['path'];rr=requests.get(url,timeout=180);rr.raise_for_status();data=rr.content;actual=hashlib.sha256(data).hexdigest();assert actual==e['lfs']['oid'],(pose,actual,e['lfs']['oid']);assert len(data)==e['size']
 dest=ROOT/'scans'/pose;dest.mkdir(parents=True,exist_ok=True);obj_hash=None;tex_hash=None
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  for name in z.namelist():
   if name.lower().endswith('.obj'):
    buf=z.read(name);(dest/Path(name).name).write_bytes(buf);obj_hash=hashlib.sha256(buf).hexdigest()
   if 'diffuse' in name.lower() and name.lower().endswith('.png'):
    buf=z.read(name);tex_hash=hashlib.sha256(buf).hexdigest();im=Image.open(io.BytesIO(buf)).convert('RGB');im.thumbnail((1024,1024));im.save(dest/'diffuse.jpg',quality=94)
 assert obj_hash and tex_hash,pose
 rec={'subject_id':sub,'pose_id':pose,'lod':'LOD2','dataset':'digitalrealitylab/HSRD-100','revision':REV,'license':'CC BY4.0','url':url,'zip_bytes':len(data),'zip_sha256':actual,'obj_sha256':obj_hash,'tex_sha256':tex_hash,'changes':'ExplicitZ-up metric import; economical mesh decimation;1024diffuseJPEG; linked pose placements. Modern clothing, no certified period costume. Dataset contains10identities, not100.'}
 (dest/'PROVENANCE.json').write_text(json.dumps(rec,indent=2));print('SCAN',pose,flush=True);return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:records=[r for r in ex.map(download,entries) if r]
records=sorted(records,key=lambda e:e['pose_id']);(ROOT/'SCAN_PROVENANCE.json').write_text(json.dumps(records,indent=2));print('READY',len(records),'additional-libraryposes plus6original source poses;',len(records)+6,'totalposes;',len({e['subject_id'] for e in records}),'uniqueidentities',flush=True)
