# PERIOD — the 1858–1875 truth law and how it is enforced

The commission's world ends in 1875. Anything later is an anachronism, and G8 re-opens on one.

## Light

Gas, fire and daylight — nothing else. `validate/v_light.py` fails a render whose declared sources
are empty, name anything electric, or name anything outside the allowed family (gas, fire, flame,
daylight, sun, sky, overcast, moonlight, candle, lantern, oil lamp, brazier, forge). `v_period.py`
independently scans the same rows for electric vocabulary. Each render row lists its period-true
source in `light_sources` and the Blender primitive that emits it in `primitives`, so the register
never conflates the flame with the point light standing in for it.

Practical notes carried in the register: a gas jet in a wall lantern is a POINT primitive of 18–150 W
with a warm colour and a small radius, plus an iron lantern body and a flame cone with emission;
daylight down a shaft is a large-radius cool source; world strength stands for sky only.

## Out of period — rejected on sight

- Triple-expansion engines (the Crossness rebuild of 1895–1901). The engines are modelled in their
  1865 single-cylinder double-acting rotative beam state: 48 in bore × 9 ft stroke historical,
  carried in this commission as 3.05 m beam stroke per C-002.
- Electric light of any kind, including arc lamps (trial installations postdate the window).
- Portland-cement-only brickwork: the period is lime mortar with Portland cement rising through it;
  joints are modelled as mortar, never as bare shadow gaps in finals.
- Reinforced concrete, steel joists, asbestos, aluminium, plywood, PVC.
- Signage in sans-serif faces; corporate logos; any date later than 1875 on a board.
- Clothing: no synthetic fibre, no zip, no wristwatch, no high-visibility material. Navvies in
  fustian, moleskin, worsted; leather boots; cloth caps or felt hats; women in cotton or wool with
  shawl or bonnet per the occupation schedule.
- Fasteners: wrought and cast iron, brass, leather, timber pegs. No hex heads of the modern profile,
  no Phillips, no nylon ties.

## In period — required where the subject appears

- Hand-made and early machine-pressed London stock brick, grey-yellow, lime bloom, soot bands above
  the splash line, sediment crust at the invert (WEAR_SCHEDULE.md; the wet line is derived from the
  chunk's HYDRAULICS depth at lay time, D-014).
- Wrought-iron penstocks and flap valves at the overflows, timber centring in the yards, navvy
  barrows and stages, gas lanterns on the embankment lampposts (312 of them), horse ginns and steam
  winding gear at the shafts.
- Engine-house architecture per C. H. Driver: Romanesque/Byzantine cast and wrought iron, coloured
  brick and Portland stone dressings at Abbey Mills and Crossness.
- Boilers: Cornish/Lancashire type, double furnace, hand-fired, with gauge glasses and safety valves
  of the weight-and-lever pattern.

## Enforcement

`v_period` audits every render row's light sources and the brick palette of a built chunk against the
stock family; the 100-view random anachronism audit of G8 runs over the final set at Stage I and is
recorded view by view. A view that fails is re-rendered or withdrawn; it is not quietly kept.
