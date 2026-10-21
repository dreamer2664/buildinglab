#!/usr/bin/env python3
"""The five lines, their profile schedules and their declared falls.

Line lengths: the record gives 82 miles = 132 km for the intercepting network but does not
give it line by line; the allocation below is a modelled allocation, its basis stated per line
and adjudicated in CONFLICTS.md C-012. Profiles per segment cite REFERENCES.md rows (G2, F39).
"""
GEN_VERSION = "cloaca-gen/1.1.0"
MASTER_SEED = "cloaca-victoria-1858"

# profile families. wythes = radial brick widths (114 mm each): 2 -> 228 mm (9 in), 3 -> 342 mm.
PROFILES = {
 "ovoid-675": {"kind":"ovoid","r":0.675,"height_m":2.700,"width_m":1.350,"wythes":2,
   "cites":["R-022","R-023","R-142","R-043"],
   "note":"canonical egg, small end down; dry-weather flow rides the narrow invert (R-018)"},
 "ovoid-900": {"kind":"ovoid","r":0.900,"height_m":3.600,"width_m":1.800,"wythes":3,
   "cites":["R-022","R-026","R-043"],
   "note":"mid-reach of the high and middle level lines; record gives mains up to 11 ft (3.4 m)"},
 "ovoid-1050":{"kind":"ovoid","r":1.050,"height_m":4.200,"width_m":2.100,"wythes":3,
   "cites":["R-022","R-027","R-043"],
   "note":"lower reaches; northern high-level mains reaching 12 ft in height (R-027)"},
 "circ-2700": {"kind":"circle","d":2.700,"height_m":2.700,"width_m":2.700,"wythes":3,
   "cites":["R-024","R-043"],"note":"circular bore where the record shows it (F39)"},
 "circ-3400": {"kind":"circle","d":3.400,"height_m":3.400,"width_m":3.400,"wythes":3,
   "cites":["R-026","R-024","R-043"],"note":"outfall culvert, 11 ft (3.4 m) high (R-026)"},
 "rect-2740": {"kind":"rect","h":2.740,"w":2.740,"height_m":2.740,"width_m":2.740,"wythes":3,
   "cites":["R-024","R-104"],"note":"Abbey Mills inlet culverts, 3 x 9 ft x 9 ft brick-lined"},
}

# (line id, name, length km, fall m/km, invert start m, segment schedule [(from_chunk, to_chunk, profile)], basis)
LINES = [
 ("N-high","Northern High-Level + Northern Outfall",30.0,1.00,42.60,
   [(0,59,"ovoid-675"),(60,179,"ovoid-900"),(180,269,"ovoid-1050"),(270,299,"circ-3400")],
   "Hampstead Heath head via Highgate, Stoke Newington and Hackney Wick to Abbey Mills, then the Northern Outfall to the Beckton penstocks (R-008, R-010, R-027)"),
 ("N-mid","Northern Mid-Level + Northern Outfall (shared reach)",27.0,0.90,36.40,
   [(0,69,"ovoid-675"),(70,189,"ovoid-900"),(190,239,"ovoid-1050"),(240,269,"circ-3400")],
   "Kensal Green head via Kilburn, Camden and Old Ford to Abbey Mills and the outfall (R-008, R-027)"),
 ("N-low","Northern Low-Level (Victoria Embankment reach)",22.0,0.45,11.80,
   [(0,79,"ovoid-675"),(80,179,"ovoid-900"),(180,219,"rect-2740")],
   "Pimlico and Chelsea head, carried in the Victoria Embankment to Abbey Mills where the low-level flows are lifted (R-008, R-025, R-099, R-101)"),
 ("S-high","Southern High-Level + Southern Outfall",28.0,1.05,39.20,
   [(0,69,"ovoid-675"),(70,189,"ovoid-900"),(190,249,"ovoid-1050"),(250,279,"circ-3400")],
   "Putney and Brixton heads via Camberwell and Deptford, then the Southern Outfall to Crossness (R-010, R-078, R-080)"),
 ("S-low","Southern Low-Level (Albert Embankment reach)",25.0,0.40,9.40,
   [(0,89,"ovoid-675"),(90,199,"ovoid-900"),(200,249,"rect-2740")],
   "Lambeth and Battersea head, carried in the Albert Embankment to Deptford and lifted there (R-025, R-100, R-102)"),
]

STATIONS = {  # pumping stations, with the engines the packet declares (8/4/6/4)
 "abbey_mills":{"line":"N-low","engines":8,"chunk":219,"cites":["R-083","R-084","R-085","R-096"]},
 "crossness":  {"line":"S-high","engines":4,"chunk":279,"cites":["R-063","R-064","R-068","R-076"]},
 "deptford":   {"line":"S-low","engines":6,"chunk":249,"cites":["R-102","R-105"]},
 "chelsea":    {"line":"N-low","chunk":0,"engines":4,"cites":["R-103","R-105"]},
}
OVERFLOWS = [  # six storm reliefs, actuated by sim conditions alone (G7, F38)
 {"id":"OF-1","line":"N-high","chunk":120,"cites":["R-025"]},
 {"id":"OF-2","line":"N-mid","chunk":150,"cites":["R-025"]},
 {"id":"OF-3","line":"N-low","chunk":95, "cites":["R-101"]},
 {"id":"OF-4","line":"S-high","chunk":140,"cites":["R-025"]},
 {"id":"OF-5","line":"S-low","chunk":110,"cites":["R-100"]},
 {"id":"OF-6","line":"S-high","chunk":230,"cites":["R-078"]},
]
GAUGES = [  # six gauges for the 28-day validation (G7)
 {"id":"G1","name":"London Bridge (Tower Pier)","pla_code":"0113","lat":51.50688,"lon":-0.07737,"km_from_london_bridge":0.0,"cites":["R-112","R-113"]},
 {"id":"G2","name":"Tower Pier","pla_code":"0113b","km_from_london_bridge":0.53,"cites":["R-117"]},
 {"id":"G3","name":"Greenwich","km_from_london_bridge":6.6,"cites":["R-117"]},
 {"id":"G4","name":"Erith / Crossness approach","km_from_london_bridge":21.0,"cites":["R-078","R-117"]},
 {"id":"G5","name":"Barking Creek / Beckton approach","km_from_london_bridge":17.0,"cites":["R-010","R-117"]},
 {"id":"G6","name":"Putney","km_from_london_bridge":-10.0,"cites":["R-117"]},
]
if __name__ == "__main__":
    tot = sum(l[2] for l in LINES); ch = sum(int(l[2]*10) for l in LINES)
    print(f"lines: {len(LINES)}  total {tot:.1f} km  chunks {ch}")
    for lid,name,km,f,z0,segs,basis in LINES:
        n=int(km*10)
        assert segs[-1][1]==n-1, (lid,segs[-1][1],n-1)
        print(f"  {lid:7s} {km:5.1f} km  {n:4d} chunks  fall {f:.2f} m/km -> {f*km:6.2f} m total  invert {z0:.2f} -> {z0-f*km:.2f} m")
    print("profiles:", len(PROFILES), " stations:", len(STATIONS), " overflows:", len(OVERFLOWS), " gauges:", len(GAUGES))
