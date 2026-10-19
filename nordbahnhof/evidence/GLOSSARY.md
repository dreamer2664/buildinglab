# NORDBAHNHOF — Technical & Architectural Glossary (`GLOSSARY.md`)

| Term | Spec / Section | Measured Value in `NORDBAHNHOF.blend` / `design/*.json` |
|---|---|---|
| **Lattice Arch Truss** | §7.1 / T1 | 8 primary wrought-iron three-hinged/tied barrel-vault lattice arches spanning `84.0 m` (3 vaults × `28.0 m`) at `21.0 m` bay centres, ridge `+26.00 m`, eaves `+14.00 m`. |
| **Rivet Pitch** | §7.1 / T1 | `60.0 mm ±1.0 mm` centre-to-centre along loaded gussets and chord flanges; `18.0 mm ±0.5 mm` dome head diameter (`RIVET_B5_*`). |
| **Gusset Plate** | §7.1 / T1 | `28 mm` wrought-iron connection plate uniting upper/lower chords and Warren/X-lattice diagonals at each panel node (`TRUSS_*_Gusset_*`). |
| **Cast-Iron Column** | §7.1 / T1 | 12 fluted cast-iron columns at `21.0 m` centres (`650 mm` diameter), octagonal granite plinth, base flange with 8 holding-down bolts & hex nuts, Corinthian capital (`COL_01`..`COL_12`). |
| **Lead Came** | §7.2 / T2 | `4.0 mm` H-section extruded lead glazing bar framing each of the `4,200` roof panes, soldered at every intersection (`CAME_Bay5_*`, `SOLDER_Bay5_*`). |
| **Standard Track Gauge** | §7.5 / §15.1 | `1,435 mm ±2 mm` between inner running faces of bullhead steel rails on creosoted oak sleepers and cast-iron chairs (`TRK_10_Rail_South/North`). |
| **Check Rail** | §7.5 / §21 | Guard rail mounted `57.5 mm` inside running rail (`TRK_10_CheckRail_*`) to guide wheel flanges approaching the buffer stop. |
| **Hydraulic Buffer Stop** | §7.5 / §21 | Heavy structural iron A-frame at platform head (`X = 2.20 m`) with twin oleo-pneumatic buffer heads at `Z = 1.05 m` touching Locomotive `V_01` buffers (`TRK_10_BufferStop_*`). |
| **Overhead Catenary** | §7.1 / §15.1 | Copper contact wire suspended at `Z = 5.50 m ±0.02 m` from messenger wire (`Z = 6.30 m`) via droppers spaced every `7.50 m` (`CAT_ContactWire_5500mm`). |
| **Graham Deadbeat Escapement** | §8 / T3 | 30-tooth brass escape wheel and steel anchor pallet driving the `3.20 m` station clock (`240` parts per clock, hands set to `16:40:00`, animated seconds hand). |
| **Split-Flap Departure Board** | §8 / T3 / F27 | Mechanical schedule board (`BOARD_Frame_Main`) housing `240` individual flipping tiles (`6 rows × 40 cols`) driven directly from `nordbahnhof/design/TIMETABLE.json`. |

Independent non-owner acceptance remains PENDING. No self-review/vote.
