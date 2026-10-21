# TOUR.md — Architectural & Exhibition Guide to PAXTON / CRYSTAL (1851)

## 1. The Building & The 24-Foot Module (`CONSTANTS.md` · `CONFLICTS.md`)
- **Site:** Southern Hyde Park, London (`51.5028° N, 0.1685° W`; ephemeris reference `51.50° N, 0.13° W`), between Rotten Row and Kensington Drive.
- **Dimensions:** `564.000 m` (`1,851 ft`) East–West length × `138.000 m` (`454 ft`) maximum North–South width (`124.440 m` / `408 ft` main body + `13.560 m` North Machinery Annex).
- **Structural Module:** Every column, girder, gutter, and bay center lies on Joseph Paxton's **`7.320 m` (`24 ft`)** module grid (`±0.000 mm` error across all `3,300` columns).
- **Vertical Tiers:** Ground floor (`Z = 0.000 m`), First Gallery (`Z = +7.320 m`), Second Clerestory Tier (`Z = +13.420 m`), Nave Roof Truss (`Z = +19.520 m`), and Transept Barrel-Vault Crown (`Z = +33.000 m` / `108 ft`).

## 2. The Three Wonders (`wonders/*.blend`)
1. **Osler's 27-ft Crystal Fountain (`wonders/fountain.blend`):** Positioned at the Transept crossing (`0.0, 0.0, 0.0`), assembled from **`1,842`** individually faceted flint-glass blocks around a concealed wrought-iron armature (`8.23 m` height, 4 tons of crystal glass).
2. **Gray & Davison Great Organ (`wonders/organ.blend` · `ledgers/ORGAN_PIPES.jsonl`):** Positioned at the North Transept Gallery (`0.0, 26.5, 7.32`), housing **`4,500`** speaking pipes across 5 divisions and 68 stops (`32-ft` pedal to `1-ft` mixtures). Every pipe's mesh length is computed from MIDI note, stop footage, diameter end-correction, and `16.0 °C` hall speed of sound (`340.865 m/s`) within `±0.02%` (`≤ 2%` law).
3. **Three Enclosed Hyde Park Elms (`wonders/elms.blend`):** The North (`185101`, `42,400` leaves), Center (`185102`, `44,800` leaves), and South (`185103`, `41,600` leaves) live elm trees enclosed inside the `33.0 m` Transept vault with `1.28 m` minimum clearance to the arch ribs (`≥ 1.20 m` law).

## 3. The 12,000 Exhibits & 33 National/Colonial Courts (`FLOORPLAN.md` · `ledgers/EXHIBITS.jsonl`)
- **West Half (`B000..B036` & `B077..B084`):** United Kingdom & Colonies across all 30 Official Catalogue Classes (`Class I` Mining & Minerals through `Class XXX` Sculpture & Fine Arts), including the North-West Machinery-in-Motion Annex (`B077..B084`), Pugin's Mediaeval Court, Sheffield, Birmingham, Manchester, India (East India Company & Koh-i-Noor cage), and Canada.
- **East Half (`B040..B076`):** Foreign States led by France (`Gobelins` & `Sèvres`), the German Zollverein, Austria, Russia (malachite doors & urns), Belgium, Switzerland, Italy, Ottoman Empire, Egypt, China, Brazil, and the United States (at the East Nave termination).

## 4. The 1,851-Foot Walk & Best Views (`renders/best/` · `ledgers/WALK_STATIONS.jsonl`)
- **Walk Stations (`W0001..W1851`):** `1,851` stations spaced `1.000 ft` (`0.3048 m`) apart along the Central Nave from East (`X = +281.94 m`) to West (`X = -281.94 m`) at `Z = 1.60 m` eye height.
- **30 Curated Views (`renders/best/BEST_01.jpg .. BEST_30.jpg`):** Spanning 4K heroes (`3840×2160`), transept vault plates, the Three Wonders, exterior approaches, measured sections, national courts, exhibit classes, Victorian crowd portraits, 1:1 material macros, sim-driven construction stills, walk stations, weather studies, and Paxton gutter walkways.
