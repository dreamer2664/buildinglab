"""Structural rebuild WIP. Actual geometric panes/arches, not schedule-only validation."""
import bpy, math, sys
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_bay as b
ROOT=Path(__file__).resolve().parents[1]

def rebuild():
    for name in ['01_IRONWORK','02_GLAZING']:
        col=bpy.data.collections.get(name)
        if col:
            for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
    structure=b.make_collection('01_IRONWORK');glazing=b.make_collection('02_GLAZING')
    def mat(name,col,metal=0,rough=.5):return b.make_pbr_mat(name,col,metal,rough,.035,35)
    iron=mat('Rebuild painted petrol iron',(.025,.065,.065),.65,.35)
    stone=mat('Rebuild limestone ashlar',(.43,.35,.25),0,.66)
    dark=mat('Rebuild recess',(.025,.033,.037),0,.7)
    brass=mat('Rebuild aged brass',(.43,.28,.09),.8,.27)
    cream=mat('Rebuild ivory enamel',(.7,.64,.48),0,.4)
    glass=bpy.data.materials.new('Rebuild thin historic glazing');glass.use_nodes=True
    n=glass.node_tree.nodes;n.clear();out=n.new('ShaderNodeOutputMaterial');mix=n.new('ShaderNodeMixShader');mix.inputs[0].default_value=.16
    trans=n.new('ShaderNodeBsdfTransparent');g=n.new('ShaderNodeBsdfGlass');g.inputs['Color'].default_value=(.8,.9,.88,1);g.inputs['Roughness'].default_value=.12
    glass.node_tree.links.new(trans.outputs[0],mix.inputs[1]);glass.node_tree.links.new(g.outputs[0],mix.inputs[2]);glass.node_tree.links.new(mix.outputs[0],out.inputs[0])
    boxes={}
    def box(name,loc,size,material,collection=structure):
        key=tuple(round(x,5) for x in size)
        if key not in boxes:boxes[key]=b.create_box_mesh('Rebuild section '+str(key),*size,bevel_m=.002)
        # Mesh materials cannot be shared between different material slots blindly.
        mesh=boxes[key]
        if mesh.materials and mesh.materials[0]!=material:mesh=mesh.copy();mesh.materials.clear()
        return b.add_mesh_obj(name,mesh,loc,mat=material,col=collection)
    def rod(name,p,q,width,depth,material=iron):
        p,q=Vector(p),Vector(q);mid,rot,length=b.orient_between(p,q)
        obj=box(name,mid,(width,length,depth),material);obj.rotation_euler=rot;return obj
    # Three continuous 28 m barrel vaults. Eight transverse lattice frames over 180 m.
    for frame in range(8):
        x=-90+180*frame/7
        for vault in range(3):
            cy=50+28*vault
            top=[];bottom=[]
            for k in range(21):
                a=math.pi*k/20
                top.append((x,cy-14*math.cos(a),14+12*math.sin(a)))
                bottom.append((x,cy-14*math.cos(a),14+10.5*math.sin(a)))
            for k in range(20):
                rod(f'FRAME_{frame}_{vault}_top{k}',top[k],top[k+1],.22,.24)
                rod(f'FRAME_{frame}_{vault}_bottom{k}',bottom[k],bottom[k+1],.18,.20)
                rod(f'FRAME_{frame}_{vault}_webA{k}',top[k],bottom[k+1],.075,.075)
                rod(f'FRAME_{frame}_{vault}_webB{k}',bottom[k],top[k+1],.075,.075)
            rod(f'Tie_{frame}_{vault}',(x,cy-14,14),(x,cy+14,14),.05,.05)
        for row in range(4):
            y=36+row*28
            box(f'Pier{frame}_{row}',(x,y,.35),(.8,.8,.7),stone)
            shaft=b.create_cyl_mesh('Fluted shaft',.23,13,verts=32)
            b.add_mesh_obj(f'Column{frame}_{row}',shaft,(x,y,7.2),mat=iron,col=structure)
            for z,r,h in [(.78,.39,.12),(1,.28,.18),(13.65,.32,.16),(13.85,.43,.18)]:
                me=b.create_cyl_mesh('Column moulding',r,h,verts=32);b.add_mesh_obj('Collar',me,(x,y,z),mat=iron,col=structure)
            box('Capital',(x,y,14),(.9,.9,.18),iron)
            for sign in (-1,1):rod('Spandrel brace',(x,y,12.4),(x+sign*2.3,y,14),.09,.12)
    # 4200 separate native panes. Rails follow the same sampled vault surface.
    count=0
    for vault in range(3):
        cy=50+28*vault
        for k in range(20):
            a0=math.pi*k/20;a1=math.pi*(k+1)/20
            ya=cy-14*math.cos(a0);yb=cy-14*math.cos(a1);za=14+12*math.sin(a0);zb=14+12*math.sin(a1)
            rod('Longitudinal purlin',(-90,ya,za),(90,ya,za),.10,.13)
            for strip in range(70):
                xa=-90+180*strip/70;xb=-90+180*(strip+1)/70
                # planar quad per pane with gap 12mm; glass thickness represented by solidify below only if needed
                verts=[(xa+.006,ya+.006,za+.035),(xb-.006,ya+.006,za+.035),(xb-.006,yb-.006,zb+.035),(xa+.006,yb-.006,zb+.035)]
                me=bpy.data.meshes.new(f'PaneMesh{count:04}');me.from_pydata(verts,[],[(0,1,2,3)]);me.materials.append(glass)
                ob=bpy.data.objects.new(f'PANE_{count:04}',me);glazing.objects.link(ob);ob['waviness_seed']=count
                if k==0:rod('Glazing bar',(xa,36+vault*28,14),(xa,64+vault*28,14),.025,.025)
                count+=1
    # Front elevation: articulated masonry, arched glazed openings and central grand portal.
    for bay in range(24):
        x=-115+10*bay
        box('Ashlar pier',(x-5,33.8,8),(1.05,1.6,16),stone)
        box('Plinth',(x,33.8,.45),(9,1.5,.9),stone)
        box('Spandrel',(x,33.8,13.7),(9,1.5,4.6),stone)
        # Splayed arched voussoirs above 7.5 m opening.
        for k in range(16):
            a=(k+.5)*math.pi/16
            obj=box('Arch voussoir',(x+4*math.cos(a),33.65,7.5+4*math.sin(a)),(.76,1.7,.47),stone)
            obj.rotation_euler.y=-a
        # Tall recessed window (central bays retain entrance clear opening).
        if bay not in (11,12,13):
            box('Glazed window',(x,33.4,5.2),(7.6,.03,8.4),glass,glazing)
            for off in (-2.5,0,2.5):box('Window mullion',(x+off,33.55,5.4),(.065,.12,8.2),iron)
            for z in (2,4.5,7):box('Window transom',(x,33.55,z),(7.6,.12,.065),iron)
        for z in (3,7.5,12.2,15.8,16.25):box('Continuous stringcourse',(x,33.8,z),(10,1.85,.22),stone)
        # Ashlar joints as geometric blocks on piers, avoiding a monolithic wall.
        for course in range(20):
            box('Pier joint',(x-5,34.615,.9+course*.72),(1.055,.014,.018),dark)
    # Upper station inscription, physically modelled text.
    curve=bpy.data.curves.new('Station name','FONT');curve.body='N O R D B A H N H O F';curve.align_x='CENTER';curve.size=1.25;curve.extrude=.016
    text=bpy.data.objects.new('Station inscription',curve);structure.objects.link(text);text.location=(10,34.7,14);text.rotation_euler=(math.pi/2,0,0);curve.materials.append(brass)
    # Enclose the volume with a brick plinth, glazed clerestory and masonry rhythm.
    brick=mat('Rebuild soot brown brick',(.16,.095,.055),0,.78)
    for side in (-1,1):
        for bay in range(12):
            y=39.5+7*bay
            box('Sidewall pier',(side*90,y,6),(.8,.65,12),brick)
            box('Sidewall dado',(side*90,y,1.8),(.65,7,3.6),brick)
            box('Sidewall glazed infill',(side*90,y,8),(.025,6.3,8),glass,glazing)
            box('Sidewall eaves',(side*90,y,13.8),(.8,7,.4),stone)
            for z in (4.3,7,9.7,12.4):box('Sidewall transom',(side*90,y,z),(.08,6.3,.055),iron)
            for dy in (-2.1,0,2.1):box('Sidewall mullion',(side*90,y+dy,8),(.08,.055,8),iron)
    for bay in range(24):
        x=-86.25+7.5*bay
        box('North wall dado',(x,120,1.8),(7.5,.65,3.6),brick)
        box('North wall pier',(x-3.75,120,7),(.6,.7,14),brick)
        box('North wall glazing',(x,120,8),(6.9,.025,8),glass,glazing)
        for z in (4.2,7,10,12):box('North wall transom',(x,120,z),(6.9,.06,.05),iron)
    # Large site prevents empty horizon at trackside and gives believable dark rail beds.
    gravel=mat('Rebuild crushed dark basalt',(.055,.047,.04),0,.9)
    paving=mat('Rebuild platform blue granite',(.17,.18,.18),0,.58)
    box('Site ground',(0,75,-.35),(300,240,.3),gravel)
    for ob in list(bpy.data.objects):
        if ob.name.startswith('STEAM_'):bpy.data.objects.remove(ob,do_unlink=True)
    # Retain detailed Bay 5 track; extend the other railway beds into the station.
    rail=mat('Rebuild rail steel',(.22,.23,.24),.9,.25)
    sleeper=mat('Rebuild creosote',(.045,.028,.018),0,.85)
    for y in (40,46,52,58,64,70,76,82,88,113):
        box('Track ballast',(0,y,.02),(180,3.1,.12),gravel)
        for dy in (-.7175,.7175):box('Rail',(0,y+dy,.19),(180,.07,.13),rail)
        for k in range(240):box('Sleeper',(-89+k*.75,y,.08),(.24,2.6,.14),sleeper)
    for y in (43,55,67,79,85,109):
        box('Additional platform',(0,y,.25),(180,2.4,.5),paving)
        for k in range(90):
            for dy in (-1.17,1.17):box('Coping',(-89+k*2,y+dy,.51),(1.98,.35,.10),stone)
    # Additional rolling stock with real window openings between separate pillars.
    carriage=mat('Rebuild carriage oxblood',(.11,.025,.018),.25,.4)
    roofmat=mat('Rebuild carriage charcoal roof',(.028,.033,.031),.3,.65)
    for train,(y,ncars) in enumerate([(40,6),(52,6),(64,6),(76,6),(88,5)]):
        for car in range(ncars):
            x=-75+car*24
            box('Coach underframe',(x,y,.94),(22,2.7,.35),iron)
            box('Coach body lower',(x,y,1.65),(22,2.8,1.05),carriage)
            box('Coach roof',(x,y,3.65),(22.3,2.95,.25),roofmat)
            for side in (-1,1):
                for win in range(10):
                    wx=x-9.6+win*2.13
                    box('Coach window',(wx,y+side*1.4,2.75),(1.6,.035,1.0),glass,glazing)
                    box('Coach window pillar',(wx-.96,y+side*1.4,2.75),(.35,.1,1.3),carriage)
                box('Coach waist trim',(x,y+side*1.43,2.18),(22,.05,.065),brass)
                box('Coach cantrail',(x,y+side*1.43,3.38),(22,.07,.13),carriage)
            for axle in (-7.7,-5.9,5.9,7.7):
                for side in (-1,1):
                    me=b.create_cyl_mesh('Coach wheel',.43,.14,verts=24,axis='Y')
                    b.add_mesh_obj('Coach wheel',me,(x+axle,y+side*.76,.6),mat=iron,col=structure)
    scene=bpy.context.scene
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-1.0
    # Correct overly pale original sky/sun balance.
    for ob in bpy.data.objects:
        if ob.type=='LIGHT' and ob.data.type=='SUN':ob.data.energy=2.2
    if scene.world:
        for node in scene.world.node_tree.nodes:
            if node.type=='BACKGROUND':node.inputs['Strength'].default_value=.35
    # Batch static meshes by material to keep CPU render memory bounded.
    # The pane construction count remains 4200; render batches are not pane counts.
    from collections import defaultdict
    batches=defaultdict(list)
    for collection in (structure,glazing):
        for ob in list(collection.objects):
            if ob.type=='MESH' and not ob.modifiers:
                key=(collection.name,ob.data.materials[0].name if ob.data.materials else '')
                batches[key].append(ob)
    bpy.ops.object.select_all(action='DESELECT')
    for key,objects in batches.items():
        if len(objects)<2:continue
        for ob in objects:ob.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.object.join()
        bpy.context.object.name='STATIC_BATCH_'+key[1]
        bpy.ops.object.select_all(action='DESELECT')
    print('ARCHITECTURE REBUILT: native panes',count,'objects',len(bpy.data.objects),'NOT ACCEPTED')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'source/NORDBAHNHOF_REBUILD.blend'),compress=True)
if __name__=='__main__':rebuild()
