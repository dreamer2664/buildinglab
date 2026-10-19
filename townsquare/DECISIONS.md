# Winterlichtplatz II — Architectural & Engineering Decisions (`DECISIONS.md`)

Every choice not explicitly fixed by the commission packet is recorded here with its UTC date and rationale.

## 2026-10-19 — D-001: Building footprints around the 64 × 52 m clear square
- **Context:** §14.1 requires a clear 64 × 52 m square (origin at centre `(0, 0, 0)`, `+X` east, `+Y` north, `+Z` up) ringed by 12 independent buildings (B01–B12) with no two sharing a party wall (freestanding gaps ≥ 1.20 m between neighbours), each able to hold 2 full 7-room apartments per residential floor plus a central stair/lift landing core.
- **Decision:** Ring the 64 × 52 m clear square with 12 freestanding buildings set along the four edges (North: B01, B02, B03; East: B04, B05, B06; South: B07, B08, B09; West: B10, B11, B12), each separated by a minimum 1.50 m alleyway gap, with floor plates sized 14.0–18.0 m × 11.5–13.0 m (161–234 m² gross per floor) so that every residential floor comfortably accommodates a common landing (`L`) and two complete 7-room apartments (`A` and `B`: entry hall, living room, kitchen, bedroom, bathroom, separate WC, storage/utility) with ≥ 75 % net occupied area and full window/door connectivity.

## 2026-10-19 — D-002: Debian Blender 4.3.2 denoiser & memory budget (F10, F20)
- **Context:** Runtime is Debian `Blender 4.3.2` (`4.3.2+dfsg-2`) on 2 CPU cores and 1.9 GiB RAM without OpenImageDenoise (OIDN).
- **Decision:** Record `use_denoising = False` in Cycles and use deterministic multi-scale procedural + packed PBR surface shading with clamped indirect light (`sample_clamp_indirect = 4.0`, `sample_clamp_direct = 8.0`) and physical area light softening so fireflies = 0 without denoiser blur (respecting §18 rule 18 and F20). Consolidate static distant geometry or use tiled rendering for 4K views to stay strictly within 1.9 GiB RAM (avoiding F10).
