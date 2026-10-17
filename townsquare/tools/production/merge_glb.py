"""Merge independently exported, already evaluated glTF2 components without geometry loss.
All index spaces, embedded byte offsets and punctual-light references are remapped.
"""
import json,struct,hashlib,copy
from pathlib import Path
R=Path(__file__).resolve().parents[2]
def read_glb(path):
 data=Path(path).read_bytes();magic,version,total=struct.unpack_from('<4sII',data);assert magic==b'glTF' and version==2 and total==len(data);offset=12;doc=None;binary=b''
 while offset<len(data):
  n,typ=struct.unpack_from('<II',data,offset);chunk=data[offset+8:offset+8+n];offset+=8+n
  if typ==0x4E4F534A:doc=json.loads(chunk)
  elif typ==0x004E4942:binary=chunk
 assert doc is not None;return doc,binary

def merge(paths,out):
 names=['bufferViews','accessors','images','samplers','textures','materials','meshes','nodes','cameras','skins','animations'];dst={'asset':{'version':'2.0','generator':'Winterlichtplatz / lossless glTF2 component index and buffer merger'},'scene':0,'scenes':[{'name':'Winterlichtplatz / complete static town','nodes':[]}],**{name:[] for name in names}};binary=bytearray();lights=[];used=set();required=set();parts=[]
 for path in paths:
  d,blob=read_glb(path);bases={name:len(dst[name]) for name in names};lightbase=len(lights)
  while len(binary)%4:binary.append(0)
  bytebase=len(binary);length=d.get('buffers',[{'byteLength':0}])[0]['byteLength'];binary.extend(blob[:length]);parts.append({'file':Path(path).name,'bytes':Path(path).stat().st_size,'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'binary_offset':bytebase})
  for v in d.get('bufferViews',[]):v['buffer']=0;v['byteOffset']=v.get('byteOffset',0)+bytebase
  for a in d.get('accessors',[]):
   if 'bufferView' in a:a['bufferView']+=bases['bufferViews']
   if 'sparse' in a:
    a['sparse']['indices']['bufferView']+=bases['bufferViews'];a['sparse']['values']['bufferView']+=bases['bufferViews']
  for im in d.get('images',[]):
   if 'bufferView' in im:im['bufferView']+=bases['bufferViews']
   assert 'uri' not in im or im['uri'].startswith('data:'),'External image dependency'
  for t in d.get('textures',[]):
   if 'source' in t:t['source']+=bases['images']
   if 'sampler' in t:t['sampler']+=bases['samplers']
   for e in t.get('extensions',{}).values():
    if isinstance(e,dict) and 'source' in e:e['source']+=bases['images']
  def material_textures(obj):
   if not isinstance(obj,dict):return
   for key,value in obj.items():
    if isinstance(value,dict):
     if key.lower().endswith('texture') and 'index' in value:value['index']+=bases['textures']
     material_textures(value)
  for mat in d.get('materials',[]):material_textures(mat)
  for mesh in d.get('meshes',[]):
   for p in mesh['primitives']:
    p['attributes']={key:idx+bases['accessors'] for key,idx in p['attributes'].items()}
    if 'indices' in p:p['indices']+=bases['accessors']
    if 'material' in p:p['material']+=bases['materials']
    for target in p.get('targets',[]):
     for key in target:target[key]+=bases['accessors']
  for node in d.get('nodes',[]):
   for key,space in [('mesh','meshes'),('camera','cameras'),('skin','skins')]:
    if key in node:node[key]+=bases[space]
   if 'children' in node:node['children']=[i+bases['nodes'] for i in node['children']]
   if 'KHR_lights_punctual' in node.get('extensions',{}):node['extensions']['KHR_lights_punctual']['light']+=lightbase
  for skin in d.get('skins',[]):
   if 'inverseBindMatrices' in skin:skin['inverseBindMatrices']+=bases['accessors']
   if 'skeleton' in skin:skin['skeleton']+=bases['nodes']
   skin['joints']=[i+bases['nodes'] for i in skin['joints']]
  for anim in d.get('animations',[]):
   for sampler in anim['samplers']:sampler['input']+=bases['accessors'];sampler['output']+=bases['accessors']
   for channel in anim['channels']:
    if 'node' in channel['target']:channel['target']['node']+=bases['nodes']
  lights+=d.get('extensions',{}).get('KHR_lights_punctual',{}).get('lights',[])
  for name in names:dst[name]+=d.get(name,[])
  dst['scenes'][0]['nodes'] += [i+bases['nodes'] for i in d['scenes'][d.get('scene',0)].get('nodes',[])]
  used.update(d.get('extensionsUsed',[]));required.update(d.get('extensionsRequired',[]))
 if lights:dst['extensions']={'KHR_lights_punctual':{'lights':lights}}
 if used:dst['extensionsUsed']=sorted(used)
 if required:dst['extensionsRequired']=sorted(required)
 dst={k:v for k,v in dst.items() if k not in names or v};dst['buffers']=[{'byteLength':len(binary)}];dst['extras']={'project':'Winterlichtplatz','revision':'R11','units':'metres','people':'36 static instances /12 separately supplied editable human rigs','auxiliary_background':'500m source snow backdrop intentionally excluded; original112x100m main ground retained','texture_budget':'512px portable photographic map caps; full-resolution packed sources separately supplied','lighting_limitations':'Read portability report; photographic world/Blender area lights/procedural nodes/colour management are not universally portable.'}
 # Canonicalize identical embedded image/sampler/texture/material payloads across components.
 # This avoids decoding repeated copies of the same photographic map during clean import.
 def dedup(space,keyfunc):
  items=dst.get(space,[]);unique=[];seen={};remap={}
  for i,item in enumerate(items):
   k=keyfunc(item)
   if k not in seen:seen[k]=len(unique);unique.append(item)
   remap[i]=seen[k]
  dst[space]=unique;return remap
 def imagekey(im):
  if 'bufferView' not in im:return im.get('uri')
  v=dst['bufferViews'][im['bufferView']];o=v.get('byteOffset',0);return hashlib.sha256(binary[o:o+v['byteLength']]).hexdigest()
 imap=dedup('images',imagekey)
 smap=dedup('samplers',lambda x:json.dumps({k:v for k,v in x.items() if k not in ['name','extras']},sort_keys=True))
 for tex in dst.get('textures',[]):
  if 'source' in tex:tex['source']=imap[tex['source']]
  if 'sampler' in tex:tex['sampler']=smap[tex['sampler']]
  for ext in tex.get('extensions',{}).values():
   if isinstance(ext,dict) and 'source' in ext:ext['source']=imap[ext['source']]
 tmap=dedup('textures',lambda x:json.dumps({k:v for k,v in x.items() if k not in ['name','extras']},sort_keys=True))
 def texremap(obj):
  if not isinstance(obj,dict):return
  for key,value in obj.items():
   if isinstance(value,dict):
    if key.lower().endswith('texture') and 'index' in value:value['index']=tmap[value['index']]
    texremap(value)
 for mat in dst.get('materials',[]):texremap(mat)
 mmap=dedup('materials',lambda x:json.dumps({k:v for k,v in x.items() if k not in ['name','extras']},sort_keys=True))
 for mesh in dst.get('meshes',[]):
  for p in mesh['primitives']:
   if 'material' in p:p['material']=mmap[p['material']]
 usedviews={im['bufferView'] for im in dst.get('images',[]) if 'bufferView' in im}
 for a in dst.get('accessors',[]):
  if 'bufferView' in a:usedviews.add(a['bufferView'])
  if 'sparse' in a:usedviews.update([a['sparse']['indices']['bufferView'],a['sparse']['values']['bufferView']])
 packed=bytearray();newviews=[];viewmap={}
 for i,v in enumerate(dst.get('bufferViews',[])):
  if i not in usedviews:continue
  while len(packed)%4:packed.append(0)
  oldoffset=v.get('byteOffset',0);v=copy.deepcopy(v);v['byteOffset']=len(packed);packed.extend(binary[oldoffset:oldoffset+v['byteLength']]);viewmap[i]=len(newviews);newviews.append(v)
 for a in dst.get('accessors',[]):
  if 'bufferView' in a:a['bufferView']=viewmap[a['bufferView']]
  if 'sparse' in a:
   for key in ['indices','values']:a['sparse'][key]['bufferView']=viewmap[a['sparse'][key]['bufferView']]
 for im in dst.get('images',[]):
  if 'bufferView' in im:im['bufferView']=viewmap[im['bufferView']]
 binary=packed;dst['bufferViews']=newviews;dst['buffers']=[{'byteLength':len(binary)}]
 js=json.dumps(dst,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\0'*((-len(binary))%4);total=12+8+len(js)+8+len(binary)
 with Path(out).open('wb') as f:f.write(struct.pack('<4sII',b'glTF',2,total));f.write(struct.pack('<II',len(js),0x4E4F534A));f.write(js);f.write(struct.pack('<II',len(binary),0x004E4942));f.write(binary)
 return dst,parts
if __name__=='__main__':
 keys=[f'B{i:02}' for i in range(1,13)]+['PUBLIC']+[f'P{i:02}' for i in range(1,13)];out=R/'.cache/final-components/Winterlichtplatz-R11.glb';d,parts=merge([R/'.cache/final-components/GLB'/(key+'.glb') for key in keys],out)
 h=hashlib.sha256()
 with out.open('rb') as f:
  while b:=f.read(1024*1024):h.update(b)
 report={'glb':str(out.relative_to(R)),'bytes':out.stat().st_size,'sha256':h.hexdigest(),'components':parts,'nodes':len(d.get('nodes',[])),'meshes':len(d.get('meshes',[])),'images':len(d.get('images',[])),'extensions_used':d.get('extensionsUsed',[]),'merger':'Index/buffer remapping only; no geometry resampling/decimation/axis change','clean_reimport':'PENDING'};(R/'evidence/production/merged-glb.json').write_text(json.dumps(report,indent=2)+'\n');print('COMPLETE_STATIC_GLB_MERGED',report['bytes'],report['sha256'],flush=True)
