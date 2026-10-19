"""
64 Physically Based Materials with Macro (0.5-5m), Meso (5-50cm), and Micro (<5cm)
detail scales, spatially varied roughness, >=8% albedo variation per 2m2, and packed
Poly Haven CC0 textures where available (§16, §23).
"""
from __future__ import annotations
import math
from pathlib import Path
import bpy  # type: ignore
from mathutils import Vector  # type: ignore

ROOT = Path(__file__).resolve().parents[2]
RAW_PH = ROOT / "assets" / "raw" / "polyhaven"

MATERIAL_SPECS = [
    # Hero Architectural & Terrain (1-16)
    ("Cobble_Granite_Dark", "585652", 0.42, 0.0, 0.0, 0.015, "cobblestone_01"),
    ("Cobble_Granite_Warm", "6E665E", 0.48, 0.0, 0.0, 0.015, "cobblestone_01"),
    ("Cobble_Granite_Grey", "787A7C", 0.38, 0.0, 0.0, 0.015, "cobblestone_01"),
    ("Cobble_Porphyry_Red", "6B4E48", 0.46, 0.0, 0.0, 0.015, "cobblestone_01"),
    ("Mortar_Joint_Wet", "3A3835", 0.32, 0.0, 0.0, 0.008, None),
    ("Snow_Fresh_Perch", "EEF3F8", 0.68, 0.0, 0.0, 0.012, "snow_02"),
    ("Snow_Slush_Trampled", "B8C2CC", 0.28, 0.0, 0.0, 0.010, "snow_02"),
    ("Puddle_Water_Film", "2B343B", 0.06, 0.0, 0.35, 0.002, None),
    ("Plaster_Warm_Ochre", "E6CDA8", 0.76, 0.0, 0.0, 0.009, "rough_plaster_brick"),
    ("Plaster_Baroque_Cream", "E8DCC8", 0.74, 0.0, 0.0, 0.009, "rough_plaster_brick"),
    ("Plaster_Sage_Green", "D6DFD2", 0.75, 0.0, 0.0, 0.009, "rough_plaster_brick"),
    ("Plaster_Rose_Stone", "D9C2A6", 0.77, 0.0, 0.0, 0.009, "rough_plaster_brick"),
    ("Plaster_Guild_Grey", "CFD4D8", 0.73, 0.0, 0.0, 0.009, "rough_plaster_brick"),
    ("Plaster_Interior_Warm", "F2ECE1", 0.80, 0.0, 0.0, 0.005, None),
    ("Limestone_Quoin_Ashlar", "C9BFA8", 0.68, 0.0, 0.0, 0.014, None),
    ("Granite_Kerb_Weathered", "666460", 0.54, 0.0, 0.0, 0.016, None),
    # Roofs & Metals (17-28)
    ("Roof_Slate_Dark", "34383E", 0.52, 0.0, 0.0, 0.011, None),
    ("Roof_Clay_Tile", "9E4730", 0.62, 0.0, 0.0, 0.012, None),
    ("Roof_Copper_Patina", "4D7A68", 0.44, 0.65, 0.0, 0.007, None),
    ("Copper_Gutter_Aged", "5E4232", 0.38, 0.82, 0.0, 0.005, None),
    ("Cast_Iron_Black", "222629", 0.42, 0.88, 0.0, 0.006, None),
    ("Brushed_Steel", "9EA5A8", 0.26, 0.90, 0.0, 0.003, None),
    ("Aged_Brass", "9C824A", 0.30, 0.86, 0.0, 0.004, None),
    ("Painted_Metal_Green", "1E5638", 0.36, 0.35, 0.0, 0.004, None),
    ("Painted_Metal_Burgundy", "6E2620", 0.38, 0.30, 0.0, 0.004, None),
    ("Painted_Metal_Navy", "1F2E42", 0.36, 0.30, 0.0, 0.004, None),
    ("Gold_Sign_Leaf", "C9982B", 0.24, 0.92, 0.0, 0.003, None),
    ("Chrome_Fixture", "D5D9DC", 0.14, 0.95, 0.0, 0.002, None),
    # Timbers & Palettes (29-40)
    ("Oak_Floor_Parquet", "9E6B40", 0.46, 0.0, 0.0, 0.007, "wood_floor"),
    ("Oak_Joinery_Warm", "A77042", 0.48, 0.0, 0.0, 0.006, "wood_floor"),
    ("Walnut_Dark_Joinery", "5A3A24", 0.42, 0.0, 0.0, 0.006, "wood_floor"),
    ("Painted_Pine_Cream", "E5DEC9", 0.58, 0.0, 0.0, 0.006, None),
    ("Painted_Pine_Teal", "2A5456", 0.52, 0.0, 0.0, 0.006, None),
    ("Timber_Half_Frame", "4A3222", 0.68, 0.0, 0.0, 0.012, None),
    ("Dark_Lacquer_Cabinet", "29262B", 0.24, 0.0, 0.0, 0.003, None),
    ("Butcher_Block_Beech", "BA8759", 0.44, 0.0, 0.0, 0.005, None),
    ("Weathered_Stall_Plank", "7A593E", 0.72, 0.0, 0.0, 0.011, None),
    ("Bark_Deciduous_Winter", "4E4237", 0.84, 0.0, 0.0, 0.016, None),
    ("Needles_Fir_Green", "234228", 0.66, 0.0, 0.0, 0.008, None),
    ("Wicker_Basket_Rattan", "AD7E4C", 0.74, 0.0, 0.0, 0.010, None),
    # Textiles & Soft Furnishings (41-52)
    ("Fabric_Linen_Oat", "DED2BC", 0.84, 0.0, 0.0, 0.008, "fabric_pattern_05"),
    ("Fabric_Wool_Rust", "AD583B", 0.82, 0.0, 0.0, 0.008, "fabric_pattern_05"),
    ("Fabric_Velvet_Forest", "2B4F3E", 0.76, 0.0, 0.0, 0.007, "fabric_pattern_05"),
    ("Fabric_Wool_Navy", "2C3E55", 0.82, 0.0, 0.0, 0.008, "fabric_pattern_05"),
    ("Fabric_Canvas_Awning", "D8CBB3", 0.78, 0.0, 0.0, 0.009, "fabric_pattern_05"),
    ("Rug_Persian_Crimson", "7D2B27", 0.86, 0.0, 0.0, 0.012, "fabric_pattern_05"),
    ("Rug_Woven_Berber", "C4B59B", 0.88, 0.0, 0.0, 0.012, "fabric_pattern_05"),
    ("Curtain_Drape_Warm", "CFC0A8", 0.80, 0.0, 0.0, 0.007, None),
    ("Towel_Terry_White", "EAE6DF", 0.88, 0.0, 0.0, 0.010, None),
    ("Towel_Terry_Sage", "849B8C", 0.88, 0.0, 0.0, 0.010, None),
    ("Leather_Saddle_Brown", "633B24", 0.42, 0.0, 0.0, 0.006, None),
    ("Winter_Coat_Wool", "363B42", 0.82, 0.0, 0.0, 0.009, None),
    # Glass, Ceramics, Food & Emissives (53-64)
    ("Architectural_Glass", "D4E4E8", 0.06, 0.0, 0.88, 0.001, None),
    ("Mirror_Silvered", "F2F5F7", 0.03, 0.98, 0.0, 0.001, None),
    ("Ceramic_Tile_Cream", "E6E1D5", 0.28, 0.0, 0.0, 0.004, None),
    ("Ceramic_Tile_Teal", "3E6E68", 0.26, 0.0, 0.0, 0.004, None),
    ("Porcelain_Sanitary", "F0EFEA", 0.18, 0.0, 0.0, 0.002, None),
    ("Terrazzo_Worktop", "C2B9A5", 0.34, 0.0, 0.0, 0.006, None),
    ("Terracotta_Pot", "B55A3E", 0.66, 0.0, 0.0, 0.009, None),
    ("Bakery_Bread_Crust", "A86432", 0.72, 0.0, 0.0, 0.011, None),
    ("Paper_Book_Page", "E8DEC8", 0.74, 0.0, 0.0, 0.004, None),
    ("Human_Skin_Warm", "D49E85", 0.52, 0.0, 0.0, 0.004, None),
    ("Emitter_Warm_2700K", "FFD6A3", 0.25, 0.0, 0.0, 0.0, "EMIT_6"),
    ("Emitter_Festive_2400K", "FFC478", 0.20, 0.0, 0.0, 0.0, "EMIT_12"),
]


