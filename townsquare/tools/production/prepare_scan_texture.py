"""Memory-bounded source photo resampling with libvips; no retouch/image generation.
Dependency: pip install pyvips pyvips-binary. Source/derivative SHA and dimensions recorded.
"""
from pathlib import Path
import json,argparse,hashlib
import pyvips
R=Path(__file__).resolve().parents[2]
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def prepare(pose,lod,size):
 suffix=''if lod=='LOD1'else'-'+lod;r=json.loads((R/'evidence/production'/('R12-actual-scan-intake-'+pose+suffix+'.json')).read_text());row=next(x for x in r['members']if x['member'].endswith('_diffuse.png'));src=R/row['path'];assert sha(src)==row['sha256'];pyvips.cache_set_max_mem(64*1024*1024);pyvips.cache_set_max(0);image=pyvips.Image.new_from_file(str(src),access='sequential');assert image.width<=16384 and image.height<=16384 and image.bands in [3,4];width,height=image.width,image.height;factor=min(1,size/max(width,height));out=src.parent/(pose+'_'+lod+'-'+str(size)+'-bounded.png');image.resize(factor,kernel='lanczos3').pngsave(str(out),compression=3);check=pyvips.Image.new_from_file(str(out),access='sequential');receipt={'source_photo':row,'actual_original_dimensions':[width,height],'derivative':str(out.relative_to(R)),'derivative_dimensions':[check.width,check.height],'derivative_sha256':sha(out),'method':'libvips sequential Lanczos3 source-photo resampling only; no retouch, generation or geometry changes','pose':pose,'lod':lod};(R/'evidence/production'/('R12-scan-texture-'+pose+'-'+lod+'-'+str(size)+'.json')).write_text(json.dumps(receipt,indent=2)+'\n');print('BOUNDED_ORIGINAL_PHOTO_RESAMPLE_PASS',pose,lod,receipt['derivative_dimensions'],receipt['derivative_sha256'],flush=True);return receipt
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--pose',required=True);a.add_argument('--lod',default='LOD1');a.add_argument('--size',type=int,default=4096);v=a.parse_args();prepare(v.pose,v.lod,v.size)
