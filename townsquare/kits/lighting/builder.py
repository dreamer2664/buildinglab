"""
Lighting & Atmosphere kit for Winterlichtplatz II (§16, §17, §20, §23 Gate G5).
Provides:
- `build_room_lighting`: 3 physical fixture meshes (ceiling rose, cord, shade/bulb) + 2 Blender lights
  per room (main 2700 K pendant + secondary 2400 K warm fill, clear_rays=8)
- `build_street_lamp`: 3.60 m cast-iron column, lantern cage, 2200 K emitter + snow cap
- `configure_world_and_color_management`: AgX view transform + blue_hour / overcast / night HDRI+sky setups.
"""
from __future__ import annotations
import math
from pathlib import Path
import bpy  # type: ignore
from townsquare.kits.core import spawn_bevel_box, spawn_lathe

RAW_HDRI = Path("/home/user/buildinglab/townsquare/assets/raw/polyhaven/hdri/cobblestone_street_night_2k.exr")


def kelvin_to_rgb(kelvin: float) -> tuple[float, float, float]:
    t = kelvin / 100.0
    if t <= 66.0:
        r = 1.0
        g = max(0.0, min(1.0, (99.4708025861 * math.log(t) - 161.1195681661) / 255.0))
        b = 0.0 if t <= 19.0 else max(0.0, min(1.0, (138.5177312231 * math.log(t - 10.0) - 305.0447927307) / 255.0))
    else:
        r = max(0.0, min(1.0, (329.698727446 * ((t - 60.0) ** -0.1332047592)) / 255.0))
        g = max(0.0, min(1.0, (288.1221695283 * ((t - 60.0) ** -0.0755148492)) / 255.0))
        b = 1.0
    return (r**2.2, g**2.2, b**2.2)


def spawn_blender_light(
    name: str,
    ltype: str,
    energy: float,
    kelvin: float,
    loc: tuple[float, float, float],
    coll: bpy.types.Collection,
    size: float = 0.25,
    rot_euler: tuple[float, float, float] = (0.0, 0.0, 0.0),
    **tags,
) -> bpy.types.Object:
    ldata = bpy.data.lights.new(name=name, type=ltype)
    ldata.energy = energy
    ldata.color = kelvin_to_rgb(kelvin)
    if ltype == "POINT":
        ldata.shadow_soft_size = size
    elif ltype == "AREA":
        ldata.size = size
    obj = bpy.data.objects.new(name=name, object_data=ldata)
    coll.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot_euler
    obj["clear_rays"] = int(tags.pop("clear_rays", 8))
    obj["kelvin"] = float(kelvin)
    for k, v in tags.items():
        obj[k] = v
    return obj


def build_room_lighting(
    room_id: str,
    cx: float,
    cy: float,
    ffl: float,
    ceil_h: float,
    w: float,
    d: float,
    mat_metal: bpy.types.Material,
    mat_emit: bpy.types.Material,
    coll: bpy.types.Collection,
    **tags,
) -> list[bpy.types.Object]:
    """
    Create 3 physical ceiling fixture props + 2 Blender lights per room (§20, G5).
    """
    cz = ffl + ceil_h
    objs = [
        spawn_lathe(
            f"{room_id}_CEIL_ROSE",
            [(0.06, 0.0), (0.05, -0.03), (0.015, -0.04)],
            (cx, cy, cz - 0.005),
            mat_metal,
            coll,
            role="prop",
            family="light_fixture",
            room_id=room_id,
            **tags,
        ),
        spawn_lathe(
            f"{room_id}_PENDANT_SHADE",
            [(0.02, 0.0), (0.02, -0.32), (0.19, -0.46), (0.18, -0.47)],
            (cx, cy, cz - 0.04),
            mat_metal,
            coll,
            role="prop",
            family="light_fixture",
            room_id=room_id,
            **tags,
        ),
        spawn_bevel_box(
            f"{room_id}_PENDANT_BULB",
            (0.065, 0.065, 0.095),
            (cx, cy, cz - 0.50),
            mat_emit,
            coll,
            role="prop",
            family="light_bulb",
            room_id=room_id,
            **tags,
        ),
        spawn_blender_light(
            f"{room_id}_LIGHT_MAIN",
            "POINT",
            energy=155.0,
            kelvin=2700.0,
            loc=(cx, cy, cz - 0.62),
            coll=coll,
            size=0.22,
            room_id=room_id,
            clear_rays=8,
            **tags,
        ),
        spawn_blender_light(
            f"{room_id}_LIGHT_SECONDARY",
            "POINT",
            energy=85.0,
            kelvin=2400.0,
            loc=(cx - w * 0.24, cy + d * 0.22, ffl + 1.65),
            coll=coll,
            size=0.18,
            room_id=room_id,
            clear_rays=8,
            **tags,
        ),
    ]
    return objs


