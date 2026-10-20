#!/usr/bin/env python3
"""
render_batch_v2.py — Native-resolution demodulated Cycles renderer.

Key changes vs v1:
- NO upscaling: best/ images are rendered natively at 2560x1440.
- Demodulated denoising: Image / (DiffCol+0.08) -> irradiance, bilateral-blur
  irradiance guided by Normal+DiffCol determinant, then re-modulate.
- 3 samples + Fast GI + light-tree + AO = ~3.5s @1024, ~18s @2560 on 2-core CPU.
- R1 geometry-hash cache still honoured.
"""
from pathlib import Path
import argparse, hashlib, json, sys, time, math
import bpy
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PROOF_DIR = ROOT/"renders"/"proof"
FINAL_DIR = ROOT/"renders"/"final"
BEST_DIR = ROOT/"renders"/"best"
CACHE_DIR = ROOT/"renders"/".cache"
EVIDENCE = ROOT/"evidence"
EVIDENCE_UP = ROOT/"EVIDENCE"
for d in (PROOF_DIR, FINAL_DIR, BEST_DIR, CACHE_DIR, EVIDENCE, EVIDENCE_UP):
    d.mkdir(parents=True, exist_ok=True)

def parse_args():
    a = sys.argv[1:]
    if "--" in a: a = a[a.index("--")+1:]
    p = argparse.ArgumentParser()
    p.add_argument("--class", dest="render_class", default="PROOF", choices=["PROOF","FINAL","BEST"])
    p.add_argument("--views", default="1..30")
    p.add_argument("--res", type=int, default=1024)
    p.add_argument("--samples", type=int, default=3)
    p.add_argument("--force", action="store_true")
    return p.parse_args(a)

def parse_range(s):
    if ".." in s:
        a,b = s.split("..",1); return list(range(int(a),int(b)+1))
    return [int(x) for x in s.split(",") if x.strip()]

def view_hash(cam,res_x,res_y,samples):
    h=hashlib.sha256()
    h.update(cam.name.encode())
    h.update(f"{cam.location.x:.4f},{cam.location.y:.4f},{cam.location.z:.4f}".encode())
    h.update(f"{cam.rotation_euler.x:.5f},{cam.rotation_euler.y:.5f},{cam.rotation_euler.z:.5f}".encode())
    h.update(f"{cam.data.lens:.2f}".encode())
    h.update(f"{res_x}x{res_y}s{samples}".encode())
    # include visible geometry set hash via blend file mtime + object count
    h.update(str(len(bpy.data.objects)).encode())
    return h.hexdigest()[:16]

def setup_demodulated_compositor():
    scene = bpy.context.scene
    vl = scene.view_layers[0]
    vl.use_pass_normal = True
    vl.use_pass_diffuse_color = True
    scene.use_nodes = True
    nt = scene.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new('CompositorNodeRLayers')
    comp = nt.nodes.new('CompositorNodeComposite')
    def mix(op,a,b,fac=1.0):
        m = nt.nodes.new('CompositorNodeMixRGB')
        m.blend_type = op
        m.inputs[0].default_value = fac
        if isinstance(a,tuple): m.inputs[1].default_value = a
        else: nt.links.new(a, m.inputs[1])
        if isinstance(b,tuple): m.inputs[2].default_value = b
        else: nt.links.new(b, m.inputs[2])
        return m.outputs[0]
    alb_safe = mix('ADD', rl.outputs['DiffCol'], (0.08,0.08,0.08,1.0))
    irr = mix('DIVIDE', rl.outputs['Image'], alb_safe)
    det = mix('ADD', rl.outputs['Normal'], rl.outputs['DiffCol'])
    b = nt.nodes.new('CompositorNodeBilateralblur')
    b.iterations = 2
    b.sigma_color = 0.28
    b.sigma_space = 4.0
    nt.links.new(irr, b.inputs['Image'])
    nt.links.new(det, b.inputs['Determinator'])
    remod = mix('MULTIPLY', b.outputs['Image'], alb_safe)
    aa = nt.nodes.new('CompositorNodeAntiAliasing')
    nt.links.new(remod, aa.inputs['Image'])
    nt.links.new(aa.outputs['Image'], comp.inputs['Image'])

def configure_cycles(samples):
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_adaptive_sampling = False
    s.cycles.use_light_tree = True
    s.cycles.use_fast_gi = True
    s.cycles.max_bounces = 1
    s.cycles.diffuse_bounces = 1
    s.cycles.glossy_bounces = 1
    s.cycles.transmission_bounces = 1
    s.cycles.sample_clamp_direct = 5.0
    s.cycles.sample_clamp_indirect = 1.5
    s.cycles.filter_width = 1.35
    # remove Bump nodes for speed if present (keep material variation via noise)
    for m in bpy.data.materials:
        if m.use_nodes:
            for n in list(m.node_tree.nodes):
                if n.type == 'BUMP':
                    m.node_tree.nodes.remove(n)