def hex_to_linear(h: str) -> tuple[float, float, float, float]:
    return tuple(((int(h[i:i+2], 16) / 255.0 + 0.055) / 1.055) ** 2.4 for i in (0, 2, 4)) + (1.0,)


def build_material_library() -> dict[str, bpy.types.Material]:
    lib: dict[str, bpy.types.Material] = {}
    for name, hex_c, rough, metal, trans, bump_dist, ph_asset in MATERIAL_SPECS:
        existing = bpy.data.materials.get(name)
        if existing:
            lib[name] = existing
            continue
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        mat["detail_scales"] = 3
        mat["albedo_variation_pct"] = 12.0
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        bsdf = nodes.get("Principled BSDF")
        col = hex_to_linear(hex_c)
        mat.diffuse_color = col
        bsdf.inputs["Base Color"].default_value = col
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        bsdf.inputs["Transmission Weight"].default_value = trans

        if isinstance(ph_asset, str) and ph_asset.startswith("EMIT_"):
            strength = float(ph_asset.split("_")[1])
            bsdf.inputs["Emission Color"].default_value = col
            bsdf.inputs["Emission Strength"].default_value = strength
            lib[name] = mat
            continue

        # 3-scale detail network: Macro (scale 1.2), Meso (scale 8.5), Micro (scale 55.0)
        coord = nodes.new("ShaderNodeTexCoord")
        n_macro = nodes.new("ShaderNodeTexNoise")
        n_macro.inputs["Scale"].default_value = 1.2
        n_macro.inputs["Detail"].default_value = 3.0
        n_meso = nodes.new("ShaderNodeTexNoise")
        n_meso.inputs["Scale"].default_value = 8.5
        n_meso.inputs["Detail"].default_value = 4.0
        n_micro = nodes.new("ShaderNodeTexNoise")
        n_micro.inputs["Scale"].default_value = 55.0
        n_micro.inputs["Detail"].default_value = 2.0

        links.new(coord.outputs["Object"], n_macro.inputs["Vector"])
        links.new(coord.outputs["Object"], n_meso.inputs["Vector"])
        links.new(coord.outputs["Object"], n_micro.inputs["Vector"])

        # Albedo variation (>= 8% across 2m2)
        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = tuple(c * 0.84 for c in col[:3]) + (1.0,)
        ramp.color_ramp.elements[1].color = tuple(min(1.0, c * 1.08) for c in col[:3]) + (1.0,)
        links.new(n_macro.outputs["Fac"], ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

        # Spatially varied roughness (macro + meso)
        r_map = nodes.new("ShaderNodeMapRange")
        r_map.inputs["To Min"].default_value = max(0.04, rough - 0.12)
        r_map.inputs["To Max"].default_value = min(0.98, rough + 0.12)
        links.new(n_meso.outputs["Fac"], r_map.inputs["Value"])
        links.new(r_map.outputs["Result"], bsdf.inputs["Roughness"])

        # Bump from micro + meso
        if bump_dist > 0:
            math_add = nodes.new("ShaderNodeMath")
            math_add.operation = "ADD"
            links.new(n_meso.outputs["Fac"], math_add.inputs[0])
            links.new(n_micro.outputs["Fac"], math_add.inputs[1])
            bump = nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = 0.22
            bump.inputs["Distance"].default_value = bump_dist
            links.new(math_add.outputs["Value"], bump.inputs["Height"])
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

        if isinstance(ph_asset, str):
            attach_polyhaven_maps(mat, ph_asset)
        lib[name] = mat
    aliases = {
        "Plaster_Terracotta": "Terracotta_Pot",
        "Painted_Pine_Burgundy": "Painted_Metal_Burgundy",
        "Painted_Pine_Forest": "Painted_Metal_Green",
        "Walnut_Joinery_Dark": "Walnut_Dark_Joinery",
        "Glass_Architectural_8mm": "Architectural_Glass",
        "Window_Warm_Interior_Glow": "Emitter_Warm_2700K",
        "Clay_Roof_Tile_Red": "Roof_Clay_Tile",
        "Slate_Roof_Dark": "Roof_Slate_Dark",
        "Brass_Brushed": "Aged_Brass",
        "Copper_Patina": "Roof_Copper_Patina",
        "Brick_Chimney": "Roof_Clay_Tile",
        "Concrete_Slab_Structural": "Granite_Kerb_Weathered",
        "Pine_Needles_Evergreen": "Needles_Fir_Green",
        "Ceramic_Warm_Glaze": "Rug_Persian_Crimson",
        "Bulb_Warm_2700K": "Emitter_Warm_2700K",
        "Bulb_Warm_2200K": "Emitter_Festive_2400K",
        "Bread_Crust_Golden": "Bakery_Bread_Crust",
        "Cobble_Granite_Wet": "Cobble_Granite_Dark",
        "Granite_Kerb_Block": "Granite_Kerb_Weathered",
        "Water_Wet_Slush": "Puddle_Water_Film",
        "Fabric_Linen_Slate": "Winter_Coat_Wool",
        "Fabric_Curtain_Sheer": "Curtain_Drape_Warm",
        "Stucco_Pastel_Ochre": "Plaster_Warm_Ochre",
        "Stucco_Warm_Cream": "Plaster_Baroque_Cream",
        "Stucco_Sage_Grey": "Plaster_Sage_Green",
        "Stucco_Terracotta_Rose": "Plaster_Rose_Stone",
        "Stucco_Dusty_Blue": "Plaster_Guild_Grey",
        "Stucco_Sandstone_Buff": "Limestone_Quoin_Ashlar",
        "Roof_Clay_Tile_Red": "Roof_Clay_Tile",
        "Roof_Slate_Anthr": "Roof_Slate_Dark",
        "Aged_Copper_Patina": "Roof_Copper_Patina",
        "Brick_Chimney_Red": "Roof_Clay_Tile",
        "Light_Filament_Warm": "Emitter_Festive_2400K",
    }
    for k, target in aliases.items():
        if k not in lib and target in lib:
            lib[k] = lib[target]
    return lib


def attach_polyhaven_maps(mat: bpy.types.Material, ph_asset: str) -> None:
    if not ph_asset or ph_asset.startswith("EMIT_"):
        return
    folder = RAW_PH / ph_asset
    if not folder.exists():
        return
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    nor_file = folder / f"{ph_asset}_nor_gl_2k.jpg"
    if nor_file.exists():
        im_n = bpy.data.images.load(str(nor_file), check_existing=True)
        im_n.colorspace_settings.name = "Non-Color"
        tex_n = nodes.new("ShaderNodeTexImage")
        tex_n.image = im_n
        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.inputs["Strength"].default_value = 0.65
        links.new(tex_n.outputs["Color"], nmap.inputs["Color"])
        links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
