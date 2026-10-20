"""CC0 MakeHuman hm08 continuous anatomy; fitted uniform prototype, not accepted."""
import bpy, math
from pathlib import Path
from mathutils import Vector

def build_human_figure(hid,loc,rot_z,height_scale,coat_mat,hair_mat,skin_mat,boot_mat,brass_mat,has_cap,has_flag,has_case,col_people):
    path=Path(__file__).resolve().parents[1]/'assets/humans/hm08.obj'
    vv=[]; ff=[]; joints={}; group=''
    for line in path.read_text().splitlines():
        t=line.split()
        if not t:continue
        if t[0]=='v': vv.append(tuple(map(float,t[1:4])))
        elif t[0]=='g':group=t[1]
        elif t[0]=='f':
            ids=[int(x.split('/')[0])-1 for x in t[1:]]
            if group=='body':ff.append(ids)
            elif group in ('joint-l-eye','joint-r-eye'):joints.setdefault(group,set()).update(ids)
    for target in path.parent.glob('*.target'):
        for line in target.read_text().splitlines():
            t=line.split()
            if len(t)==4 and not line.startswith('#'):
                i=int(t[0]);vv[i]=tuple(vv[i][a]+float(t[a+1]) for a in range(3))
    used=sorted(set(i for f in ff for i in f)); remap={i:j for j,i in enumerate(used)}
    # Source Y up, Z forward; scene Z up and Y forward. Preserve original facial topology.
    ymin=min(vv[i][1] for i in used); ymax=max(vv[i][1] for i in used)
    scale=1.75/(ymax-ymin)*height_scale
    verts=[(vv[i][0]*scale,vv[i][2]*scale,(vv[i][1]-ymin)*scale) for i in used]
    mesh=bpy.data.meshes.new(hid+'_continuous_anatomy');mesh.from_pydata(verts,[],[[remap[i] for i in f] for f in ff]);mesh.update()
    ob=bpy.data.objects.new(hid+'_Body',mesh);col_people.objects.link(ob);ob.location=loc;ob.rotation_euler.z=rot_z
    for mat in (skin_mat,coat_mat,boot_mat,hair_mat):mesh.materials.append(mat)
    # Lower arms with a smooth shoulder blend instead of leaving an A-pose.
    for v in mesh.vertices:
        x,y,z=v.co/height_scale
        if abs(x)>.15 and z>.85:
            side=1 if x>0 else -1
            weight=min(1,max(0,(abs(x)-.15)/.09))
            a=-side*.38*weight
            dx=x-side*.175;dz=z-1.40
            v.co.x=(side*.175+dx*math.cos(a)-dz*math.sin(a))*height_scale
            v.co.z=(1.40+dx*math.sin(a)+dz*math.cos(a))*height_scale
    # Prototype fitted garment with connected shoulder/arm topology. Head and hands remain skin.
    for p in mesh.polygons:
        center=sum((mesh.vertices[i].co for i in p.vertices),Vector())/len(p.vertices)
        x,y,z=center/height_scale
        p.material_index=0 if z>1.51 or (abs(x)>.30 and z<1.05) else (2 if z<.12 else 1)
        p.use_smooth=True
    # Remove covered torso polygons: no skin-shaped protrusions through tailoring.
    import bmesh
    bm=bmesh.new();bm.from_mesh(mesh)
    covered=[]
    for face in bm.faces:
        c=face.calc_center_median()/height_scale
        if .70<c.z<1.30 and abs(c.x)<.18:covered.append(face)
    bmesh.ops.delete(bm,geom=covered,context='FACES');bm.to_mesh(mesh);bm.free()
    sub=ob.modifiers.new('Anatomy subdivision','SUBSURF');sub.levels=1;sub.render_levels=1
    # Skin shader must not contain coarse stone-like noise.
    for n in skin_mat.node_tree.nodes:
        if n.type=='BUMP':n.inputs['Strength'].default_value=.004
        if n.type=='BSDF_PRINCIPLED':
            n.inputs['Subsurface Weight'].default_value=.12
            n.inputs['Subsurface Scale'].default_value=.015
    def part(name,vs,fs,mat):
        me=bpy.data.meshes.new(hid+name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update()
        obj=bpy.data.objects.new(hid+name,me);col_people.objects.link(obj);obj.location=loc;obj.rotation_euler.z=rot_z;obj.scale=(height_scale,)*3
        for p in me.polygons:p.use_smooth=True
        return obj
    # Continuous tailored coat shell loft, lapels handled with mesh rather than floating blocks.
    rings=[(.70,.245,.145),(.74,.245,.15),(.95,.21,.145),(1.13,.205,.16),(1.31,.235,.17),(1.40,.25,.16),(1.45,.09,.095)]
    vs=[];fs=[];N=64
    for z,rx,ry in rings:
        for k in range(N):
            a=2*math.pi*k/N
            fold=.002*math.sin(12*a)*(1 if z<1 else .25)
            vs.append(((rx+fold)*math.cos(a),(ry+fold)*math.sin(a),z))
    for r in range(len(rings)-1):
        for k in range(N):fs.append((r*N+k,r*N+(k+1)%N,(r+1)*N+(k+1)%N,(r+1)*N+k))
    coat=part('_TailoredCoat',vs,fs,coat_mat)
    sol=coat.modifiers.new('Wool thickness','SOLIDIFY');sol.thickness=.003
    sub=coat.modifiers.new('Soft tailoring','SUBSURF');sub.levels=2
    # Socket centers come from the morphed base's own eye-joint geometry.
    white=bpy.data.materials.get('Eye ivory') or bpy.data.materials.new('Eye ivory');white.diffuse_color=(.65,.61,.53,1)
    iris=bpy.data.materials.get('Iris umber') or bpy.data.materials.new('Iris umber');iris.diffuse_color=(.035,.025,.016,1)
    for group,ids in joints.items():
        c=sum((Vector(vv[i]) for i in ids),Vector())/len(ids)
        base=Vector((c.x*scale,c.z*scale,(c.y-ymin)*scale))
        for name,offset,rad,mat in [('Sclera',0,.0105,white),('Iris',.010,.005,iris)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,radius=rad*height_scale)
            eye=bpy.context.object;eye.name=hid+name+group
            pos=base+Vector((0,offset*height_scale,0))
            eye.location=Vector(loc)+Vector((math.cos(rot_z)*pos.x-math.sin(rot_z)*pos.y,math.sin(rot_z)*pos.x+math.cos(rot_z)*pos.y,pos.z))
            eye.data.materials.append(mat)
            for p in eye.data.polygons:p.use_smooth=True
    # Uniform collar, placket, lapels and buttons are contiguous fitted detailing.
    part('_LapelLeft',[(-.085,.10,1.46),(-.13,.15,1.39),(-.025,.18,1.27),(0,.17,1.36)],[(0,1,2,3)],coat_mat)
    part('_LapelRight',[(.085,.10,1.46),(.13,.15,1.39),(.025,.18,1.27),(0,.17,1.36)],[(3,2,1,0)],coat_mat)
    for z in (.88,1.00,1.12,1.24):
        for x in (-.055,.055):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=.009*height_scale)
            button=bpy.context.object;button.name=hid+'_Button';button.scale=(1,.45,1)
            pos=Vector((x,.168,z))*height_scale
            button.location=Vector(loc)+Vector((math.cos(rot_z)*pos.x-math.sin(rot_z)*pos.y,math.sin(rot_z)*pos.x+math.cos(rot_z)*pos.y,pos.z));button.data.materials.append(brass_mat)
    # Cap crown and visor, dimensioned to actual skull.
    if has_cap:
        vs=[];fs=[]
        for z,rx,ry in [(1.745,.108,.119),(1.775,.116,.127),(1.81,.104,.117)]:
            for k in range(48):
                a=2*math.pi*k/48;vs.append((rx*math.cos(a),ry*math.sin(a),z-.012))
        for r in range(2):
            for k in range(48):fs.append((r*48+k,r*48+(k+1)%48,(r+1)*48+(k+1)%48,(r+1)*48+k))
        fs.append(tuple(range(96,144)));part('_Cap',vs,fs,coat_mat)
        vs=[(0,.055,1.733)]+[(.11*math.cos(a),.055+.105*math.sin(a),1.721) for a in [k*math.pi/32 for k in range(33)]]
        part('_Visor',vs,[(0,k,k+1) for k in range(1,33)],boot_mat)
