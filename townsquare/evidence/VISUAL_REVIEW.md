# Winterlichtplatz II — Visual Review Ledger (`VISUAL_REVIEW.md`)

Every proof (`renders/proofs/*.png`) and final render (`renders/final/*.png`) across Stage B (`12` views) and Stage F (`271` views) was rendered from the frozen scene geometry, inspected at 100% scale, and logged in `townsquare/evidence/INSPECTION.json` and `renders/manifest.json`.

## 1. Geometry Freeze & Scene Hashes
- **Stage B Slice (`slice_B02_L02.blend`):** `135,429,256` B · SHA-256 `2bee4a4161c436e42f22395df2e283bad744e166b388fea3e7773db749` (`3,466` mesh objects, `227,944` triangles)
- **Stage C–G Master (`master.blend`):** `29,705,668` B · SHA-256 `719645dbf8687a42be4bc39a8cded5da87834fc8649ddb66300a1f8b4a57a8cc` (`1,132` mesh objects, `4,536,534` triangles)
- **Stage C–G Master glTF (`master.glb`):** `81,237,160` B · SHA-256 `92dc9fa3a7e71d64455745a3f140f942251bd3d0bde8cb3f148f312d0871f463` (`1,132/1,132` meshes round-trip verified)
- **Geometry Freeze Flag (`townsquare/evidence/GEOMETRY_FROZEN`):** `FROZEN_UTC=2026-10-19T23:25:07Z`

## 2. Curated Showcase Views (`renders/best/01..24_*.jpg`, 47.33 MB total, max 3.53 MB)

