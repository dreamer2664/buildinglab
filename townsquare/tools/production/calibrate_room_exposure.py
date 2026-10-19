"""Source-linear HDR camera exposure calibration only; never image inspection/quality acceptance."""
import bpy,os,sys,json,math,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/production'));from view_tools import apply_view,prune_for_render
from fingerprints import file_sha256
from image_tools import upgrade_images
id=os.environ['SQUARE_VIEW'];f=apply_view(id);assert f['kind']=='interior';culling=prune_for_render(f);upgrade_images(R,f);s=bpy.context.scene;s.render.resolution_x=384;s.render.resolution_y=216;s.cycles.samples=8;s.cycles.use_denoising=False;s.render.threads_mode='FIXED';s.render.threads=2;s.render.image_settings.file_format='OPEN_EXR';s.render.image_settings.color_depth='32'
revision=os.environ.get('SQUARE_REVISION','R10');out=R/('.cache/exposure-calibration-'+revision);out.mkdir(exist_ok=True);s.render.filepath=str(out/(id+'.exr'));bpy.ops.render.render(write_still=True);im=bpy.data.images.load(s.render.filepath,check_existing=False)
s.render.image_settings.file_format='PNG';s.render.image_settings.color_depth='8';probe=out/(id+'.png')
def measure(ev):
 s.view_settings.exposure=ev;im.save_render(str(probe),scene=s)
 pic=bpy.data.images.load(str(probe),check_existing=False);pixels=np.empty(len(pic.pixels),dtype=np.float32);pic.pixels.foreach_get(pixels);a=pixels.reshape(-1,4)[:,:3];bpy.data.images.remove(pic)
 # Verified Blender byte-PNG pixel access returns normalized encoded values
 # (128 maps to .50196). Target display median .53, not a quality score.
 lum=a@np.array([.2126,.7152,.0722]);return float(np.median(lum)),float(np.percentile(lum,95))
lo,hi=-4.,11.
for _ in range(11):
 mid=(lo+hi)/2;median,p95=measure(mid)
 if median<.53:lo=mid
 else:hi=mid
ev=round((lo+hi)/2,3);median,p95=measure(ev)
assert abs(median-.53)<.04,'Exposure search did not converge; source may be occluded/unlit. Do not use a saturated bound as an exposure preset.'
build=json.loads((R/'evidence/production/R10-native-build.json').read_text());r={'view':id,'ancestor_R10_native_sha256':build['full_resolution_native_sha256'],'source_stage':revision,'opened_derivative_sha256':file_sha256(bpy.data.filepath),'calibration_dimensions':[384,216],'samples':8,'base_preset_exposure_EV':f['exposure'],'calibrated_absolute_exposure_EV':ev,'camera_exposure_bias_EV':round(ev-f['exposure'],3),'measured_display_encoded_median':median,'measured_p95':p95,'method':'Low-resolution actual source render saved as linear32bitEXR. Standard AgX camera exposure binary search targets display-encoded median .53, verified against a128/255 byte-PNG pixel test; geometry/materials/lights/source untouched. Preview/measurement is NOT final quality acceptance. Actual native-resolution final must be separately opened.','inspection':'NOT INFERRED FROM MEASUREMENT'};(R/'evidence/production'/(revision+'-exposure-calibration-'+id+'.json')).write_text(json.dumps(r,indent=2)+'\n');print('CAMERA_EXPOSURE_MEASURED',id,json.dumps(r),flush=True)
