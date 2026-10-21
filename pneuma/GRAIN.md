# GRAIN.md — the grain-scaling law, its derivation, and its error bar

**The commission's premise:** 48,000 millet grains discharge through a hopper and
*cause* seven and a half minutes of theatre. True millet is ~2 mm; the sim runs
grains at 4× (8 mm) with the orifice scaled identically. This file derives the
correction and states what it costs.

> **Status: DERIVED, NOT YET CALIBRATED.** Every number below is arithmetic from
> published grain properties and the Beverloo orifice law. None of it is a
> measurement. Stage E's exit criterion is a *measured* discharge rate on the
> bench; until then the numbers in this file are targets, and `v_grain` must
> refuse to pass on arithmetic alone.

---

## 1. What a millet grain actually is

| Property | Value | Basis |
|---|---|---|
| Length × width × thickness | 2.0 × 1.5 × 1.5 mm | proso millet, typical |
| Shape model | tri-axial ellipsoid | adequate for a rigid body |
| Volume | 2.36 mm³ | (π/6)·2.0·1.5·1.5 |
| True density | 1.30 g/cm³ | dry cereal grain, standard value |
| **Mass per grain** | **3.1 mg** | 2.36 mm³ × 1.30e-3 g/mm³ |
| Bulk density (poured) | 790 kg/m³ | proso millet test weight ≈ 0.79 |
| Void fraction | 0.39 | 1 − 790/1300 |

**48,000 grains therefore weigh 148 g**, and occupy 148/790 = 187 cm³ poured.
That is the entire fuel supply of the machine. It is small — a heaped
tablespoon — and it must time 450 s.

## 2. Why the sim runs grains at 4×

Not for convenience. A 2 mm rigid body in Bullet at these solver settings is at
or below the contact margin: grains interpenetrate, tunnel through the hopper
floor, and the solver's own noise dominates the signal. At 4× (8 mm spheres)
the contacts are resolved and the flow is physically meaningful.

**What 4× does and does not preserve:**

| Quantity | At 4× | Preserved? |
|---|---|---|
| Grain diameter / orifice diameter | identical (both ×4) | **yes** — geometric similarity |
| Grain / heap diameter | identical | **yes** |
| Time | ×2 slower (Froude: t ∝ √(L/g)) | **no — must be corrected** |
| Mass per grain | ×64 if density preserved | **no** |
| Mass flow rate | ×16 (grain mass ×64, rate ×2 slower... see §4) | **no** |
| Pressure in the heap | ×4 (ρ g h) | **no** |

The correction is a **Froude scaling**: sim time = 2 × real time. A discharge
measured at 50 s in the 4× sim corresponds to 25 s of real machine time.

## 3. The derivation: what discharge rate the commission actually needs

The weight descends exactly as fast as the grain leaves, so the run time is the
grain mass divided by the mass flow rate. This is the whole timing chain:

```
T = M / Q
```

- `T` = 450 s (the film, fixed — not ours to change, §36)
- `M` = 48,000 × 3.1 mg = **148 g**
- `Q` = **0.329 g/s** ← the rate the machine must hold

**That is the number everything else is judged against.**

## 4. What a free orifice gives

Granular discharge through a circular orifice follows the **Beverloo law**:

```
Q = C · ρ_b · √g · (D_o − k·d)^2.5
```

with `C ≈ 0.58`, `k ≈ 1.5–2.5` for rounded particles, `ρ_b` the bulk density,
`g` = 9.81 m/s², `D_o` the orifice diameter, `d` the grain diameter.

| Orifice D_o | Q (Beverloo, k=2.0) | Run time T = 148/Q |
|---|---|---|
| 8.0 mm | 1.45 g/s | **102 s** |
| 7.0 mm | 0.74 g/s | 200 s |
| 6.2 mm | 0.33 g/s | **450 s** ✔ |
| 5.2 mm | 0.20 g/s | 740 s |

**The finding:** a free 6.2 mm orifice delivers the required 450 s — but at
`D_o/d = 3.1` the flow sits at the edge of **arching**, where the grains bridge
the opening and the flow stops dead. Millet is near-spherical and flows well,
but 3.1 is tight, and an arch is a hard stop, not a slowdown.

## 5. Three lawful ways to hold 0.329 g/s without arching

1. **Overburden throttling (Heron's own design).** The weight rests *on* the
   grain. The normal stress it adds at the orifice reduces the flow rate —
   granular discharge is not pressure-independent the way a liquid's is. A
   heavier weight, or a shallower heap, buys throttle. This is the honest route
   because it is the mechanism Heron actually describes, and it is
   self-regulating: more grain left, more weight, slower flow.
2. **A metering slot, not a hole.** A slot of aspect ratio ≥ 6 arches far less
   readily than a circular hole of the same open area, because it cannot form a
   self-supporting dome. Area-equal to a 6.2 mm hole is a 3.1 × 6.2 mm slot.
3. **Two orifices in series** (an 8 mm hole above a 6.2 mm throat), which
   throttles without narrowing the ratio at the arching point.

**Chosen for the build:** the 8 mm hopper orifice from §13.3 (geometric
similarity at 4×) plus overburden throttling from the weight, with the slot as
the fallback if the bench arches. The throat in `PNEUMA.blend` is currently a
plain bronze ring at 55 mm radius — **it is a placeholder, not a calibrated
meter, and it will not hold 0.329 g/s.** That is a defect with an ID, not a
claim: `D-002`, open.

## 6. The error bar, stated before it is measured

| Source of error | Magnitude | Effect on T |
|---|---|---|
| `C` in Beverloo, real millet | ±20 % | T ±20 % (±90 s) |
| `k` (1.5 vs 2.5) | the range above | T 102 s → 450 s is reachable; the setting is the dominant unknown |
| Bulk density (season, moisture) | ±10 % | T ±10 % |
| Grain mass (3.1 mg, single value) | ±25 % (varietal) | T ±25 % |
| **Combined** | | **T = 450 ± 140 s at 1σ** |

**A 450 s run with a ±140 s band is not a ±0.4 s scene change.** G4 requires
every scene change within ±0.4 s. The gap between ±140 s and ±0.4 s is not
closable by arithmetic — it is closed by **bench calibration**: measure the
actual discharge, then set the rope-drum winding geometry so each scene change
lands where the *measured* rate puts it. The grain sets the pace; the drums
distribute it. This is precisely why Heron's machine is a program: the timing
lives in the drum windings, not in the grain.

## 7. What `v_grain` must check

1. 48,000 grains **counted in sim state**, not declared (`bpy.data.objects`).
2. **Wall contacts > 0** — a grain flow that never touches the hopper walls is a
   lie (§13.3). Measured as a contact count, not an assertion.
3. Discharge rate within the `GRAIN.md` band of the *measured* bench value.
4. The 4× correction applied to any timing claim, with the factor of 2 stated.
5. No grain below the hopper floor at any sampled frame (tunnelling).

## 8. The honest fakes in this file

1. **No measurement.** Every rate here is Beverloo arithmetic on published
   properties, not a discharge test. The bench test has not run.
2. **The throat is a placeholder.** 55 mm bronze ring, uncalibrated (D-002).
3. **The 3.1 mg grain mass** is a single published figure, not this batch.

These three are the grain drive's `FAKES.md` until Stage E measures them.
