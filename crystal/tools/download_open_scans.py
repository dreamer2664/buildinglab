#!/usr/bin/env python3
"""
download_open_scans.py — Downloads real open-source 3D scans (.glb, .blend, .obj, PBR textures, HDRIs)
for humans, buildings/interiors, statues, carriages, locomotives, fountains, trees, and Victorian exhibits:
  1. The Metropolitan Museum of Art CC0 3D Scans (api.vntana.com, 100k-poly GLBs with baked PBR textures)
  2. Poly Haven CC0 Photogrammetry 3D Models + 1K PBR Texture Maps + 1K HDRIs (dl.polyhaven.org)
  3. BlenderKit Free 3D Scanned Humans, Buildings, Statues, Carriages, Locomotives, Fountains (assets.blenderkit.com)
  4. Three.js / Khronos / GitHub Open-Source Clothed Human Figures, Busts & Sponza Palace Atrium
"""
from __future__ import annotations
import concurrent.futures
import json
import os
import urllib.parse
import urllib.request
import uuid

CRYSTAL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANS_DIR = os.path.join(CRYSTAL_DIR, "build", "scans")


def fetch_bytes(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def download_file(url: str, dest: str, timeout: int = 45) -> bool:
    if os.path.exists(dest) and os.path.getsize(dest) > 1024:
        return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        data = fetch_bytes(url, timeout=timeout)
        with open(dest, "wb") as fh:
            fh.write(data)
        return True
    except Exception as exc:
        print(f"  [WARN] Failed {url} -> {exc}")
        return False


def download_met_scans() -> list[dict]:
    print("=== 1. Downloading Met Museum CC0 3D Scans (GLB with baked PBR textures) ===")
    catalog_url = "https://raw.githubusercontent.com/InconsolableCellist/met_scans/master/catalog.json"
    catalog = json.loads(fetch_bytes(catalog_url).decode("utf-8"))
    by_id = {int(item["object_id"]): item for item in catalog if item.get("object_id")}

    wanted_met = [
        (10912, "met_mourning_victory_marble"),
        (24671, "met_henry_ii_armor"),
        (39165, "met_standing_buddha_brass"),
        (48982, "met_morning_glories_screen"),
        (75765, "met_seated_court_lady"),
        (204758, "met_canova_perseus_marble"),
        (204812, "met_carpeaux_ugolino_marble"),
        (242017, "met_aphrodite_statue"),
        (242109, "met_woman_statue"),
        (242211, "met_herakles_statue"),
        (248501, "met_marble_sphinx_capital"),
        (254613, "met_bronze_boy_eastern_dress"),
        (255417, "met_marble_female_figure"),
        (444540, "met_brass_sultan_brazier"),
        (445953, "met_islamic_architectural_niche"),
        (463716, "met_medieval_pieta_sculpture"),
        (470797, "met_cloisters_arch_spandrel"),
        (471321, "met_gothic_tomb_ermengol"),
        (547802, "met_temple_of_dendur_building"),
        (775805, "met_marble_wellhead_fountain"),
        (830041, "met_standing_horse_carved"),
        (854888, "met_marble_lion_sarcophagus"),
    ]

    results = []
    met_dir = os.path.join(SCANS_DIR, "met")
    os.makedirs(met_dir, exist_ok=True)

    def _dl_one(pair):
        oid, slug = pair
        item = by_id.get(oid)
        if not item:
            return None
        glb_files = [f for f in item.get("files", []) if f.get("format") == "GLB"]
        if not glb_files:
            return None
        url = glb_files[0]["download_url"]
        dest = os.path.join(met_dir, f"{slug}.glb")
        ok = download_file(url, dest, timeout=60)
        if ok:
            print(f"  [MET] {slug}.glb ({os.path.getsize(dest)//1024} KB) — {item.get('title')}")
            return {"slug": slug, "path": dest, "title": item.get("title"), "source": "Metropolitan Museum of Art CC0"}
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(_dl_one, wanted_met):
            if r:
                results.append(r)
    return results


def download_polyhaven_scans() -> list[dict]:
    print("=== 2. Downloading Poly Haven CC0 Photogrammetry 3D Models + PBR Textures + HDRIs ===")
    ph_models = [
        "gothic_statue",
        "marble_bust_01",
        "horse_statue_01",
        "lion_head",
        "bull_head",
        "bronze_whale_statue",
        "bronze_shark_statue",
        "carved_wooden_elephant",
        "large_iron_gate",
        "large_castle_door",
        "ArmChair_01",
        "ClassicConsole_01",
        "ClassicNightstand_01",
        "GothicCabinet_01",
        "GothicCommode_01",
        "gothic_coffee_table",
        "Sofa_01",
        "vintage_grandfather_clock_01",
        "mantel_clock_01",
        "Chandelier_01",
        "Chandelier_02",
        "Chandelier_03",
        "lantern_chandelier_01",
        "chinese_chandelier",
        "chinese_armchair",
        "chinese_cabinet",
        "chinese_screen_panels",
        "chinese_console_table",
        "fancy_picture_frame_01",
        "fancy_picture_frame_02",
        "cannon_01",
        "dutch_ship_large_01",
        "drill_press_01",
        "vintage_microscope",
        "industrial_microscope",
        "Camera_01",
        "CashRegister_01",
        "brass_candleholders",
        "brass_vase_01",
        "brass_vase_03",
        "antique_ceramic_vase_01",
        "book_encyclopedia_set_01",
        "chess_set",
        "jacaranda_tree",
        "island_tree_01",
        "island_tree_02",
        "potted_plant_01",
        "potted_plant_02",
        "fern_02",
    ]
    ph_hdris = [
        "old_hall",
        "museum_of_ethnography",
        "abandoned_greenhouse",
        "kloppenheim_06_puresky",
    ]
    ph_textures = [
        "wood_floor_deck",
        "wood_table_001",
        "red_brick",
        "cobblestone_floor_01",
    ]

    results = []
    ph_dir = os.path.join(SCANS_DIR, "polyhaven")

    def _dl_ph_model(aid: str):
        try:
            d = json.loads(fetch_bytes(f"https://api.polyhaven.com/files/{aid}").decode("utf-8"))
            b_info = d.get("blend", {}).get("1k", {}).get("blend")
            if not b_info:
                return None
            model_dir = os.path.join(ph_dir, aid)
            blend_path = os.path.join(model_dir, f"{aid}_1k.blend")
            if not download_file(b_info["url"], blend_path, timeout=45):
                return None
            for rel_path, inc_info in b_info.get("include", {}).items():
                inc_dest = os.path.join(model_dir, rel_path)
                download_file(inc_info["url"], inc_dest, timeout=45)
            print(f"  [PH-MODEL] {aid} ({os.path.getsize(blend_path)//1024} KB + PBR maps)")
            return {"slug": aid, "path": blend_path, "source": "Poly Haven CC0"}
        except Exception as e:
            print(f"  [WARN] PolyHaven model {aid}: {e}")
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(_dl_ph_model, ph_models):
            if r:
                results.append(r)

    hdri_dir = os.path.join(SCANS_DIR, "hdris")
    for hid in ph_hdris:
        try:
            d = json.loads(fetch_bytes(f"https://api.polyhaven.com/files/{hid}").decode("utf-8"))
            h_url = d["hdri"]["1k"]["hdr"]["url"]
            dest = os.path.join(hdri_dir, f"{hid}_1k.hdr")
            if download_file(h_url, dest, timeout=45):
                print(f"  [PH-HDRI] {hid}_1k.hdr ({os.path.getsize(dest)//1024} KB)")
                results.append({"slug": f"hdri_{hid}", "path": dest, "source": "Poly Haven CC0 HDRI"})
        except Exception as e:
            print(f"  [WARN] PolyHaven HDRI {hid}: {e}")

    return results


def download_blenderkit_scans() -> list[dict]:
    print("=== 3. Downloading BlenderKit Free 3D Scanned Humans, Buildings, Statues & Exhibits ===")
    bk_wanted = [
        # Real 3D scanned humans & people
        ("Standing Cute Girl White Jacket Jeans", "962869a8-0d61-4446-beaf-50262f5d98a5", "human_scan_woman_jacket"),
        ("Ju Black Leather Jacket Standing 1", "dd1f7225-c325-4d71-b5d2-62652222d32f", "human_scan_standing_coat"),
        ("Ju Arms Up Gray Sweater Standing 1", "97205f2d-18a6-44ad-b208-783f96201d37", "human_scan_standing_sweater"),
        ("Standing Survivor Girl Green Top Cowboy", "26badeaf-406b-4416-8602-c4dbed9c0ceb", "human_scan_woman_hat"),
        ("Standing Cool Bald Man", "0fdffc77-d514-49c3-b84f-a38513031536", "human_scan_standing_man_01"),
        ("Axel Blue Hawaii Shirt Walking 1", "26b3b437-3515-4665-98c3-98d81863db22", "human_scan_walking_man_01"),
        ("Axel Standing", "434f475b-a297-4833-abe8-d2ed230253df", "human_scan_standing_man_02"),
        ("Ju Dad Sit Red Shirt 1", "9ebb19ba-1021-4d2c-9ae4-d0a319fe9447", "human_scan_seated_man_01"),
        ("Sitting Boy with Black Sweater and Hat", "5c890cb3-25dd-4c6e-b0fc-40c83c2aa996", "human_scan_seated_boy_hat"),
        ("Sitting German Tourist Tyler", "fca91026-1ad3-47be-96fb-2fe383e24ea2", "human_scan_seated_man_02"),
        ("Stylized 1920s Noir Gentleman", "6bffdaba-8edc-4f00-848d-a23b824325c6", "human_gentleman_coat_hat"),
        ("Low poly old gentleman", "2a56eded-0b6b-4619-9fa6-360fed17191a", "human_old_gentleman"),
        ("Low poly man wearing suit", "606422bc-c77f-4ad3-a264-000f7e3f36bf", "human_man_suit_01"),
        ("Low poly man wearing suit", "447db195-cc1c-4809-8a75-28f5f06ec606", "human_man_suit_02"),
        ("Low poly man walking", "b50a3e35-8897-44c2-baa6-b50d16057259", "human_man_walking_02"),
        ("Lowpoly Female in coat", "6b87687d-28fb-4fc6-9253-764a60a3d3ea", "human_woman_coat_01"),
        ("Lowpoly Female Walking", "15acf398-2c8d-4a7f-87ac-152f1afcf73f", "human_woman_walking_01"),
        ("Lowpoly Female Walking", "b099e6c0-ea09-44d1-975b-bfcbda9fb2b4", "human_woman_walking_02"),
        ("Lowpoly Male Standing", "72a773d9-ec82-49b2-8584-38c864a44abc", "human_man_standing_03"),
        ("Lowpoly Female Standing", "77522cd1-c481-49e7-b817-0ad6bc00a28b", "human_woman_standing_03"),
        ("Gabled Chamber Tall Hat", "ffc69ca1-a83f-4d8c-a747-4aa021a02bfa", "victorian_top_hat"),
        # Real 3D scanned buildings & architectural interiors
        ("Greenhouse 3D model", "76b264fe-38b5-4c1b-ae3a-a05f5e217886", "arch_greenhouse_hall"),
        ("Glass Pavilion", "47fdc378-c17d-45de-ac97-8fd7a43cd7c1", "arch_glass_pavilion"),
        ("Berlin Dome Side Entrance", "831d7d9b-db04-45fb-8619-baf24ef72c7a", "arch_berlin_dome_entrance_scan"),
        ("Museum", "36a1112f-738a-48ab-9e96-20553f597a46", "arch_classical_museum_hall"),
        ("Medieval Guild Hall", "36ade5bf-505f-4fdc-ba77-58c89f36358d", "arch_medieval_guild_hall"),
        ("Church doorway", "87c8a6b0-b429-4e68-b482-a10259340de3", "arch_gothic_church_doorway_scan"),
        ("Stone Archway", "e6abd657-ff68-41ac-a2a1-5d35709d4f92", "arch_stone_archway_scan"),
        ("Dome Scanned", "99cc4fdf-65f7-459b-a2e3-b354331b94f8", "arch_dome_scanned"),
        ("Chinese Pavilion", "994b2f94-9f8a-4c37-9cc0-891fedea1998", "arch_chinese_pavilion"),
        ("Small round temple", "a76fbc86-3bf7-431c-a82e-3852e3996353", "arch_rotunda_temple"),
        ("Victorian arch bridge", "694923ff-245a-4207-a1fa-846cbd661f82", "arch_victorian_iron_bridge"),
        ("Paris METRO entrance square Pigalle", "9df0d343-37fa-44ea-b312-f11361311266", "arch_cast_iron_pavilion"),
        ("Corinthians Column", "98ce0e14-3335-4789-a642-79f0b2e01211", "arch_corinthian_column"),
        ("Balustrades", "b32f8f76-c506-4259-b732-358397330b8d", "arch_balustrades"),
        ("Large gothic window", "f27a014c-30d2-4b03-9017-6eb736062d5f", "arch_large_gothic_window"),
        # Real 3D scanned statues, fountains, locomotives, carriages & exhibits
        ("Vs Polyhymnia", "1d744972-c816-4ef0-aafd-2dd00c1d73d6", "statue_scan_polyhymnia"),
        ("Vs La Nymphe Salmacis", "90cad480-838a-4fd4-9cdf-3c67ecf34622", "statue_scan_nymphe_salmacis"),
        ("Vs St Francis Xavier", "c0642486-69fe-4a24-8ba4-82cef973b4e8", "statue_scan_st_francis"),
        ("Athena promachos", "611ee5c2-2c0b-40b2-aebf-11776425f9c1", "statue_scan_athena"),
        ("Farnese Dionysos", "aa48cdfc-859b-4afa-85fd-5afe24d38b04", "statue_scan_farnese_dionysos"),
        ("Statue (Photoscanned)", "ee35d370-01f6-4535-ba81-e9c5ff507a23", "statue_scan_classical_woman"),
        ("Victorian Wall Fountain (clear)", "1a58042f-a935-4ce8-a7dd-d26044d80869", "wonder_victorian_fountain"),
        ("Fountain", "cdcb8c52-0a7d-4a79-85e1-b530b15c4ded", "wonder_tiered_fountain"),
        ("Danish Odin Steam Locomotive", "9cfd28eb-fc41-41f0-87d2-119892a6e7ed", "exh_1846_odin_steam_locomotive"),
        ("NER Y7 Steam Locomotive Green", "08169c71-3a12-443d-bddb-58087604d817", "exh_green_steam_locomotive"),
        ("Rausch landauer horse-drawn carriage", "8dceb849-e6e0-4616-994c-bab89fcdb490", "exh_landauer_horse_carriage"),
        ("Simple Old Horse-Drawn Carriage", "11ccaf87-bd01-4c31-8acd-42fb96b43477", "exh_old_horse_carriage"),
        ("Prussian 12 pound cannon, 6 horses 1842", "416910f0-96af-47fa-b306-25e6ac5d188f", "exh_1842_prussian_cannon_6_horses"),
        ("Antique Worn Sewing Machine", "a681fdb5-645e-4c17-b0f0-f5f464c0af7e", "exh_scan_antique_sewing_machine"),
        ("Grand piano", "873fe07c-76b3-4135-9c4a-5d550a86a289", "exh_grand_piano"),
        ("Faux Antique Standing Globe", "78cc1f32-254c-4c0b-81b0-026a3c5f805b", "exh_antique_standing_globe"),
        ("Glass Front Display Case", "f21d7eae-fb78-415f-9375-bd80ec8cac50", "exh_glass_display_case"),
        ("Vintage Victorian Street Bench", "660c0f2b-cc1c-4966-8d0a-263dac7db3b5", "exh_victorian_street_bench"),
    ]

    bk_dir = os.path.join(SCANS_DIR, "blenderkit")
    os.makedirs(bk_dir, exist_ok=True)
    results = []

    def _dl_bk(item):
        qname, target_id, slug = item
        dest = os.path.join(bk_dir, f"{slug}.blend")
        if os.path.exists(dest) and os.path.getsize(dest) > 4096:
            return {"slug": slug, "path": dest, "source": "BlenderKit Free"}
        try:
            u = f"https://www.blenderkit.com/api/v1/search/?query={urllib.parse.quote(qname)}+is_free:true&asset_type=model&page_size=15"
            d = json.loads(fetch_bytes(u, timeout=15).decode("utf-8"))
            match = None
            for r in d.get("results", []):
                if r.get("id") == target_id:
                    match = r
                    break
            if not match and d.get("results"):
                match = d["results"][0]
            if not match:
                return None
            # Prefer resolution_1K or resolution_2K or blend
            files_by_type = {f.get("fileType"): f.get("downloadUrl") for f in match.get("files", [])}
            dl_endpoint = (
                files_by_type.get("resolution_1K")
                or files_by_type.get("resolution_0_5K")
                or files_by_type.get("blend")
                or files_by_type.get("resolution_2K")
            )
            if not dl_endpoint:
                return None
            res_info = json.loads(fetch_bytes(f"{dl_endpoint}?scene_uuid={uuid.uuid4()}", timeout=15).decode("utf-8"))
            file_url = res_info.get("filePath")
            if not file_url:
                return None
            if download_file(file_url, dest, timeout=60):
                print(f"  [BK] {slug}.blend ({os.path.getsize(dest)//1024} KB) — {match.get('name')}")
                return {"slug": slug, "path": dest, "title": match.get("name"), "source": "BlenderKit Free"}
        except Exception as e:
            print(f"  [WARN] BK {slug}: {e}")
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        for r in ex.map(_dl_bk, bk_wanted):
            if r:
                results.append(r)
    return results


def download_threejs_and_github_scans() -> list[dict]:
    print("=== 4. Downloading Three.js / Khronos / GitHub Clothed Human Figures & Statue Scans ===")
    t_dir = os.path.join(SCANS_DIR, "github")
    os.makedirs(t_dir, exist_ok=True)
    direct_assets = [
        ("threejs_tennyson_bust.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/tennyson-bust.glb"),
        ("threejs_nemetona_statue.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/nemetona.glb"),
        ("threejs_michelle_human.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/Michelle.glb"),
        ("threejs_soldier_human.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/Soldier.glb"),
        ("threejs_kira_human.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/kira.glb"),
        ("threejs_readyplayerme_human.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/readyplayer.me.glb"),
        ("threejs_horse.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/Horse.glb"),
        ("threejs_steampunk_camera.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/steampunk_camera.glb"),
        ("threejs_anisotropy_barn_lamp.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/AnisotropyBarnLamp.glb"),
        ("threejs_iridescence_lamp.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/IridescenceLamp.glb"),
        ("threejs_sheen_chair.glb", "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/SheenChair.glb"),
        ("gh_human_tranthi.glb", "https://raw.githubusercontent.com/hmthanh/3d-human-model/main/TranThiNgocTham.glb"),
        ("gh_human_thanh.glb", "https://raw.githubusercontent.com/hmthanh/3d-human-model/main/Thanh.glb"),
        ("gh_human_suit.glb", "https://raw.githubusercontent.com/Siddu7077/3D-model/main/men_suit_short_pant.glb"),
        ("stanford_lucy.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/lucy.obj"),
        ("stanford_igea_bust.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/igea.obj"),
        ("stanford_bimba_bust.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/bimba.obj"),
        ("stanford_max_planck_bust.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/max-planck.obj"),
        ("stanford_nefertiti_bust.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/nefertiti.obj"),
        ("stanford_happy_buddha.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/happy.obj"),
        ("stanford_dragon.obj", "https://raw.githubusercontent.com/alecjacobson/common-3d-test-models/master/data/xyzrgb_dragon.obj"),
    ]
    results = []
    for fname, url in direct_assets:
        dest = os.path.join(t_dir, fname)
        if download_file(url, dest, timeout=45):
            print(f"  [GH] {fname} ({os.path.getsize(dest)//1024} KB)")
            results.append({"slug": fname, "path": dest, "source": url})
    return results


def main():
    os.makedirs(SCANS_DIR, exist_ok=True)
    all_assets = []
    all_assets.extend(download_met_scans())
    all_assets.extend(download_polyhaven_scans())
    all_assets.extend(download_blenderkit_scans())
    all_assets.extend(download_threejs_and_github_scans())

    manifest_path = os.path.join(SCANS_DIR, "SCANS_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(all_assets, fh, indent=2)
    print(f"\nDownloaded {len(all_assets)} real open-source 3D scan & photogrammetry assets -> {manifest_path}")


if __name__ == "__main__":
    main()
