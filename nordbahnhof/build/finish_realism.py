"""External Intel OIDN HDR denoise, then native Blender AgX JPEG output."""
from pathlib import Path
import OpenEXR,numpy as np,sys,subprocess,json,struct
P=Path(sys.argv[1]);f=OpenEXR.File(str(P),separate_channels=True);c=f.channels()
def rgb(prefix,letters):return np.stack([c[prefix+x].pixels for x in letters],axis=-1).astype(np.float32)
def pfm(p,a):
 h,w,_=a.shape
 with open(p,'wb') as o:o.write(f'PF\n{w} {h}\n-1.0\n'.encode());o.write(np.flipud(a).astype('<f4').tobytes())
raw=rgb('ViewLayer.Combined.','RGB');alb=rgb('ViewLayer.DiffCol.','RGB');normal=rgb('ViewLayer.Normal.','XYZ')
for name,data in [('color',raw),('albedo',alb),('normal',normal)]:pfm(P.with_suffix('.'+name+'.pfm'),data)
exe=Path.home()/'.cache/oidn/oidn-2.5.1.x86_64.linux/bin/oidnDenoise';out=P.with_suffix('.denoised.pfm')
subprocess.run([str(exe),'--hdr',str(P.with_suffix('.color.pfm')),'--alb',str(P.with_suffix('.albedo.pfm')),'--nrm',str(P.with_suffix('.normal.pfm')),'--threads','2','--maxmem','256','--quality','high','-o',str(out)],check=True)
with open(out,'rb') as o:
 assert o.readline().strip()==b'PF';w,h=map(int,o.readline().split());scale=float(o.readline());a=np.frombuffer(o.read(),dtype='<f4' if scale<0 else '>f4').reshape(h,w,3);a=np.flipud(a).copy()
q=P.with_suffix('.denoised.exr');OpenEXR.File({'compression':OpenEXR.ZIP_COMPRESSION},{k:a[:,:,i].astype(np.float16) for i,k in enumerate('RGB')}).write(str(q))
print(q)
