# DENSITY.md — Victorian Court & Crowd Density Law (PAXTON / CRYSTAL)

Per **F17** (*"the courts are crowded Victorian — dense, layered, overstuffed per `DENSITY.md`; a modern-minimal court is a defect"*) and **F36** (*"Silhouette-collision law (`≤0.5%`), min-parts law, class-by-class density schedule"*), no court in **CRYSTAL** may read as an empty white gallery box.

---

## 1. Architectural & Exhibit Layering Law (`G5`, `F17`, `F36`)

Every National Court (`COURT-01..COURT-33`) and Catalogue Class zone (`Class I..XXX`) comprises **four mandatory physical layers**:

1. **Layer 1 — Court Enclosure & Crimson Drapery:**
   - Partition screens on the `7.32 m` (`24-ft`) grid clad in Turkey-red cotton baize (`#8F1D18`) per Owen Jones's specification (`REF-038`), framed by moulded timber cornices, national shields, and gilded fascias bearing the Country or Class title in slab-serif 1851 typography.
2. **Layer 2 — Overhead Banners, Carpets & Trophies:**
   - Suspended Wilton/Axminster carpets, Gobelins tapestries, Lyon silk canopies, and national flags hanging from the gallery girders (`Z = 7.32 m`) into the ground aisles, breaking up the long axial sightlines and catching oblique `25.0°` afternoon sunlight.
3. **Layer 3 — Stepped Plinths, Mahogany Vitrines & Cast-Iron Stands:**
   - Multi-tiered mahogany-and-brass glass display cases, octagonal stepped pyramids, velvet-draped pedestals, and iron machine beds occupying **`55%–72%` of the net court floor footprint** (leaving `2.4 m–3.6 m` circulation aisles).
4. **Layer 4 — The `12,000` Individually Modelled Exhibits (`EXHIBITS.jsonl`):**
   - Average `141` exhibits per bay (`400` exhibits per Catalogue Class `I–XXX`).
   - **Minimum part count (`v_exhibits`):** `≥ 8` distinct geometric sub-parts per exhibit (e.g., base plinth, frame, body, gears/scrolls/handles, brass plaque, fasteners, crown/finial) for Classes `II–XXX`; Class `I` mineral/raw-material specimens (`≥ 4` faceted/layered cleavage & plinth parts with high-frequency mineral surface craft).
   - **Silhouette diversity (`v_exhibits`):** 60 distinct procedural generator families parameterized by catalogue dimensions, aspect ratio, symmetry order, and sub-assembly topology so pairwise silhouette-hash collisions on a `5%` (`600`-exhibit) sample are **`≤ 0.5%`**.

---

## 2. Class-by-Class Spatial Density Schedule

| Section | Classes | Exhibits | Floor Area Share | Target Objects / Bay | Vertical Tiering (`Z` span in court) |
|---|---|---:|---:|---:|---|
| **I · Raw Materials** | `I–IV` | `1,600` | `14%` | `110–145` | Stepped mineral pyramids, timber trophies rising to `Z = 6.2 m` |
| **II · Machinery** | `V–X` | `2,400` | `26%` | `120–180` | Heavy iron bedplates (`Z = 0.0–3.8 m`), overhead line-shafting & pulleys at `Z = 5.5 m` |
| **III · Manufactures** | `XI–XXIX` | `7,600` | `48%` | `150–220` | 3-tier vitrines (`Z = 0.8–3.2 m`) + suspended textile/carpet drops (`Z = 3.5–7.1 m`) |
| **IV · Fine Arts** | `XXX` | `400` | `12%` | `45–80` | Monumental nave/transept pedestals (`Z = 1.2–6.8 m`) + crimson velvet rotundas |
| **Total** | **`I–XXX`** | **`12,000`** | **`100%`** | **`~141 / bay`** | **Crowded Victorian layering enforced in all 85 bays** |

---

## 3. Crowd Distribution Law (`CROWD.md` / `STRATA.md`, `2,400` Visitors at `14:00 GMT`)

At **14:00 GMT on Saturday 11 October 1851**, the `2,400` visitors are distributed by historical attraction gravity:

| Zone | Bay Range | Visitor Count | Share | Dominant Strata | Behavioral Pattern |
|---|---|---:|---:|---|---|
| **1. Transept Crossing & Crystal Fountain** | `B037–B039` | `480` | `20.0%` | `S01, S02, S05, S07, S08, S10, S11` | Concentric ring around Osler's Fountain, gazing up at the 3 Elms and 108-ft arch; queue at Koh-i-Noor cage |
| **2. Central Nave Spine (West & East)** | `B001–B036`, `B040–B076` (`|Y| < 11m`) | `660` | `27.5%` | All strata `S01–S12` | Bidirectional promenade along the 1,851-ft walk, clustering around Nave trophies (Godfrey de Bouillon, Amazon, Greek Slave, Malachite Doors) |
| **3. Machinery in Motion & North West Aisle** | `B001–B035` N, `B077–B082` | `420` | `17.5%` | `S03, S04, S06, S12` | Dense rings around Hibbert & Platt cotton mules, Applegath Times press, and Gooch's *Lord of the Isles* locomotive |
| **4. British Manufactures & Fine Arts Courts** | `B014–B036` S | `360` | `15.0%` | `S01, S02, S04, S05, S06, S08` | Inspecting Pugin's Mediaeval Court, Sheffield Cutlery, Birmingham Hardware, and Canadian/Indian Courts |
| **5. Foreign National Courts (East Wing)** | `B040–B076` N/S | `300` | `12.5%` | `S01, S03, S04, S08, S09` | Crowds in French Gobelins, Austrian Carved Rooms, Zollverein Octagon, Ploucquet's Taxidermy, and US Court |
| **6. First Galleries & Refreshment Courts** | `B001–B076` (`Z = 7.32 m`), `COURT-33` | `180` | `7.5%` | `S01, S04, S05, S08, S10, S11` | Leaning on crimson-draped gallery railings looking down into the Nave; families seated at Schweppes Refreshment Court |
| **Total** | **All Zones** | **`2,400`** | **`100.0%`** | **`S01–S12`** | **Zero floating figures (`v_float`); zero collisions with exhibits (`v_clearance`)** |
