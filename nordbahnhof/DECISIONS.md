# NORDBAHNHOF — Engineering & Architectural Decisions (`DECISIONS.md`)

Every choice not explicitly fixed by the commission packet is recorded here with its UTC date and rationale.

## 2026-10-19 — D-001: Coordinate datum and spatial zoning within the 240 × 120 m footprint
- **Context:** §13.1 and §15.1 specify a 240 × 120 m (28,800 m²) footprint (`X ∈ [-120.0, +120.0]`, `Y ∈ [0.0, 120.0]`, `+Z` up, north = `+Y`), origin `(0, 0, 0)` at the main south entrance portico centreline on L0 (`Z = 0.00 m`), and a 180 × 84 m train shed (`X ∈ [-90.0, +90.0]`, `Y ∈ [36.0, 120.0]`, ridge `+26.0 m`, eaves `+14.0 m`).
- **Decision:**
  - **Headhouse (`Y ∈ [0.0, 36.0]`, `X ∈ [-120.0, +120.0]`):** Contains the 24 m stone entrance portico (`X ∈ [-12.0, +12.0]`, `Y = 0.0`), the 4,800 m² Concourse (`L0`, `160 × 30 m`), Ticket Hall, retail parades, restaurants & kitchens, waiting rooms, restrooms, L1 offices & stores, and L2 gallery.
  - **Train Shed (`Y ∈ [36.0, 120.0]`, `X ∈ [-90.0, +90.0]`):** 180 m long (East–West along `X`, divided into 8 structural bays defined by 8 riveted lattice trusses at 21.0 m centres and 12 cast-iron columns at 21.0 m centres) × 84 m wide (North–South along `Y`, three barrel vaults spanning 28.0 m each). Houses 8 platforms (180 m long, widths 4.0–9.0 m, heights 550 mm low / 760 mm high) and 12 standard-gauge tracks (1,435 mm ±2 mm).
  - **East & West Wings (`X ∈ [-120.0, -90.0]` and `X ∈ [+90.0, +120.0]`, `Y ∈ [36.0, 120.0]`):** Perimeter brick-and-stone station wings housing parcels/left-luggage, police/first-aid, staff rooms, plant rooms, retail units, and vertical circulation cores.
  - **Subsurface Levels (`B1` at `Z = -4.20 m`, `B2` at `Z = -9.00 m`):** Reinforced concrete subsurface levels housing the B1 baggage handling hall & stores and the B2 metro station (120 m platform, tunnel mouths, tracks, tiling, metro train, and machine/staff rooms).

## 2026-10-19 — D-002: Debian Blender 4.3.2 denoiser & memory budget (F10, F20)
- **Context:** Worker runs Debian `Blender 4.3.2` (`4.3.2+dfsg-2`) on 2 CPU cores and 1.9 GiB RAM without OpenImageDenoise (OIDN).
- **Decision:** Record missing OIDN in `TOOLCHAIN.txt` (F20); set `cycles.use_denoising = False` with clamped direct/indirect sampling (`sample_clamp_direct = 8.0`, `sample_clamp_indirect = 4.0`) and physical area light softening so fireflies = 0 without denoiser blur (§17 rule 18). Use geometry-hash render caching (R1) and 1024 px proofs before finals (R2).
