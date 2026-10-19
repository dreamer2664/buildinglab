"""Anonymous pinned HSRD-100 source intake; no credentials/no renderer execution."""
from pathlib import Path
import argparse,json,hashlib,urllib.request,zipfile,shutil
R=Path(__file__).resolve().parents[2];REV='9cc5e9c138dd310dc88c95c80e5db0a3ecb7971a';DS='digitalrealitylab/HSRD-100'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  while b:=f.read(1048576):h.update(b)
 return h.hexdigest()
def intake(pose,lod):
 assert pose.startswith('HSR')and all(c.isalnum()or c=='-'for c in pose)and lod in ['LOD0','LOD1','LOD2'];subject=pose.split('-')[0];rel=f'data/{subject}/{pose}/scans';name=f'{pose}-Scan-{lod}.zip';api=f'https://huggingface.co/api/datasets/{DS}/tree/{REV}/{rel}';rows=json.load(urllib.request.urlopen(api,timeout=90));row=next(r for r in rows if r['path'].endswith('/'+name));assert row['size']>1000000 and len(row['lfs']['oid'])==64
 url=f'https://huggingface.co/datasets/{DS}/resolve/{REV}/{rel}/{name}';folder=R/'.cache/scan-intake'/pose;folder.mkdir(parents=True,exist_ok=True);archive=folder/name
 if not archive.exists()or sha(archive)!=row['lfs']['oid']:
  partial=archive.with_suffix('.part')
  with urllib.request.urlopen(url,timeout=180)as response,partial.open('wb')as f:shutil.copyfileobj(response,f,1048576)
  assert partial.stat().st_size==row['size']and sha(partial)==row['lfs']['oid'];partial.replace(archive)
 assert archive.stat().st_size==row['size']and sha(archive)==row['lfs']['oid'];dest=folder/('extracted-'+lod);dest.mkdir(exist_ok=True);members=[]
 with zipfile.ZipFile(archive)as z:
  assert z.testzip()is None
  for member in z.infolist():
   if member.is_dir():continue
   relative=Path(member.filename);assert not relative.is_absolute()and'..'not in relative.parts;p=dest/relative;p.parent.mkdir(parents=True,exist_ok=True)
   with z.open(member)as a,p.open('wb')as f:shutil.copyfileobj(a,f,1048576)
   assert p.stat().st_size==member.file_size;members.append({'member':member.filename,'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)})
 suffix=''if lod=='LOD1'else'-'+lod;r={'stage':'ACTUAL licensed source ZIP/CRC/member digest intake, not adoption/acceptance','dataset':DS,'revision':REV,'pose':pose,'lod':lod,'source_url':url,'source_archive':str(archive.relative_to(R)),'source_archive_bytes':archive.stat().st_size,'source_archive_sha256':sha(archive),'upstream_LFS_sha256_matched':True,'license':'CC BY4.0','attribution':'Digital Reality Lab, HSRD-100 (2025), https://huggingface.co/datasets/digitalrealitylab/HSRD-100; https://creativecommons.org/licenses/by/4.0/; no endorsement. Changes: intake only, native origin normalization/lighting pending.','members':members};(R/'evidence/production'/('R12-actual-scan-intake-'+pose+suffix+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('ACTUAL_SCAN_ZIP_CRC_MEMBER_SHA_PASS',pose,lod,r['source_archive_bytes'],r['source_archive_sha256'],flush=True);return r
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--pose',required=True);a.add_argument('--lod',default='LOD1');v=a.parse_args();intake(v.pose,v.lod)
