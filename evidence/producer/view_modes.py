"""Non-destructive native scene view switcher; also embedded in final .blend Text Editor.
Run set_view('intact'), set_view('floor','L03'), set_view('section'), set_view('structure').
'floor' isolates a furnished dollhouse; 'interior' isolates with intact walls/ceiling.
No automatic file execution or add-on required. Collection visibility is reversible.
"""
import bpy

def set_view(mode='intact',level=None):
 assert mode in ['intact','floor','section','structure','interior','plan']
 s=bpy.context.scene
 for c in bpy.data.collections:
  if c.get('occupied_level'):
   hide=level is not None and mode in ['floor','interior','plan'] and c.name!=level
  elif c.name=='ROOF':hide=mode!='intact'
  elif c.name.endswith('_FACADE'):hide=mode in ['floor','section','structure','plan']
  elif c.name.endswith('_PARTITIONS_HIGH'):hide=mode in ['floor','section','structure','plan']
  elif c.name.endswith('_PARTITIONS_LOW'):hide=mode=='structure'
  elif c.name.endswith('_CEILING'):hide=mode in ['floor','section','structure','plan']
  elif c.name.endswith('_FURNITURE'):hide=mode=='structure'
  elif c.name=='CONTEXT':hide=mode in ['floor','plan','structure']
  else:hide=False
  c.hide_render=hide;c.hide_viewport=hide
 for o in s.objects:
  hide=(o.get('role')=='column' and mode in ['floor','plan','section']) or (mode=='structure' and o.get('role') in ['room_floor','door','wayfinding']) or (mode=='section' and o.name.startswith(('ENTRANCE_CANOPY','CANOPY_TIE','ENTRANCE_SIGN')))
  hide=hide or (mode in ['floor','plan','section','structure'] and o.type=='MESH' and o.get('fixture')=='room_lighting')
  o.hide_render=hide;o.hide_set(hide)
 s['display_mode']=mode;s['display_level']=level or 'ALL'
 s.view_settings.exposure=.8 if mode=='interior' else 0
 s.view_settings.look='AgX - Medium High Contrast'
 s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
 bpy.data.lights['SUN'].energy=2.2
 bpy.context.view_layer.update()

if __name__=='__main__':
 # Safe default when run by the user: restore the intact building.
 set_view('intact')
