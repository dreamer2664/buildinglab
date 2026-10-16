"""The exact 29 required individually named PNGs; not a contact sheet."""
VIEWS=[{'id':'exterior-day','camera':'CAM_EXTERIOR_DAY','mode':'intact','width':3840,'height':2160},{'id':'exterior-dusk','camera':'CAM_EXTERIOR_DUSK','mode':'intact','night':True,'width':3840,'height':2160},{'id':'all-levels-section','camera':'CAM_FULL_CUTAWAY','mode':'section','width':3840,'height':2160}]
for i in range(1,7):VIEWS.append({'id':f'L{i:02}-cutaway','camera':f'CAM_L{i:02}_AXON','level':f'L{i:02}','mode':'floor','width':3840,'height':2160})
for i in range(1,7):
 for suffix in ['INTERIOR','DETAIL']:VIEWS.append({'id':f'L{i:02}-'+suffix.lower(),'camera':f'CAM_L{i:02}_'+suffix,'level':f'L{i:02}','mode':'interior','width':2560,'height':1440})
for i in range(1,7):VIEWS.append({'id':f'L{i:02}-plan','camera':f'CAM_L{i:02}_PLAN','level':f'L{i:02}','mode':'plan','width':2560,'height':1440})
VIEWS += [{'id':'technical-structure-core','camera':'CAM_TECHNICAL','mode':'structure','width':2560,'height':1440},{'id':'technical-facade-material','camera':'CAM_FACADE_DETAIL','mode':'intact','width':2560,'height':1440}]