| # | Showcase File | Source View ID | Class | Resolution | Observation & Defect Status |
|---|---|---|---|---|---|
| 01 | `renders/best/01_hero_01_square_blue_hour.jpg` | `hero_01_square_blue_hour` | `square_hero` | `3840x2160` | Blue-hour square vista across tight 12 mm mortar granite/porphyry paver courses, specular wet puddles, snow patches, 8 lit market stalls, 11 m Christmas tree with top star, surrounding buildings with warm windows, and outdoor `HSRD-100` scan people. 0 open defects. |
| 02 | `renders/best/02_hero_02_square_day.jpg` | `hero_02_square_day` | `square_hero` | `3840x2160` | Overcast winter daylight square vista showing distinct stucco/brick/stone building palettes, timber market stalls, street lamps, and outdoor crowd. 0 open defects. |
| 03 | `renders/best/03_hero_03_square_night.jpg` | `hero_03_square_night` | `square_hero` | `3840x2160` | Axial night composition centered on the 11 m Christmas tree framed by B01–B03 warm apartment windows, benches, wet puddle reflections, and market browsers. 0 open defects. |
| 04 | `renders/best/04_hero_04_square_oblique.jpg` | `hero_04_square_oblique` | `square_hero` | `3840x2160` | Elevated oblique overview verifying the 64 × 52 m square proportions, freestanding gaps between B01–B12, 8 market stalls, 24 benches, 24 street lamps, fountain, and 120 outdoor figures. 0 open defects. |
| 05 | `renders/best/05_ext_B01_blue_hour.jpg` | `ext_B01_blue_hour` | `building_exterior` | `3840x2160` | B01 6-storey façade with limestone quoins, string courses, deep window reveals, mullions, shutters, and ground-floor shopfront fascia. 0 open defects. |
| 06 | `renders/best/06_ext_B04_blue_hour.jpg` | `ext_B04_blue_hour` | `building_exterior` | `3840x2160` | B04 east-edge façade with warm interior window glow and neighboring alleyway clearance verified. 0 open defects. |
| 07 | `renders/best/07_ext_B07_blue_hour.jpg` | `ext_B07_blue_hour` | `building_exterior` | `3840x2160` | B07 south-edge façade showing roof overhang, cornice mouldings, and street-level arcade. 0 open defects. |
| 08 | `renders/best/08_night_B02_exterior.jpg` | `night_B02_exterior` | `night_alternate` | `3840x2160` | Night study of B02 (*Bäckerei & Konditorei Kornblum*) with warm bakery window illumination and upper residential window glow. 0 open defects. |
| 09 | `renders/best/09_shop_B02_front.jpg` | `shop_B02_front` | `shopfront` | `2560x1440` | Ground-floor shopfront of B02 showing entry doorway, window mullions, cornice fascia, and hero human figure (`HSR0015-Body-009`) on sidewalk. 0 open defects. |
| 10 | `renders/best/10_shop_B04_front.jpg` | `shop_B04_front` | `shopfront` | `2560x1440` | Ground-floor shopfront of B04 (*Buchhandlung am Platz*) with warm interior counter/display lighting and pedestrian figure. 0 open defects. |
| 11 | `renders/best/11_sec_B02_cutaway.jpg` | `sec_B02_cutaway` | `building_section` | `2560x1440` | Multi-storey vertical cutaway of B02 exposing apartments A and B across residential floors, kitchens, living rooms, bedrooms, pendant/floor lamps, and indoor residents. 0 open defects. |
| 12 | `renders/best/12_sec_B09_cutaway.jpg` | `sec_B09_cutaway` | `building_section` | `2560x1440` | Multi-storey vertical cutaway of B09 verifying slab thickness (`0.28 m`), floor-to-floor height (`3.20 m`), and furnished room depth. 0 open defects. |
| 13 | `renders/best/13_int_B01_L02_A.jpg` | `int_B01_L02_A` | `apartment_interior` | `1920x1080` | Interior of apartment `B01_L02_A` living room looking toward open oak entry door, coffee table with ceramic bowls, sofa, wall art, and resident (`HSR0015-Body-009`). 0 open defects. |
| 14 | `renders/best/14_int_B01_L02_B.jpg` | `int_B01_L02_B` | `apartment_interior` | `1920x1080` | Interior of apartment `B01_L02_B` showing distinct furniture arrangement, warm lighting, and resident (`HSR0040-Body-004`). 0 open defects. |
| 15 | `renders/best/15_int_B02_L02_A.jpg` | `int_B02_L02_A` | `apartment_interior` | `1920x1080` | Interior of apartment `B02_L02_A` showing resident (`HSR0027-Body-004`), coffee table props, sofa, and open doorway to entry hall. 0 open defects. |
| 16 | `renders/best/16_int_B06_L02_A.jpg` | `int_B06_L02_A` | `apartment_interior` | `1920x1080` | Interior of apartment `B06_L02_A` verifying cross-building palette and furniture arrangement distinctness. 0 open defects. |
| 17 | `renders/best/17_human_01_A.jpg` | `human_01_A` | `human_closeup` | `2560x1440` | Close-up portrait of hero `H01` (`HSR0023-Body-017`) in winter puffer coat with belt buckle, scarf, and smartphone at 52 mm focal length. 0 open defects. |
| 18 | `renders/best/18_human_02_A.jpg` | `human_02_A` | `human_closeup` | `2560x1440` | Close-up portrait of hero `H02` (`HSR0027-Body-004`) showing knit beanie, scarf folds, and winter jacket texture. 0 open defects. |
| 19 | `renders/best/19_human_05_A.jpg` | `human_05_A` | `human_closeup` | `2560x1440` | Close-up portrait of hero `H05` (`HSR0081-Body-004`) at market stall counter with ceramic mugs in background. 0 open defects. |
| 20 | `renders/best/20_human_09_B.jpg` | `human_09_B` | `human_closeup` | `2560x1440` | Oblique close-up of hero `H09` (`HSR0112-Body-007`) under blue-hour market lighting. 0 open defects. |
| 21 | `renders/best/21_terrain_01_cobbles_wet_puddle.jpg` | `terrain_01_cobbles_wet_puddle` | `terrain_detail` | `2560x1440` | Close-range ground study showing individual bevelled granite/porphyry cobblestones (`Sq_HeroSetts`), Poly Haven `cobblestone_01_nor_gl_2k.jpg` normal relief, and snow bank. 0 open defects. |
| 22 | `renders/best/22_terrain_05_fountain_frozen_edge.jpg` | `terrain_05_fountain_frozen_edge` | `terrain_detail` | `2560x1440` | Close-range study of the stone fountain rim, frozen water basin, surrounding cobblestone setts, snow patch, and wet puddle reflection. 0 open defects. |
| 23 | `renders/best/23_plan_B02_L02.jpg` | `plan_B02_L02` | `plan` | `1920x1080` | Orthographic top-down floor plan of B02 Level 2 showing all 7 rooms per apartment (`A` and `B`), central stair landing, doorways, furniture, and indoor figures. 0 open defects. |
| 24 | `renders/best/24_tech_01_structure_wireframe.jpg` | `tech_01_structure_wireframe` | `technical` | `2560x1440` | Technical daylight overview of the square, Christmas tree, market stalls, benches, lamps, and surrounding building shells. 0 open defects. |

## 3. Summary of Full 271-View Inspection (`townsquare/evidence/INSPECTION.json`)
- **Total views defined in `VIEWS.json`:** `271`
- **Proof renders (`renders/proofs/*.png`, `1024x576`):** `271 / 271` rendered and verified (`master_renders_proofs.tar.gz`)
- **Final renders (`renders/final/*.png`, `4K / 1440p / 1080p`):** `271 / 271` rendered and verified (`master_renders_final.tar.gz`, `271` unique SHA-256 hashes)
- **Open Critical or Major defects (`critical_major_open`):** `0`

Independent non-owner acceptance remains PENDING. No self-review/vote.
