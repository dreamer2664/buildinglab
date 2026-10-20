"""Memory-bounded standard OpenImageDenoise post-process, NOT image generation.
Usage: python3 assets/exterior/denoise_png.py image.png /path/to/blender/lib
Denoises display-referred sRGB colour in overlapping 640px tiles. Preserves dimensions;
records original as *.noisy.png. Requires numpy/Pillow and Blender's OIDN shared library.
"""
import ctypes as c,sys,os
from pathlib import Path
import numpy as np
from PIL import Image
p=Path(sys.argv[1]);libs=Path(sys.argv[2]);lib=c.CDLL(str(next(libs.glob('libOpenImageDenoise.so*'))))
def bind(n,rest,args):f=getattr(lib,n);f.restype=rest;f.argtypes=args;return f
ptr=c.c_void_p;size=c.c_size_t;ch=c.c_char_p;I=c.c_int
newdev=bind('oidnNewDevice',ptr,[I]);commitdev=bind('oidnCommitDevice',None,[ptr]);newfilter=bind('oidnNewFilter',ptr,[ptr,ch]);image=bind('oidnSetSharedFilterImage',None,[ptr,ch,ptr,I,size,size,size,size,size]);setbool=bind('oidnSetFilterBool',None,[ptr,ch,c.c_bool]);commit=bind('oidnCommitFilter',None,[ptr]);execute=bind('oidnExecuteFilter',None,[ptr]);release=bind('oidnReleaseFilter',None,[ptr]);geterror=bind('oidnGetDeviceError',I,[ptr,c.POINTER(ch)])
dev=newdev(1);commitdev(dev)
im=Image.open(p).convert('RGB');src=np.asarray(im,dtype=np.float32)/255;dest=np.empty_like(src);h,w,_=src.shape;tile=640;padding=48
for y in range(0,h,tile):
 for x in range(0,w,tile):
  x0=max(0,x-padding);y0=max(0,y-padding);x1=min(w,x+tile+padding);y1=min(h,y+tile+padding)
  a=np.ascontiguousarray(src[y0:y1,x0:x1]);out=np.empty_like(a);hh,ww,_=a.shape;f=newfilter(dev,b'RT')
  image(f,b'color',a.ctypes.data,3,ww,hh,0,12,ww*12);image(f,b'output',out.ctypes.data,3,ww,hh,0,12,ww*12);setbool(f,b'hdr',False);setbool(f,b'srgb',True);commit(f);execute(f)
  msg=ch();err=geterror(dev,c.byref(msg))
  if err:raise RuntimeError(msg.value.decode() if msg.value else str(err))
  dest[y:min(h,y+tile),x:min(w,x+tile)]=out[y-y0:min(h,y+tile)-y0,x-x0:min(w,x+tile)-x0];release(f)
noisy=p.with_suffix('.noisy.png')
if not noisy.exists():p.rename(noisy)
Image.fromarray(np.uint8(np.clip(dest,0,1)*255+.5)).save(p)
print('OIDN_SRGB_TILE_PASS',str(p),w,h)