def build_street_lamp(
    name: str,
    x: float,
    y: float,
    z: float,
    mat_iron: bpy.types.Material,
    mat_glass: bpy.types.Material,
    mat_emit: bpy.types.Material,
    mat_snow: bpy.types.Material,
    coll: bpy.types.Collection,
    **tags,
) -> list[bpy.types.Object]:
    """3.60 m cast-iron column, lantern cage, warm 2200 K emitter + snow cap (§16)."""
    profile = [
        (0.18, 0.0),
        (0.18, 0.45),
        (0.13, 0.55),
        (0.10, 1.25),
        (0.075, 2.85),
        (0.065, 3.15),
        (0.12, 3.22),
    ]
    return [
        spawn_lathe(
            f"{name}_COLUMN",
            profile,
            (x, y, z),
            mat_iron,
            coll,
            segments=20,
            role="street_lamp",
            family="street_lamp",
            **tags,
        ),
        spawn_bevel_box(
            f"{name}_LANTERN_GLASS",
            (0.26, 0.26, 0.34),
            (x, y, z + 3.39),
            mat_emit,
            coll,
            bevel=0.004,
            role="street_lamp_cage",
            family="street_lamp",
            **tags,
        ),
        spawn_bevel_box(
            f"{name}_LANTERN_CAP",
            (0.34, 0.34, 0.08),
            (x, y, z + 3.60),
            mat_iron,
            coll,
            bevel=0.003,
            role="street_lamp_cap",
            family="street_lamp",
            **tags,
        ),
        spawn_bevel_box(
            f"{name}_SNOW_CAP",
            (0.30, 0.30, 0.035),
            (x, y, z + 3.655),
            mat_snow,
            coll,
            bevel=0.004,
            role="snow_perch",
            family="snow",
            **tags,
        ),
        spawn_blender_light(
            f"{name}_EMITTER",
            "POINT",
            energy=420.0,
            kelvin=2200.0,
            loc=(x, y, z + 3.39),
            coll=coll,
            size=0.22,
            clear_rays=8,
            **tags,
        ),
    ]


def configure_world_and_color_management(scene: bpy.types.Scene, preset: str = "blue_hour") -> None:
    try:
        scene.view_settings.view_transform = "AgX"
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        scene.view_settings.view_transform = "Standard"
    scene.view_settings.exposure = 0.20 if preset in ("blue_hour", "night") else -0.15

    world = scene.world or bpy.data.worlds.new("TownWorld")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    if preset == "overcast":
        sky = nt.nodes.new("ShaderNodeTexSky")
        sky.sky_type = "HOSEK_WILKIE"
        sky.turbidity = 4.2
        sky.ground_albedo = 0.45
        sky.sun_elevation = math.radians(19.0)
        sky.sun_rotation = math.radians(40.0)
        bg.inputs["Strength"].default_value = 1.65
        nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    elif preset == "night":
        if RAW_HDRI.exists():
            env = nt.nodes.new("ShaderNodeTexEnvironment")
            env.image = bpy.data.images.load(str(RAW_HDRI), check_existing=True)
            mix = nt.nodes.new("ShaderNodeMixRGB")
            mix.blend_type = "MIX"
            mix.inputs["Fac"].default_value = 0.65
            mix.inputs["Color2"].default_value = (0.048, 0.080, 0.17, 1.0)
            nt.links.new(env.outputs["Color"], mix.inputs["Color1"])
            nt.links.new(mix.outputs["Color"], bg.inputs["Color"])
            bg.inputs["Strength"].default_value = 1.55
        else:
            bg.inputs["Color"].default_value = (0.048, 0.080, 0.17, 1.0)
            bg.inputs["Strength"].default_value = 1.55
    else:  # blue_hour
        if RAW_HDRI.exists():
            env = nt.nodes.new("ShaderNodeTexEnvironment")
            env.image = bpy.data.images.load(str(RAW_HDRI), check_existing=True)
            mix = nt.nodes.new("ShaderNodeMixRGB")
            mix.blend_type = "MIX"
            mix.inputs["Fac"].default_value = 0.72
            mix.inputs["Color2"].default_value = (0.090, 0.155, 0.34, 1.0)
            nt.links.new(env.outputs["Color"], mix.inputs["Color1"])
            nt.links.new(mix.outputs["Color"], bg.inputs["Color"])
            bg.inputs["Strength"].default_value = 1.95
        else:
            bg.inputs["Color"].default_value = (0.090, 0.155, 0.34, 1.0)
            bg.inputs["Strength"].default_value = 1.95


def configure_world_lighting(preset: str = "blue_hour") -> None:
    configure_world_and_color_management(bpy.context.scene, preset=preset)


def set_scene_lighting_mood(scene: bpy.types.Scene, preset: str) -> None:
    """Adjust sun & sky-bounce lights per preset so overcast, blue_hour, and night are unmistakably distinct."""
    configure_world_and_color_management(scene, preset=preset)
    sun = bpy.data.objects.get("Sun_Key") or bpy.data.objects.get("SQUARE_WINTER_SUN")
    sky_fill = bpy.data.objects.get("SkyBounce_FacadeFill")
    if preset == "overcast":
        scene.view_settings.exposure = -0.05
        if sun and sun.data:
            sun.data.energy = 4.60
            sun.data.color = kelvin_to_rgb(5800.0)
        if sky_fill and sky_fill.data:
            sky_fill.data.energy = 950.0
            sky_fill.data.color = kelvin_to_rgb(6000.0)
    elif preset == "night":
        scene.view_settings.exposure = 0.05
        if sun and sun.data:
            sun.data.energy = 0.05
        if sky_fill and sky_fill.data:
            sky_fill.data.energy = 380.0
            sky_fill.data.color = kelvin_to_rgb(7500.0)
    else:  # blue_hour
        scene.view_settings.exposure = 0.15
        if sun and sun.data:
            sun.data.energy = 0.12
            sun.data.color = kelvin_to_rgb(6800.0)
        if sky_fill and sky_fill.data:
            sky_fill.data.energy = 520.0
            sky_fill.data.color = kelvin_to_rgb(6800.0)