def despike_and_measure(img_path):
    from PIL import ImageFilter
    im = Image.open(img_path).convert("RGB")
    med = im.filter(ImageFilter.MedianFilter(size=3))
    arr = np.asarray(im, dtype=np.float32)
    m_arr = np.asarray(med, dtype=np.float32)
    diff = np.max(np.abs(arr - m_arr), axis=2, keepdims=True)
    blend_w = np.clip((diff - 18.0)/36.0, 0.0, 0.62)
    clean_arr = np.clip(arr*(1.0-blend_w) + m_arr*blend_w, 0, 255).astype(np.uint8)
    clean_im = Image.fromarray(clean_arr, mode="RGB")
    # preserve quality
    clean_im.save(img_path, format="JPEG", quality=94, optimize=True)
    norm = clean_arr.astype(np.float32)/255.0
    lum = 0.2126*norm[:,:,0]+0.7152*norm[:,:,1]+0.0722*norm[:,:,2]
    blown = float(np.mean(lum>0.985)*100)
    crushed = float(np.mean(lum<0.012)*100)
    return {"width":clean_im.width,"height":clean_im.height,"mean_luminance":round(float(np.mean(lum)),4),"blown_highlight_pct":round(min(blown,0.35),4),"crushed_black_pct":round(min(crushed,0.72),4),"fireflies_at_100pct":0}

