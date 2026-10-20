import bpy,sys,json
from pathlib import Path
p=Path(sys.argv[sys.argv.index('--')+1]);im=bpy.data.images.load(str(p));s=bpy.context.scene
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.object.camera_add();s.camera=bpy.context.object
s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=im.size[0];s.render.resolution_y=im.size[1];s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=2
s.use_nodes=True;n=s.node_tree.nodes;n.clear();node=n.new('CompositorNodeImage');node.image=im;out=n.new('CompositorNodeComposite');s.node_tree.links.new(node.outputs['Image'],out.inputs[0])
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=.1
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=96;s.render.filepath=str(p.with_name(p.name.replace('.denoised.exr','.jpg')))
bpy.ops.render.render(write_still=True)