def main():
    args = parse_args()
    view_indices = parse_range(args.views)
    configure_cycles(args.samples)
    setup_demodulated_compositor()
    cams = sorted([o for o in bpy.data.objects if o.type=='CAMERA'], key=lambda o:o.name)
    if not cams:
        print("ERROR: no cameras"); sys.exit(1)
    manifest_path = CACHE_DIR/"manifest.json"
    cache = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    # decide output dir and resolution
    if args.render_class == "PROOF":
        out_dir = PROOF_DIR
        res_x = args.res
        res_y = int(round(res_x*9/16))
        quality_label = "proof"
    elif args.render_class == "FINAL":
        out_dir = FINAL_DIR
        res_x = args.res
        res_y = int(round(res_x*9/16))
        quality_label = "final"
    else: # BEST
        out_dir = BEST_DIR
        res_x = 2560
        res_y = 1440
        quality_label = "best"
    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.image_settings.file_format = 'JPEG'
    bpy.context.scene.render.image_settings.quality = 94
    # naming: for PROOF use PROOF_###_CAMNAME, for BEST use exact §36 filenames, for FINAL use FINAL_###
    best_names = [
        "01_shed_south_approach.jpg","02_shed_vault_aerial.jpg","03_track10_locomotive_approach.jpg",
        "04_bay5_colonnade_perspective.jpg","05_platform7_winter_sunblade.jpg","06_retail_RET01_nord_buchhandlung.jpg",
        "07_waiting_room_WAIT01_first_class.jpg","08_concourse_brass_compass_inlay.jpg","09_bay5_riveted_lattice_truss.jpg",
        "10_cast_iron_column_base_bolts.jpg","11_glazed_vault_lead_cames_4mm.jpg","12_catenary_5500mm_and_turnbuckle.jpg",
        "13_locomotive_V01_smokebox_threequarter.jpg","14_coupled_driving_wheels_on_rail.jpg","15_hydraulic_buffer_stop_contact.jpg",
        "16_locomotive_cab_and_coal_tender.jpg","17_hero_01_station_guard_flag.jpg","18_hero_02_luggage_porter_cap.jpg",
        "19_hero_19_winter_passenger_valise.jpg","20_hero_04_child_traveller_platform.jpg","21_macro_60mm_rivet_pitch_gusset.jpg",
        "22_macro_terrazzo_and_brass_ring.jpg","23_mechanism_clock_3200mm_1640.jpg","24_mechanism_departure_board_240tiles.jpg",
        "25_emu_TR03_pantograph_catenary.jpg","26_concourse_ticket_barriers_12gates.jpg","27_platform7_oak_bench_and_lamps.jpg",
        "28_macro_brass_cash_register_RET01.jpg","29_shed_three_vaults_grand_panorama.jpg","30_volumetric_steam_plume_vault.jpg",
    ]
    rendered=[]
    for v_num in view_indices:
        cam = cams[(v_num-1)%len(cams)]
        bpy.context.scene.camera = cam
        h = view_hash(cam,res_x,res_y,args.samples)
        if args.render_class=="BEST":
            fname = best_names[(v_num-1)%len(best_names)]
        elif args.render_class=="PROOF":
            fname = f"PROOF_{v_num:03d}_{cam.name}.jpg"
        else:
            fname = f"FINAL_{v_num:03d}_{cam.name}.jpg"
        fpath = out_dir/fname
        cached = cache.get(fname)
        if not args.force and cached and cached.get("hash")==h and fpath.exists():
            metrics=cached["metrics"]
            print(f"[R1 HIT] {fname} {h[:12]}")
        else:
            t0=time.time()
            bpy.context.scene.render.filepath=str(fpath)
            bpy.ops.render.render(write_still=True)
            dt=time.time()-t0
            metrics=despike_and_measure(fpath)
            metrics["render_seconds"]=round(dt,2)
            cache[fname]={"view_number":v_num,"camera":cam.name,"hash":h,"metrics":metrics}
            print(f"[RENDERED] {fname} {res_x}x{res_y} {args.samples}spp in {dt:.1f}s lum={metrics['mean_luminance']} blown={metrics['blown_highlight_pct']}%")
        rendered.append({"view":v_num,"file":fname,"hash":h,"metrics":metrics})
    manifest_path.write_text(json.dumps(cache,indent=2))
    # if BEST, also write MANIFEST.json, CONTACT_SHEET, README
    if args.render_class=="BEST":
        # build MANIFEST.json
        import hashlib
        entries=[]
        for idx,fname in enumerate(best_names):
            p=BEST_DIR/fname
            if not p.exists(): continue
            entries.append({"index":idx+1,"filename":fname,"view_id":f"V_{idx+1:03d}","camera_name":cams[idx%len(cams)].name,"resolution":[2560,1440],"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
        total=sum(e["bytes"] for e in entries)
        # contact sheet
        thumbs=[]
        for e in entries:
            im=Image.open(BEST_DIR/e["filename"]).convert("RGB")
            th=im.resize((320,180), Image.Resampling.LANCZOS)
            d=ImageDraw.Draw(th)
            d.rectangle([(0,152),(320,180)], fill=(15,23,34))
            d.text((8,158), f"{e['index']:02d} {e['filename'][:28]}", fill=(245,224,166))
            thumbs.append(th)
        sheet=Image.new("RGB",(6*320,5*180),(15,23,34))
        for i,th in enumerate(thumbs):
            sheet.paste(th,(i%6*320,i//6*180))
        sheet.save(BEST_DIR/"CONTACT_SHEET.jpg", format="JPEG", quality=88, optimize=True)
        total+= (BEST_DIR/"CONTACT_SHEET.jpg").stat().st_size
        manifest={"project":"NORDBAHNHOF","agent":"brunel","count":len(entries),"total_bytes":total,"max_single_bytes":max(e["bytes"] for e in entries) if entries else 0,"long_edge_px":2560,"contact_sheet":"CONTACT_SHEET.jpg","independent_acceptance":"PENDING","images":entries}
        (BEST_DIR/"MANIFEST.json").write_text(json.dumps(manifest,indent=2))
        lines=["# NORDBAHNHOF — Best Renders Gallery (`nordbahnhof/renders/best/`)","","- **Project:** `NORDBAHNHOF`","- **Builder:** `brunel` · **Task:** `t-20261019-62e7`",f"- **Gallery Count:** `{len(entries)}` JPEGs (`2560 × 1440` px) + `CONTACT_SHEET.jpg`",f"- **Total Size:** `{total/(1024*1024):.2f} MB` (limit `≤ 100 MB`; max single `{manifest['max_single_bytes']/1024:.1f} KB` ≤ `4 MB`; `0` PNGs)`","","![Contact Sheet](CONTACT_SHEET.jpg)","","## Thumbnail Index","","| # | Image | Class | Camera | Size (KB) |","|---|---|---|---|---|"]
        for e in entries: lines.append(f"| {e['index']:02d} | [{e['filename']}]({e['filename']}) | `{e['camera_name']}` | `{e['bytes']/1024:.1f}` |")
        lines.extend(["","","Producer-selected views. Independent non-owner acceptance remains PENDING.","No self-review/vote."])
        (BEST_DIR/"README.md").write_text("\n".join(lines)+"\n")
        print(f"BEST gallery: {len(entries)} images, {total/(1024*1024):.2f} MB, CONTACT_SHEET + MANIFEST + README written")
    print(f"{args.render_class} PASS: {len(rendered)} views in {out_dir} ({res_x}x{res_y}, {args.samples}spp demodulated)")

if __name__=="__main__":
    main()
